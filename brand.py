"""foods that move: brand constants, type and drawing helpers (shared by renderer + library)."""
import math, os
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
W, H, FPS = 1080, 1920, 30
L, R = 72, 940                       # safe zone: top 220, bottom 400, right 140


def hexc(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------ design system --
BG = hexc("FFF3E2")        # warm cream
DOT = hexc("F6E2C6")       # background dot grid
CARD = hexc("FFFFFF")
INK = hexc("2A2140")       # deep plum: text + all outlines
MUTED = hexc("8C7F9A")
LINE = hexc("EAD8BF")
ACCENT = hexc("F2542D")    # tomato
MARKER = hexc("FFDF6B")    # highlighter behind key phrases
ING = {   # bar + icon colour per ingredient (unknown ingredients fall back to MUTED)
    "flour": hexc("EBD3A4"), "milk": hexc("5AAEF2"), "egg": hexc("FFA41C"), "butter": hexc("FFD84D"),
    "water": hexc("2EC4B6"), "sugar": hexc("FF6FA8"), "brown sugar": hexc("C98A4B"), "salt": hexc("B4BACF"),
    "oil": hexc("9BD14A"), "vinegar": hexc("B78CFF"), "cream": hexc("FFE9B8"), "chocolate": hexc("7B4A2E"),
    "yolk": hexc("FF8A00"), "egg yolk": hexc("FF8A00"), "white": hexc("E3E8F0"), "egg white": hexc("E3E8F0"),
    "stock": hexc("E0A35C"), "meat": hexc("E5626B"), "fat": hexc("F4E3D0"), "rice": hexc("F3EEDD"),
    "cornmeal": hexc("F2C230"), "semolina": hexc("F2D16B"), "oats": hexc("D9C08F"), "yeast": hexc("D2B48C"),
    "baking powder": hexc("DCE3EC"), "baking soda": hexc("DCE3EC"), "honey": hexc("F5A623"),
    "mustard": hexc("E3B505"), "lemon": hexc("FFE45C"), "lemon juice": hexc("FFE45C"), "juice": hexc("FFB547"),
    "cheese": hexc("FFD166"), "parmesan": hexc("FFD166"), "wine": hexc("B83A5E"), "buttermilk": hexc("CFE9FF"),
    "cocoa": hexc("6B4230"), "jam": hexc("E8345A"), "syrup": hexc("E39B3A"), "spirit": hexc("D9A35B"),
    "espresso": hexc("5A3A2A"), "almond flour": hexc("E8C9A0"), "breadcrumbs": hexc("E2B878"), "pepper": hexc("8C8C8C"),
    "soy sauce": hexc("5A3020")}
OX, HY, CA = hexc("FF5D5D"), hexc("FFFFFF"), hexc("3B3550")   # atoms: O, H, C


def lum(c): return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255
def rgb(c, a=1.0): return (c[0] / 255, c[1] / 255, c[2] / 255, a)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): return tuple(int(round(lerp(a, b, clamp(t)))) for a, b in zip(c1, c2))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x):
    x = clamp(x); c = 2.0
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


# --------------------------------------------------------------------- text --
_fc = {}
def font(kind, size):
    key = (kind, size)
    if key not in _fc:
        if kind in ("disp", "disp_b"):
            f = ImageFont.truetype(os.path.join(FONTS, "Fredoka.ttf"), size)
            f.set_variation_by_axes([600 if kind == "disp" else 700, 100])
        elif kind in ("mono", "mono_b"):
            f = ImageFont.truetype(os.path.join(FONTS, "JetBrainsMono.ttf"), size)
            f.set_variation_by_axes([500 if kind == "mono" else 750])
        elif kind == "body":
            f = ImageFont.truetype(os.path.join(FONTS, "Inter-Medium.otf"), size)
        else:
            f = ImageFont.truetype(os.path.join(FONTS, "Inter-SemiBold.otf"), size)
        _fc[key] = f
    return _fc[key]


def tw(s, kind, size, track=0.0):
    return font(kind, size).getlength(s) + track * size * max(0, len(s) - 1)


def tokens(s):
    """'Same *3 ingredients*.' -> [(word, highlighted, glued_to_previous)]."""
    out, prev = [], ""
    for i, part in enumerate(s.split("*")):
        glue = bool(out) and part[:1] not in (" ", "") and prev[-1:] not in (" ", "")
        if part: prev = part
        for j, w in enumerate(part.split()):
            out.append((w, i % 2 == 1, glue and j == 0))
    return out


