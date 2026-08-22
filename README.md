# Console Duo

Editor visual das configurações do servidor Project Zomboid **Duo** — o
`server.ini` e o `SandboxVars.lua`, num painel só, com todas as
configurações explicadas em português e o arquivo pronto pra copiar de
volta pro servidor a cada mudança.

Publicado como artifact: https://claude.ai/code/artifact/5d279e7b-a906-43d0-a74f-833ff656c670

## Estrutura do projeto

```
console-duo/
├── source/                     os .ini/.lua originais do servidor (snapshot)
│   ├── Duo.ini
│   └── Duo_SandboxVars.lua
├── build/                      pipeline em Python que gera a página
│   ├── parse.py                 extrai cada config dos arquivos-fonte
│   ├── translate.py              dicionário de tradução das opções (EN→PT)
│   ├── ini_meta.py               rótulos/explicações de cada config do .ini
│   ├── lua_meta_1.py … 6.py      idem para o SandboxVars.lua (dividido em partes)
│   ├── assemble.py               junta tudo num único bundle.json
│   └── inject.py                 injeta o bundle.json no shell HTML
├── dist/
│   ├── console-duo-shell.html   o HTML/CSS/JS da página (o "app" em si)
│   └── console-duo.html         arquivo final, pronto pra publicar/abrir
├── generated/                   arquivos intermediários (podem ser apagados)
└── build.sh                     roda o pipeline inteiro de uma vez
```

## Como funciona

1. **`parse.py`** lê `source/Duo.ini` e `source/Duo_SandboxVars.lua` linha a
   linha. Pra cada configuração, extrai a chave, o valor atual, o comentário
   (min/max/default, opções numeradas tipo `1 = Never`, `2 = Rare`…), e monta
   uma cópia "template" de cada arquivo com todo valor editável trocado por
   um token único (`@@INI_PVP@@`, `@@LUA_MultiplierConfig_Global@@` etc.).
   Isso garante que o arquivo gerado no fim é **byte a byte igual** ao
   original em qualquer campo que não foi mexido — o motor não reescreve o
   arquivo do zero, só troca valores dentro do arquivo real.

2. **`ini_meta.py`** e **`lua_meta_*.py`** são dicionários escritos à mão
   com o rótulo em português e a explicação de cada configuração (mais
   detalhada que o tooltip do próprio jogo), organizados em categorias.
   `translate.py` traduz as opções de múltipla escolha extraídas
   automaticamente dos comentários do `.lua` (`Never` → `Nunca`,
   `Extremely Rare` → `Extremamente raro`, etc.).

3. **`assemble.py`** junta a extração automática com essas explicações
   escritas à mão e valida que toda configuração dos arquivos-fonte tem uma
   entrada correspondente (o script recusa rodar se faltar alguma). Gera
   `generated/bundle.json`.

4. **`inject.py`** cola o `bundle.json` dentro do `dist/console-duo-shell.html`
   (que tem um marcador `/*__BUNDLE_JSON__*/`) e produz o arquivo final
   `dist/console-duo.html` — uma página HTML autocontida (sem dependências
   externas além das fontes do Google Fonts), pronta pra publicar como
   artifact ou abrir direto no navegador.

## Rebuild

```bash
./build.sh
```

Isso roda os três scripts em sequência e regrava `dist/console-duo.html`.

## Pra continuar mexendo

- **Mudar a explicação/categoria de uma config**: edite o dicionário
  correspondente em `build/ini_meta.py` ou `build/lua_meta_*.py`, depois
  rode `./build.sh`.
- **Mudar o visual/comportamento da página** (CSS, layout, lógica de busca,
  geração de saída etc.): edite `dist/console-duo-shell.html` diretamente
  — é HTML/CSS/JS puro, sem framework. Depois rode `./build.sh` de novo
  (ele relê o shell e reinjeta o bundle).
- **Atualizar com uma config nova do servidor** (se o Bebel adicionar um
  mod que crie novas chaves, por exemplo): substitua os arquivos em
  `source/`, rode `python3 build/parse.py` sozinho primeiro — ele avisa
  quais chaves novas não têm entrada em `ini_meta.py`/`lua_meta_*.py` — e
  adicione as que faltarem antes de rodar o `assemble.py`.
- **Publicar a nova versão**: `dist/console-duo.html` é o arquivo que vai
  pro Artifact (ou qualquer outro host estático) — é 100% autocontido.

## Detalhe de segurança

Os campos `Password` (senha do servidor), `RCONPassword` e `DiscordToken`
nunca vêm pré-preenchidos com o valor real no `bundle.json`/na página —
mesmo que o arquivo `source/Duo.ini` tenha a senha em texto puro. Se você
deixar esses campos em branco na página, o arquivo gerado sai com um aviso
bem visível (`<<DEFINA_A_SENHA_AQUI>>`) no lugar do valor, pra nunca colar
sem querer um arquivo com senha vazia/perdida.
