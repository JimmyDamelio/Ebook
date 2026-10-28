// Render each .slide of an HTML file to its own PNG (2x scale). node slides.js in.html outdir
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [input, outdir] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    await slides[i].screenshot({ path: path.join(outdir, `etsy-${String(i + 1).padStart(2, '0')}.png`) });
  }
  await browser.close();
  console.log(slides.length + ' images');
})();
