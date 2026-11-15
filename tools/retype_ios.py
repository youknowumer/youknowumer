#!/usr/bin/env python3
"""iOS typography pass for the profile SVGs.

  * One family everywhere: SF Pro on Apple devices (-apple-system / "SF Pro Text"), with an embedded
    Inter subset ("InterUI") as the fallback so Windows / Android / Linux render the same iOS-like text.
  * Monospace labels -> SF Pro caps (iOS footnote / caption style: semibold, tracked ~0.06em).
  * iOS type scale: large titles bold with tight tracking, headings semibold-bold, body regular.
  * Weight 800 -> 700 (iOS "Bold" is the heaviest everyday weight).

Usage: retype_ios.py SRC_DIR DST_DIR       (idempotent: files already carrying InterUI are copied as-is)
"""
import re, sys, os, glob, io, base64, html
from fontTools import subset
from fontTools.ttLib import TTFont

SRC, DST = sys.argv[1], sys.argv[2]
os.makedirs(DST, exist_ok=True)
FONT_DIR = '/usr/share/fonts/opentype/inter'
WEIGHT_FILE = {400: 'Inter-Regular.otf', 500: 'Inter-Medium.otf', 600: 'Inter-SemiBold.otf', 700: 'Inter-Bold.otf'}

SANS_CSS = ('-apple-system, "SF Pro Text", "SF Pro Display", BlinkMacSystemFont, InterUI, "Segoe UI", Roboto, '
            'ui-sans-serif, "Helvetica Neue", Helvetica, Arial, sans-serif')
SANS_ATTR = SANS_CSS.replace('"', "'")

files = sorted(glob.glob(os.path.join(SRC, '*.svg')))
texts = {f: open(f, encoding='utf-8').read() for f in files}

# ---- glyph set: every character used in any SVG + ASCII -------------------------------------------
chars = set(chr(c) for c in range(0x20, 0x7F))
for s in texts.values():
    for t in re.findall(r'>([^<>]+)<', s):
        chars |= set(html.unescape(t))
chars |= set('·—–→←↑↓✓©•’‘“”…×+')
UNICODES = sorted(ord(c) for c in chars if ord(c) >= 0x20)

_cache = {}


def font_b64(weight):
    if weight not in _cache:
        opts = subset.Options()
        opts.flavor = 'woff2'
        opts.layout_features = ['kern', 'tnum', 'case', 'calt', 'liga']
        opts.name_IDs = [1, 2]
        opts.notdef_outline = True
        f = TTFont(os.path.join(FONT_DIR, WEIGHT_FILE[weight]))
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=UNICODES)
        sub.subset(f)
        buf = io.BytesIO()
        f.flavor = 'woff2'
        f.save(buf)
        _cache[weight] = base64.b64encode(buf.getvalue()).decode()
    return _cache[weight]


def weights_used(s):
    ws = {400}
    for m in re.finditer(r'font-weight[=:]\s*"?(\d+|bold)', s):
        w = 700 if m[1] == 'bold' else int(m[1])
        ws.add(min(max(round(w / 100) * 100, 400), 700))
    return ws


def to_ios_weight(s):
    return re.sub(r'font-weight([=:]\s*"?)800', r'font-weight\g<1>700', s)


def swap_families(s):
    # CSS declarations
    s = re.sub(r'font-family\s*:\s*[^;}]+', 'font-family: ' + SANS_CSS, s)
    # attributes (double-quoted value that may contain single quotes)
    s = re.sub(r'font-family="[^"]*"', 'font-family="' + SANS_ATTR + '"', s)
    return s


def tracking(s):
    """iOS-style tracking per text element, based on size."""
    def fix(m):
        tag = m[0]
        sz = re.search(r'font-size="([\d.]+)"', tag)
        if not sz:
            return tag
        size = float(sz[1])
        ls = re.search(r'letter-spacing="([-\d.]+)"', tag)
        wt = re.search(r'font-weight="(\d+)"', tag)
        weight = int(wt[1]) if wt else 400
        if ls:
            val = float(ls[1])
            if val > 0:  # tracked caps label (was monospace): iOS caption tracking, semibold
                new = round(min(val, 0.1 * size + 0.4 if size <= 12 else val), 2)
                new = max(min(new, 1.8), 0.6)
                tag = tag.replace(ls[0], f'letter-spacing="{new}"')
                if weight < 600:
                    tag = (tag.replace(wt[0], 'font-weight="600"') if wt else tag.replace('<text', '<text font-weight="600"', 1))
            return tag
        if size >= 28 and weight >= 600:
            return tag.replace('<text', f'<text letter-spacing="{round(-0.022 * size, 2)}"', 1)
        if size >= 19 and weight >= 600:
            return tag.replace('<text', f'<text letter-spacing="{round(-0.014 * size, 2)}"', 1)
        if 15 <= size < 19 and weight >= 600:
            return tag.replace('<text', f'<text letter-spacing="{round(-0.008 * size, 2)}"', 1)
        return tag
    return re.sub(r'<text\b[^>]*>', fix, s)


