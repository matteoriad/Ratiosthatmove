"""ratios that move: the drawing library. Illustrations, ingredient icons, molecule scenes.
Episodes refer to these by name (see LIBRARY.md). Add new ones here."""
import math
import numpy as np
import cairo
from brand import *  # noqa

# ----------------------------------------------------------- illustrations --
# Each is drawn around (0,0); content spans roughly x -220..220, y -250..130.

def plate(cr):
    ellipse(cr, 0, 92, 225, 64); fs(cr, CARD, 6)
    ellipse(cr, 0, 88, 168, 40); stroke(cr, LINE, 4)


def steam(cr, x, y, age, n=3, spread=44, h=90):
    for k in range(n):
        ph = (age * 0.8 + k / n) % 1.0
        a = math.sin(ph * math.pi) * 0.55
        xx = x + (k - (n - 1) / 2) * spread; yy = y - ph * 40
        cr.move_to(xx, yy)
        for i in range(1, 13):
            s = i / 12
            cr.line_to(xx + 9 * math.sin(s * 6.0 + age * 3 + k), yy - s * h)
        stroke(cr, INK, 6, a * 0.45)


def draw_crepe(cr, age, look=None):
    plate(cr)
    ax, ay = -175, 62
    a0, a1 = math.radians(-82), math.radians(-3)
    def fan(dx, dy, rr):
        cr.move_to(ax + dx, ay + dy)
        for i in range(81):
            th = a0 + (a1 - a0) * i / 80
            r = rr + 8 * math.sin(18 * th)
            cr.line_to(ax + dx + r * math.cos(th), ay + dy + 0.62 * r * math.sin(th))
        cr.close_path()
    fan(14, 12, 325); fs(cr, hexc("E9B460"), 6)                # folded layer below
    fan(0, 0, 330); fs(cr, hexc("F7D388"), 6)
    cr.save(); fan(0, 0, 330); cr.clip()
    rng = np.random.default_rng(7)                             # lacy browned spots
    g = cairo.RadialGradient(ax, ay, 20, ax, ay, 330)
    g.add_color_stop_rgba(0, *rgb(hexc("F9DC9A"))); g.add_color_stop_rgba(1, *rgb(hexc("EDB45E")))
    cr.set_source(g); cr.paint()
    for _ in range(120):
        r = rng.uniform(40, 320); th = rng.uniform(a0 + .03, a1 - .03)
        ellipse(cr, ax + r * math.cos(th), ay + 0.62 * r * math.sin(th), rng.uniform(5, 13), rng.uniform(3, 7))
        stroke(cr, hexc("C97B32"), 2.6, rng.uniform(0.35, 0.75))
    cr.move_to(ax + 40, ay - 8)                                # fold crease
    cr.curve_to(ax + 120, ay - 70, ax + 230, ay - 80, ax + 300, ay - 40); stroke(cr, hexc("E2A653"), 5)
    cr.restore()
    for x, y in ((70, -30), (110, -6), (40, 4)):              # blueberries
        cr.arc(x, y, 17, 0, 2 * math.pi); fs(cr, hexc("5965E8"), 4)
        cr.arc(x - 5, y - 6, 4, 0, 2 * math.pi); fill(cr, CARD, 0.8)
    cr.save(); cr.translate(140, -38); cr.rotate(-0.5)          # mint leaf
    cr.move_to(-22, 0); cr.curve_to(-8, -18, 14, -16, 24, 0); cr.curve_to(10, 14, -8, 14, -22, 0)
    fs(cr, hexc("57C27A"), 4); cr.restore()
    for i in range(18):                                        # powdered sugar
        rr = 0.5 + 0.5 * math.sin(i * 2.7)
        cr.arc(-60 + i * 11 + 6 * math.sin(i), -60 + 40 * rr, 2.6, 0, 2 * math.pi); fill(cr, CARD, 0.95)
    steam(cr, -20, -120, age)


def popover_puff(cr, rise):
    circles = [(0, -50 * rise - 10, 135), (-92, -80 * rise - 15, 76), (92, -74 * rise - 15, 80),
               (-42, -138 * rise - 10, 80), (52, -134 * rise - 10, 74), (0, -168 * rise, 60)]
    return circles


def draw_popover(cr, age, look=None):
    plate(cr)
    rise = 0.7 + 0.3 * ease(age / 0.9) + 0.015 * math.sin(age * 2.6)
    circ = popover_puff(cr, rise)
    for x, y, r in circ: cr.arc(x, y, r + 3, 0, 2 * math.pi); cr.close_path()
    stroke(cr, INK, 12)
    cr.save()
    for x, y, r in circ: cr.new_sub_path(); cr.arc(x, y, r, 0, 2 * math.pi)
    cr.clip()
    g = cairo.LinearGradient(0, -260, 0, 60)
    g.add_color_stop_rgb(0, *rgb(hexc("C8742E"))[:3]); g.add_color_stop_rgb(0.45, *rgb(hexc("E9A04C"))[:3])
    g.add_color_stop_rgb(1, *rgb(hexc("F8D48A"))[:3])
    cr.set_source(g); cr.paint()
    for x, y, r in circ[1:]:                                   # lumpy highlights
        cr.arc(x - r * 0.3, y - r * 0.35, r * 0.28, math.pi * 1.05, math.pi * 1.6); stroke(cr, CARD, 7, 0.55)
    cr.restore()
    cr.move_to(-120, 0); cr.line_to(120, 0); cr.line_to(98, 92); cr.line_to(-98, 92); cr.close_path()   # tin
    fs(cr, hexc("A9C3DB"), 6)
    for x in (-60, 0, 60): cr.move_to(x, 12); cr.line_to(x * 0.85, 82); stroke(cr, hexc("86A3BF"), 4)
    ellipse(cr, 0, 0, 124, 20); fs(cr, hexc("C9DAEA"), 6)
    ellipse(cr, 0, -2, 104, 13); fill(cr, hexc("E9A04C"))
    steam(cr, 0, -150 - 170 * (rise - 0.7), age, n=2, spread=70, h=60)


def draw_pancake(cr, age, look=None):
    plate(cr)
    for k in range(3):                                         # stack drops in
        drop = ease((age - k * 0.14) / 0.35)
        if drop <= 0: continue
        y = 46 - k * 44 - (1 - drop) * 260
        cr.save(); cr.translate(0, y)
        ellipse(cr, 0, 14, 175, 44); fs(cr, hexc("D8954B"), 6)
        cr.rectangle(-175, -14, 350, 28); fill(cr, hexc("D8954B"))
        cr.move_to(-175, -14); cr.line_to(-175, 14); cr.move_to(175, -14); cr.line_to(175, 14); stroke(cr, INK, 6)
        ellipse(cr, 0, -14, 175, 44); fs(cr, hexc("F5C677"), 6)
        cr.restore()
    top = 46 - 2 * 44 - 14
    s = ease((age - 0.55) / 0.4)
    if s > 0:                                                  # syrup + drips
        cr.save(); cr.translate(0, top)
        blob(cr, 0, 0, 1, age * 0.6, 1.4); cr.restore()
        cr.save(); cr.translate(0, top); cr.scale(140 * s, 34 * s); blob(cr, 0, 0, 1, age, 1.5); cr.restore()
        fs(cr, hexc("C26A1C"), 5)
        for x, ln in ((-110, 70), (-30, 110), (70, 85), (130, 50)):
            l = ln * ease((age - 0.75 - abs(x) / 900) / 0.8) * s
            if l > 4:
                cr.move_to(x, top + 20); cr.line_to(x, top + 20 + l); stroke(cr, INK, 23)
                cr.move_to(x, top + 20); cr.line_to(x, top + 20 + l); stroke(cr, hexc("C26A1C"), 13)
    b = back((age - 0.85) / 0.45)
    if b > 0:                                                  # butter pat
        cr.save(); cr.translate(10, top - 22 * b); cr.scale(b, b)
        cr.move_to(-40, -6); cr.line_to(10, -26); cr.line_to(52, -8); cr.line_to(2, 12); cr.close_path(); fs(cr, hexc("FFE58A"), 5)
        cr.move_to(-40, -6); cr.line_to(2, 12); cr.line_to(2, 30); cr.line_to(-40, 12); cr.close_path(); fs(cr, hexc("F5C842"), 5)
        cr.move_to(2, 12); cr.line_to(52, -8); cr.line_to(52, 10); cr.line_to(2, 30); cr.close_path(); fs(cr, hexc("EDB92E"), 5)
        cr.restore()
    steam(cr, -10, -150, age)


