#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
case "${1:-}" in ''|--reuse-voice) ;; *) echo 'Usage: bash scripts/build.sh [--reuse-voice]' >&2; exit 2;; esac
[[ -f .runtime/tools.sh ]] || bash scripts/setup.sh
source .runtime/tools.sh
if [[ "${1:-}" != --reuse-voice ]]; then
  "$VOICE_PYTHON" src/voice.py
fi
"$RENDER_PYTHON" src/mix.py
"$RENDER_PYTHON" src/render.py --width "${WIDTH:-720}"
"$RENDER_PYTHON" src/finish.py
"$RENDER_PYTHON" scripts/verify.py
