// node render.cjs -> pfp-A.png, pfp-B.png, pfp-C.png (1080×1080)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  p.on('pageerror', e => console.log('[error]', e.message));
  await p.goto('file://' + path.join(__dirname, 'pfp.html')); await p.evaluate(() => window.ready);
  for (const v of ['A', 'B', 'C']) {
    const b64 = await p.evaluate(v => { renderVariant(v); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, v);
    fs.writeFileSync(path.join(__dirname, `pfp-${v}.png`), Buffer.from(b64, 'base64'));
  }
  await b.close();
})();
