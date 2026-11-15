#!/usr/bin/env python3
"""Warm iOS ("Apple Glass, Amber Hour") theme + calmer motion for the profile SVGs.

Colour   iOS Blue family      ->  iOS Orange / Ember / Amber / Gold family
         cool iOS greys        ->  warm-tinted iOS greys (espresso dark, cream light)
         rgba white / slate    ->  warm-tinted glass fills and hairlines
Motion   spring entrance      ->  one decelerate curve, 14px travel, no bounce
         ambient loops < 6s   ->  slowed x1.8 so pulses breathe instead of flicker
Detail   tabular figures, geometric text rendering, warm specular edge

Usage: retheme_warm_ios.py SRC_DIR DST_DIR      (reads *.svg in SRC, writes to DST)
"""
import re, sys, glob, os

SRC, DST = sys.argv[1], sys.argv[2]
os.makedirs(DST, exist_ok=True)

# ---- accent families -------------------------------------------------------
# a1 -> a2 -> a5 is the gradient order used by every SVG (blue->indigo->sky before)
DK = dict(a1='FF9F0A', a2='FF7A3D', a3='F2C14E', a4='FFC987', a5='FFB340', ok='30D158')
LT = dict(a1='D96A00', a2='C2501A', a3='B07A00', a4='B86A1F', a5='E08A00', ok='248A3D')

# ---- neutrals --------------------------------------------------------------
N_DARK = {
    'bg': '#0C0907', 'bg2': '#16110D', 'surface': '#120E0B', 'surface2': '#1F1813', 'border2': '#3A2F26',
    'card': 'rgba(255,236,214,0.035)', 'cardHi': 'rgba(255,236,214,0.08)', 'border': 'rgba(255,226,190,0.12)',
    'text': '#FFF8F0', 'text2': '#EADFD2', 'muted': '#B8A999', 'muted2': '#8F8174',
    'chip': 'rgba(255,236,214,0.06)', 'chipB': 'rgba(255,226,190,0.17)', 'track': 'rgba(255,226,190,0.10)',
    'grid': 'rgba(255,226,190,0.05)', 'pillBg': 'rgba(255,236,214,0.06)', 'pillBorder': 'rgba(255,226,190,0.17)',
    'pillHover': 'rgba(255,236,214,0.11)', 'spec': '#FFF1DC',
}
N_LIGHT = {
    'bg': '#FFFCF7', 'bg2': '#F8F1E7', 'surface': '#FDF8F1', 'surface2': '#F8F1E7', 'border2': '#DED2C3',
    'card': 'rgba(120,84,40,0.035)', 'cardHi': 'rgba(120,84,40,0.075)', 'border': 'rgba(120,84,40,0.17)',
    'text': '#2A2018', 'text2': '#4A3B2E', 'muted': '#65533F', 'muted2': '#7D6A56',
    'chip': 'rgba(120,84,40,0.055)', 'chipB': 'rgba(120,84,40,0.22)', 'track': 'rgba(120,84,40,0.12)',
    'grid': 'rgba(120,84,40,0.07)', 'pillBg': 'rgba(120,84,40,0.05)', 'pillBorder': 'rgba(120,84,40,0.20)',
    'pillHover': 'rgba(120,84,40,0.09)', 'spec': '#D96A00',
}


def accents(P):
    return {'a1': P['a1'], 'a2': P['a2'], 'a3': P['a3'], 'a4': P['a4'], 'a5': P['a5'], 'ok': P['ok'],
            'accent1': P['a1'], 'accent2': P['a2'], 'accent3': P['a5'], 'accent4': P['a4'], 'accent5': P['a3']}


V_D = {**N_DARK, **{k: '#' + v for k, v in accents(DK).items()}}
V_L = {**N_LIGHT, **{k: '#' + v for k, v in accents(LT).items()}}

