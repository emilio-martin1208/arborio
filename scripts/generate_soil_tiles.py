"""Generates irregular, rounded tilled-soil patches (FarmImg/Soil1-12.png)
to replace the old perfect-square dirt tile. Each is a random organic
blob so planted plots look hand-tilled rather than gridded. Re-run to
regenerate/tweak.
"""
import math
import os
import random

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
CS = CELL * SCALE

DIRT_DARK = (86, 58, 34, 255)
DIRT_MID = (112, 78, 46, 255)
DIRT_LIGHT = (134, 96, 58, 255)
SPECK_DARK = (68, 46, 26, 255)
SPECK_LIGHT = (154, 114, 70, 255)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")


def blob_points(rng, cx, cy, base_r, jitter, points=14):
    pts = []
    for i in range(points):
        angle = 2 * math.pi * i / points
        r = base_r * (1 + rng.uniform(-jitter, jitter))
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def make_soil_tile(seed):
    rng = random.Random(seed)
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    cx, cy = CS / 2, CS / 2
    base_r = CS * 0.42

    # soft dark shadow rim (slightly larger, drawn first)
    shadow_pts = blob_points(rng, cx, cy + CS * 0.02, base_r * 1.04, 0.16)
    draw.polygon(shadow_pts, fill=DIRT_DARK)

    # main dirt patch
    main_pts = blob_points(rng, cx, cy, base_r, 0.16)
    draw.polygon(main_pts, fill=DIRT_MID)

    # speckles for texture
    for _ in range(26):
        angle = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0, base_r * 0.85)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        speck_r = rng.uniform(CS * 0.01, CS * 0.025)
        color = SPECK_DARK if rng.random() < 0.6 else SPECK_LIGHT
        draw.ellipse([x - speck_r, y - speck_r, x + speck_r, y + speck_r], fill=color)

    # a couple of lighter clumps for depth
    for _ in range(4):
        angle = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0, base_r * 0.6)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        clump_r = rng.uniform(CS * 0.05, CS * 0.09)
        draw.ellipse([x - clump_r, y - clump_r, x + clump_r, y + clump_r], fill=DIRT_LIGHT)

    return canvas.resize((CELL, CELL), Image.NEAREST)


def main():
    for i in range(1, 13):
        tile = make_soil_tile(seed=i * 29)
        path = os.path.join(OUT_DIR, f"Soil{i}.png")
        tile.save(path)
        print(f"wrote {path}")

    old_soil = os.path.join(OUT_DIR, "soil.png")
    if os.path.exists(old_soil):
        os.remove(old_soil)
        print(f"removed unused {old_soil}")


if __name__ == "__main__":
    main()
