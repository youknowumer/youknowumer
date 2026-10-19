#!/usr/bin/env python3
"""Generates timeline.svg in the shared 'Ember & Lagoon' token system. Usage: gen_timeline.py OUT.svg"""
import sys

W, H = 1280, 1070
CARDS = [
    dict(accent='--a1', title='Management Trainee Officer — ERP', org='Maryum N Maria', current=True,
         meta='ERP operations · SAP functional processes · Odoo implementation',
         bullets=['SAP functional processes are a core responsibility, supporting business workflows and issue follow-up.',
                  'Contribute to Odoo implementation, configuration/customization, workflow validation and operational reporting.',
                  'Investigate errors and bugs, coordinate fixes, test changes, and support deployment and go-live activities.'],
         tags=['SAP ERP', 'Odoo ERP', 'Reporting', 'Troubleshooting', 'Testing', 'Go-live support']),
    dict(accent='--a2', title='Data Annotation Specialist', org='Nex Pred Solutions', date='FEB 2026 – MAR 2026',
         meta='Remote · Lahore',
         bullets=['Prepared video datasets for computer-vision training through frame extraction, filtering and labeling workflows.',
                  'Converted annotations between YOLO and COCO formats; managed annotation tasks in CVAT.'],
         tags=['CVAT', 'YOLO', 'COCO', 'Dataset QA']),
    dict(accent='--a3', title='Human Resources Intern', org='MGA Industries Pvt. Ltd.', date='AUG 2025 – SEP 2025',
         meta='Manga Mandi, Lahore',
         bullets=['Supported recruitment, interview coordination, onboarding, employee records and payroll inputs.',
                  'Used Oracle HR records and supported workforce documentation and compliance tracking.'],
         tags=['Oracle HR', 'Recruitment', 'Onboarding', 'Payroll inputs']),
    dict(accent='--a5', title='Front-End Development Intern', org='Tara Technologies Pvt. Ltd.', date='JUL 2023 – SEP 2023',
         meta='Lahore',
         bullets=['Translated Figma and creative-tool designs into responsive HTML/CSS interfaces for live client projects.',
                  'Collaborated through Git/GitHub and iterated on UI feedback and cross-browser consistency.'],
         tags=['Figma', 'HTML / CSS', 'Git / GitHub']),
]

X0, CW = 84, 1156          # card x, width
SPINE_X = 44
EXPO = "0.16 1 0.3 1"; SOFT = "0.22 0.61 0.36 1"; IO = "0.45 0 0.55 1"


def chip(x, y, label, accent):
    w = 22 + 6.7 * len(label)
    return (f'<g><rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="24" rx="12" fill="var(--chip)" stroke="var({accent})" stroke-opacity=".45"/>'
            f'<circle cx="{x+11:.1f}" cy="{y+12}" r="2.4" fill="var({accent})"/>'
            f'<text x="{x+19:.1f}" y="{y+16}" class="m chipt">{label}</text></g>'), w + 8


