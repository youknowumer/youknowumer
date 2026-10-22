#!/usr/bin/env python3
"""iOS system-colour theme ("Apple Glass") for the profile SVGs.

Amber / teal / champagne  ->  single iOS Blue family (blue, azure, sky) + neutral greys
Warm-neutral ink          ->  iOS system greys (secondarySystemBackground family)
Linear entrances          ->  spring entrances (overshoot + settle), iOS ease curves
Flat card highlights      ->  specular glass edge (white in dark mode, blue in light mode)

Usage: retheme_ios.py SRC_DIR DST_DIR     (reads every *.svg in SRC, writes to DST)
"""
import re, sys, glob, os

SRC, DST = sys.argv[1], sys.argv[2]
os.makedirs(DST, exist_ok=True)

# ---- iOS system palette --------------------------------------------------
# dark  : iOS dark-mode system colours      light : iOS light-mode system colours (a touch deeper for text contrast)
DK = dict(blue='0A84FF', indigo='3D9BFF', purple='5AC8FA', cyan='8EC5FF', mint='64D2FF', green='30D158')
LT = dict(blue='007AFF', indigo='1F6FE0', purple='0A8FBF', cyan='3A8BEA', mint='0A84C1', green='248A3D')

def accents(P):
    # a1..a5 : gradient order is a1 -> a2 -> a5  (blue -> indigo -> purple)
    return {'a1': P['blue'], 'a2': P['indigo'], 'a3': P['mint'], 'a4': P['cyan'], 'a5': P['purple'], 'ok': P['green'],
            'accent1': P['blue'], 'accent2': P['indigo'], 'accent3': P['purple'], 'accent4': P['cyan'], 'accent5': P['mint']}

VARS_DARK = {
    'bg': '#050506', 'bg2': '#121214', 'surface': '#101012', 'surface2': '#1C1C1E', 'border2': '#38383A',
    'card': 'rgba(255,255,255,0.03)', 'cardHi': 'rgba(255,255,255,0.07)', 'border': 'rgba(255,255,255,0.11)',
    'text': '#FFFFFF', 'text2': '#E5E5EA', 'muted': '#AEAEB2', 'muted2': '#8E8E93',
    'chip': 'rgba(255,255,255,0.06)', 'chipB': 'rgba(255,255,255,0.16)', 'track': 'rgba(255,255,255,0.09)',
    'grid': 'rgba(255,255,255,0.045)', 'pillBg': 'rgba(255,255,255,0.06)', 'pillBorder': 'rgba(255,255,255,0.16)',
    'pillHover': 'rgba(255,255,255,0.10)', 'spec': '#FFFFFF',
}
VARS_LIGHT = {
    'bg': '#FFFFFF', 'bg2': '#F2F2F7', 'surface': '#F9F9FB', 'surface2': '#F2F2F7', 'border2': '#D1D1D6',
    'card': 'rgba(60,60,67,0.03)', 'cardHi': 'rgba(60,60,67,0.07)', 'border': 'rgba(60,60,67,0.16)',
    'text': '#1C1C1E', 'text2': '#3A3A3C', 'muted': '#545458', 'muted2': '#6E6E73',
    'chip': 'rgba(60,60,67,0.05)', 'chipB': 'rgba(60,60,67,0.20)', 'track': 'rgba(60,60,67,0.11)',
    'grid': 'rgba(60,60,67,0.07)', 'pillBg': 'rgba(60,60,67,0.045)', 'pillBorder': 'rgba(60,60,67,0.18)',
    'pillHover': 'rgba(60,60,67,0.08)', 'spec': '#007AFF',
}
V_D = {**VARS_DARK, **{k: '#' + v for k, v in accents(DK).items()}}
V_L = {**VARS_LIGHT, **{k: '#' + v for k, v in accents(LT).items()}}

# hard-coded hexes left over from the previous "Ember & Lagoon" pass (fallbacks, robot.svg ink)
HEX_DARK = {
    'F5B544': DK['blue'], '2DD4BF': DK['indigo'], 'FFD88C': DK['cyan'], '5EE08A': DK['green'], '38BDF8': DK['purple'],
    '3A4650': '3A3A3C', '2B343D': '2C2C2E', '06090E': '050506', '1A2128': '1C1C1E', '10131F': '0C0C0E',
    '34404A': '38383A', '1E252C': '1F1F22', '12171C': '141416', '151B21': '18181A', '080C12': '0A0A0F', '111A22': '1C1C1E',
}
HEX_LIGHT = dict(HEX_DARK, **{'F5B544': LT['blue'], '2DD4BF': LT['indigo'], 'FFD88C': LT['cyan'], '38BDF8': LT['purple']})

