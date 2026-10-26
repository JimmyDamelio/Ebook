# Launch trailer: The Perimenopause Companion

A 30-second launch trailer (1920×1080, 30 fps, stereo) for *The Perimenopause Companion*, by Sage & Season. All of it is code: the picture (Canvas 2D, watercolour and ink style) and the music (synthesised in Python).

**Watch:** [`trailer.mp4`](trailer.mp4)

## Storyboard

| Time | Scene |
|---|---|
| 0–5 s | Night, 3:06 → 3:07 a.m. "Awake again. Hot when no one else is." |
| 5–10 s | Words float up on paper (foggy, flat, tired but wired…) → "Something feels different." |
| 10–14.5 s | A 30-day grid fills in and the pattern gets circled. "What if you could see the pattern?" |
| 14.5–20 s | The book appears: 10 chapters, 30-day workbook, A4 & US Letter |
| 20–25 s | Daily tracker · checked against NICE, NHS, ACOG, The Menopause Society, NIH · "No miracle claims. No fear." |
| 25–30 s | The 30-Day Summary for the appointment → end card with the link and the price |

## Rebuild it

Needs Node, Playwright (Chromium), Python 3 with numpy, and ffmpeg.

```bash
python3 audio.py                       # -> audio.wav
node render.mjs frames 30 6            # -> frames/ (900 PNGs)
ffmpeg -framerate 30 -i frames/f_%05d.png -i audio.wav -c:v libx264 -crf 18 \
  -pix_fmt yuv420p -tune animation -c:a aac -b:a 192k -movflags +faststart -shortest trailer.mp4
```

Preview in a browser: open `film.html?play` (or `film.html?t=18.5` for a single moment).
Fonts: Fraunces and Caveat (SIL Open Font License).
