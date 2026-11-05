#!/usr/bin/env python3
"""foods that move — bright edition.

One episode = one family of recipes. Each dish gets a cartoon illustration, a
"zoom lens" showing the molecules doing the work (proteins, steam, CO2), its
ratio as colour tiles, and a set of ingredient bars (grams per 100 g flour)
that glide from dish to dish. Hook, cheat sheet and outro frame it.
Everything is drawn in code; music is a small built-in synth.

Self-contained: needs numpy, pycairo, Pillow, ffmpeg and the fonts/ folder.

Usage:
  python3 foodreel.py EPISODE.json OUT.mp4                 full render
  python3 foodreel.py EPISODE.json PREFIX --stills 2 6 12   test frames
  python3 foodreel.py EPISODE.json PREFIX --cover           grid + reel cover
"""
import json, math, os, subprocess, sys, wave
import multiprocessing as mp
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFont

from brand import *  # noqa
from library import *  # noqa

# ------------------------------------------------------------------ episode --
class Episode:
    def __init__(self, spec):
        self.spec = spec
        self.beat = beat = 60 / spec["bpm"]
        self.t_hook = spec["hook_beats"] * beat
        t = 0.0; self.dish_t = []
        for d in spec["dishes"]:
            self.dish_t.append(t); t += d["beats"] * beat
        self.t_sheet = t; t += spec["sheet_beats"] * beat
        self.t_outro = t; t += spec["outro_beats"] * beat
        self.end = t
        self.total = t + 0.6
        self.ings = spec["ingredients"]
        self.maxg = max(max(d["grams"].get(i, 0) for i in self.ings) for d in spec["dishes"])

    def dish_at(self, t):
        i = 0
        for k, s in enumerate(self.dish_t):
            if t >= s: i = k
        return i

    def start(self, k): return max(self.dish_t[k], self.t_hook + 0.2) if k == 0 else self.dish_t[k]

    def grams(self, t):
        ds = self.spec["dishes"]; prev = {i: 0.0 for i in self.ings}; vals = dict(prev)
        for k, s in enumerate(self.dish_t):
            if t < s: break
            target = {i: float(ds[k]["grams"].get(i, 0)) for i in self.ings}
            dur = 1.6 if k == 0 else 0.7
            s0 = s + (0.3 if k == 0 else 0)
            a = smooth((t - s0) / dur)
            vals = {i: prev[i] + (target[i] - prev[i]) * a for i in self.ings}
            prev = target
        return vals

    # ----------------------------------------------------------- pieces --
    def header(self, cv, t, in_hook):
        cr = cv.cr
        logo(cr, L - 6, 232 - 30, 44)
        cv.text(L + 52, 242, "foods that move", "disp", 32, INK)
        sp = self.spec
        hd = f"EP. {int(sp['episode']):02d}" if in_hook else sp["series"].upper()
        cv.text(R - tw(hd, "mono", 20, 0.12), 242, hd, "mono", 20, MUTED, 1, 0.12)

    def stepper(self, cv, t, a):
        cr = cv.cr; ds = self.spec["dishes"]; n = len(ds); di = self.dish_at(t)
        gap = 12; pw = (R - L - gap * (n - 1)) / n
        for i, d in enumerate(ds):
            x = L + i * (pw + gap); on = i == di
            rrect(cr, x, 282, pw, 58, 29)
            if on: fs(cr, INK, 4, a)
            elif i < di: fs(cr, hexc("F7E7D0"), 3, a, LINE)
            else: fs(cr, BG, 3, a, LINE)
            name = d["name"]
            col = BG if on else (INK if i < di else MUTED)
            cv.text(x + (pw - tw(name, "disp", 28)) / 2, 321, name, "disp", 28, col, a)
        frac = clamp((t - self.t_hook) / (self.t_sheet - self.t_hook))
        rrect(cr, L, 356, R - L, 6, 3); fill(cr, LINE, a)
        rrect(cr, L, 356, max(6, (R - L) * frac), 6, 3); fill(cr, ACCENT, a)

    def ratio_tiles(self, cv, x, yb, ratio, size, a, gap_txt="  :  "):
        """Ratio as colour tiles. yb = text baseline. Returns end x."""
        cr = cv.cr; h = size * 1.5
        for j, (ing, val) in enumerate(ratio):
            if j: x = cv.text(x, yb, gap_txt, "mono_b", size, INK, a) - size * 0.15
            w = tw(val, "mono_b", size) + size * 0.9
            tc = ING.get(ing, MUTED)
            rrect(cr, x, yb - size * 1.08, w, h, h * 0.32); fs(cr, tc, 4, a)
            cv.text(x + size * 0.45, yb, val, "mono_b", size, INK if lum(tc) > 0.45 else CARD, a)
            x += w
        return x

    def marked_text(self, cv, text, kind, size, y0, lh, maxw, a, since=None, col=INK, max_lines=2):
        cr = cv.cr
        while True:
            lines = wrap(tokens(text), kind, size, maxw)
            if len(lines) <= max_lines or size <= 28: break
            size -= 2
        k = 0
        for li, line in enumerate(lines):
            b = y0 + li * lh
            for w, hl, x, ww in line:
                wa = a if since is None else a * ease((since - 0.2 - k * 0.05) / 0.25)
                k += 1
                if wa <= 0: continue
                if hl:
                    rrect(cr, L + x - 6, b - size * 0.78, ww + 12, size * 1.0, 8); fill(cr, MARKER, wa)
                cv.text(L + x, b, w, kind, size, ACCENT if hl and kind != "disp" else col, wa)
        return lines

    def bars(self, cv, t, a, di, since, in_hook):
        cr = cv.cr; sp = self.spec; g = self.grams(t)
        dish = sp["dishes"][di]
        prev_g = sp["dishes"][di - 1]["grams"] if di > 0 else None
        changed = [i for i in self.ings if prev_g is not None and prev_g.get(i, 0) != dish["grams"].get(i, 0)]
        cv.text(L, 1290, sp.get("base_label") or f"GRAMS PER 100 G {sp.get('base', 'flour').upper()}", "mono", 19, MUTED, a, 0.1)
        x0, x1 = L + 64, R - 112
        for j, ing in enumerate(self.ings):
            y = 1310 + j * 52; col = ING.get(ing, MUTED)
            hl = ing in changed and not in_hook
            dim = 1.0 if (hl or not changed or in_hook) else 0.45
            icon(cr, ing, L + 22, y + 18, 46, a * (0.55 + 0.45 * dim))
            rrect(cr, x0, y, x1 - x0, 36, 18); fill(cr, hexc("F3E3CB"), a)
            v = g[ing]; w = (x1 - x0) * v / self.maxg
            if prev_g is not None and ing in changed and not in_hook:         # ghost of previous value
                pw_ = (x1 - x0) * prev_g.get(ing, 0) / self.maxg
                if pw_ > 4:
                    rrect(cr, x0, y, pw_, 36, 18); cr.set_dash([7, 6]); stroke(cr, INK, 3, a * 0.5); cr.set_dash([])
            if w > 2:
                if hl:
                    pulse = ease(since / 0.4) * (1 - ease((since - 1.4) / 0.6))
                    rrect(cr, x0 - 5, y - 5, w + 10, 46, 23); fill(cr, ACCENT, a * 0.25 * pulse)
                rrect(cr, x0, y, max(w, 36), 36, 18)
                fs(cr, mix(BG, col, dim), 4, a, mix(BG, INK, 0.35 + 0.65 * dim))
            name = ing.upper(); nw = tw(name, "mono_b", 17, 0.08)
            na = a * (0.5 + 0.5 * dim)
            if w > nw + 34: cv.text(x0 + 16, y + 24, name, "mono_b", 17, INK if lum(col) > 0.45 else CARD, na, 0.08)
            else: cv.text(x0 + max(w, 36) + 12, y + 24, name, "mono_b", 17, MUTED, na, 0.08)
            val = f"{int(round(v))} g"
            cv.text(R - tw(val, "mono_b", 28), y + 28, val, "mono_b", 28, INK if v > 0.5 else MUTED, a * (0.5 + 0.5 * dim))
        return changed, prev_g

    # ------------------------------------------------------------- frame --
    def frame(self, t):
        sp = self.spec; cv = Canvas(); cr = cv.cr
        background(cr, t)
        in_hook = t < self.t_hook
        in_outro = t >= self.t_outro
        di = self.dish_at(t); dish = sp["dishes"][di]
        since = t - self.start(di)
        # sections hand over in sequence: old fades out (0.25 s), then new comes in
        hook_a = 1 - ease((t - self.t_hook) / 0.25)
        ui = ease((t - self.t_hook - 0.2) / 0.35)
        main_a = ui * (1 - ease((t - self.t_sheet) / 0.28))
        sheet_a = ease((t - self.t_sheet - 0.25) / 0.45) * (1 - ease((t - self.t_outro) / 0.28))
        outro_a = ease((t - self.t_outro - 0.25) / 0.45)
        bars_a = 1 - ease((t - self.t_sheet) / 0.28)
        ts0 = self.t_sheet + 0.25
        self.header(cv, t, in_hook)

        # ---- hook
        if hook_a > 0:
            dy = -30 * (1 - hook_a)
            lab = sp["title"].upper()
            rrect(cr, L, 286 + dy, tw(lab, "mono", 20, 0.12) + 40, 46, 23); fs(cr, CARD, 3, hook_a)
            cv.text(L + 20, 316 + dy, lab, "mono", 20, INK, hook_a, 0.12)
            self.marked_text(cv, sp["hook"], "disp", 100, 470 + dy, 104, R - L, hook_a, max_lines=3)
            first = [i for i in self.ings if sp["dishes"][0]["grams"].get(i, 0) > 0]
            n = len(first)
            for j, ing in enumerate(first):
                x = L + 80 + j * (R - L - 160) / max(1, n - 1)
                s = back((t - 0.25 - j * 0.22) / 0.4)
                if s > 0:
                    icon(cr, ing, x, 790 + dy, 120 * s, hook_a)
                    cv.text(x - tw(ing.upper(), "mono_b", 20, 0.1) / 2, 880 + dy, ing.upper(), "mono_b", 20, MUTED, hook_a * s, 0.1)
            for j, d in enumerate(sp["dishes"]):
                x = L + 120 + j * (R - L - 240) / max(1, len(sp["dishes"]) - 1)
                age = t - 1.5 - j * 0.3
                s = back(age / 0.45)
                if s > 0:
                    cr.move_to(x, 920 + dy); cr.line_to(x, 950 + dy); stroke(cr, INK, 4, hook_a * 0.4 * s)
                    group(cr, hook_a, draw_dish, cr, d, max(age, 0) + 1.5, x, 1080 + dy, 0.5 * s)

        if bars_a > 0:
            changed, prev_g = self.bars(cv, t, bars_a, di, since, in_hook or since < 0)
        # ---- dish section
        if main_a > 0:
            self.stepper(cv, t, main_a)
            # stage: tinted blob, dish (pop swap), lens
            tint_prev = hexc(sp["dishes"][di - 1].get("tint", "FFE3C2")) if di > 0 else hexc(dish.get("tint", "FFE3C2"))
            tint = mix(tint_prev, hexc(dish.get("tint", "FFE3C2")), ease(since / 0.5))
            blob(cr, 330, 850, 238, t); fill(cr, tint, main_a)
            cx, cy, sc = 330, 868, 0.92
            if di > 0 and since < 0.22:
                prev = sp["dishes"][di - 1]
                group(cr, main_a, draw_dish, cr, prev, t - self.start(di - 1), cx, cy, sc * (1 - ease(since / 0.22)))
            pa = since - 0.15 if di > 0 else since
            pop = back(pa / 0.45)
            if pop > 0:
                group(cr, main_a, draw_dish, cr, dish, pa, cx, cy, sc * pop)
                hx, hy = HOTSPOT.get(illus_key(dish), (0, -60))
                lens(cr, dish, pa - 0.35, 772, 765, 145, (cx + hx * sc, cy + hy * sc), main_a * clamp((pa - 0.35) * 8))
                la = main_a * ease((pa - 0.7) / 0.3)
                lab = dish.get("science_label", "")
                if lab and la > 0:
                    lw_ = tw(lab, "mono_b", 19, 0.06) + 36
                    lx = min(R - lw_, 772 - lw_ / 2)
                    rrect(cr, lx, 930, lw_, 42, 21); fs(cr, INK, 3, la)
                    cv.text(lx + 18, 958, lab, "mono_b", 19, BG, la, 0.06)
            # name + ratio
            k_ = ease(since / 0.3); ndy = 12 * (1 - k_); na = k_ * main_a
            size = 140
            while size > 96 and tw(dish["name"], "disp", size) > R - L: size -= 6
            cv.text(L - 4, 512 + ndy, dish["name"], "disp", size, INK, na)
            x = self.ratio_tiles(cv, L, 590 + ndy, dish["ratio"], 32, na)
            tag = dish.get("tag", "").upper()
            if tag: cv.text(x + 22, 586 + ndy, tag, "mono", 19, MUTED, na, 0.1)
            # explanation
            self.marked_text(cv, dish["text"], "body", 40, 1118, 52, R - L, main_a, since=since)
            # bars + chip
            if prev_g is not None and changed:
                ca = ease((since - 0.45) / 0.3) * main_a
                txt = "   ".join(f"{i.capitalize()} {prev_g.get(i, 0)} g → {dish['grams'].get(i, 0)} g" for i in changed)
                cw = tw(txt, "mono_b", 23) + 72
                if ca > 0:
                    rrect(cr, L, 1190, cw, 52, 26); fs(cr, CARD, 3, ca)
                    cr.arc(L + 28, 1216, 7, 0, 2 * math.pi); fill(cr, ACCENT, ca)
                    cv.text(L + 48, 1224, txt, "mono_b", 23, INK, ca)

        # ---- cheat sheet
        if sheet_a > 0:
            a = sheet_a; dy = 30 * (1 - ease((t - ts0) / 0.45))
            cv.text(L, 318 + dy, "THE CHEAT SHEET", "mono_b", 21, ACCENT, a, 0.12)
            sv = "SAVE FOR LATER"
            sx = R - tw(sv, "mono", 19, 0.1)
            cv.text(sx, 318 + dy, sv, "mono", 19, MUTED, a, 0.1)
            cr.move_to(sx - 30, 298 + dy); cr.line_to(sx - 30, 322 + dy); cr.line_to(sx - 22, 314 + dy)
            cr.line_to(sx - 14, 322 + dy); cr.line_to(sx - 14, 298 + dy); cr.close_path(); fs(cr, ACCENT, 3, a)
            cv.text(L - 3, 420 + dy, sp["sheet_title"], "disp", 84, INK, a)
            n_ = len(sp["dishes"]); ch = 196 if n_ <= 3 else 150; k = ch / 196
            for r_, d in enumerate(sp["dishes"]):
                rk = ease((t - ts0 - 0.15 - r_ * 0.22) / 0.35); ra = a * rk
                if ra <= 0: continue
                ox = 60 * (1 - rk)
                y = 470 + r_ * (ch + 22)
                rrect(cr, L + ox, y, R - L, ch, 30 * k); fs(cr, CARD, 4, ra)
                cr.save(); cr.arc(L + ox + 92 * k, y + ch / 2, 72 * k, 0, 2 * math.pi); cr.clip()
                cr.set_source_rgba(*rgb(hexc(d.get("tint", "FFE3C2")), ra)); cr.paint()
                cr.restore()
                group(cr, ra, draw_dish, cr, d, 3.0 + t * 0.3, L + ox + 92 * k, y + ch / 2 + 22 * k, 0.3 * k)
                tx0 = L + ox + 192 * k; ns = int(50 * (0.5 + 0.5 * k))
                cv.text(tx0, y + 62 * k, d["name"], "disp", ns, INK, ra)
                cv.text(tx0 + tw(d["name"], "disp", ns) + 18, y + 58 * k, d.get("tag", "").upper(), "mono", 17, MUTED, ra, 0.1)
                self.ratio_tiles(cv, tx0, y + 120 * k, d["ratio"], int(26 * (0.6 + 0.4 * k)), ra, " : ")
                # stacked proportion bar
                tot = sum(d["grams"].values()); bx, bw = tx0, R + ox - 28 - tx0
                grow = ease((t - ts0 - 0.4 - r_ * 0.22) / 0.6)
                x = bx
                for ing in self.ings:
                    v = d["grams"].get(ing, 0)
                    if not v: continue
                    w = bw * v / tot * grow
                    rrect(cr, x, y + 146 * k, max(w, 1), 26 * k, 8 * k); fs(cr, ING.get(ing, MUTED), 3, ra)
                    x += w
            ty = 470 + n_ * (ch + 22) + 86
            lines = self.marked_text(cv, sp["sheet_text"], "body", 42, ty + dy, 54, R - L, a)
            # ingredient legend (wraps)
            lx, ly = L, ty + 54 * len(lines) + 66
            for ing in self.ings:
                wd = 46 + tw(ing.upper(), "mono_b", 17, 0.08) + 28
                if lx + wd - 28 > R: lx, ly = L, ly + 56
                icon(cr, ing, lx + 20, ly + dy, 40, a)
                lx = cv.text(lx + 46, ly + 8 + dy, ing.upper(), "mono_b", 17, MUTED, a, 0.08) + 28

        # ---- outro
        if outro_a > 0:
            a = outro_a; dy = 30 * (1 - a)
            logo(cr, L - 14, 470 + dy, 230, a)
            cv.text(L - 6, 830 + dy, "foods", "disp", 150, INK, a)
            x = cv.text(L - 6, 980 + dy, "that ", "disp", 150, INK, a)
            cv.text(x, 980 + dy, "move", "disp", 150, ACCENT, a)
            rrect(cr, L, 1040 + dy, tw(sp["handle"], "mono_b", 28) + 48, 60, 30); fs(cr, INK, 3, a)
            cv.text(L + 24, 1080 + dy, sp["handle"], "mono_b", 28, BG, a)
            if sp.get("next"):
                cv.text(L, 1160 + dy, "NEXT EPISODE", "mono_b", 19, ACCENT, a, 0.12)
                nsz = 44
                while nsz > 28 and tw(sp["next"], "disp", nsz) > R - L: nsz -= 2
                cv.text(L, 1212 + dy, sp["next"], "disp", nsz, INK, a)
            for j, d in enumerate(sp["dishes"]):
                age = t - self.t_outro - 0.5 - j * 0.15
                s = back(age / 0.45)
                if s > 0:
                    x = L + 130 + j * (R - L - 260) / max(1, len(sp["dishes"]) - 1)
                    bob = 8 * math.sin(t * 3 + j)
                    group(cr, a, draw_dish, cr, d, 3 + age, x, 1400 + bob, 0.38 * s)
        return cv.image()

    # ------------------------------------------------------------- cover --
    def cover(self):
        sp = self.spec; CW, CH, PX, PY = 1080, 1350, 90, 100
        cv = Canvas(CW, CH); cr = cv.cr
        background(cr, 0, CW, CH)
        cv.text(PX, PY + 20, sp["series"].upper(), "mono_b", 24, ACCENT, 1, 0.14)
        cv.text(CW - PX - tw(f"EP. {int(sp['episode']):02d}", "mono", 24, 0.14), PY + 20,
                f"EP. {int(sp['episode']):02d}", "mono", 24, MUTED, 1, 0.14)
        size = 150
        while size > 90:
            lines = wrap(tokens(sp["title"]), "disp", size, CW - 2 * PX)
            if len(lines) <= 2: break
            size -= 6
        for li, line in enumerate(lines):
            for w, hl, x, ww in line:
                cv.text(PX + x - 4, PY + 40 + size * 0.95 * (li + 1), w, "disp", size, INK)
        ds = sp["dishes"]; n = len(ds); colw = (CW - 2 * PX) / n
        top = PY + 60 + size * 0.95 * len(lines)
        for i, d in enumerate(ds):
            cx = PX + colw * (i + 0.5)
            blob(cr, cx, top + 150, 128, i * 2.0); fill(cr, hexc(d.get("tint", "FFE3C2")))
            draw_dish(cr, d, 3.0, cx, top + 175, 0.52)
            nw = tw(d["name"], "disp", 44)
            cv.text(cx - nw / 2, top + 345, d["name"], "disp", 44, INK)
            rw = tw(d["ratio_short"], "mono_b", 22)
            cv.text(cx - rw / 2, top + 382, d["ratio_short"], "mono_b", 22, ACCENT)
            # mini vertical bars
            k = len(self.ings); bw = 26; gx = cx - (k * bw + (k - 1) * 8) / 2; base = top + 520
            for j, ing in enumerate(self.ings):
                h = d["grams"].get(ing, 0) / self.maxg * 100
                rrect(cr, gx + j * (bw + 8), base - 4, bw, 4, 2); fill(cr, LINE)
                if h > 0:
                    rrect(cr, gx + j * (bw + 8), base - h, bw, h, 9); fs(cr, ING.get(ing, MUTED), 3)
        cv.texts_marker = True
        lines = wrap(tokens(sp["cover_text"]), "body", 40, 640)
        b0 = CH - PY - (len(lines) - 1) * 52
        for li, line in enumerate(lines):
            for w, hl, x, ww in line:
                b = b0 + li * 52
                if hl: rrect(cr, PX + x - 6, b - 31, ww + 12, 40, 8); fill(cr, MARKER)
                cv.text(PX + x, b, w, "body", 40, ACCENT if hl else INK)
        logo(cr, CW - PX - 84, CH - PY - 80, 90)
        img = cv.image()
        reel = Canvas(W, H); background(reel.cr, 0); reel = reel.image()
        reel.paste(img, (0, (H - CH) // 2))
        return img, reel


# -------------------------------------------------------------------- audio --
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
QUAL = [("maj7", [0, 4, 7, 11]), ("m7", [0, 3, 7, 10]), ("7", [0, 4, 7, 10]), ("m", [0, 3, 7]), ("", [0, 4, 7])]


def parse_chord(name):
    pc = NOTE[name[0]]; rest = name[1:]
    if rest[:1] in ("#", "b"): pc += 1 if rest[0] == "#" else -1; rest = rest[1:]
    for q, iv in QUAL:
        if rest == q: return pc % 12, iv
    return pc % 12, [0, 4, 7]


def mtof(m): return 440 * 2 ** ((m - 69) / 12)


def synth(ep, path, sr_=44100):
    sp = ep.spec; beat = ep.beat; n = int((ep.total + 0.2) * sr_)
    Lc, Rc = np.zeros(n), np.zeros(n)

    def add(sig, t0, pan=0.0):
        i0 = int(t0 * sr_)
        if i0 >= n: return
        sig = sig[: n - i0]
        Lc[i0:i0 + len(sig)] += sig * (1 - pan) * 0.5 * 2 ** 0.5 * 0.7
        Rc[i0:i0 + len(sig)] += sig * (1 + pan) * 0.5 * 2 ** 0.5 * 0.7

    t = 0.0
    for name, beats in sp["music"]:
        root, iv = parse_chord(name); dur = beats * beat
        # pad
        tt = np.arange(int((dur + 0.9) * sr_)) / sr_
        env = np.minimum(1, tt / 0.35) * np.where(tt > dur, np.exp(-(tt - dur) / 0.3), 1.0)
        for k, i in enumerate(iv):
            m = 55 + ((root + i - 7) % 12)
            f = mtof(m); sig = np.zeros_like(tt)
            for det in (-0.0018, 0.0018):
                ff = f * (1 + det)
                sig += np.sin(2 * np.pi * ff * tt) + 0.28 * np.sin(4 * np.pi * ff * tt) + 0.08 * np.sin(6 * np.pi * ff * tt)
            add(sig * env * 0.028, t, (k / max(1, len(iv) - 1) - 0.5) * 0.6)
        # bass, every 2 beats
        bm = 40 + ((root - 4) % 12)
        for b in range(0, beats, 2):
            bt = np.arange(int(1.6 * sr_)) / sr_
            benv = np.minimum(1, bt / 0.01) * np.exp(-bt / 0.55)
            f = mtof(bm)
            add((np.sin(2 * np.pi * f * bt) + 0.25 * np.sin(4 * np.pi * f * bt)) * benv * 0.17, t + b * beat)
        # marimba arp, eighth notes
        tones = sorted(67 + ((root + i - 7) % 12) for i in iv)
        pat = tones + tones[-2:0:-1]
        for e in range(beats * 2):
            m = pat[e % len(pat)]; f = mtof(m)
            at = np.arange(int(0.7 * sr_)) / sr_
            sig = np.sin(2 * np.pi * f * at) * np.exp(-at / 0.22) + 0.3 * np.sin(2 * np.pi * 4 * f * at) * np.exp(-at / 0.04)
            sig *= np.minimum(1, at / 0.004)
            add(sig * (0.055 if e % 2 == 0 else 0.04), t + e * beat / 2, 0.35 if e % 2 else -0.35)
        t += dur
    # soft "pop" on each dish change and sheet card
    pops = [ep.dish_t[k] + 0.15 for k in range(1, len(sp["dishes"]))] + [ep.t_hook + 0.2]
    pops += [ep.t_sheet + 0.4 + r * 0.22 for r in range(len(sp["dishes"]))]
    for p in pops:
        pt = np.arange(int(0.14 * sr_)) / sr_
        f = 380 + 900 * pt / 0.14
        add(np.sin(2 * np.pi * np.cumsum(f) / sr_) * np.exp(-pt / 0.04) * 0.10, p)
    mixd = np.stack([Lc, Rc], 1)
    fo = int(1.6 * sr_); mixd[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mixd = np.tanh(mixd * 1.4) / np.tanh(1.4) * 0.8
    mixd *= 0.89 / max(1e-6, np.abs(mixd).max())          # peak at about -1 dB
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr_)
        w.writeframes((mixd * 32767).astype(np.int16).tobytes())


# ------------------------------------------------------------------- render --
def _render_chunk(args):
    spec, i0, i1, path = args
    ep = Episode(spec); tmp = path[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        ff.stdin.write(ep.frame(i / FPS).tobytes())
    ff.stdin.close()
    if ff.wait() != 0: raise RuntimeError("encode failed")
    os.replace(tmp, path)
    return path


def render(spec, out, workers=None):
    ep = Episode(spec); base = os.path.splitext(out)[0]
    nfr = int(round(ep.total * FPS)); workers = workers or max(1, os.cpu_count() or 1)
    bounds = np.linspace(0, nfr, workers + 1).astype(int)
    parts = [f"{base}.chunk{k}.mp4" for k in range(workers)]
    with mp.get_context("fork").Pool(workers) as pool:
        pool.map(_render_chunk, [(spec, bounds[k], bounds[k + 1], parts[k]) for k in range(workers)])
    lst = base + ".concat.txt"
    with open(lst, "w") as f:
        for p in parts: f.write(f"file '{os.path.abspath(p)}'\n")
    wav = base + ".wav"; synth(ep, wav)
    tmp = base + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out)
    for p in parts + [lst, wav]: os.remove(p)
    print(out)


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    if "--stills" in sys.argv:
        ep = Episode(spec); i = sys.argv.index("--stills")
        for t in map(float, sys.argv[i + 1:]):
            p = f"{sys.argv[2]}_{t:05.2f}.jpg"; ep.frame(t).save(p, quality=90); print(p)
    elif "--cover" in sys.argv:
        g, r = Episode(spec).cover(); g.save(sys.argv[2] + "_grid.png"); r.save(sys.argv[2] + "_reel.png")
        print(sys.argv[2] + "_grid.png", sys.argv[2] + "_reel.png")
    else:
        render(spec, sys.argv[2])

