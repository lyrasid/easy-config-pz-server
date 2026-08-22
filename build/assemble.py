# -*- coding: utf-8 -*-
import json, sys, re
sys.path.insert(0, '.')
from translate import tr
from ini_meta import INI_META, INI_SECTIONS
from lua_meta_1 import LUA_META_1
from lua_meta_2 import LUA_META_2
from lua_meta_3 import LUA_META_3
from lua_meta_4 import LUA_META_4
from lua_meta_5 import LUA_META_5
from lua_meta_6 import LUA_META_6

LUA_META = {}
for d in [LUA_META_1, LUA_META_2, LUA_META_3, LUA_META_4, LUA_META_5, LUA_META_6]:
    LUA_META.update(d)

LUA_SECTIONS = [
 "Multiplicadores de XP por habilidade",
 "População de zumbis",
 "Loot — quantidade por categoria",
 "Loot — regras gerais",
 "Comportamento dos zumbis",
 "População avançada (Zombie Config)",
 "Sobrevivência do personagem",
 "Combate e armas de fogo",
 "Tempo e calendário",
 "Clima",
 "Infraestrutura e serviços",
 "Natureza, agricultura e pesca",
 "Animais",
 "Veículos",
 "Mapa e interface",
 "Porões e eventos do mundo",
 "Leitura, conhecimento e diversos",
]

SENSITIVE_INI = {"Password", "RCONPassword", "DiscordToken"}

def decimals_of(value_str):
    if '.' in value_str:
        return len(value_str.split('.')[1])
    return 0

def build_ini():
    data = json.load(open('../generated/ini_fields.json', encoding='utf-8'))
    out = []
    for f in data:
        key = f['key']
        meta = INI_META[key]
        sensitive = key in SENSITIVE_INI
        entry = {
            'id': 'ini.' + key,
            'ph': f'@@INI_{key}@@',
            'section': meta['section'],
            'label': meta['label'],
            'desc': meta['desc'],
            'value': '' if sensitive else f['value'],
            'sensitive': sensitive,
        }
        if sensitive:
            entry['type'] = 'password'
        elif 'type' in meta and meta['type'] == 'select':
            entry['type'] = 'select'
            entry['options'] = [{'v': v, 'l': l} for v, l in meta['options']]
        elif f['is_bool']:
            entry['type'] = 'toggle'
        elif f['min'] is not None and f['max'] is not None:
            entry['type'] = 'range'
            entry['min'] = float(f['min'])
            entry['max'] = float(f['max'])
            entry['decimals'] = decimals_of(f['value'])
        else:
            entry['type'] = 'text'
        out.append(entry)
    return out

def build_lua():
    data = json.load(open('../generated/lua_fields.json', encoding='utf-8'))
    out = []
    for f in data:
        path = f['path']
        if path == 'VERSION':
            continue
        meta = LUA_META[path]
        entry = {
            'id': 'lua.' + path,
            'ph': '@@LUA_' + path.replace('.', '_') + '@@',
            'section': meta['section'],
            'label': meta['label'],
            'desc': meta['desc'],
            'value': f['value'],
        }
        if f['is_bool']:
            entry['type'] = 'toggle'
        elif f['options']:
            entry['type'] = 'select'
            entry['options'] = [{'v': v, 'l': tr(l)} for v, l in f['options']]
        elif f['min'] is not None and f['max'] is not None:
            entry['type'] = 'range'
            entry['min'] = float(f['min'])
            entry['max'] = float(f['max'])
            entry['decimals'] = decimals_of(f['value'])
        elif f['is_string']:
            entry['type'] = 'text'
        else:
            # numeric without explicit min/max comment - infer a reasonable range
            entry['type'] = 'text'
        out.append(entry)
    return out

ini_schema = build_ini()
lua_schema = build_lua()

with open('../generated/ini_template.txt', encoding='utf-8') as fh:
    ini_template = fh.read()
with open('../generated/lua_template.txt', encoding='utf-8') as fh:
    lua_template = fh.read()

bundle = {
    'iniSections': INI_SECTIONS,
    'luaSections': LUA_SECTIONS,
    'iniFields': ini_schema,
    'luaFields': lua_schema,
    'iniTemplate': ini_template,
    'luaTemplate': lua_template,
}

with open('../generated/bundle.json', 'w', encoding='utf-8') as fh:
    json.dump(bundle, fh, ensure_ascii=False)

# sanity report
print('ini fields:', len(ini_schema))
print('lua fields:', len(lua_schema))
types = {}
for e in ini_schema + lua_schema:
    types[e['type']] = types.get(e['type'], 0) + 1
print('type counts:', types)
# check every field with type range/select/text has value substitution possible
missing_ph = [e['id'] for e in ini_schema if e['ph'] not in ini_template]
missing_ph += [e['id'] for e in lua_schema if e['ph'] not in lua_template]
print('placeholders not found in template:', missing_ph)
