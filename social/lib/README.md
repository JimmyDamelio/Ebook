# Shared kit for social films
- `brand.js`: Sage & Season drawing kit (paper, watercolour washes, boiling ink, book cover, tracker and summary cards, handwriting with a pencil, word-by-word captions `karaoke()`, grain/vignette `finish()`, `boot()`).
- `vo.py`: Kokoro voice clips (`gen`) and word timings from Whisper (`align` → `words.js`; captions use the script's own words).
- `music.py`: synthesised score + voice with ducking + cut accents, pencil scribbles and SFX (`score.json`).
- `render.mjs`: Playwright frame renderer, run from a film folder.
- `sfx/`: tick, tap, click rendered from the earshot bank.
A film folder holds `film.html` (loads `../lib/brand.js` and `words.js`), `vo.json`, `score.json`, `README.md` and the MP4.
