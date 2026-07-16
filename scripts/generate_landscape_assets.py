"""Generates landscape detail assets: trees (FarmImg/Tree1.png,
FarmImg/Tree2.png — 1 tile wide x 2 tiles tall, anchored at the bottom
like the house), extra ground decorations (FarmImg/Decor3.png rock,
FarmImg/Decor4.png bush), and a dirt walking path tile
(FarmImg/Path.png). Drawn at higher internal resolution then
downsampled with NEAREST for crisp pixel-art edges. Re-run to tweak.
"""
import math
import os
import random

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

DEFAULT_TRUNK = (96, 64, 40, 255)
DEFAULT_TRUNK_SHADE = (74, 48, 30, 255)

# Each species varies shape, size, and color so the treeline reads as a
# real mixed forest rather than one tree recolored.
TREE_SPECIES = [
    dict(name="oak", shape="round", canopy=(46, 106, 48, 255), shade=(28, 80, 34, 255), outline=(20, 56, 26, 255),
         canopy_r=0.60, canopy_cy=0.40, trunk_h=0.20, trunk_w=0.22),
    dict(name="tall_oak", shape="round", canopy=(32, 88, 42, 255), shade=(20, 64, 30, 255), outline=(16, 46, 22, 255),
         canopy_r=0.48, canopy_cy=0.30, trunk_h=0.32, trunk_w=0.18,
         trunk=(84, 56, 34, 255), trunk_shade=(64, 42, 26, 255)),
    dict(name="pine", shape="pine", canopy=(36, 90, 66, 255), shade=(24, 66, 50, 255), outline=(18, 50, 38, 255),
         canopy_r=0.54, canopy_cy=0.5, trunk_h=0.12, trunk_w=0.16,
         trunk=(80, 54, 36, 255), trunk_shade=(60, 40, 26, 255)),
    dict(name="bushy", shape="bushy", canopy=(92, 128, 52, 255), shade=(68, 100, 40, 255), outline=(50, 76, 30, 255),
         canopy_r=0.68, canopy_cy=0.5, trunk_h=0.14, trunk_w=0.26),
    dict(name="maple", shape="round", canopy=(200, 120, 54, 255), shade=(162, 90, 42, 255), outline=(122, 66, 32, 255),
         canopy_r=0.58, canopy_cy=0.40, trunk_h=0.20, trunk_w=0.22),
    dict(name="sapling", shape="round", canopy=(70, 152, 66, 255), shade=(48, 120, 52, 255), outline=(34, 92, 40, 255),
         canopy_r=0.40, canopy_cy=0.58, trunk_h=0.13, trunk_w=0.15),
    # Biome specials: sakura grove, jungle, desert
    dict(name="sakura", shape="round", canopy=(232, 158, 186, 255), shade=(206, 122, 158, 255), outline=(160, 90, 122, 255),
         canopy_r=0.60, canopy_cy=0.38, trunk_h=0.22, trunk_w=0.20,
         trunk=(90, 62, 46, 255), trunk_shade=(68, 46, 34, 255)),
    dict(name="jungle_tree", shape="bushy", canopy=(30, 96, 54, 255), shade=(18, 70, 40, 255), outline=(12, 50, 30, 255),
         canopy_r=0.72, canopy_cy=0.46, trunk_h=0.22, trunk_w=0.24),
    dict(name="cactus", shape="cactus", canopy=(70, 130, 70, 255), shade=(48, 100, 52, 255), outline=(34, 76, 40, 255)),
    dict(name="snow_pine", shape="pine", canopy=(224, 232, 236, 255), shade=(176, 196, 208, 255), outline=(140, 160, 176, 255),
         canopy_r=0.54, canopy_cy=0.5, trunk_h=0.12, trunk_w=0.16,
         trunk=(70, 56, 44, 255), trunk_shade=(52, 40, 32, 255)),
    # Archipelago special: a tall thin trunk topped with a starburst of
    # drooping fronds, for the ocean's tropical islands.
    dict(name="palm", shape="palm", canopy=(70, 148, 62, 255), shade=(50, 116, 50, 255), outline=(34, 88, 38, 255),
         canopy_r=0.62, canopy_cy=0.2, trunk_h=0.6, trunk_w=0.1,
         trunk=(168, 132, 84, 255), trunk_shade=(128, 98, 60, 255)),
]

ROCK = (150, 148, 142, 255)
ROCK_SHADE = (114, 112, 106, 255)
ROCK_HIGHLIGHT = (182, 180, 172, 255)

BUSH = (48, 108, 48, 255)
BUSH_SHADE = (30, 82, 34, 255)
BUSH_OUTLINE = (24, 62, 28, 255)

PATH_BASE = (176, 160, 130, 255)
PATH_SPECK_DARK = (150, 132, 100, 255)
PATH_SPECK_LIGHT = (196, 182, 152, 255)


