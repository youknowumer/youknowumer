#!/usr/bin/env python3
"""Original armoured hero robot ("Vanguard") for robot.svg - replaces the previous mascot.

Design: graphite plate armour with amber trim, angular helmet with a single large camera-lens eye,
broad pauldrons, segmented chest light-bar, thruster boots with a flickering exhaust.

Motion: hover + breathing on incommensurate periods, head scan with lens refocus, antenna spring,
pauldron lag, flame flicker, ground shadow reacting to height, greeting wave every 16 s.

Usage: python3 tools/gen_robot_armor.py robot.svg   (idempotent, replaces ROBOT-START..ROBOT-END)
"""
import re, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else 'robot.svg'
S = 0.84
GROUND_Y = 374           # floor line in panel coordinates
CX = 240                 # centre of left column
GROUND_N = 436           # authored floor line
TX = CX - 220 * S
TY = GROUND_Y - GROUND_N * S
START, END = '<!--ROBOT-START-->', '<!--ROBOT-END-->'
EASE, SINE, OUT = '0.45 0 0.55 1', '0.37 0 0.63 1', '0.22 1 0.36 1'
STROKE = '#2c221a'


def n(x):
    return f'{x:.4g}'


def anim(kind, frames, dur, begin=None, extra=''):
    kt = ';'.join(n(f[0]) for f in frames)
    vals = ';'.join(str(f[1]) for f in frames)
    sp = ';'.join(f[2] for f in frames[:-1])
    b = f' begin="{begin}s"' if begin is not None else ''
    head = (f'<animateTransform attributeName="transform" type="{kind}"' if kind in ('rotate', 'translate', 'scale')
            else f'<animate attributeName="{kind}"')
    return f'{head} values="{vals}" keyTimes="{kt}" calcMode="spline" keySplines="{sp}"{b} dur="{dur}s" repeatCount="indefinite"{extra}/>'


def breathe(a, b, dur, kind, begin=None):
    return anim(kind, [(0, a, SINE), (.5, b, SINE), (1, a, SINE)], dur, begin)


EXTRA_DEFS = '''
<linearGradient id="armorG" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#4b3c2f"/><stop offset=".5" stop-color="#2d231b"/><stop offset="1" stop-color="#15100c"/>
</linearGradient>
<linearGradient id="armorHi" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#6a5644"/><stop offset=".55" stop-color="#3b2e24"/><stop offset="1" stop-color="#211912"/>
</linearGradient>
<linearGradient id="trimG" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#FFB340"/><stop offset="1" stop-color="#FF7A3D"/>
</linearGradient>
<linearGradient id="flameG" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FFE2B0" stop-opacity=".95"/><stop offset=".35" stop-color="#FFB340" stop-opacity=".8"/>
  <stop offset="1" stop-color="#FF7A3D" stop-opacity="0"/>
</linearGradient>
<radialGradient id="irisG" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#FFF1DC"/><stop offset=".25" stop-color="#FFB340"/><stop offset=".7" stop-color="#FF7A3D"/>
  <stop offset="1" stop-color="#B8431A"/>
</radialGradient>
'''


def sleeve(w, h, hi=True):
    return f'<rect x="{-w/2}" y="-2" width="{w}" height="{h}" rx="{w/2.4:.1f}" fill="url(#{"armorHi" if hi else "armorG"})" stroke="{STROKE}" stroke-width="1.5"/>'


def arm_parts():
    upper = sleeve(18, 42, False) + '<rect x="-9" y="10" width="18" height="2" fill="url(#trimG)" opacity=".7"/>'
    elbow = f'<circle cx="0" cy="40" r="8.5" fill="url(#armorG)" stroke="{STROKE}" stroke-width="1.5"/><circle cx="0" cy="40" r="2.6" fill="#FFB340" opacity=".8"/>'
    fore = (sleeve(22, 40, True) + '<rect x="-11" y="12" width="22" height="2" fill="url(#trimG)" opacity=".7"/>'
            f'<rect x="-6.5" y="36" width="13" height="13" rx="4.5" fill="url(#armorG)" stroke="{STROKE}" stroke-width="1.4"/>'
            '<path d="M-2.2 41 V47 M2.2 41 V47" stroke="#000" stroke-opacity=".45" stroke-width="1"/>'
            f'<rect x="6" y="38" width="4" height="8" rx="2" fill="url(#armorG)" stroke="{STROKE}" stroke-width="1"/>')
    return upper, elbow, fore


