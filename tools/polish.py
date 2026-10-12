#!/usr/bin/env python3
"""Motion + detail polish pass. Reads originals from SRC, writes upgraded SVGs to DST."""
import re, sys, glob, os
SRC, DST = sys.argv[1], sys.argv[2]

EXPO_OUT = "0.16 1 0.3 1"      # entrance: fast attack, long settle
EASE_IO  = "0.45 0 0.55 1"     # loops: smooth in/out

def ease_entrance(s):
    # fade + rise entrances: linear -> expo-out, longer, travel a bit farther
    s = re.sub(r'<animate attributeName="opacity" from="0" to="1" begin="([\d.]+)s" dur="0\.7s" fill="freeze"/>',
               lambda m: f'<animate attributeName="opacity" values="0;1" keyTimes="0;1" calcMode="spline" keySplines="0.22 0.61 0.36 1" begin="{m[1]}s" dur="0.9s" fill="freeze"/>', s)
    s = re.sub(r'<animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="([\d.]+)s" dur="0\.7s" fill="freeze"/>',
               lambda m: f'<animateTransform attributeName="transform" type="translate" values="0 18;0 0" keyTimes="0;1" calcMode="spline" keySplines="{EXPO_OUT}" begin="{m[1]}s" dur="1.1s" fill="freeze"/>', s)
    return s

def ease_loops(s):
    # any looping <animate> with a values list and no calcMode gets eased segments
    def fix(m):
        tag = m.group(0)
        if 'calcMode' in tag or 'repeatCount="indefinite"' not in tag: return tag
        v = re.search(r'values="([^"]+)"', tag)
        if not v: return tag
        n = len(v[1].split(';'))
        if n < 2: return tag
        kt = re.search(r'keyTimes="([^"]+)"', tag)
        if kt and len(kt[1].split(';')) != n: return tag
        if 'attributeName="opacity"' in tag and kt and n >= 5: return tag  # blink patterns stay crisp
        splines = ';'.join([EASE_IO]*(n-1))
        extra = f' calcMode="spline" keySplines="{splines}"'
        if not kt:
            extra = f' keyTimes="{";".join(f"{i/(n-1):g}" for i in range(n))}"' + extra
        return tag[:-2] + extra + '/>' if tag.endswith('/>') else tag
    return re.sub(r'<animate(?:Transform)? [^>]*?/>', fix, s)

PANEL = re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" rx="([\d.]+)" fill="none" stroke="url\(#\w+\)" stroke-opacity="0\.55" stroke-width="1\.5"/>')
CARD  = re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" rx="([\d.]+)" fill="url\(#cardG\)" stroke="var\(--border\)"/>')

DEFS = '''
    <linearGradient id="pxShine" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="var(--a4,#A78BFA)" stop-opacity="0"/><stop offset="50%" stop-color="var(--a4,#A78BFA)" stop-opacity="0.20"/><stop offset="100%" stop-color="var(--a4,#A78BFA)" stop-opacity="0"/></linearGradient>
    <filter id="pxGrain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="7" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.9 -0.28"/></filter>
'''

def card_shine(s, base_delay=2.4):
    n = [0]
    defs, out = [], []
    def rep(m):
        x,y,w,h,rx = (float(m[i]) for i in range(1,6))
        if w < 120 or h < 40: return m[0]
        i = n[0]; n[0] += 1
        cid = f'pxc{i}'
        defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>')
        band = min(110, w*0.4)
        d = base_delay + i*0.45
        total = 11.0
        kt = f'0;{1.5/total:.4f};1'
        shine = (f'<g clip-path="url(#{cid})" pointer-events="none"><rect x="{x-band*1.6:.1f}" y="{y-8}" width="{band:.1f}" height="{h+16}" fill="url(#pxShine)" transform="skewX(-18)">'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;{w+band*3.2:.1f} 0;{w+band*3.2:.1f} 0" keyTimes="{kt}" calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1" dur="{total}s" begin="{d:.2f}s" repeatCount="indefinite" additive="sum"/>'
                 f'</rect></g>')
        return m[0] + shine
    s = CARD.sub(rep, s)
    if defs: s = s.replace('</defs>', '    ' + ''.join(defs) + '\n  </defs>', 1)
    return s

def panel_fx(s):
    m = PANEL.search(s)
    if not m: return s
    x,y,w,h,rx = (float(m[i]) for i in range(1,6))
    W = float(re.search(r'<svg[^>]*width="([\d.]+)"', s)[1]); H = float(re.search(r'<svg[^>]*height="([\d.]+)"', s)[1])
    s = s.replace('</defs>', DEFS + '  </defs>', 1)
    # 1) soft light sweep + grain, just above the dot grid
    dots = re.search(r'<rect[^>]*fill="url\(#(?:dots|gridP|dotsF)\)"[^>]*/>', s)
    sweep = (f'<rect x="-340" y="-20" width="300" height="{H+40:.0f}" fill="url(#pxShine)" transform="skewX(-16)" opacity="0.55" pointer-events="none">'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;{W+700:.0f} 0;{W+700:.0f} 0" keyTimes="0;0.34;1" calcMode="spline" keySplines="0.45 0 0.2 1;0 0 1 1" dur="16s" begin="1.2s" repeatCount="indefinite" additive="sum"/></rect>'
             f'<rect width="{W:.0f}" height="{H:.0f}" filter="url(#pxGrain)" opacity="0.05" pointer-events="none"/>')
    if dots: s = s.replace(dots[0], dots[0] + sweep, 1)
    # 2) travelling border beams (two, opposite phase), pathLength-normalised so dash math is perimeter-independent
    def beam(col, begin):
        out = ''
        for L, op, sw in ((22, 0.16, 2.6), (11, 0.42, 2.2), (4, 1.0, 1.8)):
            off = L - 22
            out += (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" '
                    f'stroke-opacity="{op}" pathLength="100" stroke-dasharray="{L} {100-L}" stroke-dashoffset="{off}" pointer-events="none">'
                    f'<animate attributeName="stroke-dashoffset" values="{off};{off-100}" dur="12s" begin="{begin}" repeatCount="indefinite"/></rect>')
        return out
    beams = '<g>' + beam('var(--a2,#22D3EE)', '1.6s') + beam('var(--a1,#8B5CF6)', '-4.4s') + '</g>'
    s = s.replace(m[0], m[0] + beams, 1)
    # 3) live-indicator ring on the section marker square
    s = s.replace('<rect x="40" y="39" width="8" height="8" rx="2" fill="url(#acc)"/>',
        '<rect x="40" y="39" width="8" height="8" rx="2" fill="url(#acc)"/>'
        '<circle cx="44" cy="43" r="5" fill="none" stroke="var(--a2,#22D3EE)" stroke-width="1.2" opacity="0">'
        '<animate attributeName="r" values="5;14" dur="2.8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.6 0.3 1" begin="1.4s"/>'
        '<animate attributeName="opacity" values="0.7;0" dur="2.8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.6 0.3 1" begin="1.4s"/></circle>', 1)
    return s

for f in sorted(glob.glob(os.path.join(SRC, '*.svg'))):
    s = open(f, encoding='utf-8').read()
    s = ease_entrance(s)
    s = ease_loops(s)
    s = card_shine(s, 0.9 if 'icon-' in f else 2.4)
    s = panel_fx(s)
    open(os.path.join(DST, os.path.basename(f)), 'w', encoding='utf-8').write(s)
    print('ok', os.path.basename(f))
