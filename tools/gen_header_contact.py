#!/usr/bin/env python3
"""Builds the profile header + "Get in Touch" assets (static, no glow, text drawn as outlines).

Outputs (run from repo root: python3 tools/gen_header_contact.py .):
  header-identity.svg        role / focus / location / availability strip under the banner
  cta/*.svg                  4 action buttons (Download CV, Projects, LinkedIn, Email)
  nav/*.svg                  13 section pills (each wrapped in an <a href="#..."> in the README)
  contact-hero.svg           headline + "how I can help" panel
  contact/*.svg              4 channel cards (Email, LinkedIn, Resume, GitHub)
  footer-bottom.svg          copyright strip

Theme: same warm iOS palette + light/dark switch as the other panels.
Requires: pip install fonttools brotli uharfbuzz
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgtext as T

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'

STYLE = """:root{--bg:#0C0907;--bg2:#16110D;--card:rgba(255,236,214,0.035);--cardHi:rgba(255,236,214,0.08);--border:rgba(255,226,190,0.12);--text:#FFF8F0;--text2:#EADFD2;--muted:#B8A999;--muted2:#8F8174;--a1:#FF9F0A;--a2:#FF7A3D;--a3:#F2C14E;--a4:#FFC987;--a5:#FFB340;--ok:#30D158;--chip:rgba(255,236,214,0.06);--chipB:rgba(255,226,190,0.17);--spec:#FFF1DC;--onacc:#1A1008}
@media (prefers-color-scheme: light){:root{--bg:#FFFCF7;--bg2:#F8F1E7;--card:rgba(120,84,40,0.035);--cardHi:rgba(120,84,40,0.075);--border:rgba(120,84,40,0.17);--text:#2A2018;--text2:#4A3B2E;--muted:#65533F;--muted2:#7D6A56;--a1:#D96A00;--a2:#C2501A;--a3:#B07A00;--a4:#B86A1F;--a5:#E08A00;--ok:#248A3D;--chip:rgba(120,84,40,0.055);--chipB:rgba(120,84,40,0.22);--spec:#D96A00}}"""

DEFS = """<linearGradient id="accH" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="var(--a1)"/><stop offset="55%" stop-color="var(--a2)"/><stop offset="100%" stop-color="var(--a5)"/></linearGradient>
<linearGradient id="cardG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--cardHi)"/><stop offset="100%" stop-color="var(--card)"/></linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--spec)" stop-opacity="0.075"/><stop offset="38%" stop-color="var(--a1)" stop-opacity="0"/></linearGradient>
<linearGradient id="gloss" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#fff" stop-opacity="0"/><stop offset="22%" stop-color="var(--a4)" stop-opacity="0.55"/><stop offset="62%" stop-color="var(--a2)" stop-opacity="0.35"/><stop offset="100%" stop-color="#fff" stop-opacity="0"/></linearGradient>"""

ICONS = {  # 24x24 stroke icons
    'briefcase': 'M3 8h18v12H3zM9 8V5h6v3M3 13h18',
    'layers': 'M12 3 3 8l9 5 9-5-9-5zM3 13l9 5 9-5M3 17.5 12 22l9-4.5',
    'pin': 'M12 21s-7-6.2-7-11a7 7 0 1 1 14 0c0 4.8-7 11-7 11zM12 7.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z',
    'mail': 'M3 5h18v14H3zM3 7l9 6 9-6',
    'download': 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3',
    'grid': 'M3 3h8v8H3zM13 3h8v8h-8zM3 13h8v8H3zM13 13h8v8h-8z',
    'check': 'M5 12.5l4.5 4.5L19 7.5',
    'out': 'M7 17 17 7M8 7h9v9',
    'file': 'M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8zM14 3v5h5M9 13h6M9 17h6',
}
GH = ('M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56v-2c-3.2.7-3.87-1.37-3.87-1.37-.52-1.33-1.28-1.69-1.28-1.69-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.78 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.69 5.39-5.25 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z')


def f(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return s


def svg(w, h, title, desc, body, vb=None):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(w)}" height="{f(h)}" viewBox="{vb or f"0 0 {f(w)} {f(h)}"}" '
            f'role="img" aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc>'
            f'<style>{STYLE}</style><defs>{DEFS}</defs>{body}</svg>\n')


def icon(name, cx, cy, size, stroke, sw=1.8):
    s = size / 24
    return (f'<g transform="translate({f(cx - size / 2)},{f(cy - size / 2)}) scale({f(s)})" fill="none" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"><path d="{ICONS[name]}"/></g>')


def card(x, y, w, h, rx):
    """Static glass card: base, tint, hairline border, top sheen + gloss line. No glow, no motion."""
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="var(--bg)"/>'
            f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="url(#cardG)" stroke="var(--border)"/>'
            f'<rect x="{f(x + 1)}" y="{f(y + 1)}" width="{f(w - 2)}" height="{f(h - 2)}" rx="{rx - 1}" fill="url(#sheen)"/>'
            f'<path d="M{f(x + rx + 6)} {f(y + .6)}H{f(x + w - rx - 6)}" stroke="url(#gloss)" stroke-width="1.2" stroke-linecap="round"/>')


def ring(cx, cy, r, color):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{r}" fill="{color}" fill-opacity="0.13" stroke="{color}" stroke-opacity="0.5"/>'


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)
    print(f'{path:34s} {len(content) / 1024:6.1f} KB')


