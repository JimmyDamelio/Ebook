---
name: trailer-video
description: Make a short promo video, trailer, teaser or animated explainer (MP4) entirely in code for Sage & Season products, e.g. "make a 9:16 version of the trailer", "make a trailer for the workbook", "15-second ad", "animated cover". Picture is drawn in a browser canvas, music is synthesised in Python, ffmpeg joins them.
---

# Code-made trailers

The reference film is `trailer/` (30 s launch trailer for *The Perimenopause Companion*). Start from its code: `trailer/film.html` (all visuals), `trailer/audio.py` (score), `trailer/render.mjs` (frame renderer). Its README has the storyboard and the build commands.

## Workflow
1. **Get the facts.** Product copy comes from Gumroad (`mcp__Gumroad__get_product`); never invent claims, numbers or medical promises.
2. **Storyboard first**: a table of time → scene → on-screen text, 4–7 scenes, one idea each. Show it before coding if the brief is open.
3. **Build** a copy of `trailer/` in a new folder (e.g. `trailer-9x16/`). Every frame is a pure function `renderAt(t)`; keep everything deterministic (seeded `mulberry` RNG, `BOIL = floor(t*8)` for the hand-drawn line boil).
4. **Check stills before the full render**: `node render.mjs stills 3.5 8 14 ...`, tile them with ffmpeg (`tile=3x4`) and look at the sheet. Fix, re-check. Look for empty moments between beats, overlaps, low-contrast text, hard gradient edges.
5. **Render**: `python3 audio.py`, `node render.mjs frames 30 6`, then the ffmpeg command in `trailer/README.md`. Re-check a contact sheet of the final MP4 (`fps=1/2.5,tile=4x3`).
6. Send the MP4 to the user, commit sources + MP4 (frames/ and audio.wav are git-ignored), push.

## Gotchas learned
- Canvas gradients must fade to the *same colour* at alpha 0 (`rgba(r,g,b,0)`), never `rgba(0,0,0,0)`: otherwise the paper turns muddy grey.
- Drawing helpers (`ink`, `text`, `wash`, `leaf`) multiply the current `globalAlpha`; keep it that way so group fades work.
- Fonts are local woff2 in `trailer/fonts/` (Fraunces, Caveat); `window.ready` waits for them.
- Chromium comes with Playwright (`require('playwright')`); no GPU needed for Canvas 2D. ~1.5 min to render 900 frames with 6 workers.

## House style (Sage & Season)
- Watercolour washes + boiling ink lines on warm paper, film grain, soft vignette, slow camera push.
- Palette: paper `#F3ECDF`, ink `#2F3A33`, sage `#8EA685` / `#5C7658`, terracotta `#C77B5C`, blush `#E9BCA4`, gold `#D8A55B`, night `#18222D`.
- Type: Fraunces (light, italic for emphasis), Caveat for handwritten notes.
- Tone: calm, warm, honest. No fear-based hooks, no miracle claims. Health products end with "General health education. Not a substitute for medical advice."
- Music: soft pad + arpeggiated piano in D major, bell accents on key beats, paper swooshes on transitions.

## Voice-over and Remotion
- First run `sh setup-media.sh` (fresh sessions lose installed packages and models).
- **Kokoro** (best quality, English + French `ff_siwis`): `Kokoro('/root/tts-models/kokoro-v1.0.onnx','/root/tts-models/voices-v1.0.bin').create(text, voice='af_heart', speed=.95, lang='en-us')`. Good brand voices: `af_heart`, `af_bella`, `bf_emma` (British). Samples in `voice-samples/`.
- **Piper** (fast, light): `echo "text" | python3 -m piper -m /root/tts-models/fr_FR-siwis-medium.onnx -f out.wav`.
- Time scenes to the voice: generate the voice first, read its durations, then set scene timings.
- **Remotion** (React video) lives in `remotion/`: `npx remotion render src/index.ts Teaser out/x.mp4`. Good for text-led, social and templated videos; the canvas approach in `trailer/` is better for painterly hand-made looks.

## Other styles
For a different look, take inspiration from these open libraries (clone to the scratchpad, read the style guide, adapt): lemomo-ai/lemo-opuscar (59 film styles + a skill), Vincentwei1021/mg-styles-15 (15 motion-design styles with prompts and source), JohnHeibel/ClaudeAnimationBase (p5.brush character animation), mexicat/pdoom-video (Three.js lyric video), joeseesun/opus-video-prompts, yihui-dev/awesome-opus5-5-videos, athemeroy/awesome-claude-5-5-videos (prompt collections).
