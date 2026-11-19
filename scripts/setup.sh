#!/usr/bin/env bash
set -euo pipefail
project="$(cd "$(dirname "$0")/.." && pwd)"
cd "$project"
mkdir -p .runtime
render_py="${RENDER_PYTHON:-/usr/bin/python3}"
voice_py="${VOICE_PYTHON:-python3}"
font="${DEVANAGARI_FONT:-/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf}"
render_ready() {
  command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null &&
  "$render_py" -c 'import cairo, numpy; from PIL import features; assert features.check("raqm")' 2>/dev/null && test -r "$font"
}
if ! render_ready; then
  packages=(ffmpeg python3 python3-venv python3-cairo python3-numpy python3-pil fonts-noto-core libsndfile1 espeak-ng)
  admin=()
  if [[ "$(id -u)" != 0 ]]; then
    if command -v sudo >/dev/null && sudo -n true 2>/dev/null; then admin=(sudo -n)
    else
      echo "This environment needs the Debian/Ubuntu packages: ${packages[*]}. Use a Linux sandbox with those packages or package installation access." >&2
      exit 2
    fi
  fi
  command -v apt-get >/dev/null || { echo "Use Debian/Ubuntu or install the listed Linux rendering dependencies first." >&2; exit 2; }
  "${admin[@]}" apt-get update
  "${admin[@]}" apt-get install -y "${packages[@]}"
fi
render_ready || { echo "Check RENDER_PYTHON and DEVANAGARI_FONT." >&2; exit 2; }
"$render_py" scripts/get_models.py
(
 cd models
 sha256sum -c SHA256SUMS
)
voice_ready() {
  "$1" -c 'import sys, soundfile, onnxruntime; from kokoro_onnx import Kokoro; from importlib.metadata import version; assert (3,10)<=sys.version_info[:2]<=(3,13) and version("kokoro-onnx")=="0.6.1"' 2>/dev/null
}
if ! voice_ready "$voice_py"; then
  if ! voice_ready .runtime/voice/bin/python; then
    "$voice_py" -c 'import sys; assert (3,10)<=sys.version_info[:2]<=(3,13), "Use Python 3.10 to 3.13 for Kokoro"'
    "$voice_py" -m venv .runtime/voice || { echo 'Install the matching python3-venv package or set VOICE_PYTHON to a working environment.' >&2; exit 2; }
    .runtime/voice/bin/python -m pip install -r requirements-voice.txt
  fi
  voice_py="$project/.runtime/voice/bin/python"
fi
"$voice_py" scripts/check_voice.py
"$render_py" -c 'from PIL import ImageFont; import sys; f=ImageFont.truetype(sys.argv[1],32); assert f.getlength("नाव",language="hi")>10' "$font"
ffmpeg -hide_banner -encoders 2>/dev/null > .runtime/encoders.txt
grep -q libx264 .runtime/encoders.txt
grep -q ' aac ' .runtime/encoders.txt
printf 'RENDER_PYTHON=%q\nVOICE_PYTHON=%q\nexport DEVANAGARI_FONT=%q\n' "$(command -v "$render_py")" "$(command -v "$voice_py")" "$font" > .runtime/tools.sh
echo 'Setup passed. Run bash scripts/build.sh from this folder.'
