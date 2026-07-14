"""Generates biome-specific ground decor so each biome reads as visually
distinct rather than all sharing the same generic flowers/rocks/bushes:
FarmImg/DesertDecor1-2.png, JungleDecor1-2.png, SakuraDecor1-2.png,
MapleDecor1-2.png. Drawn at higher internal resolution then downsampled
with NEAREST for crisp pixel-art edges, matching the existing decor style
(see make_flower_decor in generate_ground_tiles.py). Re-run to tweak.
"""
import os
import random

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
CS = CELL * SCALE
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

random.seed(11)


def s(v):
    return v * SCALE


def make_tumbleweed():
    import math as _m
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    cx, cy = CS * 0.5, CS * 0.6
    color = (168, 138, 76, 255)
    shade = (128, 102, 54, 255)
    r = CS * 0.26
    # a tangled ball: several overlapping irregular rings rather than thin
    # spokes, which read as almost nothing at this small a scale
    for ring in range(3):
        rr = r * (0.6 + ring * 0.2)
        wobble = [(rr * (0.8 + 0.4 * random.random())) for _ in range(10)]
        points = []
        for i in range(10):
            angle = (i / 10) * 2 * _m.pi
            rad = wobble[i]
            points.append((cx + _m.cos(angle) * rad, cy + _m.sin(angle) * rad * 0.8))
        draw.line(points + [points[0]], fill=shade if ring == 1 else color, width=max(1, int(CS * 0.02)))
    draw.ellipse([cx - r * 0.35, cy - r * 0.25, cx + r * 0.35, cy + r * 0.25], fill=shade)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_bleached_bones():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    bone = (232, 222, 200, 255)
    bone_shade = (198, 186, 160, 255)
    cx, cy = CS * 0.5, CS * 0.6
    draw.ellipse([cx - CS * 0.2, cy - CS * 0.14, cx + CS * 0.2, cy + CS * 0.1], fill=bone)
    draw.ellipse([cx - CS * 0.2, cy, cx + CS * 0.2, cy + CS * 0.1], fill=bone_shade)
    draw.ellipse([cx - CS * 0.09, cy - CS * 0.1, cx - CS * 0.02, cy - CS * 0.03], fill=(90, 70, 50, 255))
    draw.ellipse([cx + CS * 0.02, cy - CS * 0.1, cx + CS * 0.09, cy - CS * 0.03], fill=(90, 70, 50, 255))
    draw.line([(cx - CS * 0.26, cy + CS * 0.16), (cx - CS * 0.12, cy + CS * 0.05)], fill=bone, width=max(1, int(CS * 0.03)))
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_mushroom_cluster(count, cap_color, cap_shade):
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    stem = (232, 220, 196, 255)
    positions = [(0.42, 0.62), (0.58, 0.7), (0.5, 0.5)][:count]
    for i, (fx, fy) in enumerate(positions):
        cx, cy = CS * fx, CS * fy
        scale = 1.0 if i == 0 else 0.7
        r = CS * 0.11 * scale
        draw.rectangle([cx - r * 0.28, cy, cx + r * 0.28, cy + r * 0.9], fill=stem)
        draw.ellipse([cx - r, cy - r * 0.5, cx + r, cy + r * 0.6], fill=cap_color)
        draw.ellipse([cx - r, cy - r * 0.1, cx + r, cy + r * 0.6], fill=cap_shade)
        for spot in ((-0.4, -0.1), (0.35, -0.15), (0.0, -0.3)):
            sx, sy = cx + spot[0] * r, cy + spot[1] * r
            draw.ellipse([sx - r * 0.14, sy - r * 0.14, sx + r * 0.14, sy + r * 0.14], fill=(250, 246, 236, 255))
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_fern():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    green = (58, 128, 62, 255)
    green_shade = (40, 98, 46, 255)
    base = (CS * 0.5, CS * 0.78)
    for angle_deg, length_frac in ((-55, 0.85), (-20, 1.0), (15, 1.0), (50, 0.85)):
        import math as _m
        angle = _m.radians(angle_deg - 90)
        length = CS * 0.32 * length_frac
        tip = (base[0] + _m.cos(angle) * length, base[1] + _m.sin(angle) * length)
        draw.line([base, tip], fill=green_shade, width=max(1, int(CS * 0.02)))
        for t in (0.3, 0.5, 0.7, 0.9):
            mx, my = base[0] + (tip[0] - base[0]) * t, base[1] + (tip[1] - base[1]) * t
            leaflet = CS * 0.05
            draw.ellipse([mx - leaflet, my - leaflet * 0.6, mx + leaflet, my + leaflet * 0.6], fill=green)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_petal_drift():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    petal = (240, 186, 204, 255)
    petal_shade = (220, 150, 176, 255)
    for _ in range(9):
        px = CS * random.uniform(0.25, 0.75)
        py = CS * random.uniform(0.5, 0.78)
        r = CS * random.uniform(0.035, 0.06)
        draw.ellipse([px - r, py - r * 0.6, px + r, py + r * 0.6], fill=random.choice([petal, petal_shade]))
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_sakura_sprout():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    stem = (96, 70, 50, 255)
    blossom = (244, 196, 214, 255)
    blossom_shade = (226, 160, 186, 255)
    cx, cy = CS * 0.5, CS * 0.78
    draw.line([(cx, cy), (cx, cy - CS * 0.24)], fill=stem, width=max(1, int(CS * 0.025)))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (-0.7, -0.7), (0.7, -0.7)):
        bx, by = cx + dx * CS * 0.07, cy - CS * 0.24 + dy * CS * 0.07
        r = CS * 0.06
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=blossom)
    draw.ellipse([cx - CS * 0.04, cy - CS * 0.28, cx + CS * 0.04, cy - CS * 0.2], fill=blossom_shade)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_leaf_pile():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    colors = [(214, 120, 48, 255), (196, 90, 40, 255), (226, 168, 60, 255)]
    for _ in range(10):
        px = CS * random.uniform(0.28, 0.72)
        py = CS * random.uniform(0.52, 0.76)
        r = CS * random.uniform(0.04, 0.065)
        color = random.choice(colors)
        draw.polygon([(px, py - r), (px + r, py), (px, py + r), (px - r, py)], fill=color)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def main():
    make_tumbleweed().save(os.path.join(OUT_DIR, "DesertDecor1.png"))
    make_bleached_bones().save(os.path.join(OUT_DIR, "DesertDecor2.png"))
    print("wrote DesertDecor1-2.png")

    make_mushroom_cluster(3, (196, 60, 56, 255), (162, 42, 40, 255)).save(os.path.join(OUT_DIR, "JungleDecor1.png"))
    make_fern().save(os.path.join(OUT_DIR, "JungleDecor2.png"))
    print("wrote JungleDecor1-2.png")

    make_petal_drift().save(os.path.join(OUT_DIR, "SakuraDecor1.png"))
    make_sakura_sprout().save(os.path.join(OUT_DIR, "SakuraDecor2.png"))
    print("wrote SakuraDecor1-2.png")

    make_leaf_pile().save(os.path.join(OUT_DIR, "MapleDecor1.png"))
    make_mushroom_cluster(2, (168, 108, 62, 255), (132, 82, 46, 255)).save(os.path.join(OUT_DIR, "MapleDecor2.png"))
    print("wrote MapleDecor1-2.png")


if __name__ == "__main__":
    main()
