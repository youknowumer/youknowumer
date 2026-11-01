#!/usr/bin/env python3
"""Positioning + accessibility pass (idempotent).
- ERP-first copy in banner, status panel and CTA
- adds <title>/<desc> + aria-labelledby to every SVG that lacks one
Usage: python3 tools/enhance.py <repo_root>
"""
import os, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
def rw(name, pairs):
    p = os.path.join(ROOT, name); s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a in s: s = s.replace(a, b)
        elif b not in s: raise SystemExit(f"missing in {name}: {a[:50]}")
    open(p, "w", encoding="utf-8").write(s)

rw("banner.svg", [
 ("Frontend Developer<tspan", "ERP Management Trainee · SAP &amp; Odoo<tspan"),
 ("Business Intelligence &amp; Data Enthusiast<tspan", "Business Intelligence &amp; Reporting<tspan"),
 ("ERP &amp; CRM Implementation Specialist<tspan", "Frontend &amp; Creative Technology<tspan"),
])
rw("robot.svg", [
 ("Frontend interfaces, BI dashboards, and ERP systems,", "ERP workflows, BI dashboards, and frontend interfaces,"),
 (">UPTIME<", ">ROLE<"), (">99.9%<", ">ERP<"),
])
rw("footer-cta.svg", [("Open to Frontend, BI &amp; ERP Opportunities", "Open to ERP, BI &amp; Frontend Opportunities")])

DESC = {
 "banner": ("Muhammad Umer Faheem", "ERP management trainee working with SAP and Odoo, reporting and business systems, based in Lahore, Pakistan."),
 "quick-facts": ("At a glance", "Lahore Pakistan, BBIS at UMT, capstone Artisan Aura Creations, English and Urdu, open to work."),
 "robot": ("System status", "Online and ready to collaborate: ERP, business intelligence and frontend engineering."),
 "services": ("What I deliver", "Four capabilities: frontend engineering, BI and data, ERP and CRM, creative and brand."),
 "erp-lifecycle": ("ERP delivery lifecycle", "Five stages: requirements, configure, test, go-live and support."),
 "skills-overview": ("Tech stack", "Tools across web, data and BI, ERP, collaboration, design, analytics and office."),
 "skills-proficiency": ("Proficiency breakdown", "Technical, creative and soft skills with proficiency levels."),
 "timeline": ("Professional experience", "Timeline: Maryum N Maria, Nex Pred Solutions, MGA Industries, Tara Technologies."),
 "projects": ("Featured projects", "Artisan Aura Creations on Odoo ERP and the Student Registration and Library Management database in Oracle."),
 "education": ("Education and languages", "BBIS at UMT, FSc Pre-Engineering at Unique College, English and Urdu."),
 "awards": ("Awards and recognition", "Awards and recognition."),
 "certifications": ("Certifications", "Nine certifications from Google, Microsoft, IBM, SAP, Odoo, Coursera and Simplilearn."),
 "focus": ("Current focus", "Learning, building, exploring and open to."),
 "footer-cta": ("Get in touch", "Open to ERP, BI and frontend opportunities."),
 "footer-bottom": ("Footer", "Copyright 2026 Muhammad Umer Faheem, Lahore, Pakistan."),
 "footer-top": ("Footer", "Decorative footer."),
 "divider": ("", ""),
 "icon-github": ("GitHub", "GitHub profile: youknowumer"),
 "icon-linkedin": ("LinkedIn", "LinkedIn profile: in/youknowumer"),
 "icon-email": ("Email", "Send an email"),
 "icon-resume": ("Resume", "Download resume as PDF"),
}
for f in sorted(os.listdir(ROOT)):
    if not f.endswith(".svg"): continue
    k = f[:-4]; t, d = DESC.get(k, (k, ""))
    p = os.path.join(ROOT, f); s = open(p, encoding="utf-8").read()
    if "<title" in s[:1500] or not t: continue
    if 'role="img"' not in s[:600]:
        s = s.replace('xmlns="http://www.w3.org/2000/svg">', 'xmlns="http://www.w3.org/2000/svg" role="img">', 1)
    s = re.sub(r'(<svg\b[^>]*?role="img")>', lambda m: m[1] + ' aria-labelledby="t d"><title id="t">%s</title><desc id="d">%s</desc>' % (t, d), s, count=1)
    open(p, "w", encoding="utf-8").write(s)
print("enhance done")
