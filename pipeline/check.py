#!/usr/bin/env python3
"""Check episode files before they go into the queue.

  python3 pipeline/check.py episodes/queue/ep04-*.json [...]            validate only
  python3 pipeline/check.py --stills DIR episodes/queue/ep04-*.json     + cover and 6 stills per episode

Validates the schema, library names (illustrations, molecule scenes, ingredients),
timing vs music, ratios vs grams, numbering, and that every piece of text fits its
slot at the size the renderer uses. Exits 1 on any error.
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from brand import tw, wrap, tokens, ING, L, R  # noqa: E402
from library import ILLUS, MOL, ICON_FORM  # noqa: E402
import foodreel  # noqa: E402

WIDTH = R - L
FRAC = {"½": 0.5, "¼": 0.25, "¾": 0.75, "⅓": 1 / 3, "⅔": 2 / 3, "⅛": 0.125}


def num(s):
    s = s.strip(); tot = 0.0; m = re.match(r"^(\d+(?:\.\d+)?)?\s*([½¼¾⅓⅔⅛])?$", s)
    if not m or not (m.group(1) or m.group(2)): raise ValueError(s)
    if m.group(1): tot += float(m.group(1))
    if m.group(2): tot += FRAC[m.group(2)]
    return tot


def tiles_width(ratio, size, gap="  :  "):
    w = 0
    for j, (_, val) in enumerate(ratio):
        if j: w += tw(gap, "mono_b", size) - size * 0.15
        w += tw(val, "mono_b", size) + size * 0.9
    return w


def check(path, errors, warns):
    e = lambda m: errors.append(f"{os.path.basename(path)}: {m}")
    w_ = lambda m: warns.append(f"{os.path.basename(path)}: {m}")
    sp = json.load(open(path))
    for k in ("title", "series", "episode", "handle", "bpm", "hook", "hook_beats", "cover_text", "ingredients",
              "dishes", "sheet_beats", "sheet_title", "sheet_text", "outro_beats", "music", "base", "sources"):
        if k not in sp: e(f"missing key '{k}'")
    if errors and any("missing key" in x for x in errors): return sp
    if not re.match(rf"ep{int(sp['episode']):02d}-[a-z0-9-]+\.json$", os.path.basename(path)):
        e("file name must be epNN-slug.json matching 'episode'")
    ds = sp["dishes"]
    if not 2 <= len(ds) <= 4: e("needs 2-4 dishes")
    ings = sp["ingredients"]
    if sp["base"] not in ings: e("base must be one of the ingredients")
    for i in ings:
        if i not in ING: e(f"ingredient '{i}' has no colour in brand.ING (pick a listed one)")
        if i not in ICON_FORM: w_(f"ingredient '{i}' has no icon form; it will show as a plain dot")
    if len(ings) > 5: e("max 5 ingredients")
    # timing
    beats = sp["hook_beats"]
    total = sum(d["beats"] for d in ds) + sp["sheet_beats"] + sp["outro_beats"]
    music = sum(b for _, b in sp["music"])
    if music != total: e(f"music has {music} beats but the sections have {total}")
    secs = total * 60 / sp["bpm"]
    if not 26 <= secs <= 40: e(f"episode runs {secs:.1f} s (aim for 28-36)")
    if ds[0]["beats"] - beats < 7: e("first dish needs >= 7 beats after the hook")
    for name, _ in sp["music"]:
        try: foodreel.parse_chord(name)
        except Exception: e(f"chord '{name}' not understood")
    # text fits
    hook_lines = wrap(tokens(sp["hook"]), "disp", 100, WIDTH)
    if len(hook_lines) > 3: e(f"hook wraps to {len(hook_lines)} lines at 100 px (max 3)")
    if "*" not in sp["hook"]: w_("hook has no *highlighted* phrase")
    if tw(sp["sheet_title"], "disp", 84) > WIDTH: e("sheet_title too wide (max ~16 characters)")
    if len(wrap(tokens(sp["sheet_text"]), "body", 42, WIDTH)) > 2: e("sheet_text longer than 2 lines")
    if len(wrap(tokens(sp["cover_text"]), "body", 40, 640)) > 3: e("cover_text longer than 3 lines")
    t_lines = wrap(tokens(sp["title"]), "disp", 90, 1080 - 180)
    if len(t_lines) > 2: e("title too long for the cover")
    n = len(ds); pw = (WIDTH - 12 * (n - 1)) / n
    prev = None
    for k, d in enumerate(ds):
        tag = f"dish '{d.get('name')}'"
        for key in ("name", "beats", "tag", "illustration", "tint", "science", "science_label", "grams", "ratio", "ratio_short", "text"):
            if key not in d: e(f"{tag}: missing '{key}'")
        if d.get("illustration") not in ILLUS: e(f"{tag}: illustration '{d.get('illustration')}' not in library {sorted(ILLUS)}")
        if d.get("science") not in MOL: e(f"{tag}: science '{d.get('science')}' not in library {sorted(MOL)}")
        if not re.match(r"^[0-9A-Fa-f]{6}$", d.get("tint", "")): e(f"{tag}: tint must be a 6-digit hex")
        for lk, lv in (d.get("look") or {}).items():
            if isinstance(lv, str) and lk not in ("garnish", "contents", "shape", "style") and not re.match(r"^[0-9A-Fa-f]{6}$", lv):
                e(f"{tag}: look.{lk} must be a 6-digit hex")
        g = d["grams"]
        for i in g:
            if i not in ings: e(f"{tag}: grams uses '{i}' which is not in ingredients")
        if g.get(sp["base"]) != 100: e(f"{tag}: grams must have {sp['base']} = 100 (grams per 100 g base)")
        # ratio must match grams
        try:
            r0 = dict((i, num(v)) for i, v in d["ratio"])
            unit = 100 / r0[sp["base"]]
            for i, v in r0.items():
                if abs(v * unit - g.get(i, 0)) > max(2.0, 0.04 * g.get(i, 0)):
                    e(f"{tag}: ratio {i}={v} implies {v * unit:.0f} g, grams say {g.get(i, 0)}")
            for i, v in g.items():
                if v and i not in r0: e(f"{tag}: '{i}' is in grams but not in ratio")
        except (ValueError, KeyError) as x:
            e(f"{tag}: bad ratio ({x}); use digits and ½ ¼ ¾ ⅓ ⅔ ⅛, with the base ingredient included")
        if tw(d["name"], "disp", 96) > WIDTH: e(f"{tag}: name too wide")
        if tw(d["name"], "disp", 28) > pw - 20: e(f"{tag}: name too wide for the stepper pill")
        rw = tiles_width(d["ratio"], 32) + 22 + tw(d["tag"].upper(), "mono", 19, 0.1)
        if rw > WIDTH: e(f"{tag}: ratio tiles + tag too wide ({rw:.0f} > {WIDTH}); shorten the tag")
        if rw > WIDTH - 210: w_(f"{tag}: ratio + tag may touch the zoom lens ({rw:.0f} px); a shorter tag is safer")
        lines = None
        for size in range(40, 27, -2):
            lines = wrap(tokens(d["text"]), "body", size, WIDTH)
            if len(lines) <= 2: break
        if len(lines) > 2: e(f"{tag}: text longer than 2 lines even at 28 px")
        elif size < 36: w_(f"{tag}: text shrinks to {size}px; shorter is better")
        if "*" not in d["text"]: w_(f"{tag}: text has no *highlighted* phrase")
        if tw(d["science_label"], "mono_b", 19, 0.06) + 36 > 360: e(f"{tag}: science_label too long (max ~22 chars)")
        if prev is not None:
            changed = [i for i in ings if prev.get(i, 0) != g.get(i, 0)]
            if not changed: e(f"{tag}: nothing changed from the previous dish")
            chip = "   ".join(f"{i.capitalize()} {prev.get(i, 0)} g → {g.get(i, 0)} g" for i in changed)
            if tw(chip, "mono_b", 23) + 72 > WIDTH: e(f"{tag}: 'what changed' chip too wide ({len(changed)} changes)")
        prev = g
        # cheat-sheet card
        k_ = 1 if n <= 3 else 150 / 196; ns = int(50 * (0.5 + 0.5 * k_))
        card = 192 * k_ + tw(d["name"], "disp", ns) + 18 + tw(d["tag"].upper(), "mono", 17, 0.1)
        if card > WIDTH - 20: e(f"{tag}: name + tag too wide for the cheat-sheet card")
    return sp


def main():
    args = sys.argv[1:]; stills = None
    if "--stills" in args:
        i = args.index("--stills"); stills = args[i + 1]; del args[i:i + 2]
    files = args or sorted(glob.glob(os.path.join(ROOT, "episodes/queue/*.json")))
    errors, warns, specs = [], [], []
    for p in files:
        specs.append((p, check(p, errors, warns)))
    nums = [s["episode"] for _, s in specs if "episode" in s]
    if len(nums) != len(set(nums)): errors.append("duplicate episode numbers")
    for w in warns: print("warning:", w)
    for x in errors: print("ERROR:", x)
    if stills and not errors:
        os.makedirs(stills, exist_ok=True)
        for p, sp in specs:
            ep = foodreel.Episode(sp); slug = os.path.basename(p)[:-5]
            g, r = ep.cover(); g.save(os.path.join(stills, f"{slug}_cover.png"))
            ts = [ep.t_hook * 0.75] + [ep.start(k) + 2.6 for k in range(len(sp["dishes"]))] + [ep.t_sheet + 3.5, ep.t_outro + 1.5]
            for t in ts:
                ep.frame(t).save(os.path.join(stills, f"{slug}_{t:05.2f}.jpg"), quality=85)
            print("stills:", slug)
    print(f"{len(files)} file(s) checked: {len(errors)} error(s), {len(warns)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
