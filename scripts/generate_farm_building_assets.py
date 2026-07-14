"""Generates the farm base-building system's art: player-constructed
buildings (storage/production/infrastructure/defense), a mineable boulder,
raw resource icons (wood/stone/iron), and processed goods icons (flour,
feed, jam, pickles, cider, lumber, bricks, ingot, honey). Drawn at higher
internal resolution then downsampled with NEAREST for crisp pixel-art
edges, matching the rest of the game's art pipeline. Re-run to tweak.
"""
import os
import random

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
CS = CELL * SCALE
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

random.seed(19)


def s(v):
    return v * SCALE


def canvas2x2():
    w, h = CELL * 2, CELL * 2
    return Image.new("RGBA", (w * SCALE, h * SCALE), (0, 0, 0, 0)), w, h


def save(img, name, size):
    img.resize(size, Image.NEAREST).save(os.path.join(OUT_DIR, name))


# ---------------------------------------------------------------- boulder --
ROCK = (150, 148, 150, 255)
ROCK_SHADE = (108, 106, 110, 255)
ROCK_HIGHLIGHT = (196, 194, 198, 255)
ROCK_ORE = (196, 156, 60, 255)


def make_boulder():
    """A proper mineable boulder — bigger and chunkier than the small
    decorative pebble, with a visible ore glint so it reads as harvestable."""
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    cx, cy = CS * 0.5, CS * 0.58
    d.polygon([(cx - CS * 0.36, cy + CS * 0.2), (cx - CS * 0.4, cy - CS * 0.05),
               (cx - CS * 0.18, cy - CS * 0.3), (cx + CS * 0.12, cy - CS * 0.32),
               (cx + CS * 0.38, cy - CS * 0.1), (cx + CS * 0.36, cy + CS * 0.22),
               (cx + CS * 0.1, cy + CS * 0.34), (cx - CS * 0.14, cy + CS * 0.32)],
              fill=ROCK_SHADE)
    d.polygon([(cx - CS * 0.3, cy + CS * 0.14), (cx - CS * 0.32, cy - CS * 0.06),
               (cx - CS * 0.12, cy - CS * 0.26), (cx + CS * 0.1, cy - CS * 0.27),
               (cx + CS * 0.3, cy - CS * 0.08), (cx + CS * 0.28, cy + CS * 0.16),
               (cx + CS * 0.06, cy + CS * 0.26), (cx - CS * 0.12, cy + CS * 0.24)],
              fill=ROCK)
    d.polygon([(cx - CS * 0.24, cy - CS * 0.08), (cx - CS * 0.1, cy - CS * 0.22),
                (cx + CS * 0.04, cy - CS * 0.2), (cx - CS * 0.04, cy - CS * 0.02)],
              fill=ROCK_HIGHLIGHT)
    for (ox, oy) in ((-0.08, 0.02), (0.12, -0.05), (0.02, 0.14)):
        d.ellipse([cx + CS * ox - CS * 0.03, cy + CS * oy - CS * 0.03,
                   cx + CS * ox + CS * 0.03, cy + CS * oy + CS * 0.03], fill=ROCK_ORE)
    return c.resize((CELL, CELL), Image.NEAREST)


# -------------------------------------------------------------- resources --
def make_wood_icon():
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    bark = (108, 74, 46, 255)
    bark_dark = (80, 54, 32, 255)
    ring = (168, 124, 82, 255)
    for i, (x0, y0) in enumerate([(0.08, 0.14), (0.1, 0.5)]):
        d.rounded_rectangle([s(32 * x0), s(32 * y0), s(32 * x0 + 22), s(32 * y0 + 9)],
                             radius=s(3), fill=bark)
        d.ellipse([s(32 * x0 - 2), s(32 * y0), s(32 * x0 + 6), s(32 * y0 + 9)], fill=ring)
        d.ellipse([s(32 * x0), s(32 * y0 + 2), s(32 * x0 + 4), s(32 * y0 + 7)], fill=bark_dark)
    return c.resize((CELL, CELL), Image.NEAREST)


