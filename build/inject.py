# -*- coding: utf-8 -*-
"""
Injects the generated config schema (../generated/bundle.json) into the
shell template (../dist/console-duo-shell.html) to produce the final
self-contained artifact (../dist/console-duo.html).

Run this after parse.py and assemble.py (or just use build.sh, which runs
all three in order).
"""
import json

with open('../generated/bundle.json', encoding='utf-8') as f:
    bundle = json.load(f)

# Compact JSON, safe for embedding inside a <script> tag (escape "</" so a
# literal "</script>" can never appear inside the JSON string content).
json_text = json.dumps(bundle, ensure_ascii=False, separators=(',', ':'))
json_text = json_text.replace('</', '<\\/')

with open('../dist/console-duo-shell.html', encoding='utf-8') as f:
    shell = f.read()

marker = '/*__BUNDLE_JSON__*/'
if marker not in shell:
    raise SystemExit(f'marker {marker!r} not found in console-duo-shell.html')

final = shell.replace(marker, json_text)

with open('../dist/console-duo.html', 'w', encoding='utf-8') as f:
    f.write(final)

print('wrote ../dist/console-duo.html (', len(final.encode('utf-8')), 'bytes )')