# ------------------------------------------------------------------ header identity strip
def header_identity():
    W, H = 1280, 112
    cells = [
        ('CURRENT ROLE', 'ERP Management Trainee', 'Maryum N Maria', 'briefcase', 'var(--a1)'),
        ('CORE FOCUS', 'SAP · Odoo · Reporting', 'ERP implementation & support', 'layers', 'var(--a2)'),
        ('BASED IN', 'Lahore, Pakistan', 'PKT · UTC+5 · English & Urdu', 'pin', 'var(--a5)'),
        ('AVAILABILITY', 'Open to work', 'Roles & freelance · 24h reply', None, 'var(--ok)'),
    ]
    b = [card(1, 1, W - 2, H - 2, 24)]
    cw = W / 4
    for i, (lab, val, sub, ic, col) in enumerate(cells):
        x0 = cw * i
        cx, cy = x0 + 52, H / 2
        if i:
            b.append(f'<path d="M{f(x0)} 28V{H - 28}" stroke="var(--border)" stroke-width="1"/>')
        b.append(ring(cx, cy, 20, col))
        if ic:
            b.append(icon(ic, cx, cy, 20, 'var(--text)'))
        else:
            b.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5.5" fill="{col}"><animate attributeName="opacity" values="1;0.35;1" dur="3.2s" repeatCount="indefinite"/></circle>')
        tx = x0 + 86
        b.append(T.text(lab, tx, cy - 17, 600, 10.5, 'var(--muted2)', tracking=1.6))
        v = T.measure(val, 700, 17)
        assert tx + v < x0 + cw - 12, (val, v)
        b.append(T.text(val, tx, cy + 5, 700, 17, 'var(--text)', tracking=-0.15))
        b.append(T.text(sub, tx, cy + 26, 400, 12, 'var(--muted)'))
    write('header-identity.svg', svg(W, H, 'Profile summary',
          'ERP Management Trainee at Maryum N Maria. Focus on SAP, Odoo and reporting. Based in Lahore, Pakistan (PKT, UTC+5). Open to roles and freelance, typically replies within 24 hours.',
          ''.join(b)))


# ------------------------------------------------------------------ CTA buttons
M = 3  # transparent margin so inline images get breathing room on GitHub


def button(fname, label, ic, primary, glyph=None):
    H, pad, gap, isz = 44, 20, 10, 18
    lw = T.measure(label, 700 if primary else 600, 14.5, 0.1)
    W = pad + isz + gap + lw + pad + 2
    col_t = 'var(--onacc)' if primary else 'var(--text)'
    col_i = 'var(--onacc)' if primary else 'var(--a1)'
    fill = 'url(#accH)' if primary else 'var(--chip)'
    stroke = 'none' if primary else 'var(--chipB)'
    b = [f'<rect x="{M + .5}" y="{M + .5}" width="{f(W - 1)}" height="{H - 1}" rx="{H / 2 - .5}" fill="{fill}" stroke="{stroke}"/>']
    ix = M + pad + isz / 2
    if glyph:
        b.append(glyph(ix, M + H / 2, col_i))
    else:
        b.append(icon(ic, ix, M + H / 2, isz, col_i, 2))
    b.append(T.text(label, M + pad + isz + gap, M + H / 2 + 5.2, 700 if primary else 600, 14.5, col_t, tracking=0.1))
    write(f'cta/{fname}.svg', svg(W + 2 * M, H + 2 * M, label, label, ''.join(b)))
    return int(round(W + 2 * M)), H + 2 * M


