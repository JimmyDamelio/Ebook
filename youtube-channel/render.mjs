// usage: node render.mjs <episode-dir> stills 1 3.2 8.6 ...   -> <dir>/stills/t_<t>.png
//        node render.mjs <episode-dir> frames [workers]       -> <dir>/frames/f_00000.png ... (30 fps)
// The episode's film.html must define renderAt(t), window.ready, window.DURATION and a <canvas id="c">.
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
const { chromium } = createRequire(import.meta.url)('playwright'); // global install: ESM imports ignore NODE_PATH

const [dirArg, mode, ...rest] = process.argv.slice(2);
const dir = path.resolve(dirArg);
const url = 'file://' + path.join(dir, 'film.html');
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });

async function openPage() {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.log('[error]', e.message));
  await page.goto(url);
  await page.evaluate(() => window.ready);
  return page;
}
async function grab(page, t, file) {
  const b64 = await page.evaluate(t => { renderAt(t); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, t);
  fs.writeFileSync(file, Buffer.from(b64, 'base64'));
}

if (mode === 'stills') {
  fs.mkdirSync(path.join(dir, 'stills'), { recursive: true });
  const page = await openPage();
  for (const t of rest.map(Number)) await grab(page, t, path.join(dir, 'stills', `t_${t.toFixed(2)}.png`));
} else {
  const workers = +(rest[0] || 4), page0 = await openPage();
  const total = Math.round(30 * await page0.evaluate(() => window.DURATION));
  const out = path.join(dir, 'frames'); fs.mkdirSync(out, { recursive: true });
  let next = 0; const t0 = Date.now();
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const page = w ? await openPage() : page0;
    while (next < total) {
      const i = next++;
      await grab(page, i / 30, path.join(out, `f_${String(i).padStart(5, '0')}.png`));
      if (i % 100 === 0) console.log(`frame ${i}/${total} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
  }));
}
await browser.close();