def make_stone_icon():
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.polygon([(s(6), s(20)), (s(10), s(9)), (s(20), s(6)), (s(27), s(14)),
               (s(24), s(25)), (s(12), s(27))], fill=ROCK)
    d.polygon([(s(10), s(9)), (s(20), s(6)), (s(18), s(13)), (s(12), s(15))], fill=ROCK_HIGHLIGHT)
    d.polygon([(s(12), s(27)), (s(24), s(25)), (s(20), s(20)), (s(14), s(20))], fill=ROCK_SHADE)
    return c.resize((CELL, CELL), Image.NEAREST)


def make_iron_icon():
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    ore_rock = (96, 90, 92, 255)
    metal = (206, 158, 84, 255)
    metal_light = (238, 198, 120, 255)
    d.polygon([(s(6), s(21)), (s(9), s(9)), (s(19), s(6)), (s(26), s(15)),
               (s(23), s(26)), (s(11), s(27))], fill=ore_rock)
    for (mx, my, mr) in ((13, 14, 3.4), (19, 20, 3.0), (20, 12, 2.4)):
        d.ellipse([s(mx - mr), s(my - mr), s(mx + mr), s(my + mr)], fill=metal)
        d.ellipse([s(mx - mr * 0.4), s(my - mr * 0.4), s(mx), s(my)], fill=metal_light)
    return c.resize((CELL, CELL), Image.NEAREST)


# ---------------------------------------------------------- processed goods --
def make_sack(fill_color, fleck_color, label_dots=0):
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    sack = (222, 200, 158, 255)
    sack_shade = (188, 166, 128, 255)
    tie = (120, 86, 54, 255)
    d.polygon([(s(8), s(28)), (s(6), s(16)), (s(10), s(9)), (s(22), s(9)),
               (s(26), s(16)), (s(24), s(28))], fill=sack)
    d.polygon([(s(8), s(28)), (s(24), s(28)), (s(22), s(22)), (s(10), s(22))], fill=sack_shade)
    d.polygon([(s(10), s(9)), (s(22), s(9)), (s(19), s(5)), (s(13), s(5))], fill=tie)
    d.ellipse([s(11), s(13), s(21), s(20)], fill=fill_color)
    for i in range(label_dots):
        d.ellipse([s(13 + i * 3), s(15), s(15 + i * 3), s(17)], fill=fleck_color)
    return c.resize((CELL, CELL), Image.NEAREST)


def make_jar(fill_color, shine=True):
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    glass = (222, 232, 236, 200)
    lid = (150, 110, 70, 255)
    lid_dark = (110, 78, 48, 255)
    d.rounded_rectangle([s(9), s(12), s(23), s(28)], radius=s(3), fill=glass)
    d.rounded_rectangle([s(10), s(15), s(22), s(27)], radius=s(2), fill=fill_color)
    d.rectangle([s(11), s(7), s(21), s(13)], fill=lid)
    d.rectangle([s(11), s(11), s(21), s(13)], fill=lid_dark)
    if shine:
        d.line([(s(12), s(17)), (s(12), s(24))], fill=(255, 255, 255, 140), width=max(1, int(s(0.5))))
    return c.resize((CELL, CELL), Image.NEAREST)


def make_bottle(fill_color):
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    glass = (150, 176, 150, 220)
    d.polygon([(s(13), s(6)), (s(19), s(6)), (s(19), s(11)), (s(23), s(16)),
               (s(23), s(27)), (s(9), s(27)), (s(9), s(16)), (s(13), s(11))],
              fill=glass)
    d.rounded_rectangle([s(10), s(17), s(22), s(26)], radius=s(2), fill=fill_color)
    d.rectangle([s(13), s(4), s(19), s(7)], fill=(90, 70, 50, 255))
    return c.resize((CELL, CELL), Image.NEAREST)


def make_lumber():
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    plank = (196, 150, 96, 255)
    plank_shade = (162, 120, 72, 255)
    for i, y in enumerate((10, 16, 22)):
        d.rounded_rectangle([s(5), s(y), s(27), s(y + 5)], radius=s(1.5),
                             fill=plank if i % 2 == 0 else plank_shade)
        d.line([(s(5), s(y + 2.5)), (s(27), s(y + 2.5))], fill=(140, 100, 60, 255), width=max(1, int(s(0.15))))
    return c.resize((CELL, CELL), Image.NEAREST)


