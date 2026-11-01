#!/usr/bin/env python3
"""Generate erp-lifecycle.svg, reusing the shared theme/defs from services.svg.
Usage: python3 tools/gen_lifecycle.py <repo_root>
"""
import re, sys, os
from xml.sax.saxutils import escape

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
src = open(os.path.join(ROOT, "services.svg"), encoding="utf-8").read().split("\n")

W, H = 1280, 366
CARD_Y, CARD_H, CARD_W, GAP, X0 = 76, 250, 224, 20, 40
ACC = ["a1", "a2", "a3", "a4", "a5"]

STAGES = [
    ("01", "Requirements", "Understand the need first.",
     ["Map process to workflow", "Validate with end users"], "Process mapping",
     "M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2zM9 12h6M9 16h4"),
    ("02", "Configure", "Build it in Odoo / SAP.",
     ["Configure & customize", "Role-based access"], "Odoo · SAP",
     "M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"),
    ("03", "Test", "Prove it before release.",
     ["Reproduce & log bugs", "Regression checks"], "Expected vs actual",
     "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10zM9 12l2 2 4-4"),
    ("04", "Go-live", "Move into live operations.",
     ["Rollout preparation", "Hands-on user support"], "Cut-over",
     "M4.5 16.5c-1.5 1.3-2 5-2 5s3.7-.5 5-2c.7-.8.7-2.1-.1-2.9a2.2 2.2 0 0 0-2.9-.1zM12 15l-3-3a22 22 0 0 1 2-3.9A12.9 12.9 0 0 1 22 2c0 2.7-.8 7.5-6 11a22 22 0 0 1-4 2zM9 12H4s.6-3 2-4c1.6-1.1 5 0 5 0M12 15v5s3-.6 4-2c1.1-1.6 0-5 0-5"),
    ("05", "Support", "Keep operations stable.",
     ["Issue follow-up & fixes", "Operational reporting"], "Reporting",
     "M3 18v-6a9 9 0 0 1 18 0v6M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"),
]

ENTER = 'calcMode="spline" keySplines="0.22 0.61 0.36 1"'
RISE = 'calcMode="spline" keyTimes="0;0.52;0.8;1" keySplines="0.32 0.72 0 1;0.42 0 0.58 1;0.42 0 0.58 1"'

def chip_w(t): return round(len(t) * 6.6 + 24, 1)

# ---- header (lines 1..44 of services.svg) with geometry swapped ----
head = "\n".join(src[:44])
head = head.replace('width="1280" height="392" viewBox="0 0 1280 392"', f'width="{W}" height="{H}" viewBox="0 0 {W} {H}"')
head = head.replace('height="392"', f'height="{H}"').replace('height="390.5"', f'height="{H-1.5}"')
head = head.replace("M20 360 V372 H32 M1248 372 H1260 V360", f"M20 {H-32} V{H-20} H32 M1248 {H-20} H1260 V{H-32}")
head = head.replace("WHAT I DELIVER", "ERP DELIVERY LIFECYCLE").replace("FOUR CORE CAPABILITIES", "REQUIREMENT → SUPPORT")
# per-card clip paths for the shine sweep
clips = "".join(f'<clipPath id="lc{i}"><rect x="{X0+i*(CARD_W+GAP)}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="16"/></clipPath>' for i in range(5))
head = head.replace("</defs>", clips + "</defs>", 1) if "</defs>" in head else head
# replace aria: add accessible name
head = head.replace('role="img">', 'role="img" aria-labelledby="t d"><title id="t">ERP delivery lifecycle</title><desc id="d">Five stages: requirements, configure, test, go-live and support.</desc>', 1)

