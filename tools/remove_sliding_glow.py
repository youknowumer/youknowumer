#!/usr/bin/env python3
"""Removes the "sliding glow" from the panel SVGs.

Two effects were responsible:
  1. the travelling comet of light that circles every card border (a <g> holding six <rect pathLength="100">
     with animated stroke-dashoffset, drawn as wide low-opacity strokes = a soft glow);
  2. the border gradient whose x1/x2 slide back and forth (animate on <linearGradient>).
The static hairline border + gradient stay. Idempotent.

Usage: python3 tools/remove_sliding_glow.py .   (rewrites *.svg in the given directory in place)
"""
import glob, os, re, sys

DIR = sys.argv[1] if len(sys.argv) > 1 else '.'
COMET = re.compile(r'<g>(?:<rect\b[^>]*\bpathLength="100"[^>]*>(?:(?!</rect>).)*</rect>)+</g>', re.S)
GRAD_SLIDE = re.compile(r'<animate attributeName="x[12]"[^>]*/>')

for path in sorted(glob.glob(os.path.join(DIR, '*.svg'))):
    s = open(path, encoding='utf-8').read()
    s2, n_comet = COMET.subn('', s)
    s2, n_grad = GRAD_SLIDE.subn('', s2)
    if s2 != s:
        open(path, 'w', encoding='utf-8').write(s2)
    print(f'{os.path.basename(path):26s} comet groups removed: {n_comet}  sliding gradients: {n_grad}')
