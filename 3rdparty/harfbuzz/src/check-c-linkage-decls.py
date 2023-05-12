#!/usr/bin/env python3

import sys, os

os.chdir (os.getenv ('srcdir', os.path.dirname (__file__)))

def removeprefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s[:]

HBHEADERS = [os.path.basename (x) for x in os.getenv ('HBHEADERS', '').split ()] or \
	[x for x in os.listdir ('.') if x.startswith ('hb') and x.endswith ('.h')]
HBSOURCES = [
    removeprefix(x, f'src{os.path.sep}')
    for x in os.getenv('HBSOURCES', '').split()
] or [
    x
    for x in os.listdir('.')
    if x.startswith('hb') and x.endswith(('.cc', '.hh'))
]
stat = 0

for x in HBHEADERS:
    with open (x, 'r', encoding='utf-8') as f: content = f.read ()
    if ('HB_BEGIN_DECLS' not in content) or ('HB_END_DECLS' not in content):
        print(
            f'Ouch, file {x} does not have HB_BEGIN_DECLS / HB_END_DECLS, but it should'
        )
        stat = 1

for x in HBSOURCES:
	with open (x, 'r', encoding='utf-8') as f: content = f.read ()
	if ('HB_BEGIN_DECLS' in content) or ('HB_END_DECLS' in content):
		print ('Ouch, file %s has HB_BEGIN_DECLS / HB_END_DECLS, but it shouldn\'t' % x)
		stat = 1

sys.exit (stat)
