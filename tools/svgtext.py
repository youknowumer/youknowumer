"""Text -> SVG outline helper (HarfBuzz shaping + fontTools outlines).

Why: the new header / contact assets draw their text as vector paths, so they render
identically everywhere (GitHub camo, mobile, dark/light) with NO embedded font, which keeps
each file tiny (nav pills are ~1 KB instead of ~45 KB).

Requires: pip install fonttools brotli uharfbuzz
"""
import io, os
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')


def _n(v):
    s = ('%.1f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


class Font:
    def __init__(self, weight):
        tt = TTFont(os.path.join(_FONT_DIR, f'inter-{weight}.woff2'))
        self.upem = tt['head'].unitsPerEm
        self.cmap = tt.getBestCmap()
        self.glyphs = tt.getGlyphSet()
        buf = io.BytesIO()
        tt.flavor = None
        tt.save(buf)
        self.hb_font = hb.Font(hb.Face(hb.Blob(buf.getvalue())))
        self.order = tt.getGlyphOrder()

    def run(self, text, size, tracking=0.0, features=None):
        """Return (path_d, width_px). Origin = baseline-left, y grows downward."""
        for ch in text:
            if ord(ch) not in self.cmap and ch != ' ':
                raise ValueError(f'glyph {ch!r} missing in font subset')
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb_font, buf, {'kern': True, 'liga': False, **(features or {})})
        s = size / self.upem
        pen = SVGPathPen(self.glyphs, ntos=_n)
        x = 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = self.order[info.codepoint]
            tp = TransformPen(pen, (s, 0, 0, -s, x + pos.x_offset * s, -pos.y_offset * s))
            self.glyphs[name].draw(tp)
            x += pos.x_advance * s + tracking
        return pen.getCommands(), max(0.0, x - tracking)


_cache = {}


def font(weight):
    if weight not in _cache:
        _cache[weight] = Font(weight)
    return _cache[weight]


def measure(text, weight, size, tracking=0.0):
    return font(weight).run(text, size, tracking)[1]


def text(txt, x, y, weight, size, fill, tracking=0.0, anchor='start', opacity=None, extra=''):
    """Return an SVG <path> for the text, anchored at (x, y baseline)."""
    d, w = font(weight).run(txt, size, tracking)
    if anchor == 'middle':
        x -= w / 2
    elif anchor == 'end':
        x -= w
    op = f' fill-opacity="{opacity}"' if opacity is not None else ''
    return f'<path transform="translate({_n(x)},{_n(y)})" fill="{fill}"{op}{extra} d="{d}"/>'
