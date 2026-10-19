#!/bin/sh
# Local publication gate; no GitHub Actions write/scope is needed.
set -eu
python3 tools/audio.py validate --decode
python3 tools/audio.py report
python3 tools/build.py
python3 tools/build.py --check
python3 tools/check.py
python3 -m unittest discover -s tools -p 'test_*.py'
python3 -m unittest discover -s labs -p 'test_*.py'
node tools/test_app.js
node tools/test_podcast.js
node --check podcast.js
git diff --check
