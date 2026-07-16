"""Generates extra town-flavor art: a gravel path tile, a tavern (2x2
building), a parked carriage, a wooden dock + rowboat pair, and two
"civilized" potted-plant/hedge decor tiles (as opposed to the wild flower
decor used out in the fields). Drawn at higher internal resolution then
downsampled with NEAREST for crisp pixel-art edges, matching the rest of
the game's art pipeline. Re-run to tweak.
"""
import os
import random

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

random.seed(41)


def canvas1x1():
    return Image.new("RGBA", (CELL * SCALE, CELL * SCALE), (0, 0, 0, 0)), CELL, CELL


def canvas2x2():
    w, h = CELL * 2, CELL * 2
    return Image.new("RGBA", (w * SCALE, h * SCALE), (0, 0, 0, 0)), w, h


def canvas2x1():
    w, h = CELL * 2, CELL
    return Image.new("RGBA", (w * SCALE, h * SCALE), (0, 0, 0, 0)), w, h


def canvas1x2():
    w, h = CELL, CELL * 2
    return Image.new("RGBA", (w * SCALE, h * SCALE), (0, 0, 0, 0)), w, h


# --------------------------------------------------------- Gravel path --
def make_gravel_path():
    """Flush 1-tile gravel/stone road texture, distinct in color from the
    dirt path near the farmhouse so town roads read as their own material."""
    c, w, h = canvas1x1()
    d = ImageDraw.Draw(c)
    cs = CELL * SCALE
    base = (176, 171, 162, 255)
    base_dark = (156, 151, 142, 255)
    pebble_lo = (140, 135, 126, 255)
    pebble_hi = (198, 193, 184, 255)

    d.rectangle([0, 0, cs, cs], fill=base)
    for _ in range(10):
        x0 = random.uniform(0, cs)
        y0 = random.uniform(0, cs)
        rw = random.uniform(cs * 0.06, cs * 0.14)
        d.ellipse([x0, y0, x0 + rw, y0 + rw * 0.7], fill=base_dark)
    for _ in range(26):
        x0 = random.uniform(0, cs)
        y0 = random.uniform(0, cs)
        rw = random.uniform(cs * 0.02, cs * 0.05)
        fill = pebble_hi if random.random() < 0.5 else pebble_lo
        d.ellipse([x0, y0, x0 + rw, y0 + rw], fill=fill)

    return c.resize((w, h), Image.NEAREST)


# ---------------------------------------------------------- Stone path --
def make_stone_path():
    """Flush 1-tile flagstone road: irregular gray slabs with visible
    mortar joints, distinct from gravel's loose scattered pebbles."""
    c, w, h = canvas1x1()
    d = ImageDraw.Draw(c)
    cs = CELL * SCALE
    mortar = (120, 116, 110, 255)
    slab_a = (168, 164, 156, 255)
    slab_b = (152, 148, 140, 255)
    slab_shade = (128, 124, 116, 255)

    d.rectangle([0, 0, cs, cs], fill=mortar)
    # a handful of irregular flagstone slabs, jittered off a loose 3x3 grid
    # so joints don't line up into a perfect checkerboard
    cell = cs / 3
    for row in range(3):
        for col in range(3):
            jx = random.uniform(-cell * 0.08, cell * 0.08)
            jy = random.uniform(-cell * 0.08, cell * 0.08)
            x0 = col * cell + cs * 0.04 + jx
            y0 = row * cell + cs * 0.04 + jy
            x1 = (col + 1) * cell - cs * 0.05 + jx
            y1 = (row + 1) * cell - cs * 0.05 + jy
            fill = slab_a if (row + col) % 2 == 0 else slab_b
            d.rectangle([x0, y0, x1, y1], fill=fill)
            d.rectangle([x0, y1 - cs * 0.025, x1, y1], fill=slab_shade)

    return c.resize((w, h), Image.NEAREST)


# ----------------------------------------------------------- Sand path --
def make_sand_path():
    """Flush 1-tile packed-sand road: warm tan base with fine ripple lines
    and scattered darker grit, for desert/tropical settlements."""
    c, w, h = canvas1x1()
    d = ImageDraw.Draw(c)
    cs = CELL * SCALE
    base = (220, 190, 140, 255)
    ripple = (198, 166, 112, 255)
    grit_dark = (176, 144, 96, 255)
    grit_light = (236, 210, 168, 255)

    d.rectangle([0, 0, cs, cs], fill=base)
    for _ in range(5):
        y = random.uniform(cs * 0.1, cs * 0.9)
        wobble = random.uniform(cs * 0.04, cs * 0.09)
        d.arc([0, y - wobble, cs, y + wobble], 200, 340, fill=ripple, width=max(1, int(cs * 0.012)))
    for _ in range(22):
        x0 = random.uniform(0, cs)
        y0 = random.uniform(0, cs)
        rw = random.uniform(cs * 0.012, cs * 0.03)
        fill = grit_light if random.random() < 0.5 else grit_dark
        d.ellipse([x0, y0, x0 + rw, y0 + rw], fill=fill)

    return c.resize((w, h), Image.NEAREST)


