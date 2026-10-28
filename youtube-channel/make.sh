#!/bin/sh
# Build one episode: sh make.sh episodes/001-paper-boat  ->  episodes/001-paper-boat/video.mp4
set -e
cd "$(dirname "$0")"
E="$1"
python3 "$E/audio.py" "$E/audio.wav"
node render.mjs "$E" frames 4
ffmpeg -y -loglevel error -framerate 30 -i "$E/frames/f_%05d.png" -i "$E/audio.wav" -c:v libx264 -crf 18 \
  -pix_fmt yuv420p -tune animation -af loudnorm=I=-14:TP=-1.5 -ar 44100 -c:a aac -b:a 192k -movflags +faststart -shortest "$E/video.mp4"
echo "$E/video.mp4"
