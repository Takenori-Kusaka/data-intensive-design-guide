"""Shorten verbatim book quotations in review records so that no run of N or more characters matches the books.
Reviewers quoted the books to compare wording; the public records keep only the first few characters.
Usage: python tools/redact_quotes.py <books text dir> <N> <file>...   (books are not in the repository)"""
import sys, io, re, glob, os

bookdir, n, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
norm = lambda s: re.sub(r'\s+', '', s)
books = [norm(re.sub(r'===== PDF p\.\d+ / printed p\.[\d?]+ =====', '', io.open(f, encoding='utf-8').read()))
         for f in glob.glob(os.path.join(bookdir, '*.txt'))]
grams = set()
for t in books:
    for i in range(len(t) - n + 1): grams.add(t[i:i + n])
jp = re.compile(r'[぀-ヿ一-鿿]')
total = 0
for path in files:
    src = io.open(path, encoding='utf-8').read()
    out, changed = [], 0
    for line in src.split('\n'):
        while True:
            # positions of non-space characters, so matches can be mapped back to the original line
            idx = [k for k, ch in enumerate(line) if not ch.isspace()]
            s = ''.join(line[k] for k in idx)
            hit = None
            for i in range(len(s) - n + 1):
                if s[i:i + n] in grams:
                    j = i + n
                    while j < len(s) and any(s[i:j + 1] in t for t in books): j += 1
                    if len(jp.findall(s[i:j])) >= 12: hit = (i, j); break
            if not hit: break
            i, j = hit
            keep = 10
            line = line[:idx[i + keep]] + '…（中略）' + line[idx[j - 1] + 1:]
            changed += 1
        out.append(line)
    if changed:
        io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
        total += changed
        print(os.path.basename(path), changed)
print('shortened', total)
