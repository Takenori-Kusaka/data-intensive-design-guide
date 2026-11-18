// Print which slide numbers belong to which part file: node slidemap.js
const fs = require('fs');
const { makeLib, prepIcons } = require('./lib');
const PARTS = ['p00','p01','p02','p03','p04','p05','p06','p07','p08','p09','p10','p11','p12','p13','p13b','p14','p15','p16','p17'].filter((p) => fs.existsSync(p + '.js'));
(async () => {
  const src = ['lib.js', ...PARTS.map((p) => p + '.js')].map((f) => fs.readFileSync(f, 'utf8')).join('\n');
  await prepIcons([...new Set(src.match(/'Md[A-Za-z0-9]+'/g).map((s) => s.slice(1, -1)))]);
  const L = makeLib();
  let n = 0; const add = L.pres.addSlide.bind(L.pres); const titles = [];
  L.pres.addSlide = (o) => { n++; return add(o); };
  const content = L.content; L.content = (t, o) => { titles.push([n + 1, t]); return content(t, o); };
  const out = [];
  PARTS.forEach((p) => { const a = n + 1; require('./' + p)(L); out.push(p + '\t' + a + '-' + n + '\t' + (n - a + 1)); });
  fs.writeFileSync('qa/slidemap.txt', out.join('\n') + '\n\n' + titles.map((t) => 'S' + t[0] + '\t' + t[1]).join('\n') + '\n');
  console.log(out.join('\n')); console.log('total', n);
})();
