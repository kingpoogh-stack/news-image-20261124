"""Renderer for the Tuesday, 24 November 2026 front page.

Composes THE WORLD TODAY as a single broadsheet page and writes the
result to assets/final-page.png. Everything is drawn with Pillow on
the build machine at double size and downscaled at the end, which
keeps the small type smooth; the shipped main.py needs no imaging
library at all, because it only copies the finished page into place.

The page leads on the Strait of Hormuz, where three oil tankers were
reported ablaze after striking sea mines, and carries the day's
other running stories around it: the call for four-way Ukraine talks
after the Shenzhen summit, the Megaspeed blacklist in the Nvidia spy
scandal, the Banten factory fire, Norway's court ruling on oil
licences after the COP31 collapse, the Pentagon's rebuke of Canada,
and a full Sport box, markets band, weather and World in Brief.
"""

import random
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SS = 2
PAGE_W, PAGE_H = 1024, 1024


def hx(code):
    code = code.lstrip("#")
    return tuple(int(code[i:i + 2], 16) for i in (0, 2, 4))


PAPER = hx("f3eee2")
PAPER_DARK = hx("e9e2d0")
INK = hx("1a1814")
SOFT = hx("4a453c")
FAINT = hx("787163")
RED = hx("961e18")
NAVY = hx("1e324a")
RULE = hx("2b2823")
CREAM = hx("f0ead6")

FONT_FILES = {
    "serif": "liberation/LiberationSerif-Regular.ttf",
    "serif-b": "liberation/LiberationSerif-Bold.ttf",
    "serif-i": "liberation/LiberationSerif-Italic.ttf",
    "serif-bi": "liberation/LiberationSerif-BoldItalic.ttf",
    "sans": "liberation/LiberationSans-Regular.ttf",
    "sans-b": "liberation/LiberationSans-Bold.ttf",
    "sans-i": "liberation/LiberationSans-Italic.ttf",
    "display": "noto/NotoSerifDisplay-Black.ttf",
}
_fonts = {}


def font(kind, size):
    key = (kind, round(size * 2))
    if key not in _fonts:
        base = Path("/usr/share/fonts/truetype")
        try:
            _fonts[key] = ImageFont.truetype(str(base / FONT_FILES[kind]),
                                             int(size * SS))
        except OSError:
            _fonts[key] = ImageFont.truetype(
                str(base / FONT_FILES["serif-b"]), int(size * SS))
    return _fonts[key]


class Sheet:
    """The page canvas and every drawing primitive the page uses."""

    def __init__(self):
        self.im = Image.new("RGB", (PAGE_W * SS, PAGE_H * SS), PAPER)
        self.dr = ImageDraw.Draw(self.im, "RGBA")

    @staticmethod
    def _pts(points):
        return [(px * SS, py * SS) for px, py in points]

    def box(self, x, y, w, h, fill=None, edge=None, lw=1):
        self.dr.rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS],
                          fill=fill, outline=edge,
                          width=max(1, int(lw * SS)))

    def seg(self, points, fill=RULE, lw=1):
        self.dr.line(self._pts(points), fill=fill,
                     width=max(1, int(lw * SS)))

    def poly(self, points, fill):
        self.dr.polygon(self._pts(points), fill=fill)

    def disc(self, cx, cy, rx, ry, fill=None, edge=None, lw=1):
        self.dr.ellipse([(cx - rx) * SS, (cy - ry) * SS,
                         (cx + rx) * SS, (cy + ry) * SS],
                        fill=fill, outline=edge, width=max(1, int(lw * SS)))

    def say(self, x, y, s, kind, size, colour=INK, anchor="la"):
        self.dr.text((x * SS, y * SS), s, font=font(kind, size),
                     fill=colour, anchor=anchor)

    def width(self, s, kind, size):
        return font(kind, size).getlength(s) / SS

    def wrap(self, s, kind, size, maxw):
        f = font(kind, size)
        lines, cur = [], ""
        for word in s.split():
            trial = word if not cur else cur + " " + word
            if f.getlength(trial) / SS <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, kind, size, maxw, leading, colour=INK,
             centre=False, limit=None):
        lines = self.wrap(s, kind, size, maxw)
        if limit:
            lines = lines[:limit]
        for ln in lines:
            if centre:
                self.say(x + maxw / 2, y, ln, kind, size, colour, "ma")
            else:
                self.say(x, y, ln, kind, size, colour)
            y += leading
        return y

    def vgrad(self, x, y, w, h, top, bottom):
        rows = int(h * SS)
        for i in range(rows):
            t = i / max(1, rows - 1)
            col = tuple(int(top[c] + (bottom[c] - top[c]) * t)
                        for c in range(3))
            self.dr.line([(x * SS, y * SS + i), ((x + w) * SS, y * SS + i)],
                         fill=col)

    def grain(self, x, y, w, h, seed, count=240, alpha=15):
        rng = random.Random(seed)
        for _ in range(count):
            px, py = x + rng.random() * w, y + rng.random() * h
            shade = rng.choice([(0, 0, 0), (255, 255, 255)])
            self.dr.point((px * SS, py * SS), fill=shade + (alpha,))

    def save(self, path):
        self.im.resize((PAGE_W, PAGE_H), Image.LANCZOS).save(
            path, optimize=True)


