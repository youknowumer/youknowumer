#!/usr/bin/env python3
"""Rebuilds the robot mascot in robot.svg with physically-motivated (SMIL) motion.

Motion principles used
  - Hover + breathing run on incommensurate periods (6.2s / 4.6s) so the loop never looks mechanical
  - Secondary motion: head lags the torso, antenna overshoots after the head, eyes lead the head
  - Ground shadow + contact light stay on the floor and react to hover height (shrink / fade when higher)
  - Blink is a real eyelid close (ellipse ry), with an occasional double-blink
  - Right arm: raise -> 5 waves (forearm pivots at the elbow) -> lower, once every 16s
  - Single entrance (rise + fade); everything else is ambient and slow

Scaling: the mascot is authored at 1:1 and placed by ONE transform (S, TX, TY) so it
sits optically centred in the left column with its ground line aligned to the status card.

Usage: python3 tools/gen_robot.py robot.svg      (idempotent: re-run any time)
"""
import re, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else 'robot.svg'
S = 0.92                     # overall scale
GROUND_Y = 374               # where the floor sits in panel coordinates
CX = 240                     # centre of the left column (40..440)
TX = CX - 220 * S            # robot is authored around x=220
TY = GROUND_Y - 408 * S      # authored ground line is y=408
START, END = '<!--ROBOT-START-->', '<!--ROBOT-END-->'

EASE = '0.45 0 0.55 1'       # standard ease in/out
SINE = '0.37 0 0.63 1'       # sinusoidal
OUT = '0.22 1 0.36 1'        # decelerate
IN = '0.64 0 0.78 0'         # accelerate


def n(x):
    return f'{x:.4g}'


def anim(kind, frames, dur, begin=None, extra=''):
    """frames: [(t, value, ease_to_next)]  -> animate / animateTransform with spline timing."""
    kt = ';'.join(n(f[0]) for f in frames)
    vals = ';'.join(str(f[1]) for f in frames)
    sp = ';'.join(f[2] for f in frames[:-1])
    b = f' begin="{begin}s"' if begin is not None else ''
    if kind in ('rotate', 'translate', 'scale'):
        head = f'<animateTransform attributeName="transform" type="{kind}"'
    else:
        head = f'<animate attributeName="{kind}"'
    return (f'{head} values="{vals}" keyTimes="{kt}" calcMode="spline" keySplines="{sp}"{b} '
            f'dur="{dur}s" repeatCount="indefinite"{extra}/>')


def loop(vals, dur, kind, ease=SINE, begin=None):
    """symmetric a;b;a loop"""
    return anim(kind, [(0, vals[0], ease), (.5, vals[1], ease), (1, vals[0], ease)], dur, begin)


# ----------------------------------------------------------------------------- defs (added once)
EXTRA_DEFS = '''
<linearGradient id="rimWarm" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#FFB340" stop-opacity="0.55"/>
  <stop offset=".35" stop-color="#FFB340" stop-opacity="0.08"/>
  <stop offset="1" stop-color="#FF7A3D" stop-opacity="0.30"/>
</linearGradient>
<linearGradient id="glassG" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#FFF1DC" stop-opacity="0.16"/>
  <stop offset=".45" stop-color="#FFF1DC" stop-opacity="0.03"/>
  <stop offset="1" stop-color="#FFF1DC" stop-opacity="0"/>
</linearGradient>
<linearGradient id="scanG" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#FF9F0A" stop-opacity="0"/>
  <stop offset=".5" stop-color="#FFB340" stop-opacity="0.55"/>
  <stop offset="1" stop-color="#FF9F0A" stop-opacity="0"/>
</linearGradient>
<linearGradient id="screenG" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#1A130E"/><stop offset="1" stop-color="#0A0705"/>
</linearGradient>
<radialGradient id="coreG" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#FFE2B0"/><stop offset=".35" stop-color="#FFB340"/>
  <stop offset=".75" stop-color="#FF7A3D"/><stop offset="1" stop-color="#FF7A3D" stop-opacity="0.6"/>
</radialGradient>
<radialGradient id="auraG" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#FF9F0A" stop-opacity="0.13"/><stop offset=".55" stop-color="#FF9F0A" stop-opacity="0.045"/>
  <stop offset="1" stop-color="#FF9F0A" stop-opacity="0"/>
</radialGradient>
<radialGradient id="auraG2" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#FF7A3D" stop-opacity="0.10"/><stop offset="1" stop-color="#FF7A3D" stop-opacity="0"/>
</radialGradient>
<radialGradient id="floorGlow" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#FF9F0A" stop-opacity="0.38"/>
  <stop offset="1" stop-color="#FF9F0A" stop-opacity="0"/>
</radialGradient>
'''

