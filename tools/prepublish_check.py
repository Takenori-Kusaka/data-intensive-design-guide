"""Pre-publication check: local paths, personal data and book files must not be in tracked files.
Usage: python tools/prepublish_check.py   (run at the repository root)"""
import subprocess, re, zipfile, sys, io
pat = re.compile(rb'[A-Za-z]:\\?(Users|Github)|/c/Users|[A-Za-z]:/(Users|Github)|AppData|@gmail\.com|BEGIN [A-Z ]*PRIVATE', re.I)
files = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, encoding='utf-8').stdout.split('\n')
bad = []
for f in filter(None, files):
    if re.search(r'(^|/)books/|research/deck_text|quote_hits|make\.sh$|(^|/)qa/', f): bad.append((f, 'must not be tracked'))
    if f == 'tools/prepublish_check.py': continue
    data = open(f, 'rb').read()
    if f.endswith('.pptx'):
        z = zipfile.ZipFile(f)
        for n in z.namelist():
            if pat.search(z.read(n)): bad.append((f + '!' + n, 'local path or personal data'))
    elif pat.search(data): bad.append((f, pat.search(data).group(0).decode('ascii', 'replace')))
for b in bad: sys.stdout.buffer.write(('%s\t%s\n' % b).encode('utf-8'))
print('files', len([f for f in files if f]), 'problems', len(bad))
