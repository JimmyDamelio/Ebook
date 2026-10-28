// Sage & Season brand drawing kit for 9:16 social films (from trailer/ and three-am/).

const W = 1080, H = 1920;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const C = {
  paper: '#F3ECDF', paper2: '#EADFCB', ink: '#2F3A33', inkSoft: '#56645A',
  sage: '#8EA685', sageD: '#5C7658', sageDD: '#3F5641', terra: '#C77B5C', blush: '#E9BCA4',
  night: '#18222D', night2: '#2A3A48', moon: '#F2E2C0', gold: '#D8A55B', cream: '#FBF6EC'
};
let BOIL = 0;

// ---------- math ----------
function mulberry(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const eo = k => 1 - Math.pow(1 - k, 3);
const eback = k => { const c1 = 1.4, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };
// fade in over [a,a+d], out over [b-d2,b]
const life = (t, a, b, d = .6, d2 = .5) => Math.min(eo(seg(t, a, a + d)), 1 - eio(seg(t, b - d2, b)));

// ---------- paper & grain ----------
function makePaper() {
  const p = document.createElement('canvas'); p.width = W; p.height = H; const g = p.getContext('2d');
  g.fillStyle = C.paper; g.fillRect(0, 0, W, H);
  const R = mulberry(11);
  for (let i = 0; i < 26; i++) { // large soft tonal blotches
    const x = R() * W, y = R() * H, r = 200 + R() * 500;
    const gr = g.createRadialGradient(x, y, 0, x, y, r);
    const rgb = R() < .45 ? '222,206,178' : '252,248,240';
    gr.addColorStop(0, `rgba(${rgb},0.16)`); gr.addColorStop(1, `rgba(${rgb},0)`);
    g.fillStyle = gr; g.fillRect(0, 0, W, H);
  }
  g.globalAlpha = .05; g.strokeStyle = '#7a6a52'; g.lineWidth = 1;
  for (let i = 0; i < 1600; i++) { // fibres
    const x = R() * W, y = R() * H, a = R() * Math.PI, l = 4 + R() * 18;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
  }
  const id = g.getImageData(0, 0, W, H), d = id.data;
  for (let i = 0; i < d.length; i += 4) { const n = (R() - .5) * 14; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
  g.putImageData(id, 0, 0);
  return p;
}
function makeGrain(seed) {
  const p = document.createElement('canvas'); p.width = 540; p.height = 960; const g = p.getContext('2d');
  const id = g.createImageData(540, 960), d = id.data, R = mulberry(seed);
  for (let i = 0; i < d.length; i += 4) { const v = R() * 255; d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255; }
  g.putImageData(id, 0, 0); return p;
}
let PAPER, GRAINS;

// ---------- drawing primitives ----------
function blobPath(g, cx, cy, r, seed, amp = .12, n = 72, sy = 1) {
  const R = mulberry(seed); const p = [R() * 6.28, R() * 6.28, R() * 6.28];
  const f = [2 + Math.floor(R() * 2), 3 + Math.floor(R() * 3), 7 + Math.floor(R() * 5)];
  g.beginPath();
  for (let i = 0; i <= n; i++) {
    const a = i / n * Math.PI * 2;
    const k = 1 + amp * (.6 * Math.sin(a * f[0] + p[0]) + .3 * Math.sin(a * f[1] + p[1]) + .15 * Math.sin(a * f[2] + p[2]));
    const x = cx + Math.cos(a) * r * k, y = cy + Math.sin(a) * r * k * sy;
    i ? g.lineTo(x, y) : g.moveTo(x, y);
  }
  g.closePath();
}
function wash(g, cx, cy, r, col, seed, alpha = 1, layers = 12, sy = 1) {
  if (alpha <= 0 || r <= 0) return;
  const R = mulberry(seed * 7 + 3); const ga = g.globalAlpha;
  g.save(); g.fillStyle = col;
  for (let k = 0; k < layers; k++) {
    g.globalAlpha = ga * alpha * .09;
    blobPath(g, cx + (R() - .5) * r * .25, cy + (R() - .5) * r * .25 * sy, r * (.68 + .36 * R()), seed * 31 + k, .17, 72, sy);
    g.fill();
  }
  g.globalAlpha = ga * alpha * .22; g.lineWidth = 2.2; g.strokeStyle = col;
  blobPath(g, cx, cy, r * .97, seed * 31 + 99, .15, 72, sy); g.stroke();
  g.restore();
}
function densify(pts, step = 5) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[i + 1];
    const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / step));
    for (let j = 0; j < n; j++) out.push([lerp(x0, x1, j / n), lerp(y0, y1, j / n)]);
  }
  out.push(pts[pts.length - 1]); return out;
}
function ink(g, pts, o = {}) {
  const { seed = 1, amp = 1.5, width = 3, color = C.ink, prog = 1, alpha = 1, step = 5 } = o;
  if (prog <= 0 || alpha <= 0) return;
  const arr = densify(pts, step), N = Math.max(2, Math.floor(arr.length * clamp(prog)));
  const s1 = seed * 1.7 + BOIL * 2.3, s2 = seed * 3.1 + BOIL * 1.3;
  g.save(); g.globalAlpha *= alpha; g.strokeStyle = color; g.lineWidth = width; g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath();
  for (let i = 0; i < N; i++) {
    const [x, y] = arr[i];
    const dx = amp * (Math.sin(i * .19 + s1) + .5 * Math.sin(i * .051 + s2 * 2));
    const dy = amp * (Math.sin(i * .23 + s2) + .5 * Math.sin(i * .043 + s1 * 2));
    i ? g.lineTo(x + dx, y + dy) : g.moveTo(x + dx, y + dy);
  }
  g.stroke(); g.restore();
}
function curve(x0, y0, cx, cy, x1, y1, n = 40) {
  const p = []; for (let i = 0; i <= n; i++) { const k = i / n, a = (1 - k) * (1 - k), b = 2 * k * (1 - k), c = k * k; p.push([a * x0 + b * cx + c * x1, a * y0 + b * cy + c * y1]); } return p;
}
function inkRect(g, x, y, w, h, o = {}) {
  const e = 6;
  ink(g, [[x - e, y], [x + w + e * .5, y + 1], [x + w, y - e * .5], [x + w - 1, y + h + e], [x + w + e * .4, y + h], [x - e * .6, y + h - 1], [x, y + h + e * .4], [x + 1, y - e]], o);
}
function inkEllipse(g, cx, cy, rx, ry, o = {}) {
  const p = []; const n = 64; const a0 = -.4;
  for (let i = 0; i <= n * 1.12; i++) { const a = a0 + i / n * Math.PI * 2; const k = 1 + .04 * Math.sin(i * .3); p.push([cx + Math.cos(a) * rx * k, cy + Math.sin(a) * ry * k]); }
  ink(g, p, o);
}
function text(g, s, x, y, o = {}) {
  const { size = 60, font = 'Fraunces', weight = 300, italic = false, color = C.ink, align = 'left', alpha = 1, rise = 0, blur = 0, spacing = 0, rot = 0, base = 'alphabetic' } = o;
  if (alpha <= 0) return;
  g.save(); g.globalAlpha *= clamp(alpha);
  g.font = `${italic ? 'italic ' : ''}${weight} ${size}px ${font}`;
  g.textAlign = align; g.textBaseline = base; g.fillStyle = color; g.letterSpacing = spacing + 'px';
  if (blur > .2) g.filter = `blur(${blur}px)`;
  g.translate(x, y + rise); if (rot) g.rotate(rot);
  g.fillText(s, 0, 0); g.restore();
}
// text that reveals with rise + de-blur
function reveal(g, s, x, y, t, a, b, o = {}) {
  const k = life(t, a, b, o.din ?? .8, o.dout ?? .5);
  const kin = eo(seg(t, a, a + (o.din ?? .8)));
  text(g, s, x, y, { ...o, alpha: k * (o.alpha ?? 1), rise: (1 - kin) * (o.riseBy ?? 24), blur: (1 - kin) * 10 });
}
function fitSize(g, s, font, weight, italic, maxW, start) {
  let sz = start; g.font = `${italic ? 'italic ' : ''}${weight} ${sz}px ${font}`;
  while (g.measureText(s).width > maxW && sz > 10) { sz -= 1; g.font = `${italic ? 'italic ' : ''}${weight} ${sz}px ${font}`; }
  return sz;
}
function leaf(g, x, y, len, ang, wid, col, seed, alpha = 1) {
  const R = mulberry(seed); const ga = g.globalAlpha;
  g.save(); g.translate(x, y); g.rotate(ang); g.fillStyle = col;
  for (let k = 0; k < 5; k++) {
    g.globalAlpha = ga * alpha * .22; const j = (R() - .5) * 3;
    g.beginPath(); g.moveTo(0, 0);
    g.quadraticCurveTo(len * .45, -wid + j, len, j * .5);
    g.quadraticCurveTo(len * .5, wid * .9 + j, 0, 0); g.fill();
  }
  g.globalAlpha = ga * alpha * .35; g.strokeStyle = col; g.lineWidth = 1.2;
  g.beginPath(); g.moveTo(len * .05, 0); g.quadraticCurveTo(len * .5, -1, len * .92, 0); g.stroke();
  g.restore();
}
function branch(g, x0, y0, x1, y1, bend, col, leafCol, seed, prog = 1, scale = 1, alpha = 1) {
  const pts = curve(x0, y0, (x0 + x1) / 2 + bend, (y0 + y1) / 2 - bend * .4, x1, y1, 60);
  ink(g, pts, { seed, width: 2.6 * scale, color: col, prog, alpha, amp: .8 });
  const R = mulberry(seed + 5); const n = 9;
  for (let i = 1; i <= n; i++) {
    const s = i / (n + 1); if (s > prog) break;
    const idx = Math.floor(s * (pts.length - 1)); const [px, py] = pts[idx]; const [qx, qy] = pts[Math.min(idx + 1, pts.length - 1)];
    const base = Math.atan2(qy - py, qx - px); const side = i % 2 ? 1 : -1;
    const grow = eo(clamp((prog - s) * 6));
    leaf(g, px, py, (46 + R() * 22) * scale * grow * (1 - s * .35), base + side * (.75 + R() * .3), 15 * scale * grow, leafCol, seed * 13 + i, alpha);
  }
  const [ex, ey] = pts[pts.length - 1];
  if (prog >= .98) leaf(g, ex, ey, 40 * scale, Math.atan2(y1 - y0, x1 - x0) - .2, 13 * scale, leafCol, seed * 17, alpha);
}