def make_bricks():
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    brick = (176, 84, 62, 255)
    mortar = (206, 196, 180, 255)
    d.rectangle([s(6), s(9), s(26), s(27)], fill=mortar)
    rows = [(9, 0), (15, 1), (21, 0)]
    for y, offset in rows:
        bw = 9
        x = 6 - (bw // 2 if offset else 0)
        while x < 26:
            d.rectangle([s(max(x, 6)), s(y), s(min(x + bw - 1, 26)), s(y + 5)], fill=brick)
            x += bw
    return c.resize((CELL, CELL), Image.NEAREST)


def make_ingot():
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    metal = (210, 214, 220, 255)
    metal_dark = (168, 172, 180, 255)
    shine = (240, 244, 248, 255)
    d.polygon([(s(6), s(22)), (s(9), s(13)), (s(23), s(13)), (s(26), s(22)),
               (s(23), s(26)), (s(9), s(26))], fill=metal)
    d.polygon([(s(9), s(26)), (s(23), s(26)), (s(23), s(22)), (s(9), s(22))], fill=metal_dark)
    d.polygon([(s(11), s(15)), (s(21), s(15)), (s(19), s(18)), (s(13), s(18))], fill=shine)
    return c.resize((CELL, CELL), Image.NEAREST)


# ------------------------------------------------------------ construction --
def make_construction_site():
    """Scaffolding overlay drawn over a building's footprint while it's
    under construction — wooden poles + cross-bracing, no roof yet."""
    w, h = CELL * 2, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    c = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    pole = (150, 108, 68, 255)
    pole_dark = (110, 78, 48, 255)
    for x in (0.08, 0.32, 0.68, 0.92):
        d.rectangle([cs_w * x, cs_h * 0.25, cs_w * (x + 0.05), cs_h], fill=pole)
    for y in (0.35, 0.6, 0.85):
        d.line([(cs_w * 0.08, cs_h * y), (cs_w * 0.92, cs_h * y)], fill=pole_dark,
               width=max(1, int(cs_w * 0.02)))
    d.line([(cs_w * 0.1, cs_h * 0.3), (cs_w * 0.5, cs_h * 0.6)], fill=pole_dark, width=max(1, int(cs_w * 0.015)))
    d.line([(cs_w * 0.5, cs_h * 0.3), (cs_w * 0.9, cs_h * 0.6)], fill=pole_dark, width=max(1, int(cs_w * 0.015)))
    return c.resize((w, h), Image.NEAREST)


# ------------------------------------------------------------- buildings --
def make_mill():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    wood = (162, 116, 70, 255)
    wood_shade = (122, 84, 50, 255)
    roof = (108, 62, 46, 255)
    wheel_rim = (90, 62, 40, 255)
    water = (86, 138, 200, 255)

    d.rectangle([cs_w * 0.2, cs_h * 0.4, cs_w * 0.95, cs_h], fill=wood)
    d.rectangle([cs_w * 0.2, cs_h * 0.8, cs_w * 0.95, cs_h], fill=wood_shade)
    d.polygon([(cs_w * 0.16, cs_h * 0.4), (cs_w * 0.58, cs_h * 0.12), (cs_w * 0.99, cs_h * 0.4)], fill=roof)

    # waterwheel on the left side
    wcx, wcy, wr = cs_w * 0.14, cs_h * 0.68, cs_w * 0.16
    d.ellipse([wcx - wr, wcy - wr, wcx + wr, wcy + wr], outline=wheel_rim, width=max(1, int(wr * 0.22)))
    for i in range(8):
        import math
        ang = i * (math.pi / 4)
        x2, y2 = wcx + wr * 0.9 * math.cos(ang), wcy + wr * 0.9 * math.sin(ang)
        d.line([(wcx, wcy), (x2, y2)], fill=wheel_rim, width=max(1, int(wr * 0.12)))
    d.ellipse([wcx - wr * 0.15, wcy - wr * 0.15, wcx + wr * 0.15, wcy + wr * 0.15], fill=wheel_rim)
    d.rectangle([wcx - wr * 1.3, wcy + wr * 0.7, wcx + wr * 1.3, cs_h], fill=water)

    d.rectangle([cs_w * 0.55, cs_h * 0.55, cs_w * 0.75, cs_h * 0.9], fill=wood_shade)
    return c.resize((w, h), Image.NEAREST)


def make_preserving_shed():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    wood = (176, 132, 84, 255)
    wood_shade = (138, 98, 60, 255)
    roof = (90, 116, 82, 255)
    window = (72, 52, 34, 255)

    d.rectangle([cs_w * 0.08, cs_h * 0.42, cs_w * 0.92, cs_h], fill=wood)
    d.rectangle([cs_w * 0.08, cs_h * 0.82, cs_w * 0.92, cs_h], fill=wood_shade)
    d.polygon([(cs_w * 0.03, cs_h * 0.42), (cs_w * 0.5, cs_h * 0.16), (cs_w * 0.97, cs_h * 0.42)], fill=roof)
    d.rectangle([cs_w * 0.3, cs_h * 0.5, cs_w * 0.7, cs_h * 0.72], fill=window)
    for (jx, jy, jc) in ((0.38, 0.62, (196, 60, 60, 255)), (0.5, 0.6, (200, 160, 60, 255)),
                         (0.62, 0.63, (120, 160, 80, 255))):
        d.ellipse([cs_w * jx - cs_w * 0.04, cs_h * jy - cs_h * 0.045,
                   cs_w * jx + cs_w * 0.04, cs_h * jy + cs_h * 0.045], fill=jc)
    d.rectangle([cs_w * 0.36, cs_h * 0.8, cs_w * 0.64, cs_h * 0.9], fill=wood_shade)
    return c.resize((w, h), Image.NEAREST)


def make_brewery():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    stone = (128, 116, 108, 255)
    stone_shade = (96, 86, 80, 255)
    roof = (74, 54, 44, 255)
    chimney = (90, 80, 74, 255)
    barrel = (150, 106, 62, 255)
    barrel_band = (90, 66, 42, 255)

    d.rectangle([cs_w * 0.1, cs_h * 0.42, cs_w * 0.9, cs_h], fill=stone)
    d.rectangle([cs_w * 0.1, cs_h * 0.8, cs_w * 0.9, cs_h], fill=stone_shade)
    d.polygon([(cs_w * 0.05, cs_h * 0.42), (cs_w * 0.5, cs_h * 0.15), (cs_w * 0.95, cs_h * 0.42)], fill=roof)
    d.rectangle([cs_w * 0.68, cs_h * 0.05, cs_w * 0.8, cs_h * 0.32], fill=chimney)
    for (bx,) in ((0.2,), (0.36,)):
        d.rounded_rectangle([cs_w * bx, cs_h * 0.62, cs_w * (bx + 0.16), cs_h * 0.92], radius=cs_w * 0.02, fill=barrel)
        d.line([(cs_w * bx, cs_h * 0.7), (cs_w * (bx + 0.16), cs_h * 0.7)], fill=barrel_band,
               width=max(1, int(cs_w * 0.012)))
        d.line([(cs_w * bx, cs_h * 0.84), (cs_w * (bx + 0.16), cs_h * 0.84)], fill=barrel_band,
               width=max(1, int(cs_w * 0.012)))
    d.rectangle([cs_w * 0.58, cs_h * 0.5, cs_w * 0.78, cs_h * 0.72], fill=(50, 40, 34, 255))
    return c.resize((w, h), Image.NEAREST)


def make_workshop():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    wood = (150, 108, 66, 255)
    wood_shade = (114, 80, 48, 255)
    roof = (70, 70, 74, 255)
    bench = (100, 70, 42, 255)

    d.rectangle([cs_w * 0.08, cs_h * 0.4, cs_w * 0.92, cs_h], fill=wood)
    d.rectangle([cs_w * 0.08, cs_h * 0.8, cs_w * 0.92, cs_h], fill=wood_shade)
    d.polygon([(cs_w * 0.03, cs_h * 0.4), (cs_w * 0.5, cs_h * 0.14), (cs_w * 0.97, cs_h * 0.4)], fill=roof)
    d.rectangle([cs_w * 0.15, cs_h * 0.66, cs_w * 0.5, cs_h * 0.78], fill=bench)
    # saw + hammer silhouette on the workbench
    d.line([(cs_w * 0.2, cs_h * 0.66), (cs_w * 0.32, cs_h * 0.58)], fill=(190, 190, 196, 255),
           width=max(1, int(cs_w * 0.015)))
    d.rectangle([cs_w * 0.38, cs_h * 0.56, cs_w * 0.44, cs_h * 0.66], fill=(90, 62, 40, 255))
    d.rectangle([cs_w * 0.35, cs_h * 0.52, cs_w * 0.47, cs_h * 0.57], fill=(70, 70, 74, 255))
    d.rectangle([cs_w * 0.58, cs_h * 0.5, cs_w * 0.85, cs_h * 0.78], fill=(60, 50, 40, 255))
    return c.resize((w, h), Image.NEAREST)


def make_barn():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    red = (168, 60, 48, 255)
    red_shade = (128, 44, 36, 255)
    trim = (232, 224, 210, 255)
    roof = (74, 54, 44, 255)

    d.rectangle([cs_w * 0.06, cs_h * 0.4, cs_w * 0.94, cs_h], fill=red)
    d.rectangle([cs_w * 0.06, cs_h * 0.82, cs_w * 0.94, cs_h], fill=red_shade)
    d.polygon([(cs_w * 0.0, cs_h * 0.4), (cs_w * 0.5, cs_h * 0.08), (cs_w * 1.0, cs_h * 0.4),
               (cs_w * 1.0, cs_h * 0.48), (cs_w * 0.0, cs_h * 0.48)], fill=roof)
    # hayloft door + X-brace
    d.polygon([(cs_w * 0.38, cs_h * 0.5), (cs_w * 0.5, cs_h * 0.38), (cs_w * 0.62, cs_h * 0.5),
               (cs_w * 0.62, cs_h * 0.66), (cs_w * 0.38, cs_h * 0.66)], fill=trim)
    d.line([(cs_w * 0.4, cs_h * 0.52), (cs_w * 0.6, cs_h * 0.64)], fill=red_shade, width=max(1, int(cs_w * 0.012)))
    d.line([(cs_w * 0.6, cs_h * 0.52), (cs_w * 0.4, cs_h * 0.64)], fill=red_shade, width=max(1, int(cs_w * 0.012)))
    d.rectangle([cs_w * 0.14, cs_h * 0.66, cs_w * 0.34, cs_h * 0.94], fill=trim)
    d.rectangle([cs_w * 0.66, cs_h * 0.66, cs_w * 0.86, cs_h * 0.94], fill=trim)
    return c.resize((w, h), Image.NEAREST)


def make_silo():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    metal = (196, 196, 200, 255)
    metal_shade = (156, 156, 162, 255)
    cap = (140, 70, 56, 255)

    d.rounded_rectangle([cs_w * 0.28, cs_h * 0.24, cs_w * 0.72, cs_h], radius=cs_w * 0.08, fill=metal)
    for y in (0.4, 0.56, 0.72, 0.88):
        d.line([(cs_w * 0.28, cs_h * y), (cs_w * 0.72, cs_h * y)], fill=metal_shade, width=max(1, int(cs_h * 0.012)))
    d.pieslice([cs_w * 0.28, cs_h * 0.1, cs_w * 0.72, cs_h * 0.38], 180, 360, fill=cap)
    d.rectangle([cs_w * 0.46, cs_h * 0.05, cs_w * 0.54, cs_h * 0.16], fill=metal_shade)
    return c.resize((w, h), Image.NEAREST)


def make_warehouse():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    wall = (140, 130, 116, 255)
    wall_shade = (108, 100, 88, 255)
    roof = (90, 90, 96, 255)
    door = (74, 60, 46, 255)
    crate = (176, 132, 84, 255)

    d.rectangle([cs_w * 0.04, cs_h * 0.36, cs_w * 0.96, cs_h], fill=wall)
    d.rectangle([cs_w * 0.04, cs_h * 0.8, cs_w * 0.96, cs_h], fill=wall_shade)
    d.polygon([(cs_w * 0.0, cs_h * 0.36), (cs_w * 0.0, cs_h * 0.24), (cs_w * 1.0, cs_h * 0.24),
               (cs_w * 1.0, cs_h * 0.36)], fill=roof)
    d.rectangle([cs_w * 0.36, cs_h * 0.5, cs_w * 0.64, cs_h * 0.94], fill=door)
    d.rectangle([cs_w * 0.08, cs_h * 0.7, cs_w * 0.28, cs_h * 0.9], fill=crate)
    d.rectangle([cs_w * 0.72, cs_h * 0.68, cs_w * 0.92, cs_h * 0.9], fill=crate)
    return c.resize((w, h), Image.NEAREST)


def make_well_farm():
    """1-tile buildable well, distinct look from the village well."""
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    stone = (150, 140, 130, 255)
    stone_shade = (112, 104, 96, 255)
    water = (86, 138, 200, 255)
    roof = (120, 70, 54, 255)

    d.ellipse([s(6), s(18), s(26), s(30)], fill=stone_shade)
    d.ellipse([s(7), s(16), s(25), s(26)], fill=stone)
    d.ellipse([s(10), s(18), s(22), s(24)], fill=water)
    d.rectangle([s(8), s(6), s(11), s(20)], fill=stone_shade)
    d.rectangle([s(21), s(6), s(24), s(20)], fill=stone_shade)
    d.polygon([(s(6), s(8)), (s(16), s(2)), (s(26), s(8))], fill=roof)
    return c.resize((CELL, CELL), Image.NEAREST)


def make_windmill():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    stone = (176, 164, 142, 255)
    stone_shade = (140, 128, 108, 255)
    cap = (110, 62, 48, 255)
    blade = (222, 214, 196, 255)
    blade_shade = (186, 178, 162, 255)

    d.polygon([(cs_w * 0.32, cs_h), (cs_w * 0.38, cs_h * 0.2), (cs_w * 0.62, cs_h * 0.2), (cs_w * 0.68, cs_h)],
              fill=stone)
    d.polygon([(cs_w * 0.5, cs_h), (cs_w * 0.56, cs_h * 0.2), (cs_w * 0.62, cs_h * 0.2), (cs_w * 0.68, cs_h)],
              fill=stone_shade)
    d.pieslice([cs_w * 0.32, cs_h * 0.06, cs_w * 0.68, cs_h * 0.34], 180, 360, fill=cap)

    hub = (cs_w * 0.5, cs_h * 0.2)
    import math
    for i in range(4):
        ang = i * (math.pi / 2) + 0.4
        tip = (hub[0] + cs_w * 0.42 * math.cos(ang), hub[1] + cs_h * 0.42 * math.sin(ang))
        side = (hub[0] + cs_w * 0.1 * math.cos(ang + 1.2), hub[1] + cs_h * 0.1 * math.sin(ang + 1.2))
        d.polygon([hub, side, tip], fill=blade if i % 2 == 0 else blade_shade)
    d.ellipse([hub[0] - cs_w * 0.03, hub[1] - cs_w * 0.03, hub[0] + cs_w * 0.03, hub[1] + cs_w * 0.03],
              fill=(70, 54, 40, 255))
    return c.resize((w, h), Image.NEAREST)


def make_greenhouse():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    frame = (110, 96, 80, 255)
    glass = (176, 214, 210, 150)
    glass_shade = (140, 184, 180, 150)
    plant = (86, 150, 76, 255)

    d.rectangle([cs_w * 0.1, cs_h * 0.42, cs_w * 0.9, cs_h], fill=frame)
    d.polygon([(cs_w * 0.06, cs_h * 0.42), (cs_w * 0.5, cs_h * 0.18), (cs_w * 0.94, cs_h * 0.42)], fill=frame)
    d.polygon([(cs_w * 0.12, cs_h * 0.4), (cs_w * 0.5, cs_h * 0.22), (cs_w * 0.88, cs_h * 0.4)], fill=glass)
    d.rectangle([cs_w * 0.14, cs_h * 0.46, cs_w * 0.86, cs_h * 0.94], fill=glass_shade)
    for x in (0.3, 0.5, 0.7):
        d.line([(cs_w * x, cs_h * 0.46), (cs_w * x, cs_h * 0.94)], fill=frame, width=max(1, int(cs_w * 0.015)))
    for (px,) in ((0.28,), (0.48,), (0.68,)):
        d.ellipse([cs_w * px, cs_h * 0.7, cs_w * (px + 0.1), cs_h * 0.86], fill=plant)
    return c.resize((w, h), Image.NEAREST)


def make_beehive():
    """1-tile hive box with a couple of bee dots."""
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    hive = (222, 178, 90, 255)
    hive_shade = (188, 146, 66, 255)
    hole = (90, 62, 40, 255)
    bee = (40, 34, 28, 255)

    for i, y in enumerate((10, 17, 24)):
        w_ = 22 - i * 2
        x0 = 16 - w_ / 2
        d.rounded_rectangle([s(x0), s(y), s(x0 + w_), s(y + 6)], radius=s(1.5),
                             fill=hive if i % 2 == 0 else hive_shade)
    d.ellipse([s(13), s(18), s(19), s(24)], fill=hole)
    for (bx, by) in ((22, 12), (25, 18)):
        d.ellipse([s(bx), s(by), s(bx + 2.5), s(by + 2)], fill=bee)
    return c.resize((CELL, CELL), Image.NEAREST)


def make_orchard_marker():
    """A simple wooden post + fruit-basket sign marking an orchard plot."""
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    post = (120, 84, 52, 255)
    sign = (176, 132, 84, 255)
    apple = (200, 56, 56, 255)
    leaf = (86, 150, 76, 255)

    d.rectangle([s(14), s(10), s(18), s(30)], fill=post)
    d.rectangle([s(6), s(6), s(26), s(16)], fill=sign)
    d.rectangle([s(6), s(6), s(26), s(8)], fill=(140, 100, 62, 255))
    d.ellipse([s(11), s(9), s(16), s(14)], fill=apple)
    d.ellipse([s(17), s(9), s(22), s(14)], fill=apple)
    d.polygon([(s(13.5), s(9)), (s(15.5), s(6.5)), (s(16.5), s(9))], fill=leaf)
    return c.resize((CELL, CELL), Image.NEAREST)


def make_watchtower():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    wood = (120, 88, 56, 255)
    wood_shade = (90, 64, 40, 255)
    roof = (90, 46, 40, 255)
    flag = (196, 60, 56, 255)

    d.polygon([(cs_w * 0.3, cs_h), (cs_w * 0.36, cs_h * 0.3), (cs_w * 0.64, cs_h * 0.3), (cs_w * 0.7, cs_h)],
              fill=wood)
    d.polygon([(cs_w * 0.5, cs_h), (cs_w * 0.55, cs_h * 0.3), (cs_w * 0.64, cs_h * 0.3), (cs_w * 0.7, cs_h)],
              fill=wood_shade)
    for y in (0.5, 0.68, 0.86):
        d.line([(cs_w * 0.3, cs_h * y), (cs_w * 0.7, cs_h * y)], fill=wood_shade, width=max(1, int(cs_w * 0.015)))
    d.rectangle([cs_w * 0.24, cs_h * 0.16, cs_w * 0.76, cs_h * 0.3], fill=wood)
    d.rectangle([cs_w * 0.24, cs_h * 0.26, cs_w * 0.76, cs_h * 0.3], fill=wood_shade)
    d.rectangle([cs_w * 0.48, cs_h * 0.02, cs_w * 0.52, cs_h * 0.16], fill=wood_shade)
    d.polygon([(cs_w * 0.52, cs_h * 0.02), (cs_w * 0.68, cs_h * 0.07), (cs_w * 0.52, cs_h * 0.12)], fill=flag)
    return c.resize((w, h), Image.NEAREST)


def make_ward():
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    stone = (140, 132, 148, 255)
    stone_shade = (104, 98, 112, 255)
    glow = (140, 200, 240, 255)
    glow_core = (220, 240, 250, 255)

    d.polygon([(cs_w * 0.36, cs_h), (cs_w * 0.4, cs_h * 0.2), (cs_w * 0.6, cs_h * 0.2), (cs_w * 0.64, cs_h)],
              fill=stone)
    d.polygon([(cs_w * 0.5, cs_h), (cs_w * 0.54, cs_h * 0.2), (cs_w * 0.6, cs_h * 0.2), (cs_w * 0.64, cs_h)],
              fill=stone_shade)
    cx, cy, r = cs_w * 0.5, cs_h * 0.16, cs_w * 0.16
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=glow, width=max(1, int(r * 0.25)))
    d.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], fill=glow_core)
    for frac in (0.3, 0.5, 0.7):
        d.line([(cs_w * 0.4, cs_h * frac), (cs_w * 0.6, cs_h * frac)], fill=stone_shade,
               width=max(1, int(cs_w * 0.012)))
    return c.resize((w, h), Image.NEAREST)