sh = Sheet()


def framed(x, y, w, h):
    sh.box(x, y, w, h, fill=hx("d2cbbb"), edge=RULE, lw=1)


def caption(x, y, w, s, credit):
    sh.say(x, y, s, "sans-i", 9.5, SOFT)
    sh.say(x + w, y, credit, "sans-i", 9.5, SOFT, "ra")


def kicker(x, y, s, colour=RED):
    sh.say(x, y, s, "sans-b", 10.5, colour)


# ---------------------------------------------------------------- panels

def draw_tanker(x, water_y, length, flame_h, seed):
    """One tanker at the waterline: black hull, red deck stripe, a
    white superstructure aft, flames amidships, smoke drifting right."""
    hull = [(x, water_y), (x + length * 0.93, water_y),
            (x + length, water_y + 7), (x + length * 0.87, water_y + 11),
            (x + length * 0.09, water_y + 11)]
    sh.poly(hull, hx("1c1b1d"))
    sh.box(x + 2, water_y - 3.5, length * 0.9, 3.5, fill=hx("943226"))
    sh.box(x + length * 0.1, water_y - 12, 20, 8.5, fill=hx("e0dacb"))
    sh.box(x + length * 0.14, water_y - 16, 4, 4, fill=hx("3a3836"))
    rng = random.Random(seed)
    for frac in (0.52, 0.60, 0.68):
        cx = x + length * frac
        fh = flame_h * (0.8 + 0.3 * rng.random())
        sh.poly([(cx - 4.5, water_y - 3), (cx, water_y - 3 - fh),
                 (cx + 4.5, water_y - 3)], hx("e67420"))
        sh.poly([(cx - 2, water_y - 3), (cx, water_y - 3 - fh * 0.55),
                 (cx + 2, water_y - 3)], hx("f6be46"))
    for i in range(6):
        sx = x + length * 0.6 + i * 13
        sy = water_y - 16 - flame_h - i * 3.5
        sh.disc(sx + 13, sy + 5.5, 13, 5.5, fill=(88, 82, 76, 150 - i * 16))


def strait_panel(x, y, w, h):
    """The lead scene: three tankers ablaze in the strait at first
    light, a grey escort warship at the right, the far shore behind."""
    framed(x, y, w, h)
    sh.vgrad(x + 1, y + 1, w - 2, h * 0.5, hx("a89a86"), hx("bcb098"))
    sh.box(x + 1, y + h * 0.5, w - 2, 3, fill=hx("c4bca8"))
    sh.box(x + 1, y + h * 0.52, w - 2, h * 0.48 - 1, fill=hx("32485a"))
    for i in range(9):
        lx = x + 24 + i * (w - 60) / 8
        sh.seg([(lx, y + h * 0.86), (lx + 26, y + h * 0.86)],
               fill=(120, 142, 152, 120), lw=1)
    draw_tanker(x + w * 0.05, y + h * 0.60, 232, 30, 41)
    draw_tanker(x + w * 0.52, y + h * 0.545, 117, 17, 42)
    draw_tanker(x + w * 0.70, y + h * 0.565, 93, 13, 43)
    wx, wy = x + w * 0.865, y + h * 0.60
    sh.poly([(wx, wy + 6), (wx + w * 0.115, wy + 6),
             (wx + w * 0.10, wy + 11), (wx + 8, wy + 11)], hx("60666e"))
    sh.box(wx + 12, wy - 3, w * 0.055, 8, fill=hx("6e747c"))
    sh.seg([(wx + 30, wy - 3), (wx + 30, wy - 12)], fill=hx("464c54"), lw=1.5)
    sh.box(wx + 24, wy - 14, 12, 3, fill=hx("464c54"))
    sh.say(x + 14, y + 8, "THE STRAIT OF HORMUZ", "sans-b", 12, CREAM)
    sh.say(x + 14, y + 24, "Mine strikes reported Tuesday", "sans", 9.5,
           hx("d6d0c0"))
    sh.grain(x, y, w, h, seed=97, count=320, alpha=11)
    sh.box(x, y, w, h, edge=RULE, lw=1)