def col(look, key, default):
    """A colour from the dish's optional "look" dict (hex string), else the default."""
    v = (look or {}).get(key) or default
    return hexc(v)


def board(cr):
    rrect(cr, -222, 58, 444, 44, 22); fs(cr, hexc("DDA36A"), 6)
    for y, x0, x1 in ((72, -180, -40), (86, 10, 170), (78, 60, 150)):
        cr.move_to(x0, y); cr.line_to(x1, y); stroke(cr, hexc("C08446"), 3.5)


def draw_bread(cr, age, look=None):
    board(cr)
    crust = col(look, "crust", "D98A3D")
    def loaf():
        cr.move_to(-192, 66); cr.curve_to(-222, -128, 222, -128, 192, 66); cr.close_path()
    loaf(); fs(cr, crust, 6)
    cr.save(); loaf(); cr.clip()
    g = cairo.LinearGradient(0, -110, 0, 66)
    g.add_color_stop_rgb(0, *rgb(hexc("B5612A"))[:3]); g.add_color_stop_rgb(1, *rgb(hexc("F0B565"))[:3])
    cr.set_source(g); cr.paint()
    rng = np.random.default_rng(11)
    for _ in range(60):
        cr.arc(rng.uniform(-150, 150), rng.uniform(-95, -20), rng.uniform(1.5, 3.5), 0, 2 * math.pi); fill(cr, CARD, 0.55)
    cr.restore()
    loaf(); stroke(cr, INK, 6)
    for x0, y0, x1, y1 in ((-128, -18, -58, -66), (-36, -34, 34, -84), (56, -28, 122, -62)):
        for w, c in ((22, INK), (11, hexc("F7D08C"))):
            cr.move_to(x0, y0); cr.curve_to(x0 + 20, y0 - 30, x1 - 20, y1 + 6, x1, y1); stroke(cr, c, w)
    steam(cr, 0, -120, age)


def draw_pasta(cr, age, look=None):
    plate(cr)
    pc = col(look, "color", "F6D27A")
    for k in range(9):
        rx, ry, cy, ph = 158 - k * 13, 50 - k * 3.2, 46 - k * 11, k * 0.8
        def ribbon():
            for i in range(97):
                th = ph + i / 96 * 2 * math.pi * 0.92
                x = rx * math.cos(th) + 5 * math.sin(th * 6 + k)
                y = cy + ry * math.sin(th) + 3 * math.sin(th * 4 + k)
                (cr.move_to if i == 0 else cr.line_to)(x, y)
        ribbon(); stroke(cr, INK, 17)
        ribbon(); stroke(cr, pc, 9)
    for x, y in ((-30, -50), (25, -58), (0, -40)):                 # parmesan shavings
        cr.move_to(x - 14, y); cr.line_to(x + 4, y - 9); cr.line_to(x + 16, y + 3); cr.line_to(x - 2, y + 9); cr.close_path()
        fs(cr, hexc("FFF4C9"), 3)
    cr.save(); cr.translate(60, -64); cr.rotate(-0.4)               # basil
    for sx in (1, -1):
        cr.save(); cr.scale(sx, 1)
        cr.move_to(0, 0); cr.curve_to(14, -22, 40, -22, 52, 0); cr.curve_to(40, 16, 14, 14, 0, 0); fs(cr, hexc("4FB867"), 4)
        cr.restore()
    cr.restore()
    steam(cr, 0, -100, age)


def draw_pie(cr, age, look=None):
    crust, filling = col(look, "crust", "F0B962"), col(look, "filling", "D6334A")
    ellipse(cr, 0, 56, 218, 66); fs(cr, hexc("A9C3DB"), 6)
    cr.rectangle(-218, 22, 436, 34); fill(cr, hexc("A9C3DB"))
    cr.move_to(-218, 22); cr.line_to(-218, 56); cr.move_to(218, 22); cr.line_to(218, 56); stroke(cr, INK, 6)
    ellipse(cr, 0, 20, 218, 66); fs(cr, crust, 6)
    ellipse(cr, 0, 16, 178, 52); fs(cr, filling, 5)
    if (look or {}).get("lattice", True):
        cr.save(); ellipse(cr, 0, 16, 178, 52); cr.clip()
        for i in range(-3, 4):
            for w, c in ((24, INK), (15, crust)):
                cr.move_to(i * 62 - 10, -50); cr.line_to(i * 62 + 10, 80); stroke(cr, c, w)
        for j in (-1, 0, 1):
            for w, c in ((22, INK), (13, crust)):
                cr.move_to(-200, 16 + j * 30); cr.line_to(200, 16 + j * 30); stroke(cr, c, w)
        cr.restore()
    else:
        ellipse(cr, 0, 12, 182, 54); fs(cr, crust, 5)
        for a_ in (-0.6, 0, 0.6):
            cr.move_to(math.sin(a_) * 30, 0); cr.line_to(math.sin(a_) * 60, 24 * math.cos(a_)); stroke(cr, INK, 5)
    for i in range(40):
        th = 2 * math.pi * i / 40
        cr.arc(200 * math.cos(th), 19 + 60 * math.sin(th), 14, 0, 2 * math.pi); fs(cr, crust, 4)
    steam(cr, 0, -50, age)


def draw_cookie(cr, age, look=None):
    plate(cr)
    cc = col(look, "color", "DFA052"); chips = (look or {}).get("chips", True)
    rng = np.random.default_rng(5)
    for x, y, r, ph in ((92, -22, 100, 1.0), (-52, 14, 128, 2.0)):
        def shape(dy):
            cr.save(); cr.translate(x, y + dy); cr.scale(1, 0.6); blob(cr, 0, 0, r, ph * 3, 2.2); cr.restore()
        shape(16); fs(cr, mix(cc, INK, 0.25), 6)
        shape(0); fs(cr, cc, 6)
        for _ in range(4):                                          # cracks
            a0 = rng.uniform(0, 6.28); rr = rng.uniform(0.2, 0.6) * r
            cr.move_to(x + rr * math.cos(a0), y + 0.6 * rr * math.sin(a0))
            cr.line_to(x + (rr + 26) * math.cos(a0 + 0.2), y + 0.6 * (rr + 26) * math.sin(a0 + 0.2))
            stroke(cr, mix(cc, INK, 0.3), 4)
        if chips:
            for _ in range(7):
                a0 = rng.uniform(0, 6.28); rr = rng.uniform(0, 0.75) * r
                cx_, cy_ = x + rr * math.cos(a0), y + 0.6 * rr * math.sin(a0)
                cr.save(); cr.translate(cx_, cy_); cr.scale(1, 0.75); blob(cr, 0, 0, 12, a0, 3); cr.restore()
                fs(cr, hexc("4A2A1C"), 3)


