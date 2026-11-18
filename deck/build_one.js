// Build a single part for a quick check: node build_one.js p03  ->  qa/p03.pptx
const fs = require('fs');
const { makeLib, prepIcons, THEME } = require('./lib');
const { applyTheme } = require('./theme');
const p = process.argv[2];
(async () => {
  const src = ['lib.js', p + '.js'].map((f) => fs.readFileSync(f, 'utf8')).join('\n');
  const names = [...new Set(src.match(/'Md[A-Za-z0-9]+'/g).map((s) => s.slice(1, -1)))];
  await prepIcons(names);
  const L = makeLib();
  let n = 0, noRefs = 0, noNotes = 0;
  const content = L.content;
  L.content = (title, o = {}) => { n++; if (!o.refs) noRefs++; if (!o.notes) noNotes++; if (title.length > 34) console.log('LONG TITLE (' + title.length + '): ' + title); return content(title, o); };
  require('./' + p)(L);
  fs.mkdirSync('qa', { recursive: true });
  const out = 'qa/' + p + '.pptx';
  await L.pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log('wrote', out, 'content slides:', n, 'without refs:', noRefs, 'without notes:', noNotes);
})().catch((e) => { console.error(e); process.exit(1); });