def pauldron(sign):
    """sign=+1 right, -1 left; drawn around its own origin (the shoulder joint)"""
    g = f'transform="scale({sign},1)"'
    return (f'<g {g}>'
            f'<path d="M-24 8 Q-22 -22 4 -26 Q30 -24 32 6 Q22 20 -2 20 Q-18 18 -24 8Z" fill="url(#armorHi)" stroke="{STROKE}" stroke-width="2" stroke-linejoin="round"/>'
            '<path d="M-17 7 Q-14 -15 5 -19 Q24 -16 26 3" fill="none" stroke="url(#trimG)" stroke-width="1.8" stroke-linecap="round" opacity=".9"/>'
            '<path d="M-8 12 H14 M-4 16 H10" stroke="#000" stroke-opacity=".38" stroke-width="1.4" stroke-linecap="round"/>'
            '</g>')


def build():
    o = []
    A = o.append
    A('<circle cx="240" cy="240" r="200" fill="url(#auraG)"/>')
    A('<circle cx="1080" cy="320" r="220" fill="url(#auraG2)"/>')
    for x, y0, y1, d, b, r in [(100, 372, 190, 13, 0, 1.6), (372, 350, 150, 16, 4, 1.4), (310, 395, 215, 11, 8, 1.2),
                               (160, 380, 130, 15, 2, 1.1), (405, 380, 235, 12, 6, 1.5)]:
        A(f'<circle cx="{x}" cy="{y0}" r="{r}" fill="#FFC987" opacity="0">'
          + anim('cy', [(0, y0, EASE), (1, y1, EASE)], d, b)
          + anim('opacity', [(0, 0, EASE), (.2, .5, EASE), (.8, .5, EASE), (1, 0, EASE)], d, b) + '</circle>')

    A('<g opacity="0"><animate attributeName="opacity" values="0;1" keyTimes="0;1" calcMode="spline" keySplines="0.22 0.61 0.36 1" '
      'begin="0.1s" dur="0.9s" fill="freeze"/>'
      f'<animateTransform attributeName="transform" type="translate" values="0 14;0 0" keyTimes="0;1" calcMode="spline" keySplines="{OUT}" '
      'begin="0.1s" dur="1.1s" fill="freeze"/>')
    A(f'<g transform="translate({n(TX)},{n(TY)}) scale({S})">')

    # floor: thruster light pool + shadow, reacting to hover height
    A('<ellipse cx="220" cy="438" rx="72" ry="9" fill="url(#floorGlow)">' + breathe(1, .5, 6.2, 'opacity') + '</ellipse>')
    A('<ellipse cx="220" cy="438" rx="66" ry="11" fill="url(#shadowGrad)">'
      + breathe(66, 50, 6.2, 'rx') + breathe(.95, .5, 6.2, 'opacity') + '</ellipse>')

    A('<g>' + breathe('0 0', '0 -10', 6.2, 'translate'))

    # ---- legs + thruster boots (behind torso)
    A('<g transform="translate(220,356)"><g>' + breathe(0, 1.0, 6.2, 'rotate', .35) + '<g transform="translate(-220,-356)">')
    for cx in (198, 242):
        x0 = cx - 10
        A(f'<rect x="{x0}" y="354" width="20" height="28" rx="8" fill="url(#armorG)" stroke="{STROKE}" stroke-width="1.5"/>')
        A(f'<path d="M{cx-12} 380 Q{cx} 370 {cx+12} 380 L{cx+10} 392 Q{cx} 396 {cx-10} 392Z" fill="url(#armorHi)" stroke="{STROKE}" stroke-width="1.5" stroke-linejoin="round"/>')
        A(f'<rect x="{cx-9}" y="392" width="18" height="14" rx="5" fill="url(#armorG)" stroke="{STROKE}" stroke-width="1.5"/>')
        A(f'<path d="M{cx-9} 396 H{cx+9}" stroke="url(#trimG)" stroke-width="1.6" opacity=".8"/>')
        A(f'<rect x="{cx-13}" y="403" width="26" height="9" rx="4" fill="url(#armorHi)" stroke="{STROKE}" stroke-width="1.5"/>')
        A(f'<rect x="{cx-9}" y="411" width="18" height="4" rx="2" fill="#0C0907" stroke="#FFB340" stroke-width="1"/>')
        # exhaust: irregular flicker (length + brightness), not a loop you can see
        ph = 0 if cx < 220 else .23
        A(f'<g transform="translate({cx},414)"><g>'
          + anim('scale', [(0, '1 1', SINE), (.18, '.92 .78', SINE), (.37, '1.04 1.12', SINE), (.58, '.95 .86', SINE), (.8, '1.02 1.06', SINE), (1, '1 1', SINE)], 1.1, ph)
          + '<path d="M-7 0 Q-9 14 0 30 Q9 14 7 0Z" fill="url(#flameG)"/>'
          '<path d="M-3.4 0 Q-4 9 0 18 Q4 9 3.4 0Z" fill="#FFF1DC" opacity=".85"/></g></g>')
    A('</g></g></g>')

    # ---- pelvis, torso (breathing)
    A(f'<rect x="178" y="340" width="84" height="22" rx="9" fill="url(#armorG)" stroke="{STROKE}" stroke-width="1.8"/>')
    A('<g transform="translate(220,346)"><g>' + anim('scale', [(0, '1 1', SINE), (.5, '1.01 1.02', SINE), (1, '1 1', SINE)], 4.6)
      + '<g transform="translate(-220,-346)">')
    A(f'<path d="M148 252 Q220 238 292 252 L304 280 L270 346 L170 346 L136 280Z" fill="url(#armorG)" stroke="{STROKE}" stroke-width="2" stroke-linejoin="round"/>')
    A(f'<path d="M168 262 Q220 252 272 262 L264 308 Q220 318 176 308Z" fill="url(#armorHi)" stroke="{STROKE}" stroke-width="1.5" stroke-linejoin="round"/>')
    A('<path d="M150 254 Q220 241 290 254" fill="none" stroke="url(#rimWarm)" stroke-width="1.6"/>')
    # chest light-bar: 7 segments act like a level meter
    for i in range(7):
        x = 188 + i * 7.6
        dur = round(1.9 + (i * 0.37) % 1.1, 2)
        A(f'<rect x="{x:.1f}" y="278" width="5" height="16" rx="2.2" fill="url(#trimG)" opacity=".95">'
          + anim('height', [(0, 16, SINE), (.5, 7 + (i * 5) % 9, SINE), (1, 16, SINE)], dur, round(i * .21, 2))
          + anim('y', [(0, 278, SINE), (.5, 285 + ((i * 5) % 9) * .5, SINE), (1, 278, SINE)], dur, round(i * .21, 2)) + '</rect>')
    A('<rect x="183" y="299" width="74" height="1.6" rx=".8" fill="#FFB340" opacity=".45"/>')
    # abdomen plates + belt
    A('<path d="M184 318 H256 M188 326 H252 M193 334 H247" stroke="#000" stroke-opacity=".4" stroke-width="1.6" stroke-linecap="round"/>')
    A(f'<rect x="196" y="338" width="48" height="9" rx="4" fill="url(#armorHi)" stroke="{STROKE}" stroke-width="1.2"/>'
      '<path d="M220 339.5 l4 3 -4 3 -4 -3Z" fill="#FF9F0A">' + breathe(1, .45, 3.4, 'opacity') + '</path>')
    A('</g></g></g>')

    # ---- neck
    A(f'<rect x="207" y="226" width="26" height="26" rx="5" fill="url(#armorG)" stroke="{STROKE}" stroke-width="1.3"/>'
      '<path d="M208 234 H232 M208 240 H232 M208 246 H232" stroke="#000" stroke-opacity=".4" stroke-width="1.5"/>')

    # ---- head (lags breath; scans)
    A('<g>' + breathe('0 0', '0 -1.8', 4.6, 'translate', .3))
    A('<g transform="translate(220,232)"><g>')
    A(anim('rotate', [(0, 0, EASE), (.15, 0, EASE), (.27, -3.8, EASE), (.42, -3.8, EASE), (.54, .7, EASE), (.60, 0, EASE),
                      (.72, 0, EASE), (.84, 3.2, EASE), (.94, 3.2, EASE), (1, 0, EASE)], 14))
    A('<g transform="translate(-220,-232)">')
    # whip antenna with spring follow-through
    A('<g transform="translate(252,142)"><g>' + anim('rotate', [(0, 0, SINE), (.15, 0, SINE), (.30, 5, SINE), (.40, -2.4, SINE), (.48, 1.1, SINE),
                                                            (.58, 0, SINE), (.72, 0, SINE), (.88, -5, SINE), (.98, 2, SINE), (1, 0, SINE)], 14)
      + '<line x1="0" y1="2" x2="6" y2="-30" stroke="#3a2f26" stroke-width="2.4" stroke-linecap="round"/>'
        '<circle cx="6.4" cy="-32" r="3" fill="#FFB340"/><circle cx="6.4" cy="-32" r="3" fill="#FFB340" filter="url(#robotGlow)">'
      + breathe(1, .4, 3.2, 'opacity') + '</circle></g></g>')
    # helmet shell
    A(f'<path d="M188 130 L252 130 Q266 130 268 144 L272 192 Q272 208 260 216 L244 230 L196 230 L180 216 Q168 208 168 192 L172 144 Q174 130 188 130Z" '
      f'fill="url(#armorG)" stroke="{STROKE}" stroke-width="2.2" stroke-linejoin="round"/>')
    A(f'<path d="M200 130 Q220 112 240 130 L236 142 Q220 134 204 142Z" fill="url(#armorHi)" stroke="{STROKE}" stroke-width="1.6" stroke-linejoin="round"/>')
    A('<path d="M214 119 Q220 116 226 119" fill="none" stroke="url(#trimG)" stroke-width="1.6" stroke-linecap="round"/>')
    A('<path d="M175 150 Q220 138 265 150" fill="none" stroke="url(#rimWarm)" stroke-width="1.6"/>')
    # ear modules + cheek vents
    for x in (168, 272):
        A(f'<rect x="{x-5}" y="168" width="10" height="28" rx="5" fill="url(#armorHi)" stroke="{STROKE}" stroke-width="1.4"/>'
          f'<rect x="{x-1.5}" y="176" width="3" height="12" rx="1.5" fill="#FF9F0A">' + breathe(.9, .3, 5.1, 'opacity', 0 if x < 200 else .8) + '</rect>')
    A('<path d="M184 212 H196 M184 217 H192 M256 212 H244 M256 217 H248" stroke="#000" stroke-opacity=".4" stroke-width="1.6" stroke-linecap="round"/>')
    # lens eye: housing -> ring -> iris (looks around, refocuses) -> specular
    A(f'<circle cx="220" cy="176" r="24" fill="#0A0705" stroke="{STROKE}" stroke-width="2"/>')
    A('<circle cx="220" cy="176" r="21" fill="none" stroke="url(#trimG)" stroke-width="2"/>')
    A('<circle cx="220" cy="176" r="17" fill="none" stroke="#FFB340" stroke-width=".8" stroke-opacity=".4" stroke-dasharray="2.5 4">'
      '<animateTransform attributeName="transform" type="rotate" from="0 220 176" to="-360 220 176" dur="30s" repeatCount="indefinite"/></circle>')
    glance = [(0, '0 0', EASE), (.12, '0 0', EASE), (.22, '-4 .6', EASE), (.43, '-4 .6', EASE), (.50, '0 0', EASE),
              (.69, '0 0', EASE), (.80, '4 -.4', EASE), (.95, '4 -.4', EASE), (1, '0 0', EASE)]

    def focus(o, c):  # aperture closes quickly twice (refocus), opens slowly
        return [(0, o, EASE), (.58, o, EASE), (.615, c, EASE), (.67, o, EASE), (.72, o, EASE), (.74, c, EASE), (.79, o, EASE), (1, o, EASE)]
    A('<g>' + anim('translate', glance, 14))
    A('<circle cx="220" cy="176" r="15" fill="url(#eyeGlow)"/>')
    A('<ellipse cx="220" cy="176" rx="10.5" ry="10.5" fill="url(#irisG)">' + anim('ry', focus(10.5, 3.2), 6.4) + '</ellipse>')
    A('<ellipse cx="220" cy="176" rx="3.6" ry="3.6" fill="#1a0e06">' + anim('ry', focus(3.6, 1.2), 6.4) + '</ellipse>')
    A('<circle cx="216.2" cy="172.2" r="2" fill="#FFF1DC" opacity=".85">' + anim('r', focus(2, .1), 6.4) + '</circle>')
    A('</g>')
    A('<path d="M200 160 Q214 154 234 158 L226 166 Q212 164 202 172Z" fill="url(#glassG)"/>')
    A('</g></g></g></g>')  # head

    # ---- arms (+ pauldrons on top)
    A('<g>' + breathe('0 0', '0 -1', 4.6, 'translate'))
    up, el, fo = arm_parts()
    # viewer-left: relaxed sway
    A('<g transform="translate(142,272)"><g>' + breathe(4, 7, 4.6, 'rotate', .5) + '<g>' + up
      + '<g transform="translate(0,40)"><g>' + breathe(3, 6, 4.6, 'rotate', .7) + fo + '</g></g>' + el + '</g></g></g>')
    # viewer-right: greeting wave
    T = 16
    upf = [(0, -5, EASE), (.30, -5, OUT), (.37, -96, EASE), (.62, -96, EASE), (.71, -4, OUT), (.745, -6.5, EASE), (.78, -5, EASE), (1, -5, EASE)]
    fof = [(0, -3, EASE), (.30, -3, OUT), (.38, -80, SINE)]
    t = .38
    for k in range(10):
        t = round(t + .025, 4)
        fof.append((t, -80 + (-22 if k % 2 == 0 else 20), SINE))
    fof += [(.64, -80, EASE), (.71, -3, OUT), (.745, -5, EASE), (.78, -3, EASE), (1, -3, EASE)]
    fof = sorted({f[0]: f for f in fof}.values(), key=lambda f: f[0])
    A('<g transform="translate(298,272)"><g>' + anim('rotate', upf, T) + '<g>' + up
      + '<g transform="translate(0,40)"><g>' + anim('rotate', fof, T) + fo + '</g></g>' + el + '</g></g></g>')
    # pauldrons: slightly lagged counter-rotation (heavy armour settles after the chest)
    for sx, sign in ((142, -1), (298, 1)):
        A(f'<g transform="translate({sx},262)"><g>' + breathe(0, -1.4 * sign, 4.6, 'rotate', .45) + pauldron(sign) + '</g></g>')
    A('</g>')
    A('</g>')            # float
    A('</g></g>')        # scale + entrance
    return '\n'.join(o)


s = open(PATH, encoding='utf-8').read()
if 'armorG' not in s:
    s = s.replace('</defs>', EXTRA_DEFS + '\n  </defs>', 1)
body = START + build() + END
if START in s:
    s = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda m: body, s, flags=re.S)
else:
    raise SystemExit('markers not found - run gen_robot.py first')
open(PATH, 'w', encoding='utf-8').write(s)
print('armour robot built; scale', S, 'translate', round(TX, 1), round(TY, 1))