def ctas():
    for args in (
        ('cv', 'Download CV', 'download', True),
        ('projects', 'View Projects', 'grid', False),
        ('linkedin', 'LinkedIn', None, False),
        ('email', 'Email Me', 'mail', False),
    ):
        fn, label, ic, primary = args
        if fn == 'linkedin':
            # "in" monogram drawn with the brand font so it matches the other icons
            def g(cx, cy, col):
                d, w = T.font(700).run('in', 17, -0.3)
                return f'<path transform="translate({f(cx - w / 2)},{f(cy + 6)})" fill="{col}" d="{d}"/>'
            button(fn, label, None, primary, glyph=g)
        else:
            button(fn, label, ic, primary)


# ------------------------------------------------------------------ nav pills
NAV = [('about', 'About'), ('services', 'Services'), ('lifecycle', 'Lifecycle'), ('experience', 'Experience'),
       ('projects', 'Projects'), ('stack', 'Stack'), ('education', 'Education'), ('certifications', 'Certifications'),
       ('awards', 'Awards'), ('focus', 'Focus'), ('activity', 'Activity'), ('status', 'Status'), ('contact', 'Contact')]


def nav():
    H, pad = 34, 16
    for key, label in NAV:
        accent = key == 'contact'
        lw = T.measure(label, 600, 13, 0.1)
        W = lw + 2 * pad
        fill = 'var(--a1)' if accent else 'var(--chip)'
        fo = ' fill-opacity="0.14"' if accent else ''
        stroke = 'var(--a1)' if accent else 'var(--chipB)'
        so = ' stroke-opacity="0.6"' if accent else ''
        body = (f'<rect x="{M + .5}" y="{M + .5}" width="{f(W - 1)}" height="{H - 1}" rx="{H / 2 - .5}" fill="{fill}"{fo} stroke="{stroke}"{so}/>'
                + T.text(label, M + pad, M + H / 2 + 4.6, 600, 13, 'var(--a1)' if accent else 'var(--text2)', tracking=0.1))
        write(f'nav/{key}.svg', svg(W + 2 * M, H + 2 * M, label, f'Jump to {label}', body))


# ------------------------------------------------------------------ contact hero
def contact_hero():
    W, H = 1280, 346
    b = [card(1, 1, W - 2, H - 2, 28)]
    lx = 64
    # eyebrow
    b.append(f'<rect x="{lx}" y="57" width="26" height="2" rx="1" fill="url(#accH)"/>')
    b.append(T.text('GET IN TOUCH', lx + 38, 63, 700, 12, 'var(--a2)', tracking=2.2))
    # headline
    b.append(T.text('Open to roles, internships', lx, 120, 700, 40, 'var(--text)', tracking=-0.9))
    b.append(T.text('& freelance projects.', lx, 168, 700, 40, 'url(#accH)', tracking=-0.9))
    # body copy
    b.append(T.text('Share a short brief about the role or project and I’ll get back to you', lx, 210, 400, 15.5, 'var(--muted)'))
    b.append(T.text('within 24 hours. Email, LinkedIn and my CV are one click away below.', lx, 234, 400, 15.5, 'var(--muted)'))
    # chips
    chips = [('Open to roles & freelance', True), ('Replies within 24h', False), ('English · Urdu', False)]
    x = lx
    cy0 = 260
    for label, live in chips:
        tw = T.measure(label, 600, 12.5, 0.1)
        w = tw + 28 + (16 if live else 0)
        col = 'var(--ok)' if live else 'var(--chipB)'
        b.append(f'<rect x="{f(x + .5)}" y="{cy0 + .5}" width="{f(w - 1)}" height="31" rx="15.5" '
                 + (f'fill="var(--ok)" fill-opacity="0.1" stroke="var(--ok)" stroke-opacity="0.45"/>' if live else 'fill="var(--chip)" stroke="var(--chipB)"/>'))
        tx = x + 14
        if live:
            b.append(f'<circle cx="{f(x + 18)}" cy="{cy0 + 16}" r="3.5" fill="var(--ok)"/>')
            tx = x + 30
        b.append(T.text(label, tx, cy0 + 20.2, 600, 12.5, 'var(--text)', tracking=0.1))
        x += w + 10
    # right panel: how I can help
    px, py, pw, ph = 772, 36, 444, H - 72
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="20" fill="var(--card)" stroke="var(--border)"/>')
    b.append(T.text('HOW I CAN HELP', px + 28, py + 38, 700, 11, 'var(--muted2)', tracking=1.8))
    rows = [('SAP functional support', 'Process tracing, validation and user-issue handling'),
            ('Odoo implementation', 'Configuration, customization, testing and go-live'),
            ('Reporting & BI', 'Power BI, SQL and Oracle DB dashboards'),
            ('Frontend builds', 'HTML, CSS, JavaScript, WordPress and Figma')]
    y0 = py + 62
    pitch = 52.5
    for i, (t1, t2) in enumerate(rows):
        yy = y0 + i * pitch
        if i:
            b.append(f'<path d="M{px + 28} {f(yy - 7)}H{px + pw - 28}" stroke="var(--border)" stroke-width="1"/>')
        b.append(ring(px + 40, yy + 17, 12, 'var(--a1)'))
        b.append(icon('check', px + 40, yy + 17, 14, 'var(--a1)', 2.2))
        b.append(T.text(t1, px + 66, yy + 15, 700, 14.5, 'var(--text)', tracking=-0.05))
        b.append(T.text(t2, px + 66, yy + 35, 400, 12, 'var(--muted)'))
    write('contact-hero.svg', svg(W, H, 'Get in touch',
          'Open to roles, internships and freelance projects. SAP functional support, Odoo implementation, reporting and BI, and frontend builds. Typically replies within 24 hours.',
          ''.join(b)))