// ---------- transitions ----------
function blobReveal(t, a, b, cx, cy, edgeCol, drawA, drawB, seed = 5) {
  if (t < a) return drawA(t);
  if (t >= b) return drawB(t);
  const k = eio(seg(t, a, b)); const R = lerp(0, 2300, k);
  drawA(t);
  ctx.save(); blobPath(ctx, cx, cy, R, seed, .14); ctx.clip(); drawB(t); ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'multiply';
  for (let i = 0; i < 3; i++) { ctx.globalAlpha = .18 * (1 - k * .6); ctx.lineWidth = 26 - i * 8; ctx.strokeStyle = edgeCol; blobPath(ctx, cx, cy, R * (1 - i * .01), seed, .14); ctx.stroke(); }
  ctx.restore();
}
function brushWipe(t, a, b, col, drawA, drawB, seed = 3) {
  if (t < a) return drawA(t);
  if (t >= b) return drawB(t);
  const k = eio(seg(t, a, b)); const X = lerp(-260, W + 260, k);
  drawA(t);
  const edge = y => X + 70 * Math.sin(y * .006 + seed) + 26 * Math.sin(y * .019 + seed * 2) + 6 * Math.sin(y * .05 + seed);
  ctx.save(); ctx.beginPath(); ctx.moveTo(-10, -10);
  for (let y = -10; y <= H + 10; y += 6) ctx.lineTo(edge(y), y);
  ctx.lineTo(-10, H + 10); ctx.closePath(); ctx.clip(); drawB(t); ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'multiply';
  for (let i = 0; i < 4; i++) {
    ctx.globalAlpha = .14; ctx.strokeStyle = col; ctx.lineWidth = 60 - i * 14; ctx.beginPath();
    for (let y = -10; y <= H + 10; y += 6) { const x = edge(y) - 30 + i * 6; y < 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
    ctx.stroke();
  }
  ctx.restore();
}
function paperBg(g) { g.drawImage(PAPER, 0, 0); }
function camera(g, k, z = .03, cx = W / 2, cy = H / 2) {
  const s = 1 + z * k; g.translate(cx, cy); g.scale(s, s); g.translate(-cx, -cy);
}

// ---------- book cover ----------
function drawBook(g, x, y, w, alpha = 1, artProg = 1) {
  const h = w * 1.414; const sc = w / 520;
  g.save(); g.globalAlpha *= alpha;
  // shadow
  g.save(); g.globalCompositeOperation = 'multiply';
  g.save(); g.translate(x + w * .55, y + h + 6 * sc); g.scale(1, .16);
  const sg = g.createRadialGradient(0, 0, 0, 0, 0, w * .8);
  sg.addColorStop(0, 'rgba(70,60,40,.4)'); sg.addColorStop(1, 'rgba(70,60,40,0)');
  g.fillStyle = sg; g.beginPath(); g.arc(0, 0, w * .8, 0, 6.28); g.fill(); g.restore();
  g.fillStyle = 'rgba(60,50,35,.18)'; g.filter = `blur(${18 * sc}px)`; g.fillRect(x + 18 * sc, y + 26 * sc, w, h); g.filter = 'none';
  g.restore();
  // pages edge
  g.fillStyle = '#efe6d4'; g.fillRect(x + 8 * sc, y + 8 * sc, w, h - 6 * sc);
  g.strokeStyle = 'rgba(120,100,70,.25)'; g.lineWidth = 1;
  for (let i = 1; i < 5; i++) { g.beginPath(); g.moveTo(x + w + i * 1.6 * sc, y + 10 * sc); g.lineTo(x + w + i * 1.6 * sc, y + h); g.stroke(); }
  // cover
  g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip();
  const cg = g.createLinearGradient(x, y, x + w, y + h); cg.addColorStop(0, '#7E9A78'); cg.addColorStop(1, '#5D7A5A');
  g.fillStyle = cg; g.fillRect(x, y, w, h);
  g.globalCompositeOperation = 'source-over';
  wash(g, x + w * .25, y + h * .2, w * .45, '#A9BFA0', 41, .9);
  wash(g, x + w * .85, y + h * .72, w * .5, '#4E6A4C', 42, .8);
  wash(g, x + w * .6, y + h * .95, w * .35, C.blush, 43, .5);
  wash(g, x + w * .15, y + h * .85, w * .25, C.gold, 44, .25);
  // botanical
  branch(g, x + w * 1.02, y + h * .98, x + w * .48, y + h * .58, -40 * sc, '#3F5641', '#2F4532', 77, artProg, sc, .9);
  branch(g, x + w * 1.05, y + h * .86, x + w * .7, y + h * .5, 30 * sc, '#3F5641', C.blush, 78, artProg, sc * .8, .8);
  // type
  const tx = x + 46 * sc;
  text(g, 'THE', tx, y + 108 * sc, { size: 22 * sc, weight: 500, color: C.cream, spacing: 6 * sc });
  const s1 = fitSize(g, 'Perimenopause', 'Fraunces', 500, false, w - 92 * sc, 74 * sc);
  text(g, 'Perimenopause', tx, y + 182 * sc, { size: s1, weight: 500, color: C.cream });
  text(g, 'Companion', tx, y + 252 * sc, { size: s1 * 1.02, weight: 300, italic: true, color: C.cream });
  g.fillStyle = 'rgba(251,246,236,.7)'; g.fillRect(tx, y + 290 * sc, 64 * sc, 2 * sc);
  text(g, 'Guide + 30-Day Printable Workbook', tx, y + 334 * sc, { size: 23 * sc, weight: 300, color: C.cream });
  text(g, 'SAGE & SEASON', tx, y + h - 46 * sc, { size: 17 * sc, weight: 500, color: C.cream, spacing: 5 * sc, alpha: .9 });
  // spine shading
  const sp = g.createLinearGradient(x, 0, x + 34 * sc, 0); sp.addColorStop(0, 'rgba(0,0,0,.28)'); sp.addColorStop(.35, 'rgba(255,255,255,.12)'); sp.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = sp; g.fillRect(x, y, 34 * sc, h);
  g.restore();
  g.restore();
}

// ---------- cards (from trailer/) ----------
function trackerCard(g, t, x, y, a0) {
  g.save(); g.translate(x, y); g.rotate(-.025);
  g.save(); g.fillStyle = 'rgba(60,50,35,.16)'; g.filter = 'blur(16px)'; g.fillRect(16, 22, 640, 470); g.restore();
  g.fillStyle = C.cream; g.fillRect(0, 0, 640, 470);
  text(g, 'Daily tracker', 36, 62, { size: 34, weight: 500, color: C.ink });
  text(g, 'day 12', 604, 62, { font: 'Caveat', size: 34, color: C.terra, align: 'right' });
  const rows = [['sleep', C.sageD, 1], ['energy', C.gold, 2], ['mood', C.terra, 3]];
  rows.forEach(([lab, col, s], r) => {
    const yy = 150 + r * 115;
    text(g, lab, 36, yy + 8, { font: 'Caveat', size: 38, color: C.inkSoft });
    g.strokeStyle = 'rgba(80,80,60,.15)'; g.lineWidth = 1; g.beginPath(); g.moveTo(150, yy + 30); g.lineTo(600, yy + 30); g.stroke();
    const pts = []; for (let i = 0; i <= 12; i++) pts.push([150 + i * 37.5, yy + 6 - 26 * Math.sin(i * .7 + s * 1.3) * (.6 + .4 * Math.cos(i * .33 + s))]);
    const p = eo(seg(t, a0 + r * .15, a0 + .9 + r * .15));
    ink(g, pts, { seed: 80 + r, color: col, width: 4, prog: p, amp: .8 });
    pts.forEach(([px, py], i) => { if (i / 12 <= p) { g.fillStyle = col; g.beginPath(); g.arc(px, py, 5, 0, 6.28); g.fill(); } });
  });
  g.restore();
}
// sample 30-day values for the summary card's bars (0 calm, 1 some, 2 marked)
const DAYV = Array.from({ length: 30 }, (_, i) => { const c = i % 14; return (c >= 7 && c <= 10) ? 2 : (c === 6 || c === 11 || i === 3 || i === 17) ? 1 : 0; });
function summaryCard(g, t, x, y, a0) {
  g.save(); g.translate(x, y); g.rotate(.03);
  g.save(); g.fillStyle = 'rgba(60,50,35,.18)'; g.filter = 'blur(18px)'; g.fillRect(18, 24, 560, 720); g.restore();
  g.fillStyle = C.cream; g.fillRect(0, 0, 560, 720);
  g.fillStyle = C.sage; g.fillRect(0, 0, 560, 14);
  text(g, 'My 30-Day Summary', 40, 80, { size: 40, weight: 500, color: C.ink });
  text(g, 'for my appointment', 40, 122, { font: 'Caveat', size: 34, color: C.sageD });
  const bars = [['bleeding', C.terra], ['sleep', C.sageD], ['mood', C.gold]];
  bars.forEach(([lab, col], r) => {
    const yy = 190 + r * 70; text(g, lab, 40, yy + 10, { font: 'Caveat', size: 32, color: C.inkSoft });
    for (let i = 0; i < 30; i++) {
      const v = (DAYV[i] + 1) / 3 * (r === 0 ? 1 : .5 + .5 * Math.abs(Math.sin(i * .5 + r)));
      const h = 8 + 34 * v * eo(seg(t, a0 + i * .015 + r * .1, a0 + .5 + i * .015 + r * .1));
      g.fillStyle = col; g.fillRect(170 + i * 12.5, yy + 16 - h, 8, h);
    }
  });
  text(g, 'Questions to ask', 40, 440, { size: 30, weight: 500, color: C.ink });
  ['What could explain these changes?', 'Which options suit me?', 'When should I come back?'].forEach((q, i) => {
    const yy = 500 + i * 62;
    inkRect(g, 42, yy - 26, 28, 28, { seed: 110 + i, width: 2, color: C.inkSoft, amp: .7 });
    ink(g, [[46, yy - 12], [55, yy - 2], [76, yy - 34]], { seed: 120 + i, width: 4, color: C.terra, prog: eo(seg(t, a0 + .6 + i * .25, a0 + .9 + i * .25)), amp: .6 });
    text(g, q, 92, yy, { size: 26, weight: 300, color: C.ink });
  });
  g.restore();
}


// ---------- 9:16 layout ----------
// Picture area y 220–1150; spoken captions band y 1230–1440; nothing in the bottom 420 px or right 140 px.
const CX = 525, MAXW = 800;
function cap(g, s, y, t, a, b, o = {}) {
  const size = fitSize(g, s, o.font || 'Fraunces', o.weight ?? 300, !!o.italic, o.maxW || MAXW, o.size || 84);
  reveal(g, s, CX, y, t, a, b, { align: 'center', ...o, size });
}

// ---------- word-by-word captions (large, high contrast, for 40+ readers) ----------
// window.WORDS = [{w, t0, t1, line}] from lib/vo.py; a "line" is one caption page of up to ~6 words.
function karaoke(g, t, o = {}) {
  const { y = 1300, size = 74, dark = false, maxW = 840 } = o;
  const words = window.WORDS || [];
  const lines = {}; words.forEach(w => (lines[w.line] = lines[w.line] || []).push(w));
  const page = Object.values(lines).find(ws => t >= ws[0].t0 - .12 && t < ws[ws.length - 1].t1 + .35);
  if (!page) return;
  const k = eo(seg(t, page[0].t0 - .12, page[0].t0 + .1)) * (1 - eio(seg(t, page[page.length - 1].t1 + .15, page[page.length - 1].t1 + .35)));
  g.save(); g.font = `500 ${size}px Fraunces`;
  // wrap into rows that fit maxW
  const sp = g.measureText(' ').width, rows = [[]]; let rw = 0;
  for (const w of page) { const ww = g.measureText(w.w).width; if (rw && rw + sp + ww > maxW) { rows.push([]); rw = 0; } rows[rows.length - 1].push([w, ww]); rw += (rw ? sp : 0) + ww; }
  const lh = size * 1.22, y0 = y - (rows.length - 1) * lh / 2;
  // soft paper panel behind the words
  const panelW = Math.min(maxW + 80, Math.max(...rows.map(r => r.reduce((a, [, ww]) => a + ww, 0) + sp * (r.length - 1))) + 80);
  g.globalAlpha = k * (dark ? .55 : .78); g.fillStyle = dark ? 'rgba(10,15,20,1)' : C.cream;
  g.beginPath(); g.roundRect(CX - panelW / 2, y0 - size * .95, panelW, rows.length * lh + size * .5, 34); g.fill();
  rows.forEach((r, i) => {
    const tw = r.reduce((a, [, ww]) => a + ww, 0) + sp * (r.length - 1); let x = CX - tw / 2; const yy = y0 + i * lh;
    for (const [w, ww] of r) {
      const now = t >= w.t0 && t < w.t1 + .05, past = t >= w.t0;
      if (now) { g.globalAlpha = k * .9; g.fillStyle = dark ? 'rgba(199,123,92,.45)' : 'rgba(233,188,164,.75)'; g.beginPath(); g.roundRect(x - 10, yy - size * .78, ww + 20, size * 1.0, 14); g.fill(); }
      g.globalAlpha = k * (past ? 1 : .38);
      g.fillStyle = now ? (dark ? C.moon : '#8E4A2E') : (dark ? C.cream : C.ink);
      g.fillText(w.w, x, yy); x += ww + sp;
    }
  });
  g.restore();
}

// ---------- boot ----------
function boot(renderAt, duration) {
  window.DURATION = duration;
  window.ready = (async () => {
    await Promise.all(['300 40px Fraunces', '400 40px Fraunces', '500 40px Fraunces', 'italic 300 40px Fraunces', '500 40px Caveat', '600 40px Caveat'].map(f => document.fonts.load(f)));
    PAPER = makePaper(); GRAINS = [1, 2, 3, 4].map(makeGrain);
    window.renderAt = renderAt; renderAt(+new URLSearchParams(location.search).get('t') || 0);
    if (location.search.includes('play')) { const s = performance.now(); const loop = () => { renderAt(((performance.now() - s) / 1000) % duration); requestAnimationFrame(loop); }; loop(); }
    return true;
  })();
}
function finish(t) { // grain + vignette, shared by every film
  ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = .07;
  ctx.drawImage(GRAINS[Math.floor(t * 24) % GRAINS.length], 0, 0, W, H); ctx.restore();
  const vg = ctx.createRadialGradient(W / 2, H / 2, W * .55, W / 2, H / 2, H * .75);
  vg.addColorStop(0, 'rgba(60,45,30,0)'); vg.addColorStop(1, 'rgba(60,45,30,.16)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
}

// ---------- handwriting ----------
function pencil(g, x, y, alpha = 1) { // a drawn pencil, tip at (x, y)
  if (alpha <= 0) return;
  g.save(); g.globalAlpha *= clamp(alpha); g.translate(x, y); g.rotate(-.75);
  g.save(); g.fillStyle = 'rgba(60,50,35,.18)'; g.filter = 'blur(8px)'; g.fillRect(30, 10, 260, 26); g.restore();
  g.fillStyle = '#3a3a3a'; g.beginPath(); g.moveTo(0, 0); g.lineTo(14, -6); g.lineTo(14, 6); g.closePath(); g.fill();
  g.fillStyle = '#E8C9A0'; g.beginPath(); g.moveTo(14, -6); g.lineTo(44, -14); g.lineTo(44, 14); g.lineTo(14, 6); g.closePath(); g.fill();
  g.fillStyle = C.gold; g.fillRect(44, -14, 190, 28);
  g.fillStyle = 'rgba(0,0,0,.08)'; g.fillRect(44, 5, 190, 9);
  g.fillStyle = '#B9B2A4'; g.fillRect(234, -14, 22, 28);
  g.fillStyle = C.blush; g.beginPath(); g.roundRect(256, -14, 30, 28, 8); g.fill();
  g.restore();
}
// writes s left to right over [a, a+d] with the pencil on the tip
function writeText(g, s, x, y, t, a, d, o = {}) {
  const p = eio(seg(t, a, a + d)); if (p <= 0) return;
  const size = o.size || 56, font = o.font || 'Caveat', weight = o.weight ?? 500, italic = !!o.italic, align = o.align || 'left';
  g.save(); g.font = `${italic ? 'italic ' : ''}${weight} ${size}px ${font}`; const w = g.measureText(s).width;
  const x0 = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
  g.beginPath(); g.rect(x0 - 20, y - size * 1.3, (w + 40) * p, size * 2); g.clip();
  text(g, s, x0, y, { ...o, size, font, weight, italic, align: 'left' }); g.restore();
  if (o.pen !== false && p < 1) pencil(g, x0 + w * p, y - size * .2, Math.min(seg(t, a - .05, a + .1), (1 - p) * 10));
}
function tick(g, x, y, s, prog, col = C.terra, seed = 1) {
  ink(g, [[x, y], [x + 14 * s, y + 16 * s], [x + 44 * s, y - 30 * s]], { seed, color: col, width: 6 * s, prog, amp: .6 });
}