# ---------------------------------------------------------- Brick path --
def make_brick_path():
    """Flush 1-tile brick road: a running-bond pattern of warm red bricks,
    reserved for the grandest settlements (kingdoms)."""
    c, w, h = canvas1x1()
    d = ImageDraw.Draw(c)
    cs = CELL * SCALE
    mortar = (150, 138, 122, 255)
    brick_a = (150, 66, 50, 255)
    brick_b = (168, 78, 58, 255)
    brick_shade = (122, 52, 40, 255)

    d.rectangle([0, 0, cs, cs], fill=mortar)
    brick_w, brick_h = cs * 0.32, cs * 0.16
    row = 0
    y = 0.0
    while y < cs:
        offset = 0.0 if row % 2 == 0 else -brick_w / 2
        x = offset
        while x < cs:
            x0, x1 = max(x, 0), min(x + brick_w - cs * 0.015, cs)
            y0, y1 = y, min(y + brick_h - cs * 0.015, cs)
            if x1 > x0:
                fill = brick_a if int((x - offset) / brick_w) % 2 == 0 else brick_b
                d.rectangle([x0, y0, x1, y1], fill=fill)
                d.rectangle([x0, y1 - cs * 0.02, x1, y1], fill=brick_shade)
            x += brick_w
        y += brick_h
        row += 1

    return c.resize((w, h), Image.NEAREST)


# -------------------------------------------------------------- Tavern --
def make_tavern():
    """Warm timber tavern: lit amber windows, a hanging mug sign, and a
    couple of barrels out front."""
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    wall = (150, 106, 66, 255)
    wall_shade = (118, 80, 48, 255)
    timber = (66, 44, 30, 255)
    roof = (94, 46, 38, 255)
    roof_shade = (68, 32, 26, 255)
    window = (255, 214, 120, 255)
    window_frame = (54, 36, 24, 255)
    door = (72, 48, 30, 255)
    sign_post = (54, 36, 24, 255)
    sign_board = (196, 160, 90, 255)
    mug = (222, 90, 60, 255)
    barrel = (120, 82, 48, 255)
    barrel_band = (54, 36, 24, 255)

    # walls
    d.rectangle([cs_w * 0.06, cs_h * 0.4, cs_w * 0.94, cs_h], fill=wall)
    d.rectangle([cs_w * 0.06, cs_h * 0.82, cs_w * 0.94, cs_h], fill=wall_shade)
    for x in (0.06, 0.3, 0.5, 0.7, 0.94):
        d.rectangle([cs_w * x, cs_h * 0.4, cs_w * x + cs_w * 0.015, cs_h], fill=timber)

    # steep shingled roof — solid triangle (no inner notch, unlike the
    # pagoda-tier roofs elsewhere) so there's no gap showing background
    # through the peak
    d.polygon([(cs_w * -0.02, cs_h * 0.46), (cs_w * 0.5, cs_h * 0.08), (cs_w * 1.02, cs_h * 0.46)], fill=roof)
    d.polygon([(cs_w * 0.5, cs_h * 0.08), (cs_w * 1.02, cs_h * 0.46), (cs_w * 0.5, cs_h * 0.46)], fill=roof_shade)

    # lit windows either side of the door
    for wx in (0.16, 0.6):
        d.rectangle([cs_w * wx, cs_h * 0.54, cs_w * (wx + 0.2), cs_h * 0.74], fill=window_frame)
        d.rectangle([cs_w * (wx + 0.02), cs_h * 0.56, cs_w * (wx + 0.18), cs_h * 0.72], fill=window)
        d.line([(cs_w * (wx + 0.1), cs_h * 0.56), (cs_w * (wx + 0.1), cs_h * 0.72)],
               fill=window_frame, width=max(1, int(cs_w * 0.01)))

    # door
    d.rectangle([cs_w * 0.42, cs_h * 0.62, cs_w * 0.58, cs_h], fill=door)

    # hanging tavern sign (mug icon) on a post
    d.rectangle([cs_w * 0.78, cs_h * 0.42, cs_w * 0.8, cs_h * 0.62], fill=sign_post)
    d.rectangle([cs_w * 0.68, cs_h * 0.44, cs_w * 0.92, cs_h * 0.58], fill=sign_board)
    d.ellipse([cs_w * 0.75, cs_h * 0.47, cs_w * 0.85, cs_h * 0.56], fill=mug)
    d.rectangle([cs_w * 0.85, cs_h * 0.485, cs_w * 0.89, cs_h * 0.535], outline=mug, width=max(1, int(cs_w * 0.008)))

    # barrels out front
    for bx in (0.06, 0.14):
        d.rounded_rectangle([cs_w * bx, cs_h * 0.84, cs_w * (bx + 0.09), cs_h], radius=cs_w * 0.02, fill=barrel)
        d.line([(cs_w * bx, cs_h * 0.9), (cs_w * (bx + 0.09), cs_h * 0.9)], fill=barrel_band, width=max(1, int(cs_w * 0.012)))

    return c.resize((w, h), Image.NEAREST)


