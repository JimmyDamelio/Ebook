#!/bin/sh
# Installs the video/voice toolchain in a fresh cloud session (~1 min).
set -e
cd "$(dirname "$0")"
pip install -q kokoro-onnx piper-tts soundfile numpy
M=/root/tts-models; mkdir -p $M
[ -f $M/kokoro-v1.0.onnx ] || curl -sSL -o $M/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f $M/voices-v1.0.bin ] || curl -sSL -o $M/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
for v in fr/fr_FR/siwis/medium/fr_FR-siwis-medium en/en_US/lessac/medium/en_US-lessac-medium; do
  n=$(basename $v)
  [ -f $M/$n.onnx ] || { curl -sSL -o $M/$n.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/$v.onnx"; curl -sSL -o $M/$n.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/$v.onnx.json"; }
done
(cd remotion && npm install --silent)
echo "media toolchain ready"