from PIL import ImageFont
_pf = {}


def text_w(txt, size, weight=400, ls=0.0):
    key = (size, weight)
    if key not in _pf:
        _pf[key] = ImageFont.truetype(os.path.join(FONT_DIR, WEIGHT_FILE.get(weight, WEIGHT_FILE[400])), int(round(size * 8)))
    return _pf[key].getlength(html.unescape(txt)) / 8 + ls * len(txt)


PILL = re.compile(
    r'<g transform="translate\(([\d.]+),([\d.]+)\)">(<g transform="translate\(0\.0,0\.0\)">)?'
    r'<rect width="([\d.]+)" height="([\d.]+)"([^>]*)/>(<circle[^>]*/>)?'
    r'<text class="m" x="([\d.]+)"([^>]*)>([^<]*)</text>(</g>)?</g>')


def fit_chips(s):
    """pill widths were sized for monospace; refit them to the proportional text and reflow each row."""
    ms = list(PILL.finditer(s))
    if not ms:
        return s
    info = []
    for m in ms:
        X, Y, W, H, tx = float(m[1]), m[2], float(m[4]), m[5], float(m[8])
        size = float(re.search(r'font-size="([\d.]+)"', m[9])[1])
        wt = re.search(r'font-weight="(\d+)"', m[9])
        ls = re.search(r'letter-spacing="([-\d.]+)"', m[9])
        tw = text_w(m[10], size, int(wt[1]) if wt else 400, float(ls[1]) if ls else 0)
        newW = round(tx + tw + (14 if m[7] else tx), 1)
        info.append(dict(m=m, X=X, Y=Y, W=W, newW=newW))
    # group into rows (consecutive, same Y, left-to-right)
    rows, cur = [], [info[0]]
    for a in info[1:]:
        if a['Y'] == cur[-1]['Y'] and a['X'] > cur[-1]['X']:
            cur.append(a)
        else:
            rows.append(cur); cur = [a]
    rows.append(cur)
    for r in rows:
        if len(r) < 2:
            r[0]['newX'] = r[0]['X']; r[0]['newW'] = r[0]['W']; continue
        x = r[0]['X']
        for i, a in enumerate(r):
            a['newX'] = round(x, 1)
            gap = (r[i + 1]['X'] - a['X'] - a['W']) if i + 1 < len(r) else 0
            x += a['newW'] + gap
    out, pos = [], 0
    for a in info:
        m = a['m']
        out.append(s[pos:m.start()])
        t = m[0]
        t = t.replace(f'translate({m[1]},{m[2]})', f'translate({a["newX"]:g},{m[2]})', 1)
        t = t.replace(f'<rect width="{m[4]}"', f'<rect width="{a["newW"]:g}"', 1)
        out.append(t)
        pos = m.end()
    out.append(s[pos:])
    return ''.join(out)


def embed(s):
    ws = sorted(weights_used(s))
    faces = ''.join(
        '@font-face{font-family:InterUI;font-weight:%d;font-style:normal;font-display:block;'
        'src:url(data:font/woff2;base64,%s) format("woff2")}' % (w, font_b64(w)) for w in ws)
    # InterUI has no kerning for tabular numerals unless asked; keep tnum + kerning on
    block = faces + 'text{font-feature-settings:"kern","tnum","case";font-kerning:normal;-webkit-font-smoothing:antialiased}'
    if '<style>' in s:
        return s.replace('<style>', '<style>' + block, 1)
    m = re.search(r'<svg\b[^>]*>', s)
    return s[:m.end()] + '<style>' + block + '</style>' + s[m.end():]


for f in files:
    s = texts[f]
    if 'InterUI' not in s:
        s = to_ios_weight(s)
        s = swap_families(s)
        s = tracking(s)
        s = fit_chips(s)
        s = embed(s)
    open(os.path.join(DST, os.path.basename(f)), 'w', encoding='utf-8').write(s)
    print('ok', os.path.basename(f), f'{len(s)//1024} KB')