def draw_cake(cr, age, look=None):
    plate(cr)
    sponge = col(look, "sponge", "F3CF8E"); glaze = col(look, "glaze", "5A3020")
    filling = col(look, "filling", "FFF4DE"); top_y, bot_y, rx, ry = -64, 58, 165, 42
    def body():
        cr.move_to(-rx, top_y); cr.line_to(-rx, bot_y)
        cr.save(); cr.translate(0, bot_y); cr.scale(rx, ry); cr.arc_negative(0, 0, 1, math.pi, 0); cr.restore()
        cr.line_to(rx, top_y); cr.close_path()
    body(); fill(cr, sponge)
    cr.save(); body(); cr.clip()
    for y in (-14, 30):
        cr.rectangle(-rx, y, 2 * rx, 12); fill(cr, filling)
        cr.move_to(-rx, y); cr.line_to(rx, y); cr.move_to(-rx, y + 12); cr.line_to(rx, y + 12); stroke(cr, INK, 3, 0.35)
    cr.restore()
    body(); stroke(cr, INK, 6)
    ellipse(cr, 0, top_y, rx, ry); fs(cr, glaze, 6)
    if (look or {}).get("drip", True):
        rng = np.random.default_rng(2)
        for i in range(11):
            th = math.pi * (0.06 + 0.88 * i / 10)
            x = rx * math.cos(th) * 0.98; y = top_y + ry * math.sin(th)
            ln = rng.uniform(18, 70) * ease((age - 0.2 - i * 0.03) / 0.9)
            if ln > 3:
                for w, c in ((26, INK), (15, glaze)):
                    cr.move_to(x, y); cr.line_to(x, y + ln); stroke(cr, c, w)
        ellipse(cr, 0, top_y + 2, rx - 4, ry - 4); fill(cr, glaze)
    cr.arc(-60, top_y - 18, 9, math.pi * 1.1, math.pi * 1.6); stroke(cr, CARD, 6, 0.5)
    for x, y in ((-30, -78), (14, -84), (50, -74)):                 # raspberries
        for k in range(6):
            cr.arc(x + 7 * math.cos(k), y + 6 * math.sin(k), 8, 0, 2 * math.pi); fs(cr, hexc("E8345A"), 3)


def draw_cupcake(cr, age, look=None):
    style = (look or {}).get("style", "frosted")
    liner = col(look, "liner", "FF8FB1")
    cr.move_to(-112, -6); cr.line_to(112, -6); cr.line_to(86, 108); cr.line_to(-86, 108); cr.close_path(); fs(cr, liner, 6)
    for i in range(-3, 4):
        cr.move_to(i * 30, 0); cr.line_to(i * 23, 102); stroke(cr, mix(liner, INK, 0.25), 4)
    if style == "muffin":
        top = col(look, "top", "E9A54F")
        cr.save(); cr.translate(0, -40); cr.scale(1.0, 0.62); blob(cr, 0, 0, 140, 1.0, 1.8); cr.restore(); fs(cr, top, 6)
        for x, y in ((-60, -50), (20, -70), (70, -36), (-10, -24)):
            cr.arc(x, y, 12, 0, 2 * math.pi); fs(cr, hexc("5965E8"), 3)
        return
    fr = col(look, "frosting", "6B3B26")
    ellipse(cr, 0, -6, 118, 24); fs(cr, col(look, "sponge", "F3CF8E"), 5)
    wob = 0.02 * math.sin(age * 3)
    for (y, rx, ry) in ((-26, 128, 44), (-74, 98, 38), (-114, 66, 30)):
        ellipse(cr, 0, y, rx * (1 + wob), ry); fs(cr, fr, 6)
        cr.arc(-rx * 0.45, y - ry * 0.2, ry * 0.5, math.pi * 1.1, math.pi * 1.6); stroke(cr, CARD, 6, 0.4)
    cr.move_to(-30, -130); cr.curve_to(-10, -170, 20, -165, 14, -150); cr.curve_to(10, -140, 20, -132, 30, -130); fs(cr, fr, 6)
    cr.move_to(4, -178); cr.curve_to(10, -205, 28, -214, 40, -216); stroke(cr, hexc("3C8A3E"), 5)
    cr.arc(0, -172, 22, 0, 2 * math.pi); fs(cr, hexc("E8344A"), 5)
    cr.arc(-7, -179, 6, 0, 2 * math.pi); fill(cr, CARD, 0.7)


def draw_truffle(cr, age, look=None):
    plate(cr)
    c = col(look, "color", "5A3423"); dr = col(look, "drizzle", "F5E6D0")
    rng = np.random.default_rng(4)
    for i, (x, y) in enumerate(((-82, 34), (82, 34), (0, -48))):
        yy = y + (3 * math.sin(age * 3 + i) if i == 2 else 0)
        cr.arc(x, yy, 66, 0, 2 * math.pi); fs(cr, c, 6)
        for _ in range(26):
            a0 = rng.uniform(0, 6.28); rr = rng.uniform(0, 58)
            cr.arc(x + rr * math.cos(a0), yy + rr * math.sin(a0), 2.4, 0, 2 * math.pi); fill(cr, mix(c, INK, 0.5), 0.6)
        cr.arc(x - 24, yy - 24, 22, math.pi * 1.0, math.pi * 1.55); stroke(cr, CARD, 7, 0.35)
        if i == 2:
            cr.move_to(x - 50, yy - 20)
            for k in range(7): cr.line_to(x - 50 + k * 16, yy - 20 + (14 if k % 2 else -8))
            stroke(cr, INK, 11); cr.move_to(x - 50, yy - 20)
            for k in range(7): cr.line_to(x - 50 + k * 16, yy - 20 + (14 if k % 2 else -8))
            stroke(cr, dr, 5)


def draw_ramekin(cr, age, look=None):
    plate(cr)
    def body():
        cr.move_to(-150, -24); cr.line_to(-150, 66)
        cr.save(); cr.translate(0, 66); cr.scale(150, 36); cr.arc_negative(0, 0, 1, math.pi, 0); cr.restore()
        cr.line_to(150, -24); cr.close_path()
    body(); fs(cr, CARD, 6)
    cr.save(); body(); cr.clip()
    for i in range(-6, 7):
        cr.move_to(i * 24, -20); cr.line_to(i * 24, 110); stroke(cr, LINE, 4)
    cr.restore()
    ellipse(cr, 0, -24, 150, 38); fs(cr, CARD, 6)
    top = col(look, "fill", "F7D98B")
    if (look or {}).get("brulee", False):
        ellipse(cr, 0, -22, 130, 30); fs(cr, hexc("D58A2E"), 4)
        rng = np.random.default_rng(8)
        for _ in range(14):
            ellipse(cr, rng.uniform(-100, 100), -22 + rng.uniform(-18, 18), rng.uniform(6, 16), rng.uniform(3, 6)); fill(cr, hexc("A8601C"), 0.7)
        k = ease((age - 1.0) / 0.4)
        if k > 0:                                                   # the spoon crack
            for dx, dy in ((40, -8), (-30, 12), (10, 18), (-20, -16)):
                cr.move_to(20, -24); cr.line_to(20 + dx * k, -24 + dy * k); stroke(cr, hexc("6E3A10"), 3.5)
    else:
        ellipse(cr, 0, -22, 130, 30); fs(cr, top, 4)
    for k in range(6):                                              # raspberry
        cr.arc(84 + 8 * math.cos(k), -36 + 7 * math.sin(k), 9, 0, 2 * math.pi); fs(cr, hexc("E8345A"), 3)