# ----------------------------------------------------------- Carriage --
def make_carriage():
    """A parked, horseless covered wagon: wooden bed, big spoked wheels,
    cream canvas canopy. Flush on the ground, 2 tiles wide x 1 tall."""
    c, w, h = canvas2x1()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    wood = (120, 82, 48, 255)
    wood_dark = (90, 60, 36, 255)
    wheel = (58, 42, 30, 255)
    wheel_hub = (150, 120, 80, 255)
    canvas_cloth = (222, 210, 186, 255)
    canvas_shade = (192, 178, 152, 255)

    # cart bed
    d.rectangle([cs_w * 0.08, cs_h * 0.5, cs_w * 0.92, cs_h * 0.72], fill=wood)
    d.rectangle([cs_w * 0.08, cs_h * 0.64, cs_w * 0.92, cs_h * 0.72], fill=wood_dark)

    # wheels
    for wx in (0.2, 0.72):
        d.ellipse([cs_w * wx, cs_h * 0.6, cs_w * (wx + 0.22), cs_h], fill=wheel)
        d.ellipse([cs_w * (wx + 0.08), cs_h * 0.68, cs_w * (wx + 0.14), cs_h * 0.86], fill=wheel_hub)
        for ang in range(4):
            import math as _m
            cx_, cy_ = cs_w * (wx + 0.11), cs_h * 0.83
            ex = cx_ + _m.cos(ang * _m.pi / 4) * cs_w * 0.1
            ey = cy_ + _m.sin(ang * _m.pi / 4) * cs_w * 0.1
            d.line([(cx_, cy_), (ex, ey)], fill=wheel_hub, width=max(1, int(cs_w * 0.006)))

    # arched canvas canopy
    d.polygon([(cs_w * 0.1, cs_h * 0.5), (cs_w * 0.18, cs_h * 0.16), (cs_w * 0.82, cs_h * 0.16),
               (cs_w * 0.9, cs_h * 0.5)], fill=canvas_cloth)
    d.polygon([(cs_w * 0.5, cs_h * 0.16), (cs_w * 0.82, cs_h * 0.16), (cs_w * 0.9, cs_h * 0.5),
               (cs_w * 0.5, cs_h * 0.5)], fill=canvas_shade)
    for hx in (0.3, 0.5, 0.7):
        d.line([(cs_w * hx, cs_h * (0.16 if 0.3 <= hx <= 0.7 else 0.5)), (cs_w * hx, cs_h * 0.5)],
               fill=canvas_shade, width=max(1, int(cs_w * 0.01)))

    return c.resize((w, h), Image.NEAREST)


# --------------------------------------------------------------- Dock --
def make_dock():
    """A short wooden pier, 1 tile wide x 2 tall: wider decking at the
    shore end (bottom), narrowing slightly toward the water end (top),
    with a mooring post. Designed to be bottom-anchored like a building
    (shore tile at the bottom, reaching out over water at the top) and
    rotated at draw time for the other 3 approach directions."""
    c, w, h = canvas1x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    plank = (140, 100, 62, 255)
    plank_dark = (108, 74, 44, 255)
    post = (74, 50, 30, 255)

    d.rectangle([cs_w * 0.1, cs_h * 0.0, cs_w * 0.9, cs_h * 1.0], fill=plank)
    for y in (0.12, 0.3, 0.48, 0.66, 0.84):
        d.line([(cs_w * 0.1, cs_h * y), (cs_w * 0.9, cs_h * y)], fill=plank_dark, width=max(1, int(cs_h * 0.02)))
    d.line([(cs_w * 0.1, cs_h * 0.0), (cs_w * 0.1, cs_h * 1.0)], fill=plank_dark, width=max(1, int(cs_w * 0.02)))
    d.line([(cs_w * 0.9, cs_h * 0.0), (cs_w * 0.9, cs_h * 1.0)], fill=plank_dark, width=max(1, int(cs_w * 0.02)))

    # mooring post near the water end
    d.rectangle([cs_w * 0.62, cs_h * -0.04, cs_w * 0.76, cs_h * 0.22], fill=post)

    return c.resize((w, h), Image.NEAREST)