def chart_panel(x, y, w, h):
    """A dealing-room screen on a bad morning for chip shares."""
    framed(x, y, w, h)
    sh.box(x + 1, y + 1, w - 2, h - 2, fill=hx("121a28"))
    for gx in range(1, 6):
        sh.seg([(x + gx * w / 6, y + 4), (x + gx * w / 6, y + h - 4)],
               fill=hx("344258"), lw=1)
    for gy in range(1, 4):
        sh.seg([(x + 4, y + gy * h / 4), (x + w - 4, y + gy * h / 4)],
               fill=hx("344258"), lw=1)
    curve = [(0.04, 0.26), (0.20, 0.34), (0.36, 0.30), (0.52, 0.46),
             (0.68, 0.42), (0.84, 0.62), (0.97, 0.74)]
    sh.seg([(x + px * w, y + py * h) for px, py in curve],
           fill=hx("e0543c"), lw=2)
    for px, py in curve:
        sh.disc(x + px * w, y + py * h, 2.5, 2.5, fill=hx("f0963c"))
    sh.say(x + 8, y + h - 19, "BRENT  $89.86  −2.9%", "sans-b", 12,
           hx("f0be46"))
    sh.grain(x, y, w, h, seed=7, count=140, alpha=10)
    sh.box(x, y, w, h, edge=RULE, lw=1)


def flags_panel(x, y, w, h):
    """The three flags at the Shenzhen trilateral summit, drawn from
    stripe specifications rather than unrolled calls."""
    framed(x, y, w, h)
    sh.box(x + 1, y + 1, w - 2, h - 2, fill=hx("cec6b4"))
    fw, fh, gap = (w - 32) / 3, h - 26, 8
    fx = x + 8
    for i in range(7):
        sh.box(fx, y + 6 + i * fh / 7, fw, fh / 7 + 1,
               fill=hx("a82c30") if i % 2 == 0 else hx("eeeae0"))
    sh.box(fx, y + 6, fw * 0.44, fh * 0.54, fill=hx("2c366e"))
    sh.say(fx + fw / 2, y + h - 15, "USA", "sans-b", 9.5, INK, "ma")
    fx += fw + gap
    for i, code in enumerate(("eeeae0", "344a8c", "b2282c")):
        sh.box(fx, y + 6 + i * fh / 3, fw, fh / 3 + 1, fill=hx(code))
    sh.say(fx + fw / 2, y + h - 15, "RUSSIA", "sans-b", 9.5, INK, "ma")
    fx += fw + gap
    sh.box(fx, y + 6, fw, fh, fill=hx("ba2828"))
    for sx, sy, sr in ((9, 9, 3.5), (19, 6, 1.8), (22, 11, 1.8),
                       (19, 16, 1.8), (15, 19, 1.8)):
        sh.disc(fx + sx, y + 6 + sy, sr, sr, fill=hx("f4c83c"))
    sh.say(fx + fw / 2, y + h - 15, "CHINA", "sans-b", 9.5, INK, "ma")
    sh.grain(x, y, w, h, seed=3, count=120, alpha=10)
    sh.box(x, y, w, h, edge=RULE, lw=1)


