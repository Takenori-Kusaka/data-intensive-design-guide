"""Find long verbatim overlaps between the deck text and the book texts (books are not in the repository).
Usage: python tools/quote_check.py research/deck_text.md research/books/text 25
Prints slide number, length and the overlapping string for every run of N or more identical characters."""
import sys, io, re, glob, os

deck, bookdir, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
norm = lambda s: re.sub(r'\s+', '', s)
books = {}
for f in glob.glob(os.path.join(bookdir, '*.txt')):
    t = io.open(f, encoding='utf-8').read()
    t = re.sub(r'===== PDF p\.\d+ / printed p\.[\d?]+ =====', '', t)
    books[os.path.basename(f)] = norm(t)
grams = {}
for name, t in books.items():
    for i in range(0, len(t) - n + 1):
        grams.setdefault(t[i:i + n], name)
cur, hits = None, []
for line in io.open(deck, encoding='utf-8'):
    m = re.match(r'## (S\d+)', line)
    if m: cur = m.group(1); continue
    s = norm(line)
    i = 0
    while i <= len(s) - n:
        g = s[i:i + n]
        if g in grams:
            name = grams[g]; t = books[name]; j = i + n
            while j < len(s) and s[i:j + 1] in t: j += 1
            hits.append((cur, j - i, name, s[i:j], 'NOTE' if line.startswith('NOTE') else 'slide')); i = j
        else: i += 1
for h in hits: print('%s\t%d\t%s\t%s\t%s' % (h[0], h[1], h[4], h[2], h[3]))
print('hits', len(hits))