def draw_flan(cr, age, look=None):
    plate(cr)
    caramel = col(look, "caramel", "B85A1A"); body_c = col(look, "fill", "F6D47E")
    cr.save(); cr.translate(0, 84); cr.scale(205, 34); blob(cr, 0, 0, 1, 1.0, 1.5); cr.restore(); fill(cr, caramel, 0.9)
    w = 1 + 0.025 * math.sin(age * 7) * math.exp(-0.6 * (age % 3))
    cr.save(); cr.scale(w, 1)
    def body():
        cr.move_to(-108, -64); cr.line_to(-150, 52)
        cr.save(); cr.translate(0, 52); cr.scale(150, 34); cr.arc_negative(0, 0, 1, math.pi, 0); cr.restore()
        cr.line_to(108, -64); cr.close_path()
    body(); cr.restore(); fs(cr, body_c, 6)
    cr.save(); cr.scale(w, 1); ellipse(cr, 0, -64, 108, 26); cr.restore(); fs(cr, caramel, 6)
    for x, ln in ((-80, 46), (-20, 70), (50, 38), (95, 58)):
        for wd, c in ((22, INK), (12, caramel)):
            cr.move_to(x * w, -56 + abs(x) * 0.05); cr.line_to(x * w * (1 + ln / 600), -56 + ln); stroke(cr, c, wd)
    cr.arc(-40, -70, 10, math.pi * 1.1, math.pi * 1.7); stroke(cr, CARD, 5, 0.5)


def draw_bowl(cr, age, look=None):
    lk = look or {}
    fillc = col(lk, "fill", "F2E3C4"); bowl = col(lk, "bowl", "FFFFFF"); band = col(lk, "band", "5AAEF2")
    garnish = lk.get("garnish", "herbs")
    def body():
        cr.move_to(-205, -14); cr.curve_to(-198, 92, -96, 122, 0, 122); cr.curve_to(96, 122, 198, 92, 205, -14); cr.close_path()
    ellipse(cr, 0, 122, 72, 14); fs(cr, bowl, 5)
    body(); fs(cr, bowl, 6)
    cr.save(); body(); cr.clip()
    cr.move_to(-210, 30); cr.curve_to(-60, 60, 60, 60, 210, 30); stroke(cr, band, 16)
    cr.restore()
    body(); stroke(cr, INK, 6)
    ellipse(cr, 0, -14, 205, 50); fs(cr, bowl, 6)
    ellipse(cr, 0, -12, 182, 38); fs(cr, fillc, 4)
    rng = np.random.default_rng(9)
    if garnish == "grains":
        for _ in range(70):
            a0 = rng.uniform(0, 6.28); rr = math.sqrt(rng.uniform(0, 1))
            cr.save(); cr.translate(165 * rr * math.cos(a0), -12 + 32 * rr * math.sin(a0)); cr.rotate(rng.uniform(0, 3))
            ellipse(cr, 0, 0, 9, 4); cr.restore(); fs(cr, hexc("FFFFFF"), 2)
    elif garnish == "swirl":
        cr.move_to(0, -12)
        for i in range(60):
            th = i / 60 * 4 * math.pi; rr = 4 + i * 1.7
            cr.line_to(rr * math.cos(th + age * 0.4), -12 + 0.24 * rr * math.sin(th + age * 0.4))
        stroke(cr, CARD, 6, 0.9)
    elif garnish == "herbs":
        for _ in range(9):
            a0 = rng.uniform(0, 6.28); rr = rng.uniform(0.1, 0.8)
            cr.save(); cr.translate(165 * rr * math.cos(a0), -12 + 32 * rr * math.sin(a0)); cr.rotate(rng.uniform(0, 3))
            ellipse(cr, 0, 0, 10, 5); cr.restore(); fs(cr, hexc("4FB867"), 3)
    elif garnish == "pepper":
        for _ in range(30):
            a0 = rng.uniform(0, 6.28); rr = rng.uniform(0, 0.85)
            cr.arc(165 * rr * math.cos(a0), -12 + 32 * rr * math.sin(a0), 2.5, 0, 2 * math.pi); fill(cr, INK)
    if lk.get("steam", True): steam(cr, 0, -70, age)


def draw_jar(cr, age, look=None):
    lk = look or {}; fillc = col(lk, "fill", "D8E8A8"); contents = lk.get("contents", "pickles")
    lid = col(lk, "lid", "F2542D")
    rrect(cr, -112, -128, 224, 240, 44); fs(cr, hexc("EAF4FB"), 6)
    cr.save(); rrect(cr, -112, -128, 224, 240, 44); cr.clip()
    lvl = -70
    cr.move_to(-120, lvl)
    for i in range(25): cr.line_to(-120 + i * 10, lvl + 4 * math.sin(i * 0.8 + age * 2))
    cr.line_to(120, 120); cr.line_to(-120, 120); cr.close_path(); fill(cr, fillc, 0.85)
    if contents == "pickles":
        for i, (x, y, rot) in enumerate(((-50, 20, 0.3), (40, -10, -0.4), (-10, 70, 0.1), (60, 70, -0.2), (-60, 85, 0.5))):
            cr.save(); cr.translate(x, y + 2 * math.sin(age * 2 + i)); cr.rotate(rot); ellipse(cr, 0, 0, 22, 54); cr.restore()
            fs(cr, hexc("6DA34D"), 4)
    elif contents == "jam":
        rng = np.random.default_rng(1)
        for _ in range(30):
            cr.arc(rng.uniform(-90, 90), rng.uniform(-50, 100), 2.5, 0, 2 * math.pi); fill(cr, INK, 0.4)
    for k in range(4):                                              # bubbles
        p = ((age * 0.5 + k / 4) % 1)
        cr.arc(-70 + k * 45, 100 - p * 160, 6, 0, 2 * math.pi); stroke(cr, CARD, 3, 0.8)
    cr.restore()
    rrect(cr, -112, -128, 224, 240, 44); stroke(cr, INK, 6)
    cr.move_to(-80, -90); cr.line_to(-80, 60); stroke(cr, CARD, 10, 0.7)
    rrect(cr, -98, -160, 196, 40, 12); fs(cr, lid, 6)


def draw_glass(cr, age, look=None):
    lk = look or {}; liquid = col(lk, "fill", "F7C873"); shape = lk.get("shape", "tumbler")
    if shape == "coupe":
        def bowl():
            cr.move_to(-150, -120); cr.curve_to(-140, -20, 140, -20, 150, -120); cr.close_path()
        cr.save(); bowl(); cr.clip()
        cr.rectangle(-160, -104 + 3 * math.sin(age * 2), 320, 120); fill(cr, liquid)
        cr.restore()
        bowl(); stroke(cr, INK, 6)
        cr.move_to(0, -45); cr.line_to(0, 90); stroke(cr, INK, 12); cr.move_to(0, -45); cr.line_to(0, 90); stroke(cr, hexc("EAF4FB"), 4)
        ellipse(cr, 0, 94, 80, 16); fs(cr, hexc("EAF4FB"), 5)
        ellipse(cr, 0, -120, 150, 16); stroke(cr, INK, 5)
    else:
        def body():
            cr.move_to(-100, -150); cr.line_to(100, -150); cr.line_to(82, 104); cr.line_to(-82, 104); cr.close_path()
        body(); fill(cr, hexc("EAF4FB"), 0.9)
        cr.save(); body(); cr.clip()
        cr.move_to(-110, -96)
        for i in range(23): cr.line_to(-110 + i * 10, -96 + 4 * math.sin(i * 0.7 + age * 2.5))
        cr.line_to(110, 110); cr.line_to(-110, 110); cr.close_path(); fill(cr, liquid)
        for i, (x, y, rot) in enumerate(((-40, -70, 0.3), (30, -40, -0.2), (-10, 0, 0.5))):
            cr.save(); cr.translate(x, y + 3 * math.sin(age * 2 + i)); cr.rotate(rot); rrect(cr, -26, -26, 52, 52, 10); cr.restore()
            cr.set_source_rgba(1, 1, 1, 0.55); cr.fill_preserve(); stroke(cr, INK, 3, 0.6)
        cr.restore()
        body(); stroke(cr, INK, 6)
        cr.move_to(-70, -120); cr.line_to(-58, 70); stroke(cr, CARD, 9, 0.7)
    if lk.get("garnish", "lemon") == "lemon":
        cx, cy = (120, -136) if shape != "coupe" else (128, -128)
        cr.arc(cx, cy, 40, 0, 2 * math.pi); fs(cr, hexc("FFE45C"), 6)
        cr.arc(cx, cy, 30, 0, 2 * math.pi); fill(cr, hexc("FFF3A8"))
        for k in range(6):
            cr.move_to(cx, cy); cr.line_to(cx + 30 * math.cos(k * 1.047), cy + 30 * math.sin(k * 1.047)); stroke(cr, hexc("F2C94C"), 3)