STROKE = '#3a2f26'


def arm(side, px, py, rest):
    """Two-link arm. side=+1 (viewer right) / -1 (left). Pivot at shoulder (px,py)."""
    sgn = side
    # shapes are authored hanging straight down; rotation does the posing
    upper = f'<rect x="-8" y="-2" width="16" height="38" rx="8" fill="url(#limbGrad)" stroke="{STROKE}" stroke-width="1.5"/>'
    fore = (f'<rect x="-7" y="-2" width="14" height="36" rx="7" fill="url(#limbGrad)" stroke="{STROKE}" stroke-width="1.5"/>'
            f'<circle cx="0" cy="38" r="9" fill="url(#limbGrad)" stroke="{STROKE}" stroke-width="1.5"/>'
            f'<circle cx="-2.5" cy="35" r="2.6" fill="#FFF1DC" opacity="0.10"/>')
    elbow = f'<circle cx="0" cy="34" r="8" fill="url(#metalHead)" stroke="{STROKE}" stroke-width="1.5"/>'
    return upper, fore, elbow


def build():
    o = []
    A = o.append
    # --- ambient glows (accent, soft) -------------------------------------------------------
    A('<circle cx="240" cy="236" r="190" fill="url(#auraG)"/>')
    A('<circle cx="1080" cy="320" r="220" fill="url(#auraG2)"/>')
    # --- rising dust motes (slow, sparse, depth-less) ---------------------------------------
    for x, y0, y1, d, b, r in [(110, 360, 190, 13, 0, 1.6), (365, 340, 150, 16, 4, 1.4), (300, 385, 210, 11, 8, 1.2),
                               (170, 372, 130, 15, 2, 1.1), (400, 372, 230, 12, 6, 1.5)]:
        A(f'<circle cx="{x}" cy="{y0}" r="{r}" fill="#FFC987" opacity="0">'
          + anim('cy', [(0, y0, EASE), (1, y1, EASE)], d, b).replace('repeatCount="indefinite"', 'repeatCount="indefinite"')
          + anim('opacity', [(0, 0, EASE), (.2, .5, EASE), (.8, .5, EASE), (1, 0, EASE)], d, b)
          + '</circle>')

    # --- entrance wrapper -------------------------------------------------------------------
    A('<g opacity="0">'
      '<animate attributeName="opacity" values="0;1" keyTimes="0;1" calcMode="spline" keySplines="0.22 0.61 0.36 1" '
      'begin="0.1s" dur="0.9s" fill="freeze"/>'
      '<animateTransform attributeName="transform" type="translate" values="0 14;0 0" keyTimes="0;1" calcMode="spline" '
      f'keySplines="{OUT}" begin="0.1s" dur="1.1s" fill="freeze"/>')
    A(f'<g transform="translate({n(TX)},{n(TY)}) scale({S})">')

    # --- ground: contact light + shadow (stay on the floor, respond to hover height) --------
    A('<ellipse cx="220" cy="410" rx="70" ry="8" fill="url(#floorGlow)">'
      + anim('opacity', [(0, .9, SINE), (.5, .45, SINE), (1, .9, SINE)], 6.2) + '</ellipse>')
    A('<ellipse cx="220" cy="410" rx="64" ry="11" fill="url(#shadowGrad)">'
      + anim('rx', [(0, 64, SINE), (.5, 50, SINE), (1, 64, SINE)], 6.2)
      + anim('opacity', [(0, .95, SINE), (.5, .5, SINE), (1, .95, SINE)], 6.2) + '</ellipse>')

    # --- floating body ----------------------------------------------------------------------
    A('<g>' + anim('translate', [(0, '0 0', SINE), (.5, '0 -10', SINE), (1, '0 0', SINE)], 6.2))

    # legs (behind torso) – tiny counter-sway about the hip
    A('<g transform="translate(220,350)"><g>' + anim('rotate', [(0, 0, SINE), (.5, 1.2, SINE), (1, 0, SINE)], 6.2, 0.35)
      + '<g transform="translate(-220,-350)">'
      f'<rect x="186" y="350" width="20" height="34" rx="8" fill="url(#limbGrad)" stroke="{STROKE}" stroke-width="1.5"/>'
      f'<rect x="234" y="350" width="20" height="34" rx="8" fill="url(#limbGrad)" stroke="{STROKE}" stroke-width="1.5"/>'
      f'<rect x="180" y="382" width="32" height="10" rx="5" fill="url(#limbGrad)" stroke="{STROKE}" stroke-width="1.5"/>'
      f'<rect x="228" y="382" width="32" height="10" rx="5" fill="url(#limbGrad)" stroke="{STROKE}" stroke-width="1.5"/>'
      '<rect x="184" y="383.5" width="24" height="2" rx="1" fill="#FF9F0A" opacity="0.45"/>'
      '<rect x="232" y="383.5" width="24" height="2" rx="1" fill="#FF9F0A" opacity="0.45"/>'
      '</g></g></g>')

    # torso – breathing: chest expands upward from the belt line
    A('<g transform="translate(220,354)"><g>'
      + anim('scale', [(0, '1 1', SINE), (.5, '1.01 1.022', SINE), (1, '1 1', SINE)], 4.6)
      + '<g transform="translate(-220,-354)">')
    A(f'<rect x="146" y="244" width="148" height="110" rx="22" fill="url(#metalBody)" stroke="{STROKE}" stroke-width="2"/>')
    A('<clipPath id="torsoClip"><rect x="146" y="244" width="148" height="110" rx="22"/></clipPath>')
    A('<g clip-path="url(#torsoClip)">'
      '<rect x="154" y="250" width="132" height="14" rx="7" fill="#fff" opacity="0.05"/>'
      '<rect x="146" y="244" width="16" height="110" fill="#000" opacity="0.18"/>'
      '<rect x="278" y="244" width="16" height="110" fill="#000" opacity="0.18"/>'
      '<rect x="146" y="318" width="148" height="1.2" fill="#FFF1DC" opacity="0.06"/>'
      '<rect x="146" y="319.2" width="148" height="1.2" fill="#000" opacity="0.35"/></g>')
    A('<rect x="146.8" y="244.8" width="146.4" height="108.4" rx="21.4" fill="none" stroke="url(#rimWarm)" stroke-width="1.2"/>')
    # core: housing, ripple, breathing glow
    A('<circle cx="220" cy="291" r="26" fill="#0C0907" stroke="url(#visor)" stroke-width="2.5"/>')
    A('<circle cx="220" cy="291" r="27" fill="none" stroke="#FF9F0A" stroke-width="1.6" opacity="0">'
      + anim('r', [(0, 27, OUT), (1, 46, OUT)], 4.6) + anim('opacity', [(0, .55, OUT), (1, 0, OUT)], 4.6) + '</circle>')
    A('<circle cx="220" cy="291" r="19" fill="none" stroke="#FFB340" stroke-width="0.8" opacity="0.35" stroke-dasharray="3 5">'
      '<animateTransform attributeName="transform" type="rotate" from="0 220 291" to="360 220 291" dur="38s" repeatCount="indefinite"/></circle>')
    A('<circle cx="220" cy="291" r="11" fill="url(#coreG)" filter="url(#robotGlow)">'
      + anim('opacity', [(0, 1, SINE), (.5, .72, SINE), (1, 1, SINE)], 4.6) + '</circle>')
    # status LEDs – sequential "activity" rather than uniform blink
    for i, (x, c) in enumerate([(170, '#FF9F0A'), (186, '#FF7A3D'), (202, '#30D158')]):
        A(f'<circle cx="{x}" cy="338" r="3.6" fill="{c}" opacity=".35">'
          + anim('opacity', [(0, .35, EASE), (.12, 1, EASE), (.38, 1, EASE), (.5, .35, EASE), (1, .35, EASE)], 3.9, round(i * .55, 2))
          + '</circle>')
    for k in range(3):  # vents
        A(f'<rect x="236" y="{332 + k * 6}" width="40" height="2.4" rx="1.2" fill="#000" opacity=".4"/>')
    A('</g></g></g>')  # end torso/breath

    # neck
    A(f'<rect x="209" y="228" width="22" height="22" rx="4" fill="url(#limbGrad)" stroke="{STROKE}" stroke-width="1.2"/>'
      '<rect x="209" y="236" width="22" height="1.6" fill="#000" opacity=".4"/><rect x="209" y="241" width="22" height="1.6" fill="#000" opacity=".4"/>')

    # head – lags the breath, turns about the neck; contents: antenna, shell, ears, visor, eyes
    A('<g>' + anim('translate', [(0, '0 0', SINE), (.5, '0 -1.8', SINE), (1, '0 0', SINE)], 4.6, 0.3))
    A('<g transform="translate(220,236)"><g>')
    head_rot = [(0, 0, EASE), (.15, 0, EASE), (.27, -3.2, EASE), (.42, -3.2, EASE), (.54, .6, EASE), (.60, 0, EASE),
                (.72, 0, EASE), (.84, 2.6, EASE), (.94, 2.6, EASE), (1, 0, EASE)]
    A(anim('rotate', head_rot, 14))
    A('<g transform="translate(-220,-236)">')
    # antenna w/ spring follow-through (pivot = base of antenna)
    A('<g transform="translate(220,144)"><g>')
    A(anim('rotate', [(0, 0, SINE), (.15, 0, SINE), (.30, 3.2, SINE), (.40, -1.5, SINE), (.48, .7, SINE), (.58, 0, SINE),
                      (.72, 0, SINE), (.88, -3.2, SINE), (.98, 1.3, SINE), (1, 0, SINE)], 14))
    A('<g transform="translate(-220,-144)">'
      f'<line x1="220" y1="144" x2="220" y2="118" stroke="{STROKE}" stroke-width="3.6" stroke-linecap="round"/>'
      '<circle cx="220" cy="114" r="9" fill="none" stroke="#FF9F0A" stroke-width="1" opacity="0">'
      + anim('r', [(0, 5, OUT), (1, 13, OUT)], 3.2) + anim('opacity', [(0, .5, OUT), (1, 0, OUT)], 3.2) + '</circle>'
      '<circle cx="220" cy="114" r="5.5" fill="url(#coreG)" filter="url(#robotGlow)">'
      + anim('opacity', [(0, 1, SINE), (.5, .55, SINE), (1, 1, SINE)], 3.2) + '</circle>'
      '</g></g></g>')
    # shell
    A(f'<rect x="161" y="144" width="118" height="92" rx="26" fill="url(#metalHead)" stroke="{STROKE}" stroke-width="2"/>')
    A('<clipPath id="headClip"><rect x="161" y="144" width="118" height="92" rx="26"/></clipPath>')
    A('<g clip-path="url(#headClip)"><rect x="167" y="149" width="106" height="18" rx="9" fill="#fff" opacity="0.06"/></g>')
    A('<rect x="161.8" y="144.8" width="116.4" height="90.4" rx="25.2" fill="none" stroke="url(#rimWarm)" stroke-width="1.2"/>')
    # ears
    for x in (159, 281):
        A(f'<circle cx="{x}" cy="190" r="7" fill="url(#limbGrad)" stroke="{STROKE}" stroke-width="1.5"/>'
          f'<circle cx="{x}" cy="190" r="2.2" fill="#FF9F0A">' + anim('opacity', [(0, .9, SINE), (.5, .35, SINE), (1, .9, SINE)], 5.1, 0 if x < 200 else .8) + '</circle>')
    # visor
    A('<rect x="175" y="170" width="90" height="40" rx="14" fill="url(#screenG)" stroke="url(#visor)" stroke-width="2"/>')
    A('<clipPath id="visorClip"><rect x="175" y="170" width="90" height="40" rx="14"/></clipPath>')
    A('<g clip-path="url(#visorClip)">')
    A('<rect x="153" y="170" width="22" height="40" fill="url(#scanG)" opacity="0">'
      + anim('x', [(0, 153, EASE), (.55, 267, EASE), (1, 267, EASE)], 8)
      + anim('opacity', [(0, 0, EASE), (.05, 1, EASE), (.5, 1, EASE), (.55, 0, EASE), (1, 0, EASE)], 8) + '</rect>')
    # eyes (lead the head turn), blink via real ellipse ry
    glance = [(0, '0 0', EASE), (.12, '0 0', EASE), (.22, '-3.2 .4', EASE), (.43, '-3.2 .4', EASE), (.50, '0 0', EASE),
              (.69, '0 0', EASE), (.80, '3 -.3', EASE), (.95, '3 -.3', EASE), (1, '0 0', EASE)]
    def blink_f(o, c):
        return [(0, o, EASE), (.60, o, EASE), (.615, c, EASE), (.645, o, EASE), (.70, o, EASE), (.715, c, EASE),
                (.745, o, EASE), (1, o, EASE)]
    blink = blink_f(5.5, .7)
    A('<g>' + anim('translate', glance, 14))
    for x in (202, 238):
        A(f'<ellipse cx="{x}" cy="190" rx="11" ry="11" fill="url(#eyeGlow)">' + anim('ry', blink_f(11, 1.4), 6.4) + '</ellipse>')
        A(f'<ellipse cx="{x}" cy="190" rx="5.5" ry="5.5" fill="#FF7A3D">' + anim('ry', blink, 6.4) + '</ellipse>')
        A(f'<circle cx="{x - 1.8}" cy="188" r="1.5" fill="#FFF1DC" opacity=".8">' + anim('r', blink_f(1.5, .1), 6.4) + '</circle>')
    A('</g>')
    A('</g>')  # visor clip
    A('<path d="M179 176 Q 200 168 232 171 L 222 180 Q 200 177 183 186 Z" fill="url(#glassG)"/>')  # glass reflection
    A('</g></g></g></g>')  # head transforms

    # arms (shoulder rises a hair with the chest)
    A('<g>' + anim('translate', [(0, '0 0', SINE), (.5, '0 -1', SINE), (1, '0 0', SINE)], 4.6))
    # viewer-left arm: relaxed sway, delayed
    up, fo, el = arm(-1, 0, 0, 5)
    A('<g transform="translate(138,262)"><g>' + anim('rotate', [(0, 4, SINE), (.5, 7, SINE), (1, 4, SINE)], 4.6, .5) + '<g>' + up
      + f'<g transform="translate(0,34)"><g>' + anim('rotate', [(0, 3, SINE), (.5, 6, SINE), (1, 3, SINE)], 4.6, .7) + fo + '</g></g>'
      + el + '</g></g></g>')
    A('<circle cx="138" cy="262" r="10" fill="url(#metalHead)" stroke="' + STROKE + '" stroke-width="1.5"/>')
    # viewer-right arm: greeting wave every 16 s
    T = 16
    up_frames = [(0, -5, EASE), (.30, -5, OUT), (.37, -96, EASE), (.62, -96, EASE), (.71, -5, EASE), (.745, -7, EASE), (.78, -5, EASE), (1, -5, EASE)]
    # (raise: decelerate; lower: ease-in-out; settle: small overshoot)
    up_frames = [(0, -5, EASE), (.30, -5, OUT), (.37, -96, EASE), (.62, -96, EASE), (.71, -4, OUT), (.745, -6.5, EASE), (.78, -5, EASE), (1, -5, EASE)]
    fo_frames = [(0, -3, EASE), (.30, -3, OUT), (.38, -80, SINE)]
    t, sgn = .38, 1
    for k in range(10):            # 5 full waves, ~0.8 s each
        t = round(t + .025, 4)
        fo_frames.append((t, -80 + (-22 if k % 2 == 0 else 20), SINE))
    fo_frames += [(.64, -80, EASE), (.71, -3, OUT), (.745, -5, EASE), (.78, -3, EASE), (1, -3, EASE)]
    # keep strictly increasing key times
    fo_frames = sorted({f[0]: f for f in fo_frames}.values(), key=lambda f: f[0])
    up2, fo2, el2 = arm(1, 0, 0, -5)
    A('<g transform="translate(302,262)"><g>' + anim('rotate', up_frames, T)
      + '<g>' + up2 + '<g transform="translate(0,34)"><g>' + anim('rotate', fo_frames, T) + fo2 + '</g></g>' + el2 + '</g></g></g>')
    A('<circle cx="302" cy="262" r="10" fill="url(#metalHead)" stroke="' + STROKE + '" stroke-width="1.5"/>')
    A('</g>')  # arm wrapper
    A('</g>')  # float
    A('</g></g>')  # scale + entrance
    return '\n'.join(o)


s = open(PATH, encoding='utf-8').read()
if 'auraG' not in s:
    s = re.sub(r'<linearGradient id="rimWarm".*?(?=<radialGradient id="floorGlow")', '', s, flags=re.S) if 'rimWarm' in s else s
    s = re.sub(r'<radialGradient id="floorGlow".*?</radialGradient>', '', s, flags=re.S)
    s = s.replace('</defs>', EXTRA_DEFS + '\n  </defs>', 1)
body = START + build() + END
if START in s:
    s = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda m: body, s, flags=re.S)
else:
    a = s.find('<circle cx="200" cy="120" r="180"')
    b = s.find('<g opacity="0" transform="translate(0,14)">')
    assert a > 0 and b > a, 'markers not found'
    s = s[:a] + body + '\n' + s[b:]
open(PATH, 'w', encoding='utf-8').write(s)
print('robot rebuilt; scale', S, 'translate', round(TX, 1), round(TY, 1))