EXPO_OUT_OLD = '0.16 1 0.3 1'
IOS_OUT = '0.32 0.72 0 1'      # iOS "spring-like" decelerate
IOS_IO = '0.42 0 0.58 1'       # iOS standard ease-in-out
EASE_IO_OLD = '0.45 0 0.55 1'

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
        # make sure the specular token exists everywhere cards are drawn
        if '--spec' not in body and '--cardHi' in body:
            body = body.rstrip() + f' --spec: {table["spec"]};\n      '
        return m[1] + body + m[3]
    return ROOT.sub(block, s)


def retheme_hex(s):
    rngs = media_light_ranges(s)
    roots = [(m.start(), m.end()) for m in ROOT.finditer(s)]

    def sub(m):
        if any(a <= m.start() < b for a, b in roots):
            return m[0]                      # variables were handled above
        key = m[1].upper()
        light = any(a <= m.start() < b for a, b in rngs)
        tbl = HEX_LIGHT if light else HEX_DARK
        if key not in tbl:
            return m[0]
        new = tbl[key]
        return '#' + (new.lower() if m[1].islower() else new)
    return re.sub(r'#([0-9a-fA-F]{6})\b', sub, s)


def glass_edge(s):
    # specular top edge: white (dark) / blue (light) instead of a tinted gold line
    s = s.replace('<stop offset="22%" stop-color="var(--a4,#64D2FF)" stop-opacity="0.55"/>',
                  '<stop offset="22%" stop-color="var(--spec,#fff)" stop-opacity="0.62"/>')
    s = s.replace('<stop offset="62%" stop-color="var(--a2,#7D7AFF)" stop-opacity="0.35"/>',
                  '<stop offset="62%" stop-color="var(--a4,#64D2FF)" stop-opacity="0.30"/>')
    # soft inner sheen: calmer, bluer
    s = s.replace('<stop offset="0%" stop-color="var(--a1,#0A84FF)" stop-opacity="0.10"/>',
                  '<stop offset="0%" stop-color="var(--spec,#fff)" stop-opacity="0.075"/>')
    return s


def spring_entrance(s):
    # translate 18px -> 0 with a real spring: overshoot, undershoot, settle
    pat = re.compile(r'<animateTransform attributeName="transform" type="translate" values="0 18;0 0" keyTimes="0;1" '
                     r'calcMode="spline" keySplines="' + re.escape(EXPO_OUT_OLD) + r'" begin="([\d.]+)s" dur="1\.1s" fill="freeze"/>')
    return pat.sub(lambda m: (
        f'<animateTransform attributeName="transform" type="translate" values="0 22;0 -3.2;0 1.1;0 0" '
        f'keyTimes="0;0.52;0.8;1" calcMode="spline" keySplines="{IOS_OUT};{IOS_IO};{IOS_IO}" '
        f'begin="{m[1]}s" dur="1.35s" fill="freeze"/>'), s)


def ios_curves(s):
    s = s.replace(EASE_IO_OLD, IOS_IO)
    return s


def calmer_aurora(s):
    # ambient blobs: single blue family, very soft
    s = re.sub(r'(<circle cx="\d+" cy="\d+" r="\d+" fill=")var\(--a[3-5],#[0-9A-Fa-f]{6}\)(">)', r'\1var(--a1,#0A84FF)\2', s)
    s = s.replace('opacity="0.22" pointer-events="none"', 'opacity="0.13" pointer-events="none"')
    s = s.replace('.pxAur{opacity:.22}@media (prefers-color-scheme: light){.pxAur{opacity:.11}}',
                  '.pxAur{opacity:.13}@media (prefers-color-scheme: light){.pxAur{opacity:.08}}')
    return s


for f in sorted(glob.glob(os.path.join(SRC, '*.svg'))):
    s = open(f, encoding='utf-8').read()
    s = retheme_vars(s)
    s = retheme_hex(s)
    s = glass_edge(s)
    s = spring_entrance(s)
    s = ios_curves(s)
    s = calmer_aurora(s)
    open(os.path.join(DST, os.path.basename(f)), 'w', encoding='utf-8').write(s)
    print('ok', os.path.basename(f))