def factory_panel(x, y, w, h):
    """The gutted candy factory in Banten at night: a long shed, a
    caved-in roof section, fire crews' floodlights in the yard."""
    framed(x, y, w, h)
    sh.box(x + 1, y + 1, w - 2, h - 2, fill=hx("42424a"))
    sh.box(x + 1, y + h - 9, w - 2, 8, fill=hx("26262a"))
    bx, by = x + w * 0.10, y + h * 0.30
    bw, bh = w * 0.80, h * 0.52
    sh.box(bx, by, bw, bh, fill=hx("343236"))
    sh.poly([(bx - 4, by), (bx + bw * 0.45, by - 9), (bx + bw + 4, by)],
            hx("242328"))
    sh.poly([(bx + bw * 0.52, by - 7), (bx + bw * 0.80, by - 2),
             (bx + bw * 0.80, by + 7), (bx + bw * 0.52, by + 3)],
            hx("42424a"))
    for c in range(6):
        glow = hx("eeB05c") if c in (1, 4) else hx("1a1a1e")
        sh.box(bx + 8 + c * (bw - 14) / 6, by + 7, 9, bh - 14, fill=glow)
    for i in range(4):
        sh.disc(bx + bw * 0.58 + i * 10 + 9, by - 12 - i * 2, 9, 4,
                fill=(120, 116, 110, 130))
    for tx in (x + w * 0.22, x + w * 0.66):
        ly = y + h - 10
        sh.poly([(tx, ly - 20), (tx - 13, ly + 1), (tx + 13, ly + 1)],
                (250, 226, 150, 65))
        sh.seg([(tx - 5, ly), (tx, ly - 17)], fill=hx("121214"), lw=2)
        sh.seg([(tx + 5, ly), (tx, ly - 17)], fill=hx("121214"), lw=2)
        sh.disc(tx, ly - 20, 3.5, 3, fill=hx("fae6a0"))
    sh.grain(x, y, w, h, seed=53, count=150, alpha=12)
    sh.box(x, y, w, h, edge=RULE, lw=1)


def plenary_panel(x, y, w, h):
    """The COP31 plenary hall in Antalya, emptied after the collapse:
    the summit screen over two rows of delegates' desks."""
    framed(x, y, w, h)
    sh.vgrad(x + 1, y + 1, w - 2, h - 2, hx("2e3e54"), hx("3e4e60"))
    sh.box(x + 1, y + h - 8, w - 2, 7, fill=hx("685842"))
    sw, sh_h = w * 0.52, h * 0.36
    sx0, sy0 = x + (w - sw) / 2, y + 4
    sh.box(sx0, sy0, sw, sh_h, fill=hx("182636"), edge=hx("dcd6c6"), lw=1)
    sh.say(sx0 + sw / 2, sy0 + 3, "COP31  ·  ANTALYA", "sans-b", 9,
           hx("ece6d4"), "ma")
    for row, (ty, span) in enumerate(((y + h - 15, w - 90),
                                      (y + h - 7, w - 40))):
        sh.box(x + (w - span) / 2, ty, span, 3, fill=hx("4a3828"))
        seats = 11 + row * 2
        for i in range(seats):
            cx = x + (w - span) / 2 + 16 + i * (span - 32) / (seats - 1)
            sh.disc(cx, ty - 4.5, 2.5, 2.5, fill=hx("100f0e"))
    sh.grain(x, y, w, h, seed=31, count=140, alpha=12)
    sh.box(x, y, w, h, edge=RULE, lw=1)