out = []
out.append(f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Professional experience timeline: Maryum N Maria, Nex Pred Solutions, MGA Industries, Tara Technologies">
  <style>
    :root {{
      --bg: #080C12; --bg2: #111A22; --card: rgba(255,255,255,0.04); --cardHi: rgba(255,255,255,0.085);
      --border: rgba(255,255,255,0.10); --text: #F8FAFC; --text2: #DCE6EE; --muted: #AAB8C4; --muted2: #8093A3;
      --a1: #F5B544; --a2: #2DD4BF; --a3: #5B9BFF; --a4: #FFD88C; --a5: #38BDF8; --ok: #5EE08A;
      --chip: rgba(255,255,255,0.05); --track: rgba(255,255,255,0.075); --grid: rgba(255,255,255,0.05);
    }}
    @media (prefers-color-scheme: light) {{
      :root {{
        --bg: #FFFFFF; --bg2: #F8F5EE; --card: rgba(15,23,42,0.025); --cardHi: rgba(15,23,42,0.06);
        --border: rgba(15,23,42,0.12); --text: #111A30; --text2: #344563; --muted: #475569; --muted2: #7A8794;
        --a1: #B45309; --a2: #0F766E; --a3: #1D4ED8; --a4: #B45309; --a5: #0369A1; --ok: #15803D;
        --chip: rgba(15,23,42,0.04); --track: rgba(15,23,42,0.09); --grid: rgba(15,23,42,0.06);
      }}
    }}
    text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, ui-sans-serif, Helvetica, Arial, sans-serif; }}
    .m {{ font-family: "SFMono-Regular", "JetBrains Mono", Consolas, Menlo, monospace; }}
    .h {{ font-size: 21px; font-weight: 800; fill: var(--text); letter-spacing: -.2px; }}
    .org {{ font-size: 15px; font-weight: 700; }}
    .meta {{ font-size: 12.5px; fill: var(--muted2); }}
    .body {{ font-size: 14px; fill: var(--text2); }}
    .chipt {{ font-size: 11px; fill: var(--text2); }}
    .date {{ font-size: 10.5px; font-weight: 700; letter-spacing: 1.4px; fill: var(--muted); }}
    .eyebrow {{ font-size: 11px; font-weight: 700; letter-spacing: 3px; fill: var(--muted); }}
    .title {{ font-size: 27px; font-weight: 800; fill: var(--text); letter-spacing: -.4px; }}
  </style>
  <defs>
    <linearGradient id="acc" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="var(--a1)"/><stop offset="55%" stop-color="var(--a2)"/><stop offset="100%" stop-color="var(--a5)"/></linearGradient>
    <linearGradient id="bgG" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="var(--bg)"/><stop offset="100%" stop-color="var(--bg2)"/></linearGradient>
    <linearGradient id="cardG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--cardHi)"/><stop offset="100%" stop-color="var(--card)"/></linearGradient>
    <linearGradient id="spine" gradientUnits="userSpaceOnUse" x1="0" y1="140" x2="0" y2="1000"><stop offset="0%" stop-color="var(--a1)"/><stop offset="50%" stop-color="var(--a3)"/><stop offset="100%" stop-color="var(--a5)" stop-opacity=".25"/></linearGradient>
    <linearGradient id="pxGloss" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#fff" stop-opacity="0"/><stop offset="22%" stop-color="var(--a4)" stop-opacity=".55"/><stop offset="62%" stop-color="var(--a2)" stop-opacity=".35"/><stop offset="100%" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" r="1" fill="var(--grid)"/></pattern>
    <filter id="soft" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="42"/></filter>
    <clipPath id="frame"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="24"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bgG)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <g filter="url(#soft)" opacity=".26" class="aur">
    <circle cx="150" cy="140" r="90" fill="var(--a1)"><animate attributeName="cx" values="150;260;150" dur="22s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines="{IO};{IO}"/></circle>
    <circle cx="1120" cy="420" r="110" fill="var(--a5)"><animate attributeName="cy" values="420;520;420" dur="26s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines="{IO};{IO}"/></circle>
    <circle cx="640" cy="860" r="100" fill="var(--a2)"><animate attributeName="cx" values="640;520;640" dur="30s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines="{IO};{IO}"/></circle>
  </g>
  <style>.aur{{opacity:.26}} @media (prefers-color-scheme: light){{.aur{{opacity:.10}}}}</style>
  <rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="24" fill="none" stroke="url(#acc)" stroke-opacity=".55" stroke-width="1.5"/>
  <rect x="40" y="39" width="8" height="8" rx="2" fill="url(#acc)"/>
  <circle cx="44" cy="43" r="5" fill="none" stroke="var(--a2)" stroke-width="1.2" opacity="0"><animate attributeName="r" values="5;14" dur="2.8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.6 0.3 1"/><animate attributeName="opacity" values="0.7;0" dur="2.8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.6 0.3 1"/></circle>
  <text x="62" y="48" class="m eyebrow">CAREER TIMELINE</text>
  <text x="{W-40}" y="48" text-anchor="end" class="m eyebrow">ERP · DATA · DIGITAL DELIVERY</text>
  <text x="40" y="92" class="title">Professional Experience</text>
  <line x1="40" y1="108" x2="{W-40}" y2="108" stroke="var(--border)"/>
  <rect x="40" y="107" width="72" height="2" rx="1" fill="url(#acc)"/>