def draw_meringue(cr, age, look=None):
    plate(cr)
    c = col(look, "color", "FFFDF8")
    for i, (x, y, s) in enumerate(((-100, 40, 0.9), (100, 40, 0.9), (0, 10, 1.1))):
        cr.save(); cr.translate(x, y); cr.scale(s, s)
        for k in range(4):
            ry = 26 - 4 * k; rx = 76 - 18 * k
            cr.save(); cr.translate(0, -k * 30); cr.scale(rx, ry); blob(cr, 0, 0, 1, k + i, 1.2); cr.restore()
            fs(cr, c, 5 / s)
            for j in (-2, -1, 1, 2):
                cr.move_to(j * rx * 0.3, -k * 30 + ry * 0.6); cr.line_to(j * rx * 0.22, -k * 30 - ry * 0.4); stroke(cr, LINE, 3)
        cr.move_to(0, -100); cr.curve_to(4, -130, 22, -140, 30 + 3 * math.sin(age * 2 + i), -132); stroke(cr, INK, 13)
        cr.move_to(0, -100); cr.curve_to(4, -130, 22, -140, 30 + 3 * math.sin(age * 2 + i), -132); stroke(cr, hexc("F7E3B5"), 6)
        cr.restore()


def draw_sausage(cr, age, look=None):
    board(cr)
    c = col(look, "color", "C8553D")
    for i, (y, bend) in enumerate(((-70, 24), (-10, 30), (46, 20))):
        def link():
            cr.move_to(-170, y + bend); cr.curve_to(-80, y - bend, 80, y - bend, 170, y + bend)
        link(); stroke(cr, INK, 64); link(); stroke(cr, c, 52)
        cr.move_to(-120, y + 2); cr.curve_to(-60, y - bend + 6, 20, y - bend + 6, 60, y - bend * 0.6); stroke(cr, CARD, 7, 0.35)
        for k in range(4):
            x = -90 + k * 55
            cr.move_to(x, y - bend * 0.75 - 14); cr.line_to(x + 14, y - bend * 0.75 + 14); stroke(cr, hexc("6B2418"), 6, 0.8)
    steam(cr, 0, -130, age)


ILLUS = {"crepe": draw_crepe, "popover": draw_popover, "pancake": draw_pancake, "bread": draw_bread,
         "pasta": draw_pasta, "pie": draw_pie, "cookie": draw_cookie, "cake": draw_cake, "cupcake": draw_cupcake,
         "truffle": draw_truffle, "ramekin": draw_ramekin, "flan": draw_flan, "bowl": draw_bowl, "jar": draw_jar,
         "glass": draw_glass, "meringue": draw_meringue, "sausage": draw_sausage}
HOTSPOT = {"crepe": (-10, -40), "popover": (10, -120), "pancake": (-20, -70), "bread": (0, -40), "pasta": (-40, 10),
           "pie": (60, 16), "cookie": (-60, 14), "cake": (-80, 10), "cupcake": (0, -70), "truffle": (0, -48),
           "ramekin": (-30, -22), "flan": (-40, 0), "bowl": (-40, -12), "jar": (0, 30), "glass": (0, -20),
           "meringue": (0, -30), "sausage": (-40, -12)}


def illus_key(dish):
    return dish.get("illustration") or dish["name"].lower().replace("ê", "e").replace("é", "e")


def draw_dish(cr, dish, age, x, y, scale):
    cr.save(); cr.translate(x, y); cr.scale(scale, scale)
    ILLUS.get(illus_key(dish), draw_bowl)(cr, age, dish.get("look"))
    cr.restore()


# ------------------------------------------------------------ ingredient icons
ICON_FORM = {"flour": "sack", "rice": "sack", "cornmeal": "sack", "semolina": "sack", "oats": "sack", "cocoa": "sack",
             "almond flour": "sack", "breadcrumbs": "sack",
             "milk": "carton", "cream": "carton", "stock": "carton", "buttermilk": "carton",
             "oil": "bottle", "vinegar": "bottle", "wine": "bottle", "soy sauce": "bottle",
             "butter": "block", "sugar": "cube", "brown sugar": "cube", "yeast": "cube",
             "egg": "egg", "yolk": "yolk", "white": "white", "egg white": "white", "egg yolk": "yolk",
             "water": "drop", "lemon": "drop", "lemon juice": "drop", "juice": "drop", "espresso": "drop",
             "salt": "shaker", "baking powder": "shaker", "baking soda": "shaker", "pepper": "shaker",
             "chocolate": "bar", "meat": "meat", "fat": "fat", "cheese": "cheese", "parmesan": "cheese",
             "honey": "jar", "mustard": "jar", "jam": "jar", "spirit": "bottle", "syrup": "jar"}