cards = []
for i, (num, title, sub, bullets, chip, icon) in enumerate(STAGES):
    x = X0 + i * (CARD_W + GAP); a = f"var(--{ACC[i]})"; d = 0.10 + i * 0.12
    g = [f'<g opacity="0"><animate attributeName="opacity" values="0;1" keyTimes="0;1" {ENTER} begin="{d:.2f}s" dur="0.9s" fill="freeze"/>'
         f'<animateTransform attributeName="transform" type="translate" values="0 22;0 -3.2;0 1.1;0 0" {RISE} begin="{d:.2f}s" dur="1.35s" fill="freeze"/>']
    g.append(f'<rect x="{x}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="16" fill="url(#cardG)" stroke="var(--border)"/>')
    g.append(f'<rect x="{x+1}" y="{CARD_Y+1}" width="{CARD_W-2}" height="{CARD_H-2}" rx="15" fill="url(#pxSheen)" pointer-events="none"/>')
    g.append(f'<path d="M{x+20} {CARD_Y+.6}H{x+CARD_W-20}" stroke="url(#pxGloss)" stroke-width="1.2" stroke-linecap="round" pointer-events="none"/>')
    g.append(f'<g clip-path="url(#lc{i})" pointer-events="none"><rect x="{x-150}" y="{CARD_Y-8}" width="110" height="{CARD_H+16}" fill="url(#pxShine)" transform="skewX(-18)">'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;{CARD_W+330} 0;{CARD_W+330} 0" keyTimes="0;0.1364;1" calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1" dur="11.0s" begin="{2.4+i*0.45:.2f}s" repeatCount="indefinite" additive="sum"/></rect></g>')
    g.append(f'<rect x="{x+20}" y="{CARD_Y-0.5}" width="46" height="3" rx="1.5" fill="{a}"/>')
    g.append(f'<path d="M{x+CARD_W-21} {CARD_Y+CARD_H-8} H{x+CARD_W-8} V{CARD_Y+CARD_H-21}" fill="none" stroke="{a}" stroke-opacity="0.55" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')
    cx, cy = x + 41, 119
    g.append(f'<circle cx="{cx}" cy="{cy}" r="25" fill="none" stroke="{a}" stroke-opacity="0.18" stroke-dasharray="2 3"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="21" fill="{a}" fill-opacity="0.12" stroke="{a}" stroke-opacity="0.45"/>')
    g.append(f'<g transform="translate({cx-9.7:.1f},{cy-9.7:.1f}) scale(0.805)" fill="none" stroke="{a}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{icon}"/></g>')
    g.append(f'<text class="m" x="{x+CARD_W-20}" y="116" font-size="12" text-anchor="end" fill="{a}">{num}</text>')
    g.append(f'<text x="{x+20}" y="176" font-size="19" font-weight="700" fill="var(--text)">{escape(title)}</text>')
    g.append(f'<text x="{x+20}" y="197" font-size="12.5" fill="var(--muted)">{escape(sub)}</text>')
    g.append(f'<line x1="{x+20}" y1="212" x2="{x+CARD_W-20}" y2="212" stroke="var(--border)"/>')
    for j, b in enumerate(bullets):
        y = 227 + j * 28
        g.append(f'<g transform="translate({x+20},{y}) scale(0.5833)" fill="none" stroke="{a}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></g>')
        g.append(f'<text x="{x+42}" y="{y+11}" font-size="13" fill="var(--text2)">{escape(b)}</text>')
    cw = chip_w(chip)
    g.append(f'<g transform="translate({x+20},{CARD_Y+CARD_H-42})"><rect width="{cw}" height="22" rx="11" fill="{a}" fill-opacity="0.09" stroke="{a}" stroke-opacity="0.42"/><text class="m" x="12" y="15" font-size="11" fill="var(--text)">{escape(chip)}</text></g>')
    g.append("</g>")
    cards.append("".join(g))
    # connector chevron + travelling pulse in the gap
    if i < 4:
        gx = x + CARD_W + GAP / 2
        cards.append(f'<g><path d="M{gx-3} {cy-5}l5 5-5 5" fill="none" stroke="var(--muted2)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
                     f'<circle cx="{gx}" cy="{cy}" r="7" fill="none" stroke="var(--a2)" stroke-opacity="0.0"><animate attributeName="r" values="4;11" dur="3.2s" begin="{1.6+i*0.8:.1f}s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values="0.6;0" dur="3.2s" begin="{1.6+i*0.8:.1f}s" repeatCount="indefinite"/></circle></g>')

out = head + "\n" + "\n".join(cards) + "\n</g>\n</svg>\n"
open(os.path.join(ROOT, "erp-lifecycle.svg"), "w", encoding="utf-8").write(out)
print("wrote erp-lifecycle.svg", len(out), "bytes")