def capitol_panel(x, y, w, h):
    """The US Capitol at dusk. The dome is swept as an arc of points
    rather than a pieslice, over a colonnaded block in silhouette."""
    framed(x, y, w, h)
    sh.vgrad(x + 1, y + 1, w - 2, h - 2, hx("60687a"), hx("8c929e"))
    sh.box(x + 1, y + h - 6, w - 2, 5, fill=hx("34343a"))
    cx, by = x + w / 2, y + h - 12
    bw = w * 0.62
    bx = cx - bw / 2
    sh.box(bx, by - 13, bw, 13, fill=hx("262830"))
    for i in range(9):
        lx = bx + 8 + i * (bw - 16) / 8
        sh.seg([(lx, by - 12), (lx, by - 2)], fill=hx("c4c6cc"), lw=1)
    sh.box(bx - 6, by - 15, bw + 12, 2.5, fill=hx("1e2028"))
    arc = [(cx + 21 * cos(pi * t / 24), by - 16 - 24 * sin(pi * t / 24))
           for t in range(25)]
    sh.poly(arc + [(cx + 21, by - 14), (cx - 21, by - 14)], hx("2c2f38"))
    sh.box(cx - 4, by - 45, 8, 6, fill=hx("2c2f38"))
    sh.seg([(cx, by - 45), (cx, by - 49)], fill=hx("18191e"), lw=1.5)
    for sx in (x + w * 0.10, x + w * 0.86):
        sh.box(sx, by - 9, w * 0.13, 9, fill=hx("282a32"))
    sh.grain(x, y, w, h, seed=23, count=110, alpha=10)
    sh.box(x, y, w, h, edge=RULE, lw=1)


# ---------------------------------------------------------------- layout

MARGIN = 28
CW = PAGE_W - 2 * MARGIN
COL_W = 309
GUT = 20.5
COL_X = [MARGIN, MARGIN + COL_W + GUT, MARGIN + 2 * (COL_W + GUT)]


def vrule(x, y1, y2):
    sh.seg([(x, y1), (x, y2)], fill=FAINT, lw=1)


def brief(x, y, head, body):
    """A World in Brief item: the bold head starts the first line and
    the rest of the brief wraps beneath it, newspaper style."""
    hw = sh.width(head, "sans-b", 9) + 6
    words, first, rest = body.split(), "", ""
    for wd in words:
        trial = wd if not first else first + " " + wd
        if sh.width(trial, "serif", 9.5) <= COL_W - hw or not first:
            first = trial
        else:
            rest = " ".join(words[len(first.split()):])
            break
    sh.say(x, y, head, "sans-b", 9, RED)
    sh.say(x + hw, y, first, "serif", 9.5, INK)
    if rest:
        sh.say(x, y + 10.5, sh.wrap(rest, "serif", 9.5, COL_W)[0],
               "serif", 9.5, INK)


def headline(s, y, size, maxw):
    while size > 12 and sh.width(s, "serif-b", size) > maxw:
        size -= 1
    sh.say(PAGE_W / 2, y, s, "serif-b", size, INK, "ma")


# --- folio, masthead, ticker, inside strip --------------------------------

sh.seg([(MARGIN, 16), (PAGE_W - MARGIN, 16)], fill=RULE, lw=2.5)
sh.say(MARGIN, 22, "Vol. XLI  ·  No. 328", "sans", 10.5, SOFT)
sh.say(PAGE_W / 2, 21, "TUESDAY, 24 NOVEMBER 2026", "sans-b", 12.5, RED, "ma")
sh.say(PAGE_W - MARGIN, 22, "World Edition  ·  Price $2.00  ·  theworldtoday.news",
       "sans", 10.5, SOFT, "ra")
sh.say(PAGE_W / 2, 38, "THE WORLD TODAY", "display", 45, INK, "ma")
sh.seg([(MARGIN, 94), (PAGE_W - MARGIN, 94)], fill=RULE, lw=2.5)
sh.seg([(MARGIN, 99), (PAGE_W - MARGIN, 99)], fill=RULE, lw=1)

sh.box(MARGIN, 105, CW, 22, fill=INK)
sh.say(PAGE_W / 2, 109.5,
       "BRENT  $89.86    ·    WTI  $80.89    ·    GOLD  +2.7%    ·    "
       "VIX  35.89    ·    NIKKEI 225  −5.06%    ·    KOSPI  −4%    ·    US GAS  $3.56",
       "sans-b", 11.5, hx("f0ead6"), "ma")

sh.say(MARGIN, 133, "INSIDE TODAY:", "sans-b", 10, RED)
sh.say(MARGIN + 92, 133,
       "Hormuz crisis — full report p.2–3   ·   Ukraine talks p.6   ·   "
       "Nvidia blacklist p.14   ·   Antalya fallout p.9   ·   Factory fire p.7   ·   Sport p.24",
       "sans", 10, SOFT)
sh.seg([(MARGIN, 148), (PAGE_W - MARGIN, 148)], fill=RULE, lw=1)

# --- the lead: Hormuz -------------------------------------------------------

