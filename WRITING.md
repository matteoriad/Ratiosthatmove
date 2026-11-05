# Writing episodes

One episode = **one cooking idea told through ratios by weight**: a family of 2–4 dishes
where changing one number changes the dish (same batter, more egg → crêpe; same flour,
water vs egg vs butter → bread / pasta / pie dough). The page wins on "I learned
something" and saves, so every episode needs a clear takeaway line.

Episodes live in `episodes/queue/epNN-slug.json`, numbered without gaps. The daily
workflow posts the lowest number not yet in `posted.json`.

## Rules

1. **One idea per episode, never repeat a topic.** Read every file in `episodes/queue/`
   (posted and unposted) first. Don't reuse a dish family or the same takeaway.
2. **Facts must be checked.** Every ratio comes from at least two independent sources
   found with web search (Ruhlman's *Ratio* / ruhlman.com, Serious Eats, King Arthur,
   America's Test Kitchen, Baker Bettie, etc.). If sources disagree on the numbers, pick
   another topic. Put the URLs in `"sources"`.
3. **Ratios by weight.** `grams` is "grams per 100 g of the base ingredient", so the
   base is always 100. `ratio` is the same thing in small parts and must match the grams
   (the checker enforces this). Use the conventional form people know (bread 5 : 3).
4. **Science must be right.** Pick the molecule scene that shows the real mechanism
   (see the table below). If none fits honestly, choose another topic.
5. **Only use what is in the library.** Illustrations, molecule scenes and ingredient
   names must be from the lists below. Don't change the renderer code in a writing
   run; if a great topic needs a new illustration, skip it and mention it in the summary.
6. **Run the checker and look at the stills** (see "Checking").

## The file

```json
{"title": "Flour doughs", "series": "Doughs", "episode": 2, "handle": "@foodsthatmove",
 "bpm": 86, "base": "flour",
 "hook": "Same flour. *Swap what you add*, get a new dough.", "hook_beats": 5,
 "cover_text": "Same flour, *one swap*, three different doughs",
 "ingredients": ["flour", "water", "egg", "butter"],
 "dishes": [
  {"name": "Bread", "beats": 12, "tag": "chewy & airy",
   "illustration": "bread", "tint": "FFE3C2", "look": {},
   "science": "gluten", "science_label": "GLUTEN TRAPS GAS",
   "grams": {"flour": 100, "water": 60},
   "ratio": [["flour", "5"], ["water", "3"]], "ratio_short": "5 : 3",
   "text": "Just water. Kneading lines up *gluten* into stretchy strands that trap gas."},
  ...
 ],
 "sheet_beats": 10, "sheet_title": "Flour + one more thing",
 "sheet_text": "Water makes it *chewy*, egg makes it silky, fat makes it tender.",
 "outro_beats": 6,
 "music": [["Am7", 12], ["Dm7", 8], ["G7", 8], ["Cmaj7", 10], ["Am7", 6]],
 "sources": ["https://… (what it confirms)", "https://…"]}
```

- `*stars*` mark the one highlighted phrase (hook, each dish text, sheet_text, cover_text).
- `hook`: max 3 lines at display size (~50 characters). Must work as the first 3 seconds.
- `dishes[].text`: one sentence or two short ones, max 2 lines (~85 characters). Say
  what changed and why it matters.
- `tag`: 2–3 words, lower case, the texture ("thin & lacy").
- `science_label`: max ~22 characters, uppercase, "X → Y" style.
- `tint`: a light pastel behind the dish (FFD9E2 pink, D3EAFF blue, FFEBAD yellow,
  FFE3C2 peach, D9F5E5 mint, E8E0FF lilac, F3D9C9 cocoa).
- `ingredients`: 2–5, in the order the bars should appear; first is usually the base.
- Each dish must change at least one number from the previous dish, and few enough
  numbers that the "what changed" chip fits (about 3 changes max).

## Timing and music

Beats: hook 5, first dish 12, other dishes 8, cheat sheet 10, outro 6.
3 dishes = 44 beats (84 bpm → 31 s). 4 dishes = 52 beats: use 90–96 bpm.
`music` is a chord loop whose beats must add up to the section total; one chord per
section is the house style. Chords: major (`C`), minor (`Am`), `maj7`, `m7`, `7`,
with `#`/`b`. Vary the key and bpm (76–96) from episode to episode.

## Library

### Illustrations (`illustration`, optional `look` colours as 6-digit hex)

| name | draws | `look` options |
|---|---|---|
| crepe | folded lacy crêpe with blueberries | – |
| popover | tall puffed popover in its tin | – |
| pancake | stack with syrup and butter | – |
| bread | crusty scored loaf on a board | crust |
| pasta | nest of fresh tagliatelle | color |
| pie | lattice pie | crust, filling, lattice (true/false) |
| cookie | two cookies | color, chips (true/false) |
| cake | layer cake with a glaze drip | sponge, glaze, filling, drip (true/false) |
| cupcake | frosted cupcake / muffin | frosting, liner, sponge, style ("muffin"), top |
| truffle | three chocolate truffles | color, drizzle |
| ramekin | custard in a ramekin / crème brûlée | fill, brulee (true/false) |
| flan | unmolded caramel flan | fill, caramel |
| bowl | bowl of something (sauce, soup, rice, polenta, oats…) | fill, bowl, band, garnish ("herbs", "grains", "swirl", "pepper", "none"), steam (true/false) |
| jar | glass jar (pickles, jam, sauce) | fill, lid, contents ("pickles", "jam", "sauce") |
| glass | drink in a tumbler or coupe | fill, shape ("tumbler", "coupe"), garnish ("lemon", "none") |
| meringue | meringue kisses | color |
| sausage | sausages on a board | color |

### Molecule scenes (`science`)

| name | shows | use for |
|---|---|---|
| protein_net | egg proteins uncoil and link into a net | eggs setting: crêpes, custards, pasta, quiche |
| steam | water molecules turning into rising steam | steam leavening: popovers, choux, puff pastry |
| co2 | CO₂ bubbles from baking powder/soda | chemical leavening: pancakes, muffins, biscuits |
| gluten | gluten strands align and stretch around a gas bubble | bread, pizza, kneaded doughs |
| fat_coating | butter coats flour so water can't reach it | pie dough, shortbread, tender biscuits |
| starch_gel | starch granules swell and leak chains | roux sauces, gravy, rice, polenta, pastry cream |
| emulsion | many fat droplets packed in water | mayonnaise, thick ganache, hollandaise, vinaigrette (shaken) |
| emulsion_loose | few fat droplets, lots of water | thin sauces, loose ganache, broken/thin emulsions |
| fat_crystals | fat molecules stack into a crystal (sets firm) | truffles, firm ganache, butter, shortbread setting |
| foam | air bubbles lined with proteins | meringue, whipped cream, sponge cakes, mousse |
| sugar | sucrose leaves the crystal and dissolves | syrups, sorbet, candy, sweet brines |
| salt | NaCl dissolves into Na⁺ and Cl⁻ ions in water | brines, pasta water, curing, pickles |

### Ingredient names

flour, milk, egg, butter, water, sugar, brown sugar, salt, oil, vinegar, cream, chocolate,
yolk, white, stock, meat, fat, rice, cornmeal, semolina, oats, yeast, baking powder,
baking soda, honey, mustard, lemon juice, juice, cheese, parmesan, wine, buttermilk,
cocoa, jam, syrup, spirit, espresso, almond flour, breadcrumbs, pepper, soy sauce.

## Topic ideas (verify every number before using)

Roux sauces (thin / medium / thick béchamel) · vinaigrette vs mayonnaise · 1-2-3 cookie
vs shortbread · biscuits vs pie dough (water and fat swapped) · custards (crème anglaise
/ crème brûlée / flan) · meringues (French / Swiss / Italian) · pound cake family ·
choux paste · simple syrups (1:1 / 2:1) · brines (pasta water / brine / cure) · rice
and grains water ratios · polenta (soft / firm) · sausage 3:1 · stock 3:2 · pizza
hydration (Neapolitan / New York / focaccia) · pancake vs waffle vs crêpe · muffin vs
cake · whipped ganache · sorbet sugar · pickles · cocktails sour 2:1:1 (drinks are fine
now and then).

## Checking

```
python3 pipeline/check.py --stills /tmp/stills episodes/queue/ep05-*.json
```

Fix every ERROR. Then open the cover and stills and look: no text running into the
lens or off the right edge, the right illustration, readable tiles. Render at least one
new episode fully to prove the pipeline works:

```
python3 foodreel.py episodes/queue/ep05-....json /tmp/ep05.mp4
```
