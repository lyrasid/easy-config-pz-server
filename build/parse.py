import re, json

# ---------- INI PARSER ----------
def parse_ini(path):
    fields = []
    template_lines = []
    comment_buf = []
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            comment_buf.append(stripped.lstrip('#').strip())
            template_lines.append(line)
            continue
        if stripped == '':
            comment_buf = []
            template_lines.append(line)
            continue
        m = re.match(r'^([A-Za-z0-9_]+)=(.*)$', line)
        if m:
            key, value = m.group(1), m.group(2)
            comment = ' '.join(comment_buf).strip()
            comment_buf = []
            placeholder = f'@@INI_{key}@@'
            template_lines.append(f'{key}={placeholder}')
            # extract min/max/default
            mm = re.search(r'Min:\s*(-?[\d.]+)\s*Max:\s*(-?[\d.]+)(?:\s*Default:\s*(-?[\d.]+))?', comment)
            minv = maxv = defv = None
            if mm:
                minv, maxv, defv = mm.group(1), mm.group(2), mm.group(3)
            is_bool = value in ('true', 'false')
            fields.append({
                'key': key,
                'value': value,
                'comment': comment,
                'is_bool': is_bool,
                'min': minv,
                'max': maxv,
                'default': defv,
            })
        else:
            template_lines.append(line)
    template = '\n'.join(template_lines)
    return fields, template

# ---------- LUA PARSER ----------
def parse_lua(path):
    fields = []
    template_lines = []
    comment_buf = []
    stack = []  # nesting stack of table names
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    enum_re = re.compile(r'^--\s*(\d+)\s*=\s*(.+)$')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('--'):
            comment_buf.append(stripped.lstrip('-').strip())
            template_lines.append(line)
            continue
        if stripped == '' or stripped == 'SandboxVars = {' or stripped == '}':
            if stripped == '}' and stack:
                stack.pop()
            comment_buf = []
            template_lines.append(line)
            continue
        # nested table open: Key = {
        mtab = re.match(r'^([A-Za-z0-9_]+)\s*=\s*\{$', stripped)
        if mtab:
            stack.append(mtab.group(1))
            comment_buf = []
            template_lines.append(line)
            continue
        if stripped == '},':
            if stack:
                stack.pop()
            comment_buf = []
            template_lines.append(line)
            continue
        # key = value,  (value can be number, true/false, "string")
        mkv = re.match(r'^([A-Za-z0-9_]+)\s*=\s*(.+?),?$', stripped)
        if mkv:
            key, value = mkv.group(1), mkv.group(2)
            value = value.rstrip(',')
            if key == 'VERSION' and not stack:
                # internal SandboxVars format version marker - not a gameplay
                # setting, leave it baked into the template untouched so no
                # placeholder is left unresolved in the generated output.
                comment_buf = []
                template_lines.append(line)
                continue
            path_parts = stack + [key]
            fpath = '.'.join(path_parts)
            comment_lines = comment_buf
            comment_buf = []
            # separate enum option lines from general description lines
            options = []
            desc_lines = []
            for cl in comment_lines:
                em = enum_re.match('-- ' + cl) if not cl.startswith('--') else None
                # cl already stripped of leading --, so re-check against raw pattern differently
                em2 = re.match(r'^(\d+)\s*=\s*(.+)$', cl)
                if em2:
                    options.append((em2.group(1), em2.group(2)))
                else:
                    desc_lines.append(cl)
            comment = ' '.join(desc_lines).strip()
            mm = re.search(r'Min:\s*(-?[\d.]+)\s*Max:\s*(-?[\d.]+)(?:\s*Default:\s*(-?[\d.]+))?', comment)
            minv = maxv = defv = None
            if mm:
                minv, maxv, defv = mm.group(1), mm.group(2), mm.group(3)
            is_bool = value in ('true', 'false')
            is_string = value.startswith('"') and value.endswith('"')
            placeholder = '@@LUA_' + fpath.replace('.', '_') + '@@'
            # preserve quotes for strings
            if is_string:
                inner = value[1:-1]
                new_line = line.replace('"' + inner + '"', '"' + placeholder + '"', 1)
            else:
                new_line = line.replace('= ' + value, '= ' + placeholder, 1)
                if new_line == line:
                    # fallback replace last occurrence of value
                    idx = line.rfind(value)
                    new_line = line[:idx] + placeholder + line[idx+len(value):]
            template_lines.append(new_line)
            fields.append({
                'path': fpath,
                'value': value.strip('"') if is_string else value,
                'comment': comment,
                'options': options,
                'is_bool': is_bool,
                'is_string': is_string,
                'min': minv,
                'max': maxv,
                'default': defv,
            })
            continue
        template_lines.append(line)
    template = '\n'.join(template_lines)
    return fields, template

ini_fields, ini_template = parse_ini('../source/Duo.ini')
lua_fields, lua_template = parse_lua('../source/Duo_SandboxVars.lua')

with open('../generated/ini_fields.json', 'w', encoding='utf-8') as f:
    json.dump(ini_fields, f, ensure_ascii=False, indent=1)
with open('../generated/lua_fields.json', 'w', encoding='utf-8') as f:
    json.dump(lua_fields, f, ensure_ascii=False, indent=1)
with open('../generated/ini_template.txt', 'w', encoding='utf-8') as f:
    f.write(ini_template)
with open('../generated/lua_template.txt', 'w', encoding='utf-8') as f:
    f.write(lua_template)

print('INI fields:', len(ini_fields))
print('LUA fields:', len(lua_fields))