def icon(cr, ing, x, y, s, a=1.0):
    """Little sticker icon, s = box size in px. The form depends on the ingredient (ICON_FORM)."""
    form = ICON_FORM.get(ing, "dot"); c = ING.get(ing, MUTED)
    def body():
        cr.save(); cr.translate(x, y); cr.scale(s / 100, s / 100)
        if form == "sack":
            cr.move_to(-30, -28); cr.curve_to(-44, 10, -42, 40, -34, 44); cr.line_to(34, 44)
            cr.curve_to(42, 40, 44, 10, 30, -28); cr.close_path(); fs(cr, c, 6)
            cr.move_to(-30, -28); cr.line_to(-22, -44); cr.line_to(0, -36); cr.line_to(22, -44); cr.line_to(30, -28)
            cr.close_path(); fs(cr, c, 6)
            cr.move_to(-30, -28); cr.line_to(30, -28); stroke(cr, INK, 6)
            m = mix(c, INK, 0.3)
            cr.move_to(0, 32); cr.line_to(0, -4); stroke(cr, m, 5)
            for k in range(3):
                for sgn in (-1, 1): ellipse(cr, sgn * 7, 20 - k * 11, 6, 3.5); fill(cr, m)
        elif form == "carton":
            def box():
                cr.move_to(-26, -14); cr.line_to(0, -40); cr.line_to(26, -14); cr.line_to(26, 46); cr.line_to(-26, 46); cr.close_path()
            box(); fill(cr, CARD); cr.rectangle(-26, 4, 52, 22); fill(cr, c)
            box(); stroke(cr, INK, 6); cr.move_to(-26, -14); cr.line_to(26, -14); stroke(cr, INK, 5)
            rrect(cr, -6, -50, 12, 12, 3); fs(cr, c, 5)
        elif form == "bottle":
            cr.move_to(-10, -46); cr.line_to(10, -46); cr.line_to(10, -22); cr.curve_to(28, -14, 28, -6, 28, 0)
            cr.line_to(28, 46); cr.line_to(-28, 46); cr.line_to(-28, 0); cr.curve_to(-28, -6, -28, -14, -10, -22); cr.close_path()
            fs(cr, c, 6); rrect(cr, -12, -54, 24, 12, 3); fs(cr, INK, 2)
            cr.move_to(-16, 4); cr.line_to(-16, 34); stroke(cr, CARD, 5, 0.6)
        elif form in ("block", "cube"):
            top, front, side = mix(c, (255, 255, 255), 0.45), c, mix(c, INK, 0.15)
            if form == "cube": top, front, side = (255, 255, 255), mix(c, (255, 255, 255), 0.5), c
            cr.move_to(-40, -6); cr.line_to(-8, -26); cr.line_to(40, -12); cr.line_to(8, 8); cr.close_path(); fs(cr, top, 6)
            cr.move_to(-40, -6); cr.line_to(8, 8); cr.line_to(8, 34); cr.line_to(-40, 20); cr.close_path(); fs(cr, front, 6)
            cr.move_to(8, 8); cr.line_to(40, -12); cr.line_to(40, 14); cr.line_to(8, 34); cr.close_path(); fs(cr, side, 6)
        elif form == "egg":
            blob(cr, 0, 4, 42, 2.0, 2.6); fs(cr, CARD, 6)
            cr.arc(4, 2, 19, 0, 2 * math.pi); fs(cr, c, 6); cr.arc(-2, -4, 5, 0, 2 * math.pi); fill(cr, CARD, 0.9)
        elif form == "yolk":
            cr.arc(0, 4, 30, 0, 2 * math.pi); fs(cr, c, 6); cr.arc(-9, -6, 8, 0, 2 * math.pi); fill(cr, CARD, 0.8)
        elif form == "white":
            blob(cr, 0, 4, 40, 1.0, 2.6); fs(cr, CARD, 6); cr.arc(-12, -8, 7, 0, 2 * math.pi); fill(cr, LINE)
        elif form == "drop":
            cr.move_to(0, -44); cr.curve_to(10, -20, 34, 4, 34, 18); cr.curve_to(34, 38, 18, 46, 0, 46)
            cr.curve_to(-18, 46, -34, 38, -34, 18); cr.curve_to(-34, 4, -10, -20, 0, -44); cr.close_path(); fs(cr, c, 6)
            cr.arc(-12, 18, 8, math.pi * 0.9, math.pi * 1.5); stroke(cr, CARD, 5, 0.8)
        elif form == "shaker":
            rrect(cr, -26, -14, 52, 60, 14); fs(cr, c, 6)
            cr.move_to(-26, -14); cr.curve_to(-26, -46, 26, -46, 26, -14); cr.close_path(); fs(cr, hexc("C9D2E3"), 6)
            for dx in (-10, 0, 10): cr.arc(dx, -28, 3, 0, 2 * math.pi); fill(cr, INK)
        elif form == "bar":
            rrect(cr, -34, -44, 68, 90, 8); fs(cr, c, 6)
            for gx in (-17, 17):
                for gy in (-25, 0, 25): rrect(cr, gx - 13, gy - 10, 26, 20, 4); stroke(cr, mix(c, INK, 0.45), 4)
            cr.move_to(-34, 18); cr.line_to(34, -6); cr.line_to(34, 46); cr.line_to(-34, 46); cr.close_path(); fs(cr, hexc("D9DEE8"), 5)
        elif form == "meat":
            blob(cr, 0, 0, 40, 0.5, 2.5); fs(cr, c, 6)
            cr.move_to(-20, -10); cr.curve_to(0, -24, 20, 0, 6, 16); stroke(cr, CARD, 6, 0.8)
        elif form == "fat":
            rrect(cr, -36, -26, 72, 54, 14); fs(cr, c, 6)
        elif form == "cheese":
            cr.move_to(-40, 30); cr.line_to(40, 30); cr.line_to(40, -2); cr.line_to(-40, -30); cr.close_path(); fs(cr, c, 6)
            for hx, hy in ((14, 12), (-12, 14), (24, -4)): cr.arc(hx, hy, 6, 0, 2 * math.pi); fill(cr, mix(c, INK, 0.25))
        elif form == "jar":
            rrect(cr, -30, -26, 60, 72, 14); fs(cr, c, 6); rrect(cr, -26, -44, 52, 18, 5); fs(cr, ACCENT, 5)
        else:
            cr.arc(0, 0, 36, 0, 2 * math.pi); fs(cr, c, 6)
        cr.restore()
    group(cr, a, body)


# ---------------------------------------------------------------- molecules --
# ---------------------------------------------------------------- molecules --
def h2o(cr, x, y, rot, s=1.0):
    for sg in (-1, 1):
        th = rot + sg * math.radians(52)
        hx, hy = x + 23 * s * math.cos(th), y + 23 * s * math.sin(th)
        cr.move_to(x, y); cr.line_to(hx, hy); stroke(cr, INK, 4 * s)
        cr.arc(hx, hy, 9 * s, 0, 2 * math.pi); fs(cr, HY, 3 * s)
    cr.arc(x, y, 14 * s, 0, 2 * math.pi); fs(cr, OX, 3 * s)


def co2(cr, x, y, rot, s=1.0):
    dx, dy = math.cos(rot), math.sin(rot); nx, ny = -dy, dx
    for sg in (-1, 1):
        for o in (-3.5, 3.5):
            cr.move_to(x + nx * o * s, y + ny * o * s); cr.line_to(x + sg * 25 * s * dx + nx * o * s, y + sg * 25 * s * dy + ny * o * s)
            stroke(cr, INK, 3 * s)
    for sg in (-1, 1):
        cr.arc(x + sg * 25 * s * dx, y + sg * 25 * s * dy, 11 * s, 0, 2 * math.pi); fs(cr, OX, 3 * s)
    cr.arc(x, y, 12 * s, 0, 2 * math.pi); fs(cr, CA, 3 * s)


def mol_protein(cr, age, r):
    cr.set_source_rgba(*rgb(hexc("FFF6E0"))); cr.paint()
    u = smooth((age - 0.45) / 1.4)
    centers = [(-52, -58), (56, -44), (-48, 46), (58, 62)]
    chains = []
    for j in range(4):
        cx, cy = centers[j]; pts = []
        for i in range(11):
            phi = i * 1.05 + j * 1.3
            rad = 16 + 9 * math.sin(i * 1.7 + j)
            coil = (cx + rad * math.cos(phi), cy + rad * math.sin(phi))
            sx = -108 + i * 21.6
            line = (sx, -66 + j * 44 + 7 * math.sin(sx / 16 + j + age * 2.2))
            jig = 1.6 * math.sin(age * 9 + i * 2 + j)
            pts.append((lerp(coil[0], line[0], u) + jig, lerp(coil[1], line[1], u) - jig))
        chains.append(pts)
    la = ease((age - 1.75) / 0.5)
    if la > 0:
        for j in range(3):
            for i in range(11):
                if (i + j) % 3 == 0:
                    (x0, y0), (x1, y1) = chains[j][i], chains[j + 1][i]
                    cr.move_to(x0, y0); cr.line_to(lerp(x0, x1, la), lerp(y0, y1, la)); stroke(cr, ACCENT, 5, 0.9)
    for pts in chains:
        cr.move_to(*pts[0])
        for p in pts[1:]: cr.line_to(*p)
        stroke(cr, INK, 4)
        for p in pts: cr.arc(p[0], p[1], 8, 0, 2 * math.pi); fs(cr, ING["egg"], 3)


def mol_steam(cr, age, r):
    cr.set_source_rgba(*rgb(hexc("F3F9FF"))); cr.paint()
    cr.move_to(-r, r)
    for i in range(41):
        x = -r + 2 * r * i / 40
        cr.line_to(x, 62 + 6 * math.sin(x / 22 + age * 3))
    cr.line_to(r, r); cr.close_path(); fill(cr, hexc("CDE6FB"))
    T = 2.4
    for i in range(13):
        p = ((age + i / 13 * T) % T) / T
        y = 120 - p * 270
        x = -110 + (i * 71) % 220 + 14 * math.sin(age * 2 + i) * p
        jig = 1 if y > 60 else 0
        h2o(cr, x + jig * math.sin(age * 12 + i), y, age * (1.5 + i % 3) * (0.3 + p) + i, 0.95)
    for k in range(3):                                         # heat lines below
        x = -50 + k * 50
        cr.move_to(x, 140); cr.line_to(x, 120); stroke(cr, ACCENT, 4, 0.5 + 0.4 * math.sin(age * 6 + k))