''')

y = 128
GAP = 18
spine_top = y + 30
last_node = None
for i, c in enumerate(CARDS):
    rows = len(c['bullets'])
    h = 112 + rows * 26 + 44      # header 112, bullets, chip row
    a = c['accent']
    d = 0.15 + i * 0.18
    node_y = y + 34
    last_node = node_y
    g = [f'<g opacity="0"><animate attributeName="opacity" values="0;1" keyTimes="0;1" calcMode="spline" keySplines="{SOFT}" begin="{d:.2f}s" dur="0.9s" fill="freeze"/>'
         f'<animateTransform attributeName="transform" type="translate" values="0 18;0 0" keyTimes="0;1" calcMode="spline" keySplines="{EXPO}" begin="{d:.2f}s" dur="1.1s" fill="freeze"/>']
    # connector from spine to card
    g.append(f'<path d="M{SPINE_X+9} {node_y}H{X0}" stroke="var({a})" stroke-opacity=".45" stroke-width="1.2" stroke-dasharray="2 4" stroke-linecap="round"/>')
    # node
    g.append(f'<circle cx="{SPINE_X}" cy="{node_y}" r="9" fill="var(--bg)" stroke="var({a})" stroke-width="2"/><circle cx="{SPINE_X}" cy="{node_y}" r="3.6" fill="var({a})"/>')
    if c.get('current'):
        g.append(f'<circle cx="{SPINE_X}" cy="{node_y}" r="9" fill="none" stroke="var({a})" stroke-width="1.4" opacity="0">'
                 f'<animate attributeName="r" values="9;22" dur="2.8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.6 0.3 1"/>'
                 f'<animate attributeName="opacity" values="0.8;0" dur="2.8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.6 0.3 1"/></circle>')
    # card body
    g.append(f'<rect x="{X0}" y="{y}" width="{CW}" height="{h}" rx="18" fill="url(#cardG)" stroke="var(--border)"/>')
    g.append(f'<path d="M{X0+22} {y+.6}H{X0+CW-22}" stroke="url(#pxGloss)" stroke-width="1.2" stroke-linecap="round"/>')
    g.append(f'<rect x="{X0}" y="{y+18}" width="4" height="{h-36}" rx="2" fill="var({a})"/>')
    # header
    g.append(f'<text x="{X0+30}" y="{y+40}" class="h">{c["title"]}</text>')
    g.append(f'<text x="{X0+30}" y="{y+64}"><tspan class="org" fill="var({a})">{c["org"]}</tspan><tspan class="meta" dx="9">·  {c["meta"]}</tspan></text>')
    # right badge
    if c.get('current'):
        bx = X0 + CW - 24 - 150
        g.append(f'<rect x="{bx}" y="{y+22}" width="150" height="28" rx="14" fill="var(--chip)" stroke="var(--ok)" stroke-opacity=".6"/>'
                 f'<circle cx="{bx+18}" cy="{y+36}" r="3.4" fill="var(--ok)"><animate attributeName="opacity" values="1;.35;1" dur="2.4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines="{IO};{IO}"/></circle>'
                 f'<text x="{bx+32}" y="{y+40}" class="m date" fill="var(--ok)" style="fill:var(--ok)">CURRENT ROLE</text>')
    else:
        dw = 26 + 7.4 * len(c['date'])
        bx = X0 + CW - 24 - dw
        g.append(f'<rect x="{bx:.1f}" y="{y+22}" width="{dw:.1f}" height="28" rx="14" fill="var(--chip)" stroke="var(--border)"/>'
                 f'<text x="{bx+dw/2:.1f}" y="{y+40}" text-anchor="middle" class="m date">{c["date"]}</text>')
    # divider
    g.append(f'<line x1="{X0+30}" y1="{y+80}" x2="{X0+CW-24}" y2="{y+80}" stroke="var(--border)"/>')
    # bullets
    by = y + 108
    for b in c['bullets']:
        g.append(f'<path d="M{X0+33} {by-4}l3 3 5-6" fill="none" stroke="var({a})" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<text x="{X0+52}" y="{by}" class="body">{b}</text>')
        by += 26
    # chips
    cx = X0 + 30
    cy = y + h - 38
    for t in c['tags']:
        s, adv = chip(cx, cy, t, a)
        g.append(s); cx += adv
    g.append('</g>')
    out.append('\n'.join(g))
    y += h + GAP

# spine behind everything (drawn last into list but inserted early via order trick)
spine = (f'<line x1="{SPINE_X}" y1="{spine_top-20}" x2="{SPINE_X}" y2="{last_node}" stroke="url(#spine)" stroke-width="2" stroke-linecap="round" stroke-dasharray="{last_node-spine_top+20}" stroke-dashoffset="{last_node-spine_top+20}">'
         f'<animate attributeName="stroke-dashoffset" values="{last_node-spine_top+20};0" dur="1.6s" begin="0.1s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="{EXPO}"/></line>')
out.insert(1, spine)
out.append('</g></svg>')
total = y
print('content bottom', total - GAP)
open(sys.argv[1], 'w', encoding='utf-8').write('\n'.join(out))