def wrap(toks, kind, size, maxw):
    """-> list of lines, each a list of (word, hl, x, width)."""
    sp = tw(" ", kind, size); lines, line, x = [], [], 0.0
    for w, hl, glue in toks:
        ww = tw(w, kind, size)
        if line and not glue and x + sp + ww > maxw:
            lines.append(line); line, x = [], 0.0
        if line and not glue: x += sp
        line.append((w, hl, x, ww)); x += ww
    if line: lines.append(line)
    return lines


class Canvas:
    """Cairo for shapes, Pillow for type (queued, drawn on top)."""
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
        self.cr = cairo.Context(self.surf)
        self.texts = []

    def text(self, x, y, s, kind, size, col, a=1.0, track=0.0):
        if a > 0.004: self.texts.append((x, y, s, kind, size, col, a, track))
        return x + tw(s, kind, size, track)

    def image(self):
        self.surf.flush()
        buf = np.ndarray((self.h, self.surf.get_stride() // 4, 4), np.uint8, self.surf.get_data())
        img = Image.fromarray(buf[:, :self.w, [2, 1, 0]].copy())
        for x, y, s, kind, size, col, a, track in self.texts:
            # draw into a coverage mask, scale it by opacity, paste the colour through it
            f = font(kind, size)
            pad = int(size * 0.6); x0, y0 = int(x) - pad, int(y - size * 1.3)
            w_ = int(tw(s, kind, size, track)) + 2 * pad; h_ = int(size * 1.9)
            m = Image.new("L", (w_, h_), 0); md = ImageDraw.Draw(m)
            fx, fy = x - x0, y - y0
            if not track:
                md.text((fx, fy), s, font=f, fill=255, anchor="ls")
            else:
                for i, ch in enumerate(s):
                    md.text((fx + f.getlength(s[:i]) + track * size * i, fy), ch, font=f, fill=255, anchor="ls")
            if a < 0.996: m = m.point(lambda v, k=clamp(a): int(v * k))
            img.paste(tuple(col), (x0, y0), m)
        return img


# ------------------------------------------------------------ cairo helpers --
def rrect(cr, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    cr.close_path()


def ellipse(cr, x, y, rx, ry):
    cr.save(); cr.translate(x, y); cr.scale(max(rx, 0.01), max(ry, 0.01)); cr.new_sub_path()
    cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()


def fs(cr, fill, lw=5, a=1.0, ink=INK):
    """fill + ink outline (the sticker look)."""
    cr.set_source_rgba(*rgb(fill, a)); cr.fill_preserve()
    cr.set_source_rgba(*rgb(ink, a)); cr.set_line_width(lw); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.stroke()


def fill(cr, col, a=1.0): cr.set_source_rgba(*rgb(col, a)); cr.fill()


def stroke(cr, col, lw, a=1.0):
    cr.set_source_rgba(*rgb(col, a)); cr.set_line_width(lw)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.stroke()


def blob(cr, cx, cy, r, t, wob=1.0):
    n = 90
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        rr = r * (1 + wob * (0.035 * math.sin(3 * th + t * 0.9) + 0.022 * math.sin(5 * th - t * 1.3)))
        (cr.move_to if i == 0 else cr.line_to)(cx + rr * math.cos(th), cy + rr * math.sin(th))
    cr.close_path()


def group(cr, a, fn, *args):
    """Draw fn as one layer at opacity a (no outline see-through)."""
    if a <= 0.004: return
    if a >= 0.996: fn(*args); return
    cr.push_group(); fn(*args); cr.pop_group_to_source(); cr.paint_with_alpha(a)


def background(cr, t, w=W, h=H):
    cr.set_source_rgb(*rgb(BG)[:3]); cr.paint()
    tile = cairo.ImageSurface(cairo.FORMAT_ARGB32, 40, 40); tc = cairo.Context(tile)
    tc.arc(20, 20, 2.6, 0, 2 * math.pi); tc.set_source_rgba(*rgb(DOT)); tc.fill()
    pat = cairo.SurfacePattern(tile); pat.set_extend(cairo.EXTEND_REPEAT)
    m = cairo.Matrix(); m.translate(0, (t * 10) % 40); pat.set_matrix(m)
    cr.set_source(pat); cr.paint()