def mol_co2(cr, age, r):
    cr.set_source_rgba(*rgb(hexc("F9E6BE"))); cr.paint()
    T = 2.8
    for i in range(8):
        p = ((age + i / 8 * T) % T) / T
        y = 130 - p * 280
        x = -95 + (i * 67) % 190 + 10 * math.sin(age * 1.6 + i)
        br = 14 + 24 * p
        cr.arc(x, y, br, 0, 2 * math.pi)
        cr.set_source_rgba(1, 1, 1, 0.55); cr.fill_preserve(); stroke(cr, INK, 3, 0.8)
        co2(cr, x, y, age * 0.9 + i, 0.55 + 0.35 * p)
    for k in range(5):                                         # baking-powder grains
        x = -80 + k * 40
        rrect(cr, x - 6, 118 + 4 * math.sin(k), 12, 12, 3); fs(cr, CARD, 3)


def h2o_small(cr, x, y, rot, s=0.55): h2o(cr, x, y, rot, s)


def mol_gluten(cr, age, r):
    """Glutenin chains go from tangled to aligned (kneading), then a gas bubble stretches them."""
    cr.set_source_rgba(*rgb(hexc("F8EEDC"))); cr.paint()
    u = smooth((age - 0.3) / 1.2)
    bub = 52 * ease((age - 1.3) / 1.3) + (3 * math.sin(age * 3) if age > 1.3 else 0)
    bx, by = 0, 6
    for j in range(7):
        y0 = -114 + j * 38
        pts = []
        for i in range(17):
            x = -150 + i * 18.75
            tang = (x * 0.55 + 26 * math.sin(i * 1.3 + j * 2.1), y0 + 30 * math.sin(i * 0.9 + j * 1.7))
            alig = (x + 5 * math.sin(age * 2 + j), y0 + 6 * math.sin(x / 24 + age * 2 + j))
            px, py = lerp(tang[0], alig[0], u), lerp(tang[1], alig[1], u)
            dx, dy = px - bx, py - by; d = math.hypot(dx, dy) or 1
            if bub > 0 and d < bub + 24:
                push = (bub + 24 - d); px += dx / d * push; py += dy / d * push
            pts.append((px, py))
        cr.move_to(*pts[0])
        for p in pts[1:]: cr.line_to(*p)
        stroke(cr, INK, 4)
        for k, p in enumerate(pts):
            cr.arc(p[0], p[1], 6.5 if k % 2 else 5, 0, 2 * math.pi); fs(cr, hexc("E4B866") if k % 2 else hexc("F3D9A0"), 2.5)
    if bub > 6:
        cr.arc(bx, by, bub, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.7); cr.fill_preserve(); stroke(cr, INK, 3)
        if bub > 26: co2(cr, bx, by, age * 0.8, 0.7)


def mol_fat_coating(cr, age, r):
    """Butter coats flour particles, so water can't reach them and little gluten forms."""
    cr.set_source_rgba(*rgb(hexc("FFF7E4"))); cr.paint()
    c = ease((age - 0.3) / 0.9)
    parts = [(-70, -60), (40, -80), (100, 10), (-20, 10), (-100, 50), (30, 90), (110, 100), (-60, -130)]
    for i, (x, y) in enumerate(parts):
        jx = 2 * math.sin(age * 3 + i)
        if c > 0:
            cr.arc(x + jx, y, 24 + 13 * c, 0, 2 * math.pi); fs(cr, ING["butter"], 3, 0.95)
        cr.arc(x + jx, y, 24, 0, 2 * math.pi); fs(cr, ING["flour"], 3)
    for k in range(7):                                              # water droplets bounce off
        p = ((age * 0.35 + k / 7) % 1)
        x = -150 + p * 300; y = -120 + k * 38 + 18 * math.sin(p * 9 + k)
        cr.arc(x, y, 8, 0, 2 * math.pi); fs(cr, ING["water"], 2.5)


def mol_starch(cr, age, r):
    """Starch granules drink up water, swell, and leak chains that thicken the liquid."""
    cr.set_source_rgba(*rgb(hexc("EEF6FF"))); cr.paint()
    s = 1 + 0.65 * smooth((age - 0.3) / 1.4)
    leak = ease((age - 1.3) / 1.0)
    grans = [(-62, -58, 0.3), (58, -64, -0.4), (-70, 58, 0.8), (64, 56, 0.1), (0, 0, -0.2)]
    for i, (x, y, rot) in enumerate(grans):
        if leak > 0:
            for k in range(3):
                th = rot + k * 2.1 + i
                cr.move_to(x, y)
                for t_ in range(1, 12):
                    d = t_ * 7 * leak * 1.4
                    cr.line_to(x + d * math.cos(th) + 5 * math.sin(t_ + age * 3), y + d * math.sin(th) + 5 * math.cos(t_ + age * 3))
                stroke(cr, hexc("D2A85A"), 4, 0.9)
    for i, (x, y, rot) in enumerate(grans):
        cr.save(); cr.translate(x, y); cr.rotate(rot)
        for ring, (rx, ry) in enumerate(((30, 22), (20, 14), (10, 7))):
            ellipse(cr, 0, 0, rx * s, ry * s)
            if ring == 0: fs(cr, hexc("F7EEDA"), 3)
            else: stroke(cr, hexc("D9C7A0"), 2.5)
        cr.restore()
    for k in range(6):
        th = age * 0.9 + k * 1.05; rr = 120 - 40 * ((age * 0.5 + k / 6) % 1)
        h2o(cr, rr * math.cos(th), rr * math.sin(th), th * 2, 0.5)


def _emulsion(cr, age, n, seed, bg):
    cr.set_source_rgba(*rgb(hexc(bg))); cr.paint()
    rng = np.random.default_rng(seed)
    for i in range(n):
        x, y = rng.uniform(-120, 120), rng.uniform(-120, 120); rr = rng.uniform(12, 28)
        if math.hypot(x, y) > 135: continue
        x += 4 * math.sin(age * 1.5 + i); y += 4 * math.cos(age * 1.3 + i * 2)
        cr.arc(x, y, rr, 0, 2 * math.pi); fs(cr, ING["butter"], 3)
        cr.arc(x - rr * 0.35, y - rr * 0.35, rr * 0.3, math.pi, math.pi * 1.6); stroke(cr, CARD, 3, 0.7)
        for k in range(5):                                          # emulsifier "tadpoles" on the surface
            th = k * 1.256 + age * 0.5
            hx, hy = x + (rr + 7) * math.cos(th), y + (rr + 7) * math.sin(th)
            cr.move_to(hx, hy); cr.line_to(x + (rr - 4) * math.cos(th), y + (rr - 4) * math.sin(th)); stroke(cr, INK, 2)
            cr.arc(hx, hy, 3.5, 0, 2 * math.pi); fs(cr, ACCENT, 1.5)


def mol_emulsion(cr, age, r): _emulsion(cr, age, 22, 3, "E6F1FB")
def mol_emulsion_loose(cr, age, r): _emulsion(cr, age, 8, 5, "E6F1FB")


