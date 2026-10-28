# Channel autopilot playbook

Every scheduled run follows this file from top to bottom. One run = one new YouTube Short, made and posted with no human in the loop.

## The channel
- **Name:** Edunos Studio (store: edunosstudio.gumroad.com). Language: English.
- **Series:** *One prompt. One video.* Every Short shows the prompt being typed, then the animation Claude Code wrote from it, entirely in code (no stock footage, no AI video model).
- **Goal:** show what code-made animation can do, and send viewers to the guide **Prompt to Reel** ($9.99, https://edunosstudio.gumroad.com/l/prompt-to-reel). Quote only what this file says about it (scheduled runs have no Gumroad tool); never invent claims, numbers or results.
- **Posting schedule:** Tuesday, Thursday and Saturday, uploads around 17:40 UTC (12:40 New York, 17:40 London). The schedule lives in the scheduled task, not here.

## Format (every episode)
- 9:16, 1080×1920, 30 fps, **15–30 s**, stereo, normalised to −14 LUFS by `make.sh`.
- 0–3.5 s: the **prompt card** (prompt typed out letter by letter + "Made 100% by Claude Code"). The hook is the prompt itself: one vivid sentence with a small story in it (a problem and a turn).
- Middle: the animation. One clear subject, one turn, readable on a phone (big shapes, high contrast, nothing important in the bottom 15% or the right 10%, where YouTube puts its buttons).
- Last 3 s: the **end card**: "No app. No editing. / Just one prompt. / Learn how: Prompt to Reel / link in description".
- Copy `episodes/001-paper-boat/` as the starting point: it has the prompt card, the end card, grain, vignette and the audio skeleton. Change everything in between.

## Choosing the next prompt
1. `python3 youtube-channel/upload.py list` shows past uploads (title | prompt). Never repeat a subject; do not reuse the style of any of the last 3 episodes.
2. Rotate through these styles: watercolour and ink · paper cut-out · neon synthwave · pixel art · isometric 3D (three.js) · kinetic typography · chalkboard · risograph print · origami / folded paper · particles · flat geometric (Bauhaus) · lo-fi night scene · a chart that draws itself (real public data only, with the source in the description).
3. Subjects: small visual stories everyone gets in one second (a seed becoming a tree, a lost kite, a city waking up, a whale made of stars…). **Never:** real people, brands, logos, copyrighted characters, religion, politics, health or money claims, anything scary or sad without a turn.
4. Write the prompt in one sentence of 10–20 words.

## Making the video
Follow the `video-in-code` skill (and `motion-design` for timing; `threejs-*` for 3D; `gsap-timeline` for sequencing).
1. `cp -r youtube-channel/episodes/001-paper-boat youtube-channel/episodes/NNN-slug` (next number, then a short slug) and rewrite `film.html` and `audio.py`. Keep `window.DURATION`, `renderAt(t)` and `window.ready`; keep everything deterministic (seeded `mulberry`, no `Math.random`, no clock).
2. Stills before the full render: `node youtube-channel/render.mjs <dir> stills 0.5 2 4 …` (8–14 moments), tile them (`ffmpeg -pattern_type glob -i '<dir>/stills/t_*.png' -vf scale=270:-1,tile=7x2 <dir>/sheet.png`) and **look at the sheet**. Fix empty beats, overlaps, unreadable text and muddy gradients. Repeat until it looks good.
3. Sound: real recordings first (`openverse`, CC0 only; put any CC BY credit in the description), otherwise synthesise in `audio.py`. Keep music under the whole film and a sound on every visual event. Check with `earshot critique <dir>/video.mp4` and fix the major findings. Openverse may time out from the cloud: if it does, synthesise and move on.
4. `sh youtube-channel/make.sh youtube-channel/episodes/NNN-slug` → `video.mp4`. Make a contact sheet of the final video (`-vf fps=1/1.75,scale=216:-1,tile=6x2`) and look at it once more.

## Title, description, upload
Write `<dir>/meta.json`:
```json
{
  "title": "I typed one sentence. Claude Code made this. #shorts",
  "description": "Prompt: \"<the prompt>\"\n\nNo app, no editing, no AI video model: Claude Code wrote the code that draws every frame and makes the sound.\n\nLearn to make videos like this: Prompt to Reel, the beginner's guide → https://edunosstudio.gumroad.com/l/prompt-to-reel\n\nIndependent creator, not affiliated with or endorsed by Anthropic. \"Claude\" is a trademark of Anthropic.\n\n#claudecode #animation #creativecoding",
  "tags": ["claude code", "ai animation", "creative coding", "motion design", "<style>", "<subject>"]
}
```
- **The first line of the description is always `Prompt: "…"`**: `upload.py list` reads it to avoid repeats.
- Vary the title (≤ 60 characters, curiosity, no clickbait lies), e.g. "One prompt → a whale made of stars", "Claude Code drew this from 14 words".
- At most 3–5 hashtags.

Then: `python3 youtube-channel/upload.py <dir>/video.mp4 <dir>/meta.json`. It prints the Short's URL.

## If something is missing
- **No `YT_*` secrets** (upload.py says "missing environment variables"): still make the video, then send `video.mp4` and `meta.json` to the user with `SendUserFile` so they can post it by hand, and remind them in one line to finish the setup in `youtube-channel/README.md`.
- **The upload comes back `private`, or YouTube says the video is locked as private:** the Google Cloud project has not passed YouTube's API audit yet. Send the URL to the user and remind them in one line to make it public from the YouTube Studio app (and that the audit form is in the README).
- Any other API error: report it word for word, do not retry more than once.

## End of run
Reply in French, in 2–3 lines: the prompt, the style, the URL (or the file). Nothing is committed: YouTube is the record of what was posted. Only commit if you improved this playbook or the shared scripts.
