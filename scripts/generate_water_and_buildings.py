"""Generates water tile (3-frame ripple strip), blacksmith and fisherman
buildings (2x2 tiles like the house/stable), and a "Fish.png" icon used
as a tradeable good. All drawn at higher internal resolution then
downsampled with NEAREST for crisp pixel-art edges. Re-run to tweak.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

CELL = 32
SCALE = 8
CS = CELL * SCALE
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

random.seed(11)


def s(v):
    return v * SCALE


# --------------------------------------------------------------- water --
# Same technique as the grass tiles (see _make_edge_mask in
# generate_ground_tiles.py): each tile is drawn oversized and overlapping
# its neighbors, with a guaranteed-solid core but an irregular, blurred
# alpha silhouette at the margin instead of a flat opaque square — that
# alpha falloff is what actually breaks up the "grid of blue squares" look;
# oversized-overlap rendering alone does nothing without it. 12 shape
# variants (matching the 12 grass ground variants per biome) keep a whole
# lake from reading as one shape stamped over and over — farm.py assigns a
# variant per tile via coherent noise so patches of the same shape blend into their
# neighbors rather than every tile repeating identically.
GRASS_FRAME_SIZE = 46  # match EXPORT_CELL in generate_ground_tiles.py
OVERFLOW = (GRASS_FRAME_SIZE - CELL) / (2 * CELL)  # ~0.22
WATER_VARIANTS = 12


def _make_water_edge_mask(rng):
    export_cs = GRASS_FRAME_SIZE * SCALE
    margin = export_cs * (OVERFLOW / (1 + 2 * OVERFLOW))
    mask = Image.new("L", (export_cs, export_cs), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rectangle([margin, margin, export_cs - margin, export_cs - margin], fill=255)

    # Fewer, larger, much-softer-blurred bumps than the grass mask: water has
    # no internal texture to distract the eye, so a tight scalloped edge reads
    # as a cartoon cloud/flower shape instead of a natural shoreline ripple.
    edge_lines = [
        lambda t: (margin + t * (export_cs - 2 * margin), margin),
        lambda t: (margin + t * (export_cs - 2 * margin), export_cs - margin),
        lambda t: (margin, margin + t * (export_cs - 2 * margin)),
        lambda t: (export_cs - margin, margin + t * (export_cs - 2 * margin)),
    ]
    for edge_fn in edge_lines:
        for _ in range(2):
            t = rng.uniform(0.15, 0.85)
            x, y = edge_fn(t)
            r = rng.uniform(margin * 0.35, margin * 0.7)
            mdraw.ellipse([x - r, y - r, x + r, y + r], fill=255)

    return mask.filter(ImageFilter.GaussianBlur(radius=max(1.0, export_cs * 0.045)))


def make_water_frame(variant_seed, phase):
    """phase: 0..2 — subtle ripple positions offset per frame so still water
    slowly rolls without looking mechanical. variant_seed reseeds the RNG
    from scratch each call so the edge mask (drawn last, from whatever RNG
    state remains) is identical across all 3 phases of the same variant —
    the coastline shape doesn't wobble as the ripple animates, only the
    ripples inside it move."""
    rng = random.Random(variant_seed)
    export_cs = GRASS_FRAME_SIZE * SCALE
    c = Image.new("RGBA", (export_cs, export_cs), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    deep = (54, 96, 156, 255)
    mid = (86, 138, 200, 255)
    shine = (176, 208, 240, 255)
    d.rectangle([0, 0, export_cs, export_cs], fill=deep)
    for i in range(6):
        bx = export_cs * (0.15 + i * 0.15 + phase * 0.03)
        by = export_cs * (0.3 + math.sin(i + phase) * 0.12)
        r = export_cs * 0.28
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=mid)
    for i in range(3):
        y = export_cs * (0.22 + i * 0.24 + phase * 0.03)
        d.arc([export_cs * 0.15, y - export_cs * 0.04, export_cs * 0.85, y + export_cs * 0.04],
              0, 180, fill=shine, width=max(1, int(export_cs * 0.008)))
    c = c.filter(ImageFilter.GaussianBlur(radius=SCALE * 0.4))

    edge_mask = _make_water_edge_mask(rng)
    c.putalpha(edge_mask)
    return c.resize((GRASS_FRAME_SIZE, GRASS_FRAME_SIZE), Image.NEAREST)


def make_water_strip(variant_seed):
    strip = Image.new("RGBA", (GRASS_FRAME_SIZE * 3, GRASS_FRAME_SIZE), (0, 0, 0, 0))
    for i in range(3):
        strip.paste(make_water_frame(variant_seed, i), (i * GRASS_FRAME_SIZE, 0))
    return strip


# ------------------------------------------------------------- blacksmith --
def make_blacksmith():
    """A 2-tile-wide x 2-tall smithy: dark stone walls, a red-hot forge
    glow through an open front, a chimney bellowing smoke, and an anvil
    silhouetted in the doorway. Anchored at the bottom like the house."""
    w, h = CELL * 2, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    c = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    stone = (108, 100, 96, 255)
    stone_shade = (78, 72, 68, 255)
    stone_dark = (52, 48, 46, 255)
    roof = (64, 48, 40, 255)
    roof_shade = (44, 32, 28, 255)
    forge_glow = (240, 128, 40, 255)
    forge_deep = (196, 68, 24, 255)
    smoke = (196, 196, 200, 255)

    # main body
    d.rectangle([0, cs_h * 0.36, cs_w, cs_h], fill=stone)
    # mortar/stone-block lines
    for row_y in (0.5, 0.65, 0.8):
        d.line([(0, cs_h * row_y), (cs_w, cs_h * row_y)], fill=stone_shade,
               width=max(1, int(cs_h * 0.01)))
    for col_x in (0.15, 0.35, 0.55, 0.75, 0.95):
        d.line([(cs_w * col_x, cs_h * 0.36), (cs_w * col_x, cs_h)], fill=stone_shade,
               width=max(1, int(cs_w * 0.008)))
    # pitched roof
    d.polygon([(0, cs_h * 0.36), (cs_w / 2, cs_h * 0.08), (cs_w, cs_h * 0.36),
               (cs_w, cs_h * 0.42), (0, cs_h * 0.42)], fill=roof)
    d.polygon([(0, cs_h * 0.36), (cs_w / 2, cs_h * 0.08), (cs_w / 2, cs_h * 0.2), (0, cs_h * 0.42)],
              fill=roof_shade)
    # chimney puffing smoke
    d.rectangle([cs_w * 0.68, cs_h * 0.06, cs_w * 0.82, cs_h * 0.32], fill=stone_dark)
    for (sx, sy, sr) in ((0.75, 0.02, 0.04), (0.72, -0.04, 0.06), (0.78, -0.1, 0.05)):
        d.ellipse([cs_w * (sx - sr), cs_h * (sy - sr), cs_w * (sx + sr), cs_h * (sy + sr)], fill=smoke)
    # open forge doorway with glowing forge inside
    d.rectangle([cs_w * 0.18, cs_h * 0.5, cs_w * 0.55, cs_h * 0.94], fill=stone_dark)
    d.rectangle([cs_w * 0.22, cs_h * 0.68, cs_w * 0.51, cs_h * 0.9], fill=forge_glow)
    d.rectangle([cs_w * 0.22, cs_h * 0.82, cs_w * 0.51, cs_h * 0.9], fill=forge_deep)
    # anvil silhouette in front (small, off to the right of the door)
    d.polygon([(cs_w * 0.65, cs_h * 0.78), (cs_w * 0.9, cs_h * 0.78),
               (cs_w * 0.9, cs_h * 0.83), (cs_w * 0.65, cs_h * 0.83)], fill=stone_dark)
    d.polygon([(cs_w * 0.7, cs_h * 0.83), (cs_w * 0.85, cs_h * 0.83),
               (cs_w * 0.82, cs_h * 0.92), (cs_w * 0.73, cs_h * 0.92)], fill=stone_dark)
    # hammer icon over the door
    d.rectangle([cs_w * 0.3, cs_h * 0.42, cs_w * 0.43, cs_h * 0.45], fill=stone_dark)
    d.rectangle([cs_w * 0.34, cs_h * 0.4, cs_w * 0.39, cs_h * 0.48], fill=stone_dark)

    return c.resize((w, h), Image.NEAREST)


# ------------------------------------------------------------- fisherman --
def make_fisherman_shack():
    """A 2-tile-wide x 2-tall wooden shack on stilts, with a dock jutting
    out and a hanging fish sign — implies water is right next to it."""
    w, h = CELL * 2, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    c = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    wood = (156, 108, 68, 255)
    wood_shade = (122, 82, 50, 255)
    wood_dark = (86, 58, 36, 255)
    roof = (128, 76, 52, 255)
    roof_shade = (94, 56, 38, 255)
    fish = (108, 168, 200, 255)
    fish_shade = (76, 128, 160, 255)

    # dock planks jutting out from the bottom-right
    for i, plank_y in enumerate((0.9, 0.94)):
        d.rectangle([cs_w * 0.05, cs_h * plank_y, cs_w * 0.98, cs_h * (plank_y + 0.03)],
                    fill=wood_shade if i == 0 else wood_dark)
    # stilts holding up the shack
    for stilt_x in (0.15, 0.45, 0.75):
        d.rectangle([cs_w * stilt_x, cs_h * 0.72, cs_w * (stilt_x + 0.04), cs_h * 0.9], fill=wood_dark)
    # shack body
    d.rectangle([cs_w * 0.1, cs_h * 0.42, cs_w * 0.8, cs_h * 0.75], fill=wood)
    # vertical plank lines
    for x in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        d.line([(cs_w * x, cs_h * 0.42), (cs_w * x, cs_h * 0.75)], fill=wood_shade,
               width=max(1, int(cs_w * 0.008)))
    d.rectangle([cs_w * 0.1, cs_h * 0.7, cs_w * 0.8, cs_h * 0.75], fill=wood_shade)
    # slanted roof
    d.polygon([(cs_w * 0.06, cs_h * 0.44), (cs_w * 0.45, cs_h * 0.12), (cs_w * 0.85, cs_h * 0.44)],
              fill=roof)
    d.polygon([(cs_w * 0.06, cs_h * 0.44), (cs_w * 0.45, cs_h * 0.12), (cs_w * 0.45, cs_h * 0.24)],
              fill=roof_shade)
    # doorway
    d.rectangle([cs_w * 0.34, cs_h * 0.55, cs_w * 0.5, cs_h * 0.75], fill=wood_dark)
    # hanging fish sign
    d.line([(cs_w * 0.68, cs_h * 0.46), (cs_w * 0.68, cs_h * 0.6)], fill=wood_dark,
           width=max(1, int(cs_w * 0.01)))
    d.ellipse([cs_w * 0.6, cs_h * 0.58, cs_w * 0.78, cs_h * 0.7], fill=fish)
    d.polygon([(cs_w * 0.6, cs_h * 0.64), (cs_w * 0.55, cs_h * 0.6), (cs_w * 0.55, cs_h * 0.68)], fill=fish)
    d.ellipse([cs_w * 0.72, cs_h * 0.6, cs_w * 0.75, cs_h * 0.63], fill=(30, 20, 24, 255))

    return c.resize((w, h), Image.NEAREST)


# --------------------------------------------------------------- fish --
def make_fish():
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    body = (108, 168, 200, 255)
    body_dark = (68, 128, 160, 255)
    belly = (232, 228, 200, 255)
    fin = (86, 140, 176, 255)
    eye = (30, 20, 24, 255)
    d.ellipse([s(4), s(11), s(26), s(23)], fill=body)
    d.ellipse([s(4), s(17), s(26), s(23)], fill=body_dark)
    d.ellipse([s(8), s(15), s(22), s(21)], fill=belly)
    # tail
    d.polygon([(s(4), s(17)), (s(0), s(11)), (s(0), s(23))], fill=fin)
    # top fin
    d.polygon([(s(11), s(11)), (s(16), s(5)), (s(20), s(11))], fill=fin)
    # eye
    d.ellipse([s(21), s(14), s(23), s(16)], fill=eye)
    return c.resize((CELL, CELL), Image.NEAREST)


# --------------------------------------------------------------- sword icon --
def make_sword():
    c = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    blade = (232, 232, 240, 255)
    edge = (176, 176, 190, 255)
    guard = (168, 128, 60, 255)
    grip = (86, 58, 40, 255)
    pommel = (208, 168, 80, 255)
    # blade
    d.polygon([(s(4), s(28)), (s(9), s(23)), (s(23), s(9)), (s(28), s(4)),
               (s(24), s(8)), (s(10), s(24))], fill=blade)
    d.polygon([(s(4), s(28)), (s(9), s(23)), (s(10), s(24))], fill=edge)
    # crossguard
    d.polygon([(s(6), s(26)), (s(12), s(20)), (s(14), s(22)), (s(8), s(28))], fill=guard)
    # grip
    d.rectangle([s(3), s(25), s(8), s(30)], fill=grip)
    # pommel
    d.ellipse([s(2), s(27), s(6), s(31)], fill=pommel)
    return c.resize((CELL, CELL), Image.NEAREST)


def main():
    for i in range(1, WATER_VARIANTS + 1):
        make_water_strip(variant_seed=i * 97).save(os.path.join(OUT_DIR, f"Water{i}.png"))
        print(f"wrote Water{i}.png (3-frame ripple strip)")
    make_blacksmith().save(os.path.join(OUT_DIR, "Blacksmith.png"))
    print("wrote Blacksmith.png")
    make_fisherman_shack().save(os.path.join(OUT_DIR, "FishermanShack.png"))
    print("wrote FishermanShack.png")
    make_fish().save(os.path.join(OUT_DIR, "Fish.png"))
    print("wrote Fish.png")
    make_sword().save(os.path.join(OUT_DIR, "Sword.png"))
    print("wrote Sword.png")


if __name__ == "__main__":
    main()