#Trees are drawn on a canvas 2 tiles wide (canopies can be wider than a
#single tile) but every size fraction is relative to ref_w (1 tile), so
#the canopy stays the same visual size — it just has room not to clip.
def _draw_trunk(draw, cs_w, cs_h, ref_w, species):
    trunk = species.get("trunk", DEFAULT_TRUNK)
    trunk_shade = species.get("trunk_shade", DEFAULT_TRUNK_SHADE)
    trunk_w = ref_w * species["trunk_w"]
    trunk_h = cs_h * species["trunk_h"]
    trunk_x0 = cs_w / 2 - trunk_w / 2
    draw.rectangle([trunk_x0, cs_h - trunk_h, trunk_x0 + trunk_w, cs_h], fill=trunk)
    draw.rectangle([trunk_x0, cs_h - trunk_h, trunk_x0 + trunk_w * 0.4, cs_h], fill=trunk_shade)
    return cs_h - trunk_h  # y where the canopy should sit on top of the trunk


def _draw_organic_canopy(draw, cs_w, cs_h, ref_w, species, rng):
    """An irregular, lumpy silhouette built from several overlapping
    randomly-placed lobes (circles) instead of one perfect ellipse — since
    they share the same solid fill color, overlapping lobes merge into one
    blob with no visible seams, so this reads as a single natural crown
    rather than a cluster of balls. rng is seeded per-tree-shape-variant,
    so every variant gets a different lobe layout while staying within the
    species' overall size envelope — this is what makes same-species trees
    actually look different from each other instead of reusing one fixed
    silhouette."""
    canopy_cy = cs_h * species["canopy_cy"]
    canopy_r = ref_w * species["canopy_r"]
    outline_pad = ref_w * 0.05

    lobe_count = rng.randint(5, 8)
    lobes = [(0.0, -0.05, rng.uniform(0.72, 0.85))]  # centered anchor lobe closes any gap
    for _ in range(lobe_count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0.15, 0.62)
        lobes.append((math.cos(angle) * dist, math.sin(angle) * dist * 0.85, rng.uniform(0.4, 0.72)))

    for dx, dy, scale in lobes:
        cx, cy, r = cs_w / 2 + dx * canopy_r, canopy_cy + dy * canopy_r, canopy_r * scale
        draw.ellipse([cx - r - outline_pad, cy - r * 0.9 - outline_pad,
                      cx + r + outline_pad, cy + r * 0.9 + outline_pad], fill=species["outline"])
    for dx, dy, scale in lobes:
        cx, cy, r = cs_w / 2 + dx * canopy_r, canopy_cy + dy * canopy_r, canopy_r * scale
        draw.ellipse([cx - r, cy - r * 0.9, cx + r, cy + r * 0.9], fill=species["canopy"])

    for _ in range(16):
        angle = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0, canopy_r * 0.68)
        x = cs_w / 2 + r * math.cos(angle)
        y = canopy_cy + r * math.sin(angle) * 0.9
        br = rng.uniform(canopy_r * 0.14, canopy_r * 0.24)
        draw.ellipse([x - br, y - br, x + br, y + br], fill=species["shade"])


def _draw_bushy_canopy(draw, cs_w, cs_h, ref_w, species, rng):
    canopy_cy = cs_h * species["canopy_cy"]
    canopy_r = ref_w * species["canopy_r"]
    base_lobes = [(-0.42, 0.08, 0.72), (0.42, 0.08, 0.72), (0.0, -0.12, 1.0)]
    # per-variant jitter on the base 3-lobe layout, plus 1-2 extra small
    # lobes at random, so bushy/jungle trees vary between instances too
    lobes = [(dx + rng.uniform(-0.08, 0.08), dy + rng.uniform(-0.06, 0.06), scale * rng.uniform(0.9, 1.1))
             for dx, dy, scale in base_lobes]
    for _ in range(rng.randint(0, 2)):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0.3, 0.6)
        lobes.append((math.cos(angle) * dist, math.sin(angle) * dist * 0.7, rng.uniform(0.35, 0.55)))

    for dx, dy, scale in lobes:
        cx, cy, r = cs_w / 2 + dx * canopy_r, canopy_cy + dy * canopy_r, canopy_r * scale
        pad = ref_w * 0.05
        draw.ellipse([cx - r - pad, cy - r * 0.85 - pad, cx + r + pad, cy + r * 0.85 + pad], fill=species["outline"])
    for dx, dy, scale in lobes:
        cx, cy, r = cs_w / 2 + dx * canopy_r, canopy_cy + dy * canopy_r, canopy_r * scale
        draw.ellipse([cx - r, cy - r * 0.85, cx + r, cy + r * 0.85], fill=species["canopy"])
    for _ in range(14):
        angle = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0, canopy_r * 0.9)
        x = cs_w / 2 + r * math.cos(angle)
        y = canopy_cy - canopy_r * 0.15 + r * math.sin(angle) * 0.55
        br = rng.uniform(canopy_r * 0.12, canopy_r * 0.2)
        draw.ellipse([x - br, y - br, x + br, y + br], fill=species["shade"])


