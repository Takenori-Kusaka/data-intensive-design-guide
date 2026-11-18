"""Dump slide text, evidence lines and speaker notes to research/deck_text.md (for fact-checking).
Usage: python tools/deck_text.py deck/guide.pptx research/deck_text.md"""
import sys, io
from pptx import Presentation

def cell_text(shape):
    rows = []
    for r in shape.table.rows:
        rows.append(' | '.join(c.text.replace('\n', ' / ').strip() for c in r.cells))
    return rows

prs = Presentation(sys.argv[1])
out = io.open(sys.argv[2], 'w', encoding='utf-8', newline='\n')
for i, sl in enumerate(prs.slides, 1):
    out.write('\n## S%d\n' % i)
    for sh in sl.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            t = sh.text_frame.text.strip().replace('\n', ' / ')
            if t.isdigit() or t.startswith('データ指向で設計する大規模クラウドサービス｜'):
                continue
            out.write('- ' + t + '\n')
        if getattr(sh, 'has_table', False) and sh.has_table:
            for r in cell_text(sh):
                out.write('  | ' + r + ' |\n')
    if sl.has_notes_slide:
        n = sl.notes_slide.notes_text_frame.text.strip()
        if n:
            out.write('NOTE: ' + n.replace('\n', ' ') + '\n')
out.close()
print('slides', len(prs.slides))
