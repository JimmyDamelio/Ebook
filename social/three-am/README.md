# Social clip: "3 a.m." — The Perimenopause Companion

27.5 s, 1080×1920 (9:16), 30 fps, for TikTok, Instagram Reels and Facebook Reels. Voice-over, burned-in captions, music, and a loop at the end back to the first frame.
Strategy and script by the TikTok Strategist agent; picture drawn in code (Canvas 2D, same watercolour/ink style as `trailer/`), music synthesised in Python, voice by Kokoro (`af_heart`).

**Watch:** [`three-am-9x16.mp4`](three-am-9x16.mp4)

## Strategy
Angle: "from scattered moments to one clear page". The video follows a familiar moment (3 a.m.) to a pattern on a 30-day grid, then to one summary page for the appointment. The hook is a moment people recognise, shown from frame 0, and it never asks the viewer about her health. Words keep people watching, and the grid filling leaves a question open until the circle closes it. The product arrives as the answer. CTA: soft "link in bio". The end wipes back to the opening frame so the clip loops.

A/B hooks to test later: (A) open on the circled grid, "What 30 days of notes can show."; (B) open on the summary page, "What to bring to the appointment."

## Storyboard
| Time | Picture | On-screen text / voice |
|---|---|---|
| 0–3.0 s | Night window, moon, bedside clock 3:07 (lit on frame 0) | "Wide awake. Again." |
| 3.0–6.4 s | Words rise: heat shimmer, fog, flat line, zig-zag | Hot. Foggy. Flat. Tired but wired. |
| 6.4–10.0 s | Scattered scraps: notes, calendar corner, sticky "?" | Perimenopause can bring / changes that come and go. |
| 10.0–14.2 s | 30-day grid fills, moon days circled | Written down, day by day, / a pattern can appear. |
| 14.2–19.8 s | The book, daily tracker page, sources stamp | The Perimenopause Companion / Guide + 30-day printable workbook |
| 19.8–23.5 s | 30-Day Summary page ticked, appointment ringed | A 30-Day Summary, / ready for the appointment. |
| 23.5–27.5 s | End card: wordmark, book, $24 · Link in bio, disclaimer; wipe back to frame 0 | Sage and Season. Link in bio. |

Text stays inside x 125–925, y 230–1450 (clear of the platform buttons and captions).

## Post copy
**TikTok** (104 chars): 3 a.m. wake-ups, fog, tired but wired. A calm, printable way to see the pattern before the appointment.
#perimenopause #menopause #womenshealth #over40 #perimenopausesupport

**Instagram / Facebook:**
```
3 a.m. wake-ups. Foggy days. Tired but wired.
Perimenopause can bring changes that come and go, and they're easy to forget by the time of an appointment.
The Perimenopause Companion is a calm, evidence-based guide (10 chapters) plus a 30-day printable workbook with a daily tracker and a 30-Day Summary page to bring along. Checked against NICE, NHS, ACOG, The Menopause Society and NIH. No miracle claims. No fear.
Link in bio. Not ready yet? The free "Before Your Appointment" checklist is there too.
General health education. Not a substitute for medical advice.
#perimenopause #menopause #womenshealth #womenover40 #midlifewomen
```

## Sound check (earshot critique)
Launch-grade: 22 of 23 metrics in the range of professional launch films, −14.6 LUFS integrated, −1.4 dBTP true peak. The one minor note is a near-mono image, which comes from the centred voice-over.

## Rebuild
Needs Node + Playwright (Chromium), Python 3 with numpy, soundfile and kokoro-onnx (`sh setup-media.sh`), and ffmpeg.
```bash
python3 voice.py                       # -> vo/*.wav
python3 audio.py                       # -> audio.wav (music + voice, ducked)
node render.mjs frames 30 6            # -> frames/ (825 PNGs)
ffmpeg -framerate 30 -i frames/f_%05d.png -i audio.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -tune animation \
  -c:a aac -b:a 192k -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 44100 -movflags +faststart -shortest three-am-9x16.mp4
```
Preview: open `film.html?play`, or `film.html?t=13.9` for one moment. Stills: `node render.mjs stills 3.5 13.9 ...`.
