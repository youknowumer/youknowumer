#!/usr/bin/env python3
"""Theme pass: violet/cyan -> Amber / Teal / Blue ("Ember & Lagoon"), plus detail upgrades.
Usage: retheme.py SRC_DIR DST_DIR   (reads every *.svg in SRC, writes to DST)"""
import re, sys, glob, os

SRC, DST = sys.argv[1], sys.argv[2]
os.makedirs(DST, exist_ok=True)

# ---- palette -------------------------------------------------------------
# dark-surface values (also used for any hardcoded colour outside a light block)
DARK = {
    '9B6DFF': 'F5B544',  # a1  violet  -> amber
    '28E0F0': '2DD4BF',  # a2  cyan    -> teal
    '6978FF': '5B9BFF',  # a3  indigo  -> blue
    'C0A2FF': 'FFD88C',  # a4  lilac   -> champagne
    '4AC8FF': '38BDF8',  # a5  sky     -> sky
    '42E6B4': '5EE08A',  # ok  mint    -> green
    '7C3AED': 'F5B544', '4F46E5': '5B9BFF', '087F9C': '2DD4BF', '0878B5': '38BDF8', '087F65': '5EE08A',
    '22D3EE': '2DD4BF', 'A78BFA': 'FFC56B', '8B5CF6': 'E89B1C', 'C4B5FD': 'FFE0A8',
    '67E8F9': '5EEAD4', 'A5F3FC': '99F6E4', '10B981': '34D399', '2563EB': '3B82F6', '164E63': '134E4A',
    # ink / neutrals: navy -> warm-neutral ink with a hint of teal
    '070B18': '080C12', '10182D': '111A22', '030712': '05080C', '060A14': '06090E',
    '3A4468': '3A4650', '2B3350': '2B343D', '343D5C': '34404A', '20263A': '20272E',
    '1E2438': '1E252C', '1A2036': '1A2128', '151A29': '151B21', '12151F': '12171C', '11152A': '11161C',
    '7889A8': '8093A3', 'A6B6D0': 'AAB8C4', 'D6E2F3': 'DCE6EE', 'F3F6FF': 'F8F5EE',
}
# light-surface overrides (inside @media (prefers-color-scheme: light))
LIGHT = dict(DARK)
LIGHT.update({
    '7C3AED': 'B45309', '4F46E5': '1D4ED8', '087F9C': '0F766E', '0878B5': '0369A1', '087F65': '15803D',
    'F3F6FF': 'F8F5EE', '7889A8': '7A8794', 'D6E2F3': 'D6E2F3',
})

HEX = re.compile(r'#([0-9a-fA-F]{6})\b')


def light_ranges(s):
    out = []
    for m in re.finditer(r'@media\s*\(prefers-color-scheme:\s*light\)\s*\{', s):
        i, depth = m.end(), 1
        while i < len(s) and depth:
            depth += (s[i] == '{') - (s[i] == '}')
            i += 1
        out.append((m.start(), i))
    return out


def recolor(s):
    rngs = light_ranges(s)
    def sub(m):
        key = m[1].upper()
        in_light = any(a <= m.start() < b for a, b in rngs)
        tbl = LIGHT if in_light else DARK
        if key not in tbl:
            return m[0]
        new = tbl[key]
        return '#' + (new.lower() if m[1].islower() else new)
    return HEX.sub(sub, s)


# ---- detail upgrades -----------------------------------------------------
CARD = re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" rx="([\d.]+)" fill="url\(#cardG\)" stroke="var\(--border\)"/>')

GLOSS_DEFS = (
    '<linearGradient id="pxGloss" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0%" stop-color="#fff" stop-opacity="0"/><stop offset="22%" stop-color="var(--a4,#FFD88C)" stop-opacity="0.55"/>'
    '<stop offset="62%" stop-color="var(--a2,#2DD4BF)" stop-opacity="0.35"/><stop offset="100%" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    '<linearGradient id="pxSheen" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0%" stop-color="var(--a1,#F5B544)" stop-opacity="0.10"/><stop offset="38%" stop-color="var(--a1,#F5B544)" stop-opacity="0"/></linearGradient>'
)


def card_detail(s):
    def rep(m):
        x, y, w, h, rx = (float(m[i]) for i in range(1, 6))
        if w < 120 or h < 40:
            return m[0]
        # top-edge gloss hairline + soft warm sheen inside the card + bottom shadow lip
        return (m[0]
                + f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="{h-2}" rx="{max(rx-1,0)}" fill="url(#pxSheen)" pointer-events="none"/>'
                + f'<path d="M{x+rx+4:.1f} {y+0.6:.1f}H{x+w-rx-4:.1f}" stroke="url(#pxGloss)" stroke-width="1.2" stroke-linecap="round" pointer-events="none"/>'
                + f'<path d="M{x+rx+10:.1f} {y+h-0.6:.1f}H{x+w-rx-10:.1f}" stroke="var(--a2,#2DD4BF)" stroke-opacity="0.14" stroke-width="1" stroke-linecap="round" pointer-events="none"/>')
    n = len(CARD.findall(s))
    if not n:
        return s
    s = CARD.sub(rep, s)
    return s.replace('</defs>', '    ' + GLOSS_DEFS + '\n  </defs>', 1)


def soften_aurora(s):
    # metaball threshold filter (hard-edged discs) -> soft diffuse aurora
    s = re.sub(r'<filter id="pxGoo"[^>]*>.*?</filter>',
               '<filter id="pxGoo" x="-20%" y="-40%" width="140%" height="180%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="42"/></filter>',
               s, flags=re.S)
    s = s.replace('<g filter="url(#pxGoo)" opacity="0.2"', '<g class="pxAur" filter="url(#pxGoo)" opacity="0.22"')
    if 'pxAur' in s:  # calmer wash on light backgrounds
        s = s.replace('</style>', '.pxAur{opacity:.22}@media (prefers-color-scheme: light){.pxAur{opacity:.11}}</style>', 1)
    return s


TEXT_FIXES = {
    ">Odoo implementation, customization &amp; reporting<": ">Odoo implementation &amp; customization<",
    ">Odoo implementation, customization & reporting<": ">Odoo implementation &amp; customization<",
    '>Implement, improve and support business workflows.<': '>Implement &amp; support ERP workflows.<',
    '>Odoo: implementation, customization, reporting, HR<': '>Odoo: setup, customization, reporting<',
    "ICAISAI'26 exhibition selectee": "ICAISAI'26 exhibitor",
}

for f in sorted(glob.glob(os.path.join(SRC, '*.svg'))):
    s = open(f, encoding='utf-8').read()
    s = recolor(s)
    s = soften_aurora(s)
    s = card_detail(s)
    for a, b in TEXT_FIXES.items():
        s = s.replace(a, b)
    open(os.path.join(DST, os.path.basename(f)), 'w', encoding='utf-8').write(s)
    print('ok', os.path.basename(f))
