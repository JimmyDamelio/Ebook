// Render an HTML file to PDF or PNG with the preinstalled Playwright Chromium.
// node render.js pdf in.html out.pdf | node render.js png in.html out.png WIDTH HEIGHT
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [mode, input, output, w, h] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage(mode === 'png' ? { viewport: { width: +w, height: +h } } : {});
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  if (mode === 'pdf') {
    await page.pdf({ path: output, format: 'A4', printBackground: true, preferCSSPageSize: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="width:100%;font:7.5pt Inter,sans-serif;color:#9AA6A5;padding:0 17mm;display:flex;justify-content:space-between"><span>Nid Serein · Guide du parent employeur 2026-2027</span><span class="pageNumber"></span></div>' });
  } else {
    await page.screenshot({ path: output, fullPage: false });
  }
  await browser.close();
})();