def _draw_pine_canopy(draw, cs_w, cs_h, ref_w, species, trunk_top_y, rng):
    half_w = ref_w * species["canopy_r"]
    top_y = cs_h * 0.06
    layer_count = 4
    layer_h = (trunk_top_y - top_y) / layer_count
    outline_pad = ref_w * 0.04
    # small per-layer jitter (width, a slight left/right lean) so conifers
    # aren't perfectly symmetric cones but still read as coniferous, unlike
    # the lumpier organic broadleaf canopies
    jitter = [(rng.uniform(0.9, 1.1), rng.uniform(-0.06, 0.06)) for _ in range(layer_count)]
    for i in range(layer_count):
        frac = i / (layer_count - 1)  # 0 at top (narrow), 1 at bottom (wide)
        w_scale, lean = jitter[i]
        w = half_w * (0.35 + 0.65 * frac) * w_scale
        y0 = top_y + i * layer_h * 0.82
        y1 = y0 + layer_h * 1.35
        cx = cs_w / 2 + lean * ref_w
        draw.polygon([(cx, y0 - outline_pad), (cx + w + outline_pad, y1 + outline_pad),
                      (cx - w - outline_pad, y1 + outline_pad)], fill=species["outline"])
    for i in range(layer_count):
        frac = i / (layer_count - 1)
        w_scale, lean = jitter[i]
        w = half_w * (0.35 + 0.65 * frac) * w_scale
        y0 = top_y + i * layer_h * 0.82
        y1 = y0 + layer_h * 1.35
        cx = cs_w / 2 + lean * ref_w
        color = species["canopy"] if i % 2 == 0 else species["shade"]
        draw.polygon([(cx, y0), (cx + w, y1), (cx - w, y1)], fill=color)


def _draw_cactus(draw, cs_w, cs_h, ref_w, species):
    body_w = ref_w * 0.32
    body_h = cs_h * 0.5
    cx = cs_w / 2
    top_y = cs_h - body_h
    pad = ref_w * 0.04

    draw.rounded_rectangle([cx - body_w / 2 - pad, top_y - pad, cx + body_w / 2 + pad, cs_h],
                            radius=body_w / 2 + pad, fill=species["outline"])
    draw.rounded_rectangle([cx - body_w / 2, top_y, cx + body_w / 2, cs_h],
                            radius=body_w / 2, fill=species["canopy"])
    draw.rounded_rectangle([cx - body_w / 2, top_y, cx - body_w * 0.1, cs_h],
                            radius=body_w / 2, fill=species["shade"])

    # one arm poking out to the side
    arm_w = body_w * 0.62
    arm_top = top_y + body_h * 0.3
    arm_bottom = top_y + body_h * 0.62
    draw.rounded_rectangle([cx + body_w / 2 - arm_w * 0.4 - pad, arm_top - arm_w / 2 - pad,
                             cx + body_w / 2 + arm_w * 0.9 + pad, arm_bottom + arm_w / 2 + pad],
                            radius=arm_w / 2 + pad, fill=species["outline"])
    draw.rounded_rectangle([cx + body_w / 2 - arm_w * 0.4, arm_top - arm_w / 2,
                             cx + body_w / 2 + arm_w * 0.9, arm_bottom + arm_w / 2],
                            radius=arm_w / 2, fill=species["canopy"])


def _draw_palm_canopy(draw, cs_w, cs_h, ref_w, species, trunk_top_y, rng):
    """A starburst of drooping frond blades radiating from the crown, plus
    a couple of coconuts — simplified to flat blades rather than trying to
    render individual leaflets, which reads better at this pixel scale."""
    cx = cs_w / 2
    cy = trunk_top_y + cs_h * 0.015
    frond_len = ref_w * species["canopy_r"]
    frond_w = ref_w * 0.17
    base_angles = [-100, -62, -28, 4, 32, 66, 102]
    angles = [a + rng.uniform(-8, 8) for a in base_angles]
    outline_pad = ref_w * 0.035

    def frond_end(angle_deg, length):
        rad = math.radians(angle_deg - 90)
        return cx + math.cos(rad) * length, cy + math.sin(rad) * length * 0.7 + length * 0.3

    for pad, shrink, use_shade in ((outline_pad, 1.0, None), (0, 0.94, True)):
        for a in angles:
            ex, ey = frond_end(a, frond_len * shrink)
            mx, my = (cx + ex) / 2, (cy + ey) / 2
            rad = math.radians(a - 90)
            perp_x, perp_y = -math.sin(rad), math.cos(rad)
            w = frond_w + pad
            fill = species["outline"] if use_shade is None else (species["canopy"] if abs(a) < 20 else species["shade"])
            draw.polygon([(cx, cy), (mx + perp_x * w, my + perp_y * w),
                          (ex, ey), (mx - perp_x * w, my - perp_y * w)], fill=fill)

    for _ in range(rng.randint(2, 3)):
        ox = cx + rng.uniform(-0.08, 0.08) * ref_w
        oy = cy + rng.uniform(0.0, 0.1) * ref_w
        r = ref_w * 0.055
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(94, 66, 42, 255))


