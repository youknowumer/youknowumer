#!/usr/bin/env python3
"""Removes decorative background effects from the profile SVGs, keeping content + glass cards.

Removed : animated aurora blobs (.pxAur / .aur), large ambient radial glows (gl1..gl5, auraG*),
          dot / grid texture, film grain, and the diagonal 'shine' band that sweeps across cards.
Kept    : base background gradient, glass cards (cardG / sheen / hairline), accents, content, robot.

Usage: clean_bg.py SRC_DIR DST_DIR
"""
import re, sys, os, glob
from lxml import etree

SRC, DST = sys.argv[1], sys.argv[2]
os.makedirs(DST, exist_ok=True)
NS = '{http://www.w3.org/2000/svg}'
BG_REF = re.compile(r'url\(#(dots|gridP|pxGrain|gl\d|auraG\d?)\)')
SHINE = re.compile(r'url\(#pxShine\)')


def drop(el):
    p = el.getparent()
    if p is not None:
        p.remove(el)


for path in sorted(glob.glob(os.path.join(SRC, '*.svg'))):
    tree = etree.parse(path)
    root = tree.getroot()
    removed = 0
    for el in list(root.iter()):
        if not isinstance(el.tag, str) or el.getparent() is None:
            continue
        if el.tag in (NS + 'defs', NS + 'style', NS + 'title', NS + 'desc'):
            continue
        # inside defs? leave definitions alone
        if any(a.tag == NS + 'defs' for a in el.iterancestors()):
            continue
        cls = (el.get('class') or '').split()
        refs = ' '.join(filter(None, [el.get('fill'), el.get('filter'), el.get('style')]))
        if 'pxAur' in cls or 'aur' in cls or BG_REF.search(refs):
            drop(el); removed += 1
    # shine sweep = <g clip-path=...><rect fill=url(#pxShine) ...animateTransform/></g>
    for g in list(root.iter(NS + 'g')):
        kids = [k for k in g if isinstance(k.tag, str)]
        if g.getparent() is not None and len(kids) == 1 and kids[0].tag == NS + 'rect' and SHINE.search(kids[0].get('fill') or ''):
            drop(g); removed += 1
    out = etree.tostring(root, encoding='unicode')
    open(os.path.join(DST, os.path.basename(path)), 'w', encoding='utf-8').write(out)
    print(f'{os.path.basename(path):24s} removed {removed}')
