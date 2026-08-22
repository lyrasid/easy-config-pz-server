#!/usr/bin/env bash
# Rebuilds dist/console-duo.html from source/*.ini/*.lua + build/*.py.
#
# Usage:
#   ./build.sh
#
# What it does:
#   1. parse.py    reads source/Duo.ini and source/Duo_SandboxVars.lua,
#                   extracts every field (key, current value, comment,
#                   min/max, enum options) and writes a "template" copy of
#                   each file with every editable value replaced by a
#                   unique @@PLACEHOLDER@@ token -> generated/
#   2. assemble.py  merges that extraction with the hand-written
#                   translations/explanations in build/ini_meta.py and
#                   build/lua_meta_*.py, and writes generated/bundle.json
#                   (the full schema the web page reads).
#   3. inject.py    embeds generated/bundle.json into dist/console-duo-shell.html
#                   (the HTML/CSS/JS shell) to produce dist/console-duo.html,
#                   the finished, self-contained, single-file page.
set -euo pipefail
cd "$(dirname "$0")/build"
python3 parse.py
python3 assemble.py
python3 inject.py
echo "Build complete -> dist/console-duo.html"
