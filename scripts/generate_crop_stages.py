"""Generates the generic (crop-agnostic) growth-stage sprites used before
a crop reaches its mature/harvestable art, plus a withered/dead stage
shown after a ripe crop is left too long: FarmImg/Stage_Seedling.png,
Stage_Sprout.png, Stage_Growing.png, Stage_Withered.png.
"""
import os

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
CS = CELL * SCALE

LEAF = (86, 158, 62, 255)
LEAF_DARK = (62, 122, 44, 255)
STEM = (74, 132, 50, 255)
WITHER = (150, 122, 78, 255)
WITHER_DARK = (110, 88, 56, 255)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")


def s(v):
    return v * SCALE


def make_seedling():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    base_y = 25
    draw.line([(s(16), s(base_y)), (s(16), s(base_y - 4))], fill=STEM, width=int(s(0.55)))
    draw.ellipse([s(13.5), s(base_y - 6.5), s(18.5), s(base_y - 2.5)], fill=LEAF)
    draw.ellipse([s(14.7), s(base_y - 5.5), s(17.3), s(base_y - 3.2)], fill=LEAF_DARK)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_sprout():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    base_y = 25
    draw.line([(s(16), s(base_y)), (s(16), s(base_y - 5))], fill=STEM, width=int(s(0.4)))
    # two small leaves
    draw.ellipse([s(12.5), s(base_y - 7), s(16), s(base_y - 4)], fill=LEAF)
    draw.ellipse([s(16), s(base_y - 8), s(19.5), s(base_y - 5)], fill=LEAF_DARK)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_growing():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    base_y = 26
    draw.line([(s(16), s(base_y)), (s(16), s(base_y - 9))], fill=STEM, width=int(s(0.5)))
    # a fuller leafy bush, no fruit yet
    leaf_positions = [
        (s(12), s(base_y - 10), s(17), s(base_y - 5), LEAF),
        (s(15.5), s(base_y - 13), s(20.5), s(base_y - 7), LEAF_DARK),
        (s(11.5), s(base_y - 6), s(16.5), s(base_y - 1), LEAF_DARK),
        (s(15), s(base_y - 7), s(20), s(base_y - 2), LEAF),
    ]
    for box in leaf_positions:
        draw.ellipse(box[:4], fill=box[4])
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_withered():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    base_y = 26
    # drooping stem
    draw.line([(s(16), s(base_y)), (s(16), s(base_y - 6))], fill=WITHER_DARK, width=int(s(0.45)))
    draw.line([(s(16), s(base_y - 6)), (s(12.5), s(base_y - 8))], fill=WITHER_DARK, width=int(s(0.4)))
    draw.line([(s(16), s(base_y - 6)), (s(19.5), s(base_y - 4))], fill=WITHER_DARK, width=int(s(0.4)))
    # drooped, curled leaves
    draw.ellipse([s(10.5), s(base_y - 9.5), s(14.5), s(base_y - 6)], fill=WITHER)
    draw.ellipse([s(18), s(base_y - 6.5), s(21.5), s(base_y - 3)], fill=WITHER)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def main():
    stages = {
        "Stage_Seedling": make_seedling(),
        "Stage_Sprout": make_sprout(),
        "Stage_Growing": make_growing(),
        "Stage_Withered": make_withered(),
    }
    for name, img in stages.items():
        path = os.path.join(OUT_DIR, f"{name}.png")
        img.save(path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