# ------------------------------------------------------------------ contact channel cards
def channel_cards():
    cards = [
        ('email', 'WRITE TO ME', 'Email', 'umerfaheem632@gmail.com', 'var(--a1)', 'mail'),
        ('linkedin', 'CONNECT', 'LinkedIn', 'in/youknowumer', 'var(--a2)', 'in'),
        ('resume', 'DOWNLOAD PDF', 'Résumé', 'Muhammad_Umer_Faheem_CV.pdf', 'var(--a5)', 'file'),
        ('github', 'FOLLOW', 'GitHub', '@youknowumer', 'var(--a1)', 'gh'),
    ]
    m, W, H = 4, 620, 140
    for key, cap, title, val, col, ic in cards:
        o = m
        b = [card(o, o, W, H, 22)]
        cx, cy = o + 70, o + H / 2
        b.append(ring(cx, cy, 32, col))
        if ic == 'in':
            d, w = T.font(700).run('in', 26, -0.4)
            b.append(f'<path transform="translate({f(cx - w / 2)},{f(cy + 9)})" fill="var(--text)" d="{d}"/>')
        elif ic == 'gh':
            b.append(f'<g transform="translate({f(cx - 15)},{f(cy - 15)}) scale(1.25)" fill="var(--text)"><path d="{GH}"/></g>')
        else:
            b.append(icon(ic, cx, cy, 28, 'var(--text)', 1.7))
        tx = o + 128
        b.append(T.text(cap, tx, o + 44, 700, 10.5, col, tracking=1.8))
        b.append(T.text(title, tx, o + 77, 700, 24, 'var(--text)', tracking=-0.3))
        b.append(T.text(val, tx, o + 104, 400, 14.5, 'var(--muted)'))
        ax = o + W - 50
        b.append(f'<circle cx="{ax}" cy="{f(cy)}" r="19" fill="var(--chip)" stroke="var(--chipB)"/>')
        b.append(icon('out', ax, cy, 16, col, 2))
        write(f'contact/{key}.svg', svg(W + 2 * m, H + 2 * m, f'{title}: {val}', cap.title(), ''.join(b)))


# ------------------------------------------------------------------ footer
def footer_bottom():
    W, H = 1280, 80
    b = [card(1, 1, W - 2, H - 2, 22)]
    b.append(T.text('© 2026 Muhammad Umer Faheem', W / 2, 36, 700, 14.5, 'var(--text)', tracking=0.05, anchor='middle'))
    b.append(T.text('Designed & built with intention · Lahore, Pakistan', W / 2, 58, 400, 12.5, 'var(--muted)', anchor='middle'))
    write('footer-bottom.svg', svg(W, H, 'Footer', 'Copyright 2026 Muhammad Umer Faheem, Lahore, Pakistan.', ''.join(b)))


if __name__ == '__main__':
    header_identity()
    ctas()
    nav()
    contact_hero()
    channel_cards()
    footer_bottom()