# --------------------------------------------------------------- Boat --
def make_boat():
    """Small rowboat viewed at a 3/4 angle, sized to float within a
    single water tile near a dock."""
    c, w, h = canvas1x1()
    d = ImageDraw.Draw(c)
    cs = CELL * SCALE
    hull = (120, 76, 44, 255)
    hull_dark = (90, 56, 32, 255)
    trim = (196, 160, 90, 255)
    oar = (100, 70, 42, 255)

    d.polygon([(cs * 0.08, cs * 0.55), (cs * 0.18, cs * 0.78), (cs * 0.82, cs * 0.78), (cs * 0.92, cs * 0.55),
               (cs * 0.76, cs * 0.42), (cs * 0.24, cs * 0.42)], fill=hull)
    d.polygon([(cs * 0.18, cs * 0.78), (cs * 0.82, cs * 0.78), (cs * 0.92, cs * 0.55), (cs * 0.86, cs * 0.55),
               (cs * 0.78, cs * 0.72), (cs * 0.22, cs * 0.72), (cs * 0.14, cs * 0.55), (cs * 0.08, cs * 0.55)],
              fill=hull_dark)
    d.line([(cs * 0.24, cs * 0.42), (cs * 0.76, cs * 0.42)], fill=trim, width=max(1, int(cs * 0.015)))
    d.line([(cs * 0.1, cs * 0.4), (cs * 0.9, cs * 0.68)], fill=oar, width=max(1, int(cs * 0.02)))
    d.line([(cs * 0.9, cs * 0.4), (cs * 0.1, cs * 0.68)], fill=oar, width=max(1, int(cs * 0.02)))

    return c.resize((w, h), Image.NEAREST)


# --------------------------------------------------------- Town plants --
def make_town_plant1():
    """A terracotta potted plant — the 'civilized' counterpart to the wild
    flower decor used out in the fields."""
    c, w, h = canvas1x1()
    d = ImageDraw.Draw(c)
    cs = CELL * SCALE
    pot = (176, 106, 68, 255)
    pot_shade = (140, 82, 50, 255)
    leaf = (76, 128, 62, 255)
    leaf_dark = (54, 100, 46, 255)

    d.polygon([(cs * 0.36, cs * 0.7), (cs * 0.64, cs * 0.7), (cs * 0.6, cs * 0.94), (cs * 0.4, cs * 0.94)], fill=pot)
    d.polygon([(cs * 0.4, cs * 0.86), (cs * 0.6, cs * 0.86), (cs * 0.6, cs * 0.94), (cs * 0.4, cs * 0.94)],
              fill=pot_shade)
    for lx, ly, lr in ((0.5, 0.42, 0.16), (0.36, 0.54, 0.13), (0.64, 0.54, 0.13), (0.5, 0.6, 0.14)):
        d.ellipse([cs * (lx - lr), cs * (ly - lr), cs * (lx + lr), cs * (ly + lr)],
                  fill=leaf if lx == 0.5 else leaf_dark)

    return c.resize((w, h), Image.NEAREST)


def make_town_plant2():
    """A small trimmed hedge/bush."""
    c, w, h = canvas1x1()
    d = ImageDraw.Draw(c)
    cs = CELL * SCALE
    hedge = (70, 118, 58, 255)
    hedge_dark = (50, 92, 44, 255)
    hedge_light = (94, 142, 78, 255)

    d.ellipse([cs * 0.14, cs * 0.5, cs * 0.86, cs * 0.98], fill=hedge_dark)
    d.ellipse([cs * 0.18, cs * 0.4, cs * 0.82, cs * 0.86], fill=hedge)
    d.ellipse([cs * 0.28, cs * 0.32, cs * 0.62, cs * 0.62], fill=hedge_light)

    return c.resize((w, h), Image.NEAREST)


def main():
    make_gravel_path().save(os.path.join(OUT_DIR, "GravelPath.png"))
    make_stone_path().save(os.path.join(OUT_DIR, "StonePath.png"))
    make_sand_path().save(os.path.join(OUT_DIR, "SandPath.png"))
    make_brick_path().save(os.path.join(OUT_DIR, "BrickPath.png"))
    make_tavern().save(os.path.join(OUT_DIR, "Tavern.png"))
    make_carriage().save(os.path.join(OUT_DIR, "Carriage.png"))
    make_dock().save(os.path.join(OUT_DIR, "Dock.png"))
    make_boat().save(os.path.join(OUT_DIR, "Boat.png"))
    make_town_plant1().save(os.path.join(OUT_DIR, "TownPlant1.png"))
    make_town_plant2().save(os.path.join(OUT_DIR, "TownPlant2.png"))
    print("wrote GravelPath, StonePath, SandPath, BrickPath, Tavern, Carriage, Dock, Boat, TownPlant1, TownPlant2")


if __name__ == "__main__":
    main()
