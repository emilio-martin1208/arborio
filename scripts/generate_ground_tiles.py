"""Regenerates the grass ground tiles (FarmImg/Ground1..6.png) as
3-frame wind-sway animation strips with natural color variation between
patches, plus a couple of small sparse flower decorations
(FarmImg/Decor1-2.png) that get scattered thinly on top by farm.py.

Each Ground file is a horizontal strip of 3 frames (neutral, lean-left,
lean-right) — the same blade layout redrawn with tilted tips, so it
reads as blades swaying rather than a flicker. Re-run to tweak.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

CELL = 32
SCALE = 8
# Each grass frame is drawn oversized and overlapped when rendered in-game
# (see GRASS_EXPORT_CELL in farm.py) so blade tips spill across tile
# boundaries instead of every tile reading as a hard perfect square.
OVERFLOW = 0.22
EXPORT_CELL = round(CELL * (1 + 2 * OVERFLOW))  # 46
AREA_RATIO = (EXPORT_CELL / CELL) ** 2
CS = EXPORT_CELL * SCALE

# Each palette is a subtly different natural grass patch (sun/shade/moisture
# variation) rather than a wildly different texture, so the field still
# reads as one cohesive lawn. Grouped per-biome; meadow and maple forest
# share the same ground (only their tree mix differs).
VARIANT_PALETTES = [
    dict(base=(94, 153, 64), light=(118, 178, 86), dark=(76, 126, 50)),
    dict(base=(104, 150, 58), light=(128, 174, 80), dark=(84, 122, 46)),
    dict(base=(80, 142, 72), light=(102, 166, 94), dark=(62, 114, 56)),
    dict(base=(110, 158, 62), light=(134, 182, 84), dark=(88, 130, 48)),
    dict(base=(88, 134, 60), light=(110, 158, 82), dark=(68, 108, 46)),
    dict(base=(98, 156, 74), light=(122, 180, 96), dark=(78, 128, 58)),
]
DIRT_FLECK = (118, 96, 66, 140)

# Sakura grove: soft green with pale pink fallen-petal flecks instead of dirt
SAKURA_PALETTES = [
    dict(base=(120, 162, 108), light=(144, 186, 130), dark=(98, 136, 88)),
    dict(base=(132, 168, 118), light=(156, 192, 140), dark=(108, 144, 96)),
]
PETAL_FLECK = (240, 196, 210, 210)

# Jungle: deep, saturated, denser green
JUNGLE_PALETTES = [
    dict(base=(38, 108, 56), light=(54, 132, 70), dark=(24, 82, 42)),
    dict(base=(46, 118, 62), light=(64, 142, 78), dark=(30, 90, 48)),
]

# Desert: sand, no blades — static texture (dunes/pebbles instead of grass)
SAND_PALETTES = [
    dict(base=(216, 190, 140), light=(232, 208, 160), dark=(190, 164, 114)),
    dict(base=(206, 178, 128), light=(224, 198, 150), dark=(180, 152, 104)),
]

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")


def _make_edge_mask(rng):
    """An alpha mask that keeps the tile's nominal core rectangle fully
    solid (guaranteeing full coverage, never a gap) while giving the
    outer overflow margin an irregular, non-rectangular silhouette via
    random soft blobs poking out from each edge. Blurred for a soft,
    organic boundary instead of a crisp line."""
    margin = CS * (OVERFLOW / (1 + 2 * OVERFLOW))
    mask = Image.new("L", (CS, CS), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rectangle([margin, margin, CS - margin, CS - margin], fill=255)

    edge_lines = [
        lambda t: (margin + t * (CS - 2 * margin), margin),       # top
        lambda t: (margin + t * (CS - 2 * margin), CS - margin),  # bottom
        lambda t: (margin, margin + t * (CS - 2 * margin)),       # left
        lambda t: (CS - margin, margin + t * (CS - 2 * margin)),  # right
    ]
    for edge_fn in edge_lines:
        for _ in range(3):
            t = rng.uniform(0.12, 0.88)
            x, y = edge_fn(t)
            r = rng.uniform(margin * 0.5, margin * 1.1)
            mdraw.ellipse([x - r, y - r, x + r, y + r], fill=255)

    return mask.filter(ImageFilter.GaussianBlur(radius=max(1.0, CS * 0.016)))


def make_grass_frame(variant_seed, palette, sway, fleck_color=DIRT_FLECK):
    """sway: -1 (lean left), 0 (neutral), 1 (lean right). Same rng seed
    across sway values so it's the same blades (and the same edge shape),
    just tilted."""
    rng = random.Random(variant_seed)
    canvas = Image.new("RGBA", (CS, CS), palette["base"])
    draw = ImageDraw.Draw(canvas)
    tilt = sway * CS * 0.045

    blade_count = rng.randint(round(58 * AREA_RATIO), round(82 * AREA_RATIO))  # irregular density per tile
    for _ in range(blade_count):
        x = rng.uniform(0, CS)
        y = rng.uniform(CS * 0.08, CS)
        h = rng.uniform(CS * 0.045, CS * 0.115)
        shade = palette["light"] if rng.random() < 0.5 else palette["dark"]
        draw.line([(x, y), (x + tilt, y - h)], fill=shade, width=max(1, int(CS * 0.012)))

    # a few tiny flecks/imperfections so it doesn't read as too clean
    for _ in range(rng.randint(2, 5)):
        x, y = rng.uniform(0, CS), rng.uniform(0, CS)
        r = rng.uniform(CS * 0.008, CS * 0.02)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fleck_color)

    # rng continues from the same seed/sequence-position regardless of sway,
    # so the edge silhouette stays identical across a tile's 3 anim frames
    edge_mask = _make_edge_mask(rng)
    canvas.putalpha(edge_mask)

    return canvas.resize((EXPORT_CELL, EXPORT_CELL), Image.NEAREST)


def make_grass_strip(variant_seed, palette, fleck_color=DIRT_FLECK):
    strip = Image.new("RGBA", (EXPORT_CELL * 3, EXPORT_CELL), (0, 0, 0, 0))
    for i, sway in enumerate((0, -1, 1)):  # neutral, lean-left, lean-right
        strip.paste(make_grass_frame(variant_seed, palette, sway, fleck_color), (i * EXPORT_CELL, 0))
    return strip


def make_sand_frame(variant_seed, palette):
    """Sand doesn't sway, but still gets the same irregular edge mask and
    oversized overlap treatment as grass so biome boundaries stay consistent."""
    rng = random.Random(variant_seed)
    canvas = Image.new("RGBA", (CS, CS), palette["base"])
    draw = ImageDraw.Draw(canvas)

    # low dunes: soft wide streaks rather than blades
    for _ in range(rng.randint(10, 16)):
        x = rng.uniform(0, CS)
        y = rng.uniform(0, CS)
        w = rng.uniform(CS * 0.12, CS * 0.28)
        h = rng.uniform(CS * 0.02, CS * 0.04)
        shade = palette["light"] if rng.random() < 0.5 else palette["dark"]
        draw.ellipse([x - w, y - h, x + w, y + h], fill=shade)

    # small pebbles
    for _ in range(rng.randint(4, 8)):
        x, y = rng.uniform(0, CS), rng.uniform(0, CS)
        r = rng.uniform(CS * 0.006, CS * 0.016)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=palette["dark"])

    edge_mask = _make_edge_mask(rng)
    canvas.putalpha(edge_mask)

    return canvas.resize((EXPORT_CELL, EXPORT_CELL), Image.NEAREST)


def make_sand_strip(variant_seed, palette):
    frame = make_sand_frame(variant_seed, palette)
    strip = Image.new("RGBA", (EXPORT_CELL * 3, EXPORT_CELL), (0, 0, 0, 0))
    for i in range(3):  # static — same frame 3 times keeps the loader code uniform
        strip.paste(frame, (i * EXPORT_CELL, 0))
    return strip


def make_flower_decor(kind):
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    cx, cy = CS * 0.5, CS * 0.6

    if kind == "purple":
        petal = (176, 118, 214, 255)
        center = (250, 214, 90, 255)
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        r = CS * 0.09
        for dx, dy in offsets:
            draw.ellipse([cx + dx * r * 1.3 - r, cy + dy * r * 1.3 - r,
                          cx + dx * r * 1.3 + r, cy + dy * r * 1.3 + r], fill=petal)
        draw.ellipse([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], fill=center)
        bx, by = cx + CS * 0.16, cy - CS * 0.12
        r2 = r * 0.6
        for dx, dy in offsets:
            draw.ellipse([bx + dx * r2 * 1.3 - r2, by + dy * r2 * 1.3 - r2,
                          bx + dx * r2 * 1.3 + r2, by + dy * r2 * 1.3 + r2], fill=petal)
        draw.ellipse([bx - r2 * 0.7, by - r2 * 0.7, bx + r2 * 0.7, by + r2 * 0.7], fill=center)

    else:  # daisy
        petal = (250, 250, 246, 255)
        center = (240, 190, 60, 255)
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-0.7, -0.7), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7)]
        r = CS * 0.075
        for dx, dy in offsets:
            draw.ellipse([cx + dx * r * 1.4 - r, cy + dy * r * 1.4 - r,
                          cx + dx * r * 1.4 + r, cy + dy * r * 1.4 + r], fill=petal)
        draw.ellipse([cx - r * 0.9, cy - r * 0.9, cx + r * 0.9, cy + r * 0.9], fill=center)

    return canvas.resize((CELL, CELL), Image.NEAREST)


def main():
    # Ground1-6: meadow/maple (shared). Ground7-8: sakura. Ground9-10: jungle.
    # Ground11-12: desert sand. Indices are fixed contracts with farm.py's
    # BIOME_GROUND_INDICES — keep this order in sync if it changes.
    idx = 1
    for palette in VARIANT_PALETTES:
        strip = make_grass_strip(variant_seed=idx * 17, palette=palette)
        path = os.path.join(OUT_DIR, f"Ground{idx}.png")
        strip.save(path)
        print(f"wrote {path} ({strip.size[0]}x{strip.size[1]}) [meadow]")
        idx += 1

    for palette in SAKURA_PALETTES:
        strip = make_grass_strip(variant_seed=idx * 17, palette=palette, fleck_color=PETAL_FLECK)
        path = os.path.join(OUT_DIR, f"Ground{idx}.png")
        strip.save(path)
        print(f"wrote {path} [sakura]")
        idx += 1

    for palette in JUNGLE_PALETTES:
        strip = make_grass_strip(variant_seed=idx * 17, palette=palette)
        path = os.path.join(OUT_DIR, f"Ground{idx}.png")
        strip.save(path)
        print(f"wrote {path} [jungle]")
        idx += 1

    for palette in SAND_PALETTES:
        strip = make_sand_strip(variant_seed=idx * 17, palette=palette)
        path = os.path.join(OUT_DIR, f"Ground{idx}.png")
        strip.save(path)
        print(f"wrote {path} [desert]")
        idx += 1

    for kind, name in [("purple", "Decor1"), ("daisy", "Decor2")]:
        decor = make_flower_decor(kind)
        path = os.path.join(OUT_DIR, f"{name}.png")
        decor.save(path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