# hard-coded hexes currently in the files (outside :root) -> warm equivalents
HEX_DARK = {
    '0A84FF': DK['a1'], '3D9BFF': DK['a2'], '8EC5FF': DK['a4'], '64D2FF': DK['a3'], '5AC8FA': DK['a5'],
    '050506': '0C0907', '121214': '16110D', '1C1C1E': '1F1813', '2C2C2E': '2A211A', '3A3A3C': '3A2F26',
    '38383A': '3A2F26', '1F1F22': '231B15', '18181A': '1B1510', '141416': '17120E', '101012': '120E0B',
    '0C0C0E': '0F0B08', 'E5E5EA': 'EADFD2', 'AEAEB2': 'B8A999', '8E8E93': '8F8174',
}
HEX_LIGHT = {
    '007AFF': LT['a1'], '1F6FE0': LT['a2'], '3A8BEA': LT['a4'], '0A84C1': LT['a3'], '0A8FBF': LT['a5'],
    '1C1C1E': '2A2018', '3A3A3C': '4A3B2E', '545458': '65533F', '6E6E73': '7D6A56', 'F2F2F7': 'F8F1E7',
    'F9F9FB': 'FDF8F1', 'D1D1D6': 'DED2C3', 'FFFFFF': 'FFFFFF',
}
# colours that appear in both schemes' shared (non-media) code are dark-scheme colours
ROOT = re.compile(r'(:root\s*\{)([^}]*)(\})')
DECL = re.compile(r'--([A-Za-z0-9]+)\s*:\s*([^;]+);')


def media_light_ranges(s):
    out = []
    for m in re.finditer(r'@media\s*\(prefers-color-scheme:\s*light\)\s*\{', s):
        i, depth = m.end(), 1
        while i < len(s) and depth:
            depth += (s[i] == '{') - (s[i] == '}')
            i += 1
        out.append((m.start(), i))
    return out


def retheme_vars(s):
    rngs = media_light_ranges(s)

    def block(m):
        light = any(a <= m.start() < b for a, b in rngs)
        table = V_L if light else V_D
        body = DECL.sub(lambda d: f'--{d[1]}: {table[d[1]]};' if d[1] in table else d[0], m[2])
        return m[1] + body + m[3]
    return ROOT.sub(block, s)


def retheme_hex(s):
    rngs = media_light_ranges(s)
    roots = [(m.start(), m.end()) for m in ROOT.finditer(s)]

    def sub(m):
        if any(a <= m.start() < b for a, b in roots):
            return m[0]
        light = any(a <= m.start() < b for a, b in rngs)
        tbl = HEX_LIGHT if light else HEX_DARK
        new = tbl.get(m[1].upper())
        return m[0] if new is None else '#' + (new.lower() if m[1].islower() else new)
    return re.sub(r'#([0-9a-fA-F]{6})\b', sub, s)


def retheme_rgba(s):
    # glass fills / hairlines: neutral white & slate -> warm tint (alpha preserved)
    s = re.sub(r'rgba\(255,\s*255,\s*255,\s*([\d.]+)\)', r'rgba(255,236,214,\1)', s)
    s = re.sub(r'rgba\(60,\s*60,\s*67,\s*([\d.]+)\)', r'rgba(120,84,40,\1)', s)
    return s


# ---- motion ----------------------------------------------------------------
SPRING = re.compile(
    r'<animateTransform attributeName="transform" type="translate" values="0 \d+;0 -[\d.]+;0 [\d.]+;0 0" '
    r'keyTimes="0;[\d.]+;[\d.]+;1" calcMode="spline" keySplines="[^"]+" begin="([\d.]+)s" dur="[\d.]+s" fill="freeze"/>')
SMOOTH = ('<animateTransform attributeName="transform" type="translate" values="0 14;0 0" keyTimes="0;1" '
          'calcMode="spline" keySplines="0.22 1 0.36 1" begin="{b}s" dur="1.05s" fill="freeze"/>')
AMBIENT_SLOWDOWN = 1.8


def calm_motion(s):
    s = SPRING.sub(lambda m: SMOOTH.format(b=m[1]), s)

    def slow(m):
        tag = m[0]
        if 'repeatCount="indefinite"' not in tag:
            return tag
        d = re.search(r'dur="([\d.]+)s"', tag)
        if not d or float(d[1]) >= 6:
            return tag
        return tag.replace(d[0], f'dur="{round(float(d[1]) * AMBIENT_SLOWDOWN, 2):g}s"')
    return re.sub(r'<animate\w*\b[^>]*>', slow, s)


def detailing(s):
    # tabular figures for stats/counters, crisp glyph rendering, warm specular token present
    s = s.replace('text { font-family:',
                  'text { font-variant-numeric: tabular-nums; text-rendering: geometricPrecision; font-family:', 1)
    return s


for path in sorted(glob.glob(os.path.join(SRC, '*.svg'))):
    s = open(path, encoding='utf-8').read()
    s = retheme_vars(s)
    s = retheme_hex(s)
    s = retheme_rgba(s)
    s = calm_motion(s)
    s = detailing(s)
    open(os.path.join(DST, os.path.basename(path)), 'w', encoding='utf-8').write(s)
    print('ok', os.path.basename(path))
