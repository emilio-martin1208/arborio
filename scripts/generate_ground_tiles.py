"""Regenerates the grass/sand ground tiles (FarmImg/Ground1..48.png) as
3-frame wind-sway animation strips with natural color variation between
patches, plus a couple of small sparse flower decorations
(FarmImg/Decor1-2.png) that get scattered thinly on top by farm.py.

Each Ground file is a horizontal strip of 3 frames (neutral, lean-left,
lean-right) — the same blade layout redrawn with tilted tips, so it
reads as blades swaying rather than a flicker. Re-run to tweak.

Palettes are generated programmatically (12 per biome family) by jittering
hue/saturation/lightness around one anchor color per family, rather than
hand-authoring dozens of near-identical tuples — the family still reads as
one cohesive biome (same hue neighborhood) while every tile is a little
different, instead of the same 2-6 textures repeating constantly.
"""
import colorsys
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

VARIANTS_PER_FAMILY = 12


def _hls_to_rgb255(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0.03, min(0.97, l)), max(0.0, min(1.0, s)))
    return (round(r * 255), round(g * 255), round(b * 255), 255)


def make_palette_family(anchor_rgb, count, seed, hue_jitter=0.025, sat_jitter=0.10, light_jitter=0.05,
                         light_step=0.13, dark_step=0.15):
    """count (base, light, dark) palettes clustered around one anchor color —
    same hue neighborhood (so the biome still reads as one cohesive lawn),
    each with its own small sun/shade/moisture-style push in hue/sat/lightness."""
    rng = random.Random(seed)
    r, g, b = [c / 255 for c in anchor_rgb]
    anchor_h, anchor_l, anchor_s = colorsys.rgb_to_hls(r, g, b)
    palettes = []
    for _ in range(count):
        h = anchor_h + rng.uniform(-hue_jitter, hue_jitter)
        s = anchor_s + rng.uniform(-sat_jitter, sat_jitter)
        l = anchor_l + rng.uniform(-light_jitter, light_jitter)
        palettes.append(dict(
            base=_hls_to_rgb255(h, l, s),
            light=_hls_to_rgb255(h, l + light_step, s),
            dark=_hls_to_rgb255(h, l - dark_step, s),
        ))
    return palettes


# Grouped per-biome; meadow and maple forest share the same ground (only
# their tree mix differs). Each family's anchor color is the original
# hand-picked base tone from before this was made procedural.
VARIANT_PALETTES = make_palette_family((94, 153, 64), VARIANTS_PER_FAMILY, seed=1001)
DIRT_FLECK = (118, 96, 66, 140)

# Sakura grove: soft green with pale pink fallen-petal flecks instead of dirt
SAKURA_PALETTES = make_palette_family((120, 162, 108), VARIANTS_PER_FAMILY, seed=1002,
                                       hue_jitter=0.02, sat_jitter=0.08)
PETAL_FLECK = (240, 196, 210, 210)

# Jungle: deep, saturated, denser green
JUNGLE_PALETTES = make_palette_family((38, 108, 56), VARIANTS_PER_FAMILY, seed=1003,
                                       hue_jitter=0.02, sat_jitter=0.08)

# Desert: sand, no blades — static texture (dunes/pebbles instead of grass)
SAND_PALETTES = make_palette_family((216, 190, 140), VARIANTS_PER_FAMILY, seed=1004,
                                     hue_jitter=0.015, sat_jitter=0.06, light_jitter=0.04,
                                     light_step=0.08, dark_step=0.11)

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
    # Ground1-12: meadow/maple (shared). Ground13-24: sakura. Ground25-36: jungle.
    # Ground37-48: desert sand. Indices are fixed contracts with farm.py's
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