kicker(MARGIN, 156, "STRAIT OF HORMUZ  ·  SHIPPING CRISIS")
sh.say(PAGE_W - MARGIN, 156, "THIRD DAY OF ATTACKS ON GULF SHIPPING",
       "sans-b", 10.5, SOFT, "ra")
headline("THREE TANKERS ABLAZE IN HORMUZ STRAIT", 168, 39, CW - 8)
sh.para(MARGIN + 60, 222,
        "Iran's Revolutionary Guard says three oil tankers struck sea mines "
        "and caught fire in the strait, as a decoy tanker spoofing its own "
        "signals adds to the confusion and US warships move in to escort shipping",
        "serif-i", 14, CW - 120, 18, SOFT, centre=True)

strait_panel(MARGIN, 264, CW, 112)
caption(MARGIN, 380, CW,
        "Smoke rises over the Strait of Hormuz, where three tankers were reported ablaze on Tuesday.",
        "Illustration: Staff  ·  Reporting: Gulf Bureau")

sh.say(MARGIN, 398, "By the Gulf Bureau", "serif-bi", 11.5, INK)
sh.para(MARGIN, 416,
        "DUBAI — Three oil tankers hit sea mines and caught fire in "
        "the Strait of Hormuz, Iran's Revolutionary Guard said on "
        "Tuesday, in the most serious attack yet on shipping in the "
        "waterway that carries about a fifth of the world's oil. "
        "Crews were reported to be abandoning one of the vessels.",
        "serif", 11.5, COL_W, 14.5)
vrule(COL_X[1] - GUT / 2, 416, 500)
sh.para(COL_X[1], 416,
        "The US Navy said warships were moving to escort merchant "
        "shipping through the strait. Tracking firms also reported a "
        "decoy tanker — its name translates as “Line Breaker” — "
        "broadcasting false positions as if it had broken the US "
        "embargo, in an apparent effort to tie up traffic.",
        "serif", 11.5, COL_W, 14.5)
vrule(COL_X[2] - GUT / 2, 416, 500)
sh.box(COL_X[2], 416, COL_W, 84, fill=PAPER_DARK, edge=RULE, lw=1)
sh.say(COL_X[2] + 13, 423, "“", "serif-b", 28, RED)
sh.para(COL_X[2] + 33, 428,
        "An unwelcome addition to an already dangerous situation.",
        "serif-bi", 12.5, COL_W - 47, 15.5)
sh.say(COL_X[2] + 33, 480, "— Mark Douglas, Starboard Maritime Intelligence, "
       "on the decoy tanker", "sans-i", 9.5, SOFT)
sh.seg([(MARGIN, 512), (PAGE_W - MARGIN, 512)], fill=RULE, lw=1.5)

# --- row A ------------------------------------------------------------------

RA = 520
kicker(COL_X[0], RA, "UKRAINE WAR  ·  SHENZHEN")
flags_panel(COL_X[0], RA + 14, COL_W, 44)
caption(COL_X[0], RA + 61, COL_W, "Flags of the three powers at Shenzhen.", "Staff")
y = sh.para(COL_X[0], RA + 78, "ZELENSKYY URGES FOUR-WAY TALKS",
            "serif-b", 18, COL_W, 21)
sh.para(COL_X[0], y + 2,
        "President Zelenskyy called for a four-party meeting with Russia, "
        "the United States and European leaders “as soon as possible”, "
        "saying Kyiv was ready to meet as early as Tuesday — a day after "
        "the Shenzhen trilateral summit. Brussels ruled out bilateral "
        "security talks with Moscow.",
        "serif", 11, COL_W, 13.5)

vrule(COL_X[1] - GUT / 2, RA, RA + 180)
kicker(COL_X[1], RA, "TECHNOLOGY  ·  MARKETS")
chart_panel(COL_X[1], RA + 14, COL_W, 44)
caption(COL_X[1], RA + 61, COL_W, "Screens in Tokyo as the tech rout ran on.", "Staff")
y = sh.para(COL_X[1], RA + 78, "US BLACKLISTS MEGASPEED IN NVIDIA SPY SCANDAL",
            "serif-b", 18, COL_W, 21)
