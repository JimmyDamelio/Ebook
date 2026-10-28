# Ebook — Sage & Season

Products (on Gumroad, store sageandseason.gumroad.com):
- **The Perimenopause Companion** — Guide + 30-Day Printable Workbook, $24 (main product)
- **The 30-Day Perimenopause Workbook**, $9
- **Before Your Appointment** — free printable checklist

Audience: women in their 40s–50s. Tone: calm, clear, evidence-based (NICE, NHS, ACOG, The Menopause Society, NIH), no miracle claims, no fear marketing. Always keep the health-education disclaimer.

The owner speaks French; reply in French. Marketing copy for the products is in English.

## Contents
- `trailer/` — 30 s launch trailer made in code (MP4 + sources). To make more videos, use the `trailer-video` skill in `.claude/skills/`.
- `remotion/` — Remotion (React video) project; test teaser 9:16 with voice-over.
- `.claude/skills/trailer-video` — Sage & Season brand video skill (palette, type, tone).
- General skills and agents (video-in-code, motion-design, GSAP, Three.js, design-dna, genjutsu, real-sfx, earshot, openverse, 49 active agents + 235 in a library) live in the shared toolkit github.com/JimmyDamelio/edunos-claude-toolkit, installed into ~/.claude by its install.sh.
- `voice-samples/` — text-to-speech samples (Kokoro, Piper).
- `setup-media.sh` — the toolkit repo is private: in a cloud session, attach it with `add_repo` (JimmyDamelio/edunos-claude-toolkit, cloned to /home/user/edunos-claude-toolkit) before running the script. Run first in a new session if the toolkit isn't installed yet: installs the toolkit (voices, Agent Reach, skills, agents) and Remotion deps (`agent-reach read <url>` to read X/Twitter, YouTube subtitles, Reddit…; binary in ~/.local/bin).

## Social videos (Facebook, Instagram, TikTok) — main focus of this repo
- Tools: `trailer-video` skill (brand look), `video-in-code` (general method), Remotion in `remotion/` for text-led clips; sound via `openverse` → `real-sfx` → check with `earshot`. Agents for strategy: `marketing-tiktok-strategist`, `marketing-instagram-curator`, `marketing-social-media-strategist`, `marketing-short-video-editing-coach`, `paid-media-paid-social-strategist`.
- Formats: 9:16 1080×1920 for Reels, TikTok and Stories (main format); 4:5 1080×1350 for Facebook/Instagram feed; 1:1 1080×1080 if needed. 30 fps, H.264 + AAC.
- Safe zones in 9:16: keep text out of the top ~220 px, the bottom ~420 px and the right ~140 px (platform buttons and captions). The Instagram profile grid crops Reels to the centre 3:4.
- Length 15–30 s. Hook in the first 1–2 s (a question or a relatable moment, never fear). Burned-in captions: most people watch muted. End card: product name, price, "link in bio" / sageandseason.gumroad.com, and the disclaimer.
- Ads policy (Meta and TikTok, health): never imply you know the viewer's health status ("Are you in perimenopause?", "Your hot flashes…"). Talk about the topic, not the person ("Perimenopause can bring…"). No before/after, no cure or weight-loss claims.
- Output files go in `social/<name>/` (sources + final MP4s named `<name>-9x16.mp4`, `<name>-4x5.mp4`).