def main():
    make_boulder().save(os.path.join(OUT_DIR, "Boulder.png"))
    make_wood_icon().save(os.path.join(OUT_DIR, "Wood.png"))
    make_stone_icon().save(os.path.join(OUT_DIR, "Stone.png"))
    make_iron_icon().save(os.path.join(OUT_DIR, "Iron.png"))
    print("wrote Boulder.png, Wood.png, Stone.png, Iron.png")

    make_sack((222, 214, 188, 255), (196, 168, 120, 255), label_dots=0).save(os.path.join(OUT_DIR, "Flour.png"))
    make_sack((208, 178, 110, 255), (150, 110, 60, 255), label_dots=3).save(os.path.join(OUT_DIR, "Feed.png"))
    make_jar((196, 56, 60, 255)).save(os.path.join(OUT_DIR, "Jam.png"))
    make_jar((120, 156, 90, 255)).save(os.path.join(OUT_DIR, "Pickles.png"))
    make_jar((232, 178, 60, 255)).save(os.path.join(OUT_DIR, "Honey.png"))
    make_bottle((196, 140, 60, 255)).save(os.path.join(OUT_DIR, "Cider.png"))
    make_lumber().save(os.path.join(OUT_DIR, "Lumber.png"))
    make_bricks().save(os.path.join(OUT_DIR, "Bricks.png"))
    make_ingot().save(os.path.join(OUT_DIR, "Ingot.png"))
    print("wrote Flour/Feed/Jam/Pickles/Honey/Cider/Lumber/Bricks/Ingot.png")

    make_construction_site().save(os.path.join(OUT_DIR, "ConstructionSite.png"))
    print("wrote ConstructionSite.png")

    make_mill().save(os.path.join(OUT_DIR, "Mill.png"))
    make_preserving_shed().save(os.path.join(OUT_DIR, "PreservingShed.png"))
    make_brewery().save(os.path.join(OUT_DIR, "Brewery.png"))
    make_workshop().save(os.path.join(OUT_DIR, "Workshop.png"))
    make_barn().save(os.path.join(OUT_DIR, "Barn.png"))
    make_silo().save(os.path.join(OUT_DIR, "Silo.png"))
    make_warehouse().save(os.path.join(OUT_DIR, "Warehouse.png"))
    make_well_farm().save(os.path.join(OUT_DIR, "FarmWell.png"))
    make_windmill().save(os.path.join(OUT_DIR, "Windmill.png"))
    make_greenhouse().save(os.path.join(OUT_DIR, "Greenhouse.png"))
    make_beehive().save(os.path.join(OUT_DIR, "BeeHive.png"))
    make_orchard_marker().save(os.path.join(OUT_DIR, "OrchardMarker.png"))
    make_watchtower().save(os.path.join(OUT_DIR, "Watchtower.png"))
    make_ward().save(os.path.join(OUT_DIR, "MagicWard.png"))
    print("wrote all 13 building sprites")


if __name__ == "__main__":
    main()