sh.para(COL_X[1], y + 2,
        "Washington placed Singapore's Megaspeed International and six "
        "other Southeast Asian firms on its export blacklist, at the "
        "centre of an alleged Nvidia spy scandal. Nvidia reinstated its "
        "chief executive, Jensen Huang, after days of turmoil at the "
        "chipmaker, as the rout in technology shares ran into a second day.",
        "serif", 11, COL_W, 13.5)

vrule(COL_X[2] - GUT / 2, RA, RA + 180)
kicker(COL_X[2], RA, "INDONESIA")
factory_panel(COL_X[2], RA + 14, COL_W, 44)
caption(COL_X[2], RA + 61, COL_W, "Floodlights at the factory in Banten.", "Agencies")
y = sh.para(COL_X[2], RA + 78, "FACTORY FIRE DEATH TOLL RISES TO 24",
            "serif-b", 18, COL_W, 21)
sh.para(COL_X[2], y + 2,
        "The death toll from the fire at a candy factory in Banten rose "
        "to 24 as rescue teams searched the gutted plant for workers "
        "still missing. Emergency crews worked through the night while "
        "investigators sought the cause of the blaze.",
        "serif", 11, COL_W, 13.5)
sh.seg([(MARGIN, RA + 188), (PAGE_W - MARGIN, RA + 188)], fill=RULE, lw=1.5)

# --- row B ------------------------------------------------------------------

RB = RA + 194
kicker(COL_X[0], RB, "CLIMATE  ·  AFTER ANTALYA")
plenary_panel(COL_X[0], RB + 14, COL_W, 40)
caption(COL_X[0], RB + 57, COL_W, "The emptied plenary hall in Antalya.", "Staff")
y = sh.para(COL_X[0], RB + 74, "NORWAY COURT VOIDS OIL LICENCES",
            "serif-b", 17.5, COL_W, 20)
sh.para(COL_X[0], y + 2,
        "Norway's supreme court ruled its climate-disputed oil licences "
        "invalid, two days after the COP31 talks in Antalya ended without "
        "a deal. Experts met online on Tuesday to chart a way forward "
        "for climate action after the collapse.",
        "serif", 11, COL_W, 13.5)

vrule(COL_X[1] - GUT / 2, RB, RB + 172)
kicker(COL_X[1], RB, "UNITED STATES")
capitol_panel(COL_X[1], RB + 14, COL_W, 40)
caption(COL_X[1], RB + 57, COL_W, "The Capitol in Washington at dusk.", "Staff")
y = sh.para(COL_X[1], RB + 74, "PENTAGON REBUKES CANADA OVER DEFENCE",
            "serif-b", 17.5, COL_W, 20)
sh.para(COL_X[1], y + 2,
        "The Pentagon accused Canada of falling short as a credible "
        "partner in defending North America, citing defence-spending "
        "shortfalls and Ottawa's review of its planned purchase of "
        "American F-35 fighter jets.",
        "serif", 11, COL_W, 13.5)

sx = COL_X[2]
sh.box(sx, RB, COL_W, 172, edge=RULE, lw=1.2)
sh.box(sx, RB, COL_W, 20, fill=INK)
sh.say(sx + 10, RB + 4, "SPORT", "sans-b", 11.5, hx("f0ead6"))
sh.say(sx + COL_W - 10, RB + 5, "MILAN  ·  MELBOURNE", "sans", 9,
       hx("c8c2b2"), "ra")
y = sh.para(sx + 10, RB + 27, "SEVEN-GOAL THRILLER STUNS INTER",
            "serif-b", 14.5, COL_W - 20, 18)
y = sh.para(sx + 10, y + 1,
            "Tresoldi's hat-trick condemned Inter to a historic defeat "
            "in a seven-goal thriller at San Siro.",
            "serif", 10.5, COL_W - 20, 13)
sh.seg([(sx + 10, y + 4), (sx + COL_W - 10, y + 4)], fill=FAINT, lw=1)
y = sh.para(sx + 10, y + 9, "INGLIS, CAREY PUT AUSTRALIA ON TOP",
            "serif-b", 14.5, COL_W - 20, 18)
y = sh.para(sx + 10, y + 1,
            "Josh Inglis and Alex Carey put Australia in command of the "
            "deciding Test against South Africa.",
            "serif", 10.5, COL_W - 20, 13)
