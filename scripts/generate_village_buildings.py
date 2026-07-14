"""Generates village landmark structures for extra settlement variety:
FarmImg/Well.png (a single stone well, 1 tile, sits flush on its tile) and
FarmImg/Shrine.png (a small stone shrine, 2 tiles wide x 2 tall, anchored at
the bottom like the house/stable). Drawn at higher internal resolution then
downsampled with NEAREST for crisp pixel-art edges. Re-run to tweak.
"""
import os

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

STONE = (150, 148, 142, 255)
STONE_SHADE = (114, 112, 106, 255)
STONE_DARK = (86, 84, 80, 255)
WOOD = (140, 98, 58, 255)
WOOD_SHADE = (108, 74, 42, 255)
WATER = (86, 138, 168, 255)
WATER_LIGHT = (140, 190, 214, 255)
ROOF = (120, 58, 44, 255)
ROOF_SHADE = (94, 42, 32, 255)
GOLD = (210, 176, 90, 255)
GOLD_SHADE = (168, 136, 62, 255)


def s(v):
    return v * SCALE


def make_well():
    w, h = CELL, CELL
    cs = CELL * SCALE
    canvas = Image.new("RGBA", (cs, cs), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # circular stone rim, water visible inside
    draw.ellipse([cs * 0.14, cs * 0.4, cs * 0.86, cs * 0.86], fill=STONE_DARK)
    draw.ellipse([cs * 0.18, cs * 0.38, cs * 0.82, cs * 0.78], fill=STONE)
    draw.ellipse([cs * 0.18, cs * 0.58, cs * 0.82, cs * 0.78], fill=STONE_SHADE)
    draw.ellipse([cs * 0.3, cs * 0.44, cs * 0.7, cs * 0.62], fill=WATER)
    draw.ellipse([cs * 0.34, cs * 0.45, cs * 0.56, cs * 0.54], fill=WATER_LIGHT)
    for frac in (0.28, 0.44, 0.6, 0.76):
        draw.line([(cs * frac, cs * 0.42), (cs * frac, cs * 0.8)], fill=STONE_DARK, width=max(1, int(cs * 0.012)))

    # roof posts + peaked roof over the well
    draw.rectangle([cs * 0.08, cs * 0.1, cs * 0.16, cs * 0.5], fill=WOOD)
    draw.rectangle([cs * 0.84, cs * 0.1, cs * 0.92, cs * 0.5], fill=WOOD)
    draw.rectangle([cs * 0.08, cs * 0.42, cs * 0.16, cs * 0.5], fill=WOOD_SHADE)
    draw.rectangle([cs * 0.84, cs * 0.42, cs * 0.92, cs * 0.5], fill=WOOD_SHADE)
    draw.polygon([(cs * 0.02, cs * 0.14), (cs * 0.5, cs * 0.0), (cs * 0.98, cs * 0.14), (cs * 0.98, cs * 0.22),
                  (cs * 0.5, cs * 0.08), (cs * 0.02, cs * 0.22)], fill=ROOF)
    draw.polygon([(cs * 0.02, cs * 0.14), (cs * 0.5, cs * 0.0), (cs * 0.5, cs * 0.08), (cs * 0.02, cs * 0.22)],
                 fill=ROOF_SHADE)

    # rope + bucket hanging from the crossbeam
    draw.rectangle([cs * 0.14, cs * 0.4, cs * 0.86, cs * 0.44], fill=WOOD_SHADE)
    draw.line([(cs * 0.5, cs * 0.42), (cs * 0.5, cs * 0.56)], fill=(80, 64, 48, 255), width=max(1, int(cs * 0.012)))
    draw.rectangle([cs * 0.44, cs * 0.54, cs * 0.56, cs * 0.62], fill=WOOD)

    return canvas.resize((w, h), Image.NEAREST)


def make_shrine():
    w, h = CELL * 2, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # stone base platform
    draw.rectangle([cs_w * 0.06, cs_h * 0.72, cs_w * 0.94, cs_h * 0.96], fill=STONE)
    draw.rectangle([cs_w * 0.06, cs_h * 0.86, cs_w * 0.94, cs_h * 0.96], fill=STONE_SHADE)

    # two side pillars + a central shrine body
    for px in (0.12, 0.72):
        draw.rectangle([cs_w * px, cs_h * 0.34, cs_w * (px + 0.16), cs_h * 0.74], fill=STONE)
        draw.rectangle([cs_w * px, cs_h * 0.34, cs_w * (px + 0.05), cs_h * 0.74], fill=STONE_SHADE)
    draw.rectangle([cs_w * 0.32, cs_h * 0.4, cs_w * 0.68, cs_h * 0.74], fill=STONE_DARK)
    draw.rectangle([cs_w * 0.36, cs_h * 0.46, cs_w * 0.64, cs_h * 0.74], fill=(40, 38, 44, 255))

    # a small glowing gold emblem inside the alcove
    draw.ellipse([cs_w * 0.44, cs_h * 0.52, cs_w * 0.56, cs_h * 0.64], fill=GOLD)
    draw.ellipse([cs_w * 0.47, cs_h * 0.55, cs_w * 0.53, cs_h * 0.61], fill=GOLD_SHADE)

    # peaked stone roof over everything, with a jagged/weathered underside
    draw.polygon([(cs_w * 0.02, cs_h * 0.36), (cs_w * 0.5, cs_h * 0.04), (cs_w * 0.98, cs_h * 0.36),
                  (cs_w * 0.98, cs_h * 0.46), (cs_w * 0.5, cs_h * 0.16), (cs_w * 0.02, cs_h * 0.46)], fill=STONE)
    draw.polygon([(cs_w * 0.02, cs_h * 0.36), (cs_w * 0.5, cs_h * 0.04), (cs_w * 0.5, cs_h * 0.16),
                  (cs_w * 0.02, cs_h * 0.46)], fill=STONE_SHADE)
    for i in range(5):
        fx = 0.1 + i * 0.18
        draw.polygon([(cs_w * fx, cs_h * 0.4), (cs_w * (fx + 0.06), cs_h * 0.34), (cs_w * (fx + 0.12), cs_h * 0.4)],
                     fill=STONE_DARK)

    return canvas.resize((w, h), Image.NEAREST)


def main():
    make_well().save(os.path.join(OUT_DIR, "Well.png"))
    print("wrote Well.png")
    make_shrine().save(os.path.join(OUT_DIR, "Shrine.png"))
    print("wrote Shrine.png")


if __name__ == "__main__":
    main()
