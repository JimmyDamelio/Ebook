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
- `setup-media.sh` — run first in a new session if the toolkit isn't installed yet: installs the toolkit (voices, Agent Reach, skills, agents) and Remotion deps (`agent-reach read <url>` to read X/Twitter, YouTube subtitles, Reddit…; binary in ~/.local/bin).