sh.seg([(sx + 10, y + 4), (sx + COL_W - 10, y + 4)], fill=FAINT, lw=1)
sh.para(sx + 10, y + 9,
        "FIFA confirmed the US, Mexico, Costa Rica and Jamaica as hosts "
        "of the 2031 Women's World Cup, and the UK for 2035.",
        "sans", 9.5, COL_W - 20, 12, SOFT)
sh.seg([(MARGIN, RB + 180), (PAGE_W - MARGIN, RB + 180)], fill=RULE, lw=1.5)

# --- markets band, weather, briefs, footer -----------------------------------

DB = RB + 186
sh.box(MARGIN, DB, 636, 38, fill=PAPER_DARK, edge=RULE, lw=1)
sh.say(MARGIN + 10, DB + 3, "MARKETS AT A GLANCE", "sans-b", 9, RED)
DATA = [("BRENT", "$89.86"), ("WTI", "$80.89"), ("GOLD", "+2.7%"),
        ("VIX", "35.89"), ("NIKKEI 225", "−5.06%"), ("KOSPI", "−4.0%"),
        ("S&P 500", "−3.7%"), ("NASDAQ", "−5.3%")]
for i, (name, val) in enumerate(DATA):
    cx = MARGIN + 10 + (i % 4) * 158
    cy = DB + 16 + (i // 4) * 12
    sh.say(cx, cy, name, "sans-b", 8.5, SOFT)
    sh.say(cx + 60, cy, val, "sans-b", 8.5, RED if val.startswith("−") else INK)
sh.box(MARGIN + 648, DB, 320, 38, edge=RULE, lw=1)
sh.say(MARGIN + 658, DB + 3, "WEATHER TODAY", "sans-b", 9, NAVY)
sh.say(MARGIN + 658, DB + 16,
       "Antalya 17° clearing  ·  Kyiv 1° snow  ·  Tokyo 12° fair",
       "sans", 8.5, SOFT)
sh.say(MARGIN + 658, DB + 28,
       "New York 7° clear  ·  London 8° rain  ·  Shenzhen 23° humid",
       "sans", 8.5, SOFT)

WB = DB + 40
sh.box(MARGIN, WB, CW, 17, fill=NAVY)
sh.say(MARGIN + 10, WB + 3.5, "WORLD IN BRIEF", "sans-b", 10, hx("f0ead6"))
sh.say(PAGE_W / 2, WB + 3.5, "PAGE 1  ·  WORLD", "sans", 9.5,
       hx("cdd0d8"), "ma")
sh.say(PAGE_W - MARGIN - 10, WB + 3.5, "TUESDAY, 24 NOVEMBER 2026",
       "sans-b", 10, hx("f0ead6"), "ra")
BRIEFS = [
    ("SOUTH KOREA", "Russian aircraft entered its air defence zone over "
                    "waters off Japan; Seoul corrected reports of a "
                    "territorial violation."),
    ("CHINA", "An official surnamed Ma was sentenced to death for "
              "spying for an unnamed foreign country."),
    ("SUDAN", "RSF drone attacks struck power stations and triggered "
              "mass blackouts across the country."),
    ("EBOLA", "Kenya discharged its last Ebola patient, even as the "
              "death toll in Congo passed 5,300."),
    ("RUSSIA", "Moscow told the UN Security Council it will not agree "
               "to any new grain deal with Ukraine."),
    ("SOUTH AFRICA", "Voters cast ballots as anger over power cuts and "
                     "failing services threatened the ANC."),
]
for i, (head, body) in enumerate(BRIEFS):
    brief(COL_X[i % 3], WB + 22 + (i // 3) * 22, head, body)

sh.say(MARGIN, 1010, "Page 1  ·  WORLD  ·  Continued inside", "sans-b", 8.5, SOFT)
sh.say(PAGE_W - MARGIN, 1010, "Markets p.14  ·  Sport p.24  ·  theworldtoday.news",
       "sans", 8.5, SOFT, "ra")

# ---------------------------------------------------------------- output

out = Path(__file__).resolve().parent.parent / "assets" / "final-page.png"
sh.save(out)
print("wrote", out)