def make_tree(rng_seed, species):
    # canvas is 2 tiles wide so wide canopies have room; ref_w (1 tile) is
    # what all the species size fractions are relative to
    w, h = CELL * 2, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    ref_w = CELL * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    rng = random.Random(rng_seed)

    if species["shape"] == "cactus":
        _draw_cactus(draw, cs_w, cs_h, ref_w, species)
        return canvas.resize((w, h), Image.NEAREST)

    trunk_top_y = _draw_trunk(draw, cs_w, cs_h, ref_w, species)

    if species["shape"] == "pine":
        _draw_pine_canopy(draw, cs_w, cs_h, ref_w, species, trunk_top_y, rng)
    elif species["shape"] == "bushy":
        _draw_bushy_canopy(draw, cs_w, cs_h, ref_w, species, rng)
    elif species["shape"] == "palm":
        _draw_palm_canopy(draw, cs_w, cs_h, ref_w, species, trunk_top_y, rng)
    else:
        _draw_organic_canopy(draw, cs_w, cs_h, ref_w, species, rng)

    return canvas.resize((w, h), Image.NEAREST)


def make_rock():
    cs = CELL * SCALE
    canvas = Image.new("RGBA", (cs, cs), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    cx, cy = cs * 0.5, cs * 0.62
    draw.ellipse([cx - cs * 0.3, cy - cs * 0.2, cx + cs * 0.3, cy + cs * 0.22], fill=ROCK_SHADE)
    draw.ellipse([cx - cs * 0.27, cy - cs * 0.22, cx + cs * 0.2, cy + cs * 0.14], fill=ROCK)
    draw.ellipse([cx - cs * 0.14, cy - cs * 0.18, cx - cs * 0.02, cy - cs * 0.08], fill=ROCK_HIGHLIGHT)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_bush():
    cs = CELL * SCALE
    canvas = Image.new("RGBA", (cs, cs), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    rng = random.Random(7)
    cx, cy = cs * 0.5, cs * 0.6
    draw.ellipse([cx - cs * 0.36, cy - cs * 0.28, cx + cs * 0.36, cy + cs * 0.3], fill=BUSH_OUTLINE)
    draw.ellipse([cx - cs * 0.32, cy - cs * 0.24, cx + cs * 0.32, cy + cs * 0.26], fill=BUSH)
    for _ in range(6):
        angle = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0, cs * 0.2)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle) * 0.8
        br = rng.uniform(cs * 0.05, cs * 0.09)
        draw.ellipse([x - br, y - br, x + br, y + br], fill=BUSH_SHADE)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_path():
    cs = CELL * SCALE
    canvas = Image.new("RGBA", (cs, cs), PATH_BASE)
    draw = ImageDraw.Draw(canvas)
    rng = random.Random(42)
    for _ in range(30):
        x = rng.uniform(0, cs)
        y = rng.uniform(0, cs)
        r = rng.uniform(cs * 0.015, cs * 0.03)
        color = PATH_SPECK_DARK if rng.random() < 0.6 else PATH_SPECK_LIGHT
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
    return canvas.resize((CELL, CELL), Image.NEAREST)


#Each species gets several shape variants (different lobe layout/jitter),
#assigned randomly per tree at world-gen time in farm.py, so a stand of
#oaks doesn't reuse one fixed silhouette for every single tree.
TREE_SHAPE_VARIANTS = 4


def main():
    for i, species in enumerate(TREE_SPECIES, start=1):
        for j in range(TREE_SHAPE_VARIANTS):
            path = os.path.join(OUT_DIR, f"Tree{i}_v{j}.png")
            make_tree(rng_seed=i * 23 + j * 997, species=species).save(path)
        print(f"wrote Tree{i}_v0..{TREE_SHAPE_VARIANTS - 1}.png ({species['name']})")

    make_rock().save(os.path.join(OUT_DIR, "Decor3.png"))
    make_bush().save(os.path.join(OUT_DIR, "Decor4.png"))
    make_path().save(os.path.join(OUT_DIR, "Path.png"))
    print("wrote Decor3.png, Decor4.png, Path.png")


if __name__ == "__main__":
    main()