def mol_fat_crystals(cr, age, r):
    """Fat molecules (cocoa butter, butter) stack into an ordered crystal as they cool: it sets firm."""
    cr.set_source_rgba(*rgb(hexc("F4E8DC"))); cr.paint()
    u = smooth((age - 0.3) / 1.6)
    rng = np.random.default_rng(6)
    for gy in range(-3, 4):
        for gx in range(-3, 4):
            tx, ty = gx * 36, gy * 34
            sx, sy, sr = rng.uniform(-130, 130), rng.uniform(-130, 130), rng.uniform(0, 3.14)
            x, y, rot = lerp(sx, tx, u), lerp(sy, ty, u), lerp(sr, 0, u)
            x += (1 - u) * 6 * math.sin(age * 4 + gx); y += (1 - u) * 6 * math.cos(age * 4 + gy)
            cr.save(); cr.translate(x, y); cr.rotate(rot)
            for k in (-7, 0, 7):                                    # three fatty-acid tails
                cr.move_to(-12, k); cr.line_to(12, k)
            cr.restore(); stroke(cr, hexc("8A5A3C"), 4)
            cr.save(); cr.translate(x, y); cr.rotate(rot); rrect(cr, -16, -10, 6, 20, 3); cr.restore(); fs(cr, ING["egg"], 2)
    if u > 0.95:
        for k in range(4):
            a = 0.5 + 0.5 * math.sin(age * 5 + k)
            x, y = -90 + k * 60, -110 + (k % 2) * 220
            for th in (0, 1.047, 2.094):
                cr.move_to(x - 10 * math.cos(th), y - 10 * math.sin(th)); cr.line_to(x + 10 * math.cos(th), y + 10 * math.sin(th))
            stroke(cr, ACCENT, 3, a)


def mol_foam(cr, age, r):
    """Whisking traps air; proteins (or fat) line each bubble and hold it."""
    cr.set_source_rgba(*rgb(hexc("FFFDF6"))); cr.paint()
    bubs = [(-60, -50, 48), (52, -66, 40), (70, 34, 46), (-30, 56, 42), (-108, 26, 26), (0, -2, 24), (120, -40, 22)]
    for i, (x, y, br) in enumerate(bubs):
        g = ease((age - 0.2 - i * 0.12) / 0.8)
        if g <= 0: continue
        rr = br * g + 1.5 * math.sin(age * 3 + i)
        cr.arc(x, y, rr, 0, 2 * math.pi); fs(cr, hexc("EAF4FB"), 3)
        cr.arc(x - rr * 0.35, y - rr * 0.35, rr * 0.3, math.pi, math.pi * 1.6); stroke(cr, CARD, 4, 0.9)
        pa = ease((age - 1.0 - i * 0.1) / 0.6)
        for k in range(12):
            if k / 12 > pa: break
            th = k / 12 * 2 * math.pi + i
            cr.arc(x + (rr + 5) * math.cos(th), y + (rr + 5) * math.sin(th), 4.5, 0, 2 * math.pi); fs(cr, ING["egg"], 2)


def _sucrose(cr, x, y, rot, s=1.0):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(s, s)
    cr.move_to(-8, 0); cr.line_to(8, 0); stroke(cr, INK, 3)
    for cx, n, rr in ((-20, 6, 13), (19, 5, 12)):
        for k in range(n):
            th = k / n * 2 * math.pi + 0.5
            (cr.move_to if k == 0 else cr.line_to)(cx + rr * math.cos(th), rr * math.sin(th))
        cr.close_path(); fs(cr, ING["sugar"], 3)
    cr.restore()


def mol_sugar(cr, age, r):
    """Sugar crystals dissolve: sucrose molecules leave the crystal and mix with water."""
    cr.set_source_rgba(*rgb(hexc("EEF6FF"))); cr.paint()
    gone = int(10 * clamp((age - 0.3) / 2.5))
    for k in range(10):
        gx, gy = -70 + (k % 5) * 34, 92 + (k // 5) * 30
        if k < gone:
            p = ((age - 0.3) / 2.5 * 10 - k)
            x = gx + 40 * math.sin(p * 1.3 + k); y = gy - 70 * min(p, 3) - 20 * math.sin(age + k)
            _sucrose(cr, x, y, age * 0.6 + k, 0.8)
        else:
            rrect(cr, gx - 15, gy - 13, 30, 26, 5); fs(cr, hexc("FFFFFF"), 3)
    for k in range(6):
        th = age * 0.7 + k * 1.05
        h2o(cr, 110 * math.cos(th), -30 + 70 * math.sin(th), th, 0.55)


def mol_salt(cr, age, r):
    """Salt dissolves into ions (Na+, Cl−), each wrapped in water."""
    cr.set_source_rgba(*rgb(hexc("EEF6FF"))); cr.paint()
    NA, CL = hexc("9B8CFF"), hexc("5BD18B")
    gone = int(8 * clamp((age - 0.3) / 2.2))
    for k in range(12):
        gx, gy = -75 + (k % 6) * 30, 90 + (k // 6) * 30
        na = (k % 2) == (k // 6) % 2
        if k < gone:
            p = ((age - 0.3) / 2.2 * 8 - k)
            x = gx + 50 * math.sin(p + k); y = gy - 60 * min(p, 3.2)
            for w in range(3):
                th = age * 1.5 + w * 2.09
                h2o(cr, x + 28 * math.cos(th), y + 28 * math.sin(th), th + math.pi, 0.42)
        else:
            x, y = gx, gy
        cr.arc(x, y, 10 if na else 14, 0, 2 * math.pi); fs(cr, NA if na else CL, 3)


MOL = {"protein_net": mol_protein, "steam": mol_steam, "co2": mol_co2, "gluten": mol_gluten,
       "fat_coating": mol_fat_coating, "starch_gel": mol_starch, "emulsion": mol_emulsion,
       "emulsion_loose": mol_emulsion_loose, "fat_crystals": mol_fat_crystals, "foam": mol_foam,
       "sugar": mol_sugar, "salt": mol_salt}


def lens(cr, dish, age, cx, cy, r, src, a):
    """Magnifier: a dashed ring on the dish + a cone to a round 'zoom' view."""
    def body():
        sx, sy = src
        dx, dy = cx - sx, cy - sy; d = math.hypot(dx, dy); nx, ny = -dy / d, dx / d
        k = ease(age / 0.5)
        rr = r * k
        cr.move_to(sx + nx * 26, sy + ny * 26); cr.line_to(cx + nx * rr, cy + ny * rr)
        cr.move_to(sx - nx * 26, sy - ny * 26); cr.line_to(cx - nx * rr, cy - ny * rr)
        cr.set_dash([10, 10], -age * 30); stroke(cr, INK, 4, 0.55); cr.set_dash([])
        cr.arc(sx, sy, 26, 0, 2 * math.pi); cr.set_dash([8, 7], -age * 30); stroke(cr, INK, 4); cr.set_dash([])
        if rr < 4: return
        cr.arc(cx + 6, cy + 8, rr, 0, 2 * math.pi); fill(cr, INK, 0.12)         # soft shadow
        cr.save(); cr.arc(cx, cy, rr, 0, 2 * math.pi); cr.clip()
        cr.translate(cx, cy); cr.scale(k, k)
        MOL.get(dish.get("science", ""), mol_co2)(cr, age, r)
        cr.restore()
        cr.arc(cx, cy, rr, 0, 2 * math.pi); stroke(cr, INK, 7)
    group(cr, a, body)


def logo(cr, x, y, size, a=1.0):
    """Mark: three stacked rounded bars (a ratio) in flour / milk / egg."""
    def body():
        s = size / 120
        cr.save(); cr.translate(x, y); cr.scale(s, s)
        for col, yy, w in ((ING["flour"], 14, 100), (ING["milk"], 46, 74), (ING["egg"], 78, 48)):
            rrect(cr, 10, yy, w, 26, 13); fs(cr, col, 6)
        cr.restore()
    group(cr, a, body)


