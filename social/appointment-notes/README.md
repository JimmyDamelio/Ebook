# Social clip: "3 things to write down before a perimenopause appointment"

27.8 s, 1080×1920 (9:16), 30 fps. Useful/save pillar; CTA = free "Before Your Appointment" checklist.
**Watch:** [`appointment-notes-9x16.mp4`](appointment-notes-9x16.mp4)

**Why this topic:** it is the most frequent question on r/Perimenopause ("What questions should I ask?", "How to advocate for myself", "Write down your symptoms, rate them"). It leads to the free checklist, so it fills the email list.

**Picture:** one notebook page stays on screen. The 3-item list shows faintly from frame 0 so viewers see what's coming, a pencil writes each part, and each item is ticked when it's done. Then three weeks of pages appear, then the checklist end card. Captions are word by word (large, high contrast, for 40+ readers).

## Post copy
**TikTok**
```
3 things to write down before a perimenopause appointment 📝

1. Symptoms: how often, and how much they affect daily life
2. Cycle: the dates, and any changes in timing or flow
3. Questions: and what you'd like to leave the room with

Save this for later. Free printable checklist in bio 🌿

General health education. Not a substitute for medical advice.

#perimenopause #menopause #womenshealth #over40 #perimenopausesupport #midlifewomen #doctorappointment
```
**Instagram / Facebook:** the same text, with "link in bio" and the hashtags #perimenopause #menopause #womenshealth #womenover40 #midlifewomen.
Pinned first comment: "Which one is hardest to remember on the day: symptoms, dates or questions? 👇"

## Sound
earshot critique: launch-grade (21 of 22 metrics), −14.5 LUFS. Effects: pencil scribbles (synthesised), ticks / taps / clicks from the earshot bank (fitted from CC0 recordings).

## Rebuild (from this folder)
```bash
python3 ../lib/vo.py gen && python3 ../lib/vo.py align   # voice clips + words.js
python3 ../lib/music.py                                   # audio.wav from score.json + vo.json
node ../lib/render.mjs frames 30 6
ffmpeg -framerate 30 -i frames/f_%05d.png -i audio.wav -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -tune animation \
  -c:a aac -b:a 192k -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 44100 -movflags +faststart -shortest appointment-notes-9x16.mp4
```
