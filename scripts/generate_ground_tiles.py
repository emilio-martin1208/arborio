"""Regenerates the grass ground tiles (FarmImg/Ground1..4.png) so they read
as one cohesive, uniform field instead of a patchwork of unrelated textures,
plus a couple of small sparse flower decorations (FarmImg/Decor1-2.png)
that get scattered thinly on top by farm.py. Re-run to tweak the palette.
"""
import os
import random

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
CS = CELL * SCALE

BASE_GREEN = (94, 153, 64, 255)
LIGHT_BLADE = (118, 178, 86, 255)
DARK_BLADE = (76, 126, 50, 255)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")


def make_grass_tile(variant_seed):
    rng = random.Random(variant_seed)
    canvas = Image.new("RGBA", (CS, CS), BASE_GREEN)
    draw = ImageDraw.Draw(canvas)

    for _ in range(70):
        x = rng.uniform(0, CS)
        y = rng.uniform(CS * 0.1, CS)
        h = rng.uniform(CS * 0.05, CS * 0.11)
        shade = LIGHT_BLADE if rng.random() < 0.5 else DARK_BLADE
        draw.line([(x, y), (x, y - h)], fill=shade, width=max(1, int(CS * 0.012)))

    return canvas.resize((CELL, CELL), Image.NEAREST)


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
        # a second, smaller bud nearby
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
    for i in range(1, 5):
        tile = make_grass_tile(variant_seed=i * 17)
        path = os.path.join(OUT_DIR, f"Ground{i}.png")
        tile.save(path)
        print(f"wrote {path}")

    for kind, name in [("purple", "Decor1"), ("daisy", "Decor2")]:
        decor = make_flower_decor(kind)
        path = os.path.join(OUT_DIR, f"{name}.png")
        decor.save(path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
