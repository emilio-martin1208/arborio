"""Generates the trading structures: FarmImg/Outpost1-4.png (small stalls,
1 tile wide x 2 tall, anchored at the bottom like a tree) and
FarmImg/Marketplace1-3.png (larger stalls, 2 tiles wide x 2 tall like the
house), plus FarmImg/Emerald.png (currency icon for the HUD/trade UI).

Each stall gets a colorful striped, scalloped-edge canopy, a pennant flag,
hanging produce, and a mixed crate/barrel display — aiming for a lively
"market square" feel with real variety between stalls rather than one
stall recolored. Drawn at higher internal resolution then downsampled
with NEAREST for crisp pixel-art edges. Re-run to tweak.
"""
import os

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

POST = (120, 84, 52, 255)
POST_SHADE = (94, 64, 38, 255)
COUNTER = (172, 132, 84, 255)
COUNTER_SHADE = (144, 106, 62, 255)
CRATE = (168, 124, 74, 255)
CRATE_SHADE = (136, 98, 56, 255)
BARREL = (150, 108, 62, 255)
BARREL_BAND = (90, 66, 42, 255)

# (stripe_a, stripe_b, shade, pennant) — each a distinct market identity
CANOPY_PALETTES = [
    dict(a=(196, 70, 62, 255), b=(232, 220, 200, 255), shade=(150, 48, 44, 255), pennant=(232, 220, 200, 255)),
    dict(a=(70, 108, 176, 255), b=(238, 238, 232, 255), shade=(48, 78, 132, 255), pennant=(238, 238, 232, 255)),
    dict(a=(140, 78, 168, 255), b=(238, 206, 108, 255), shade=(100, 54, 124, 255), pennant=(238, 206, 108, 255)),
    dict(a=(74, 138, 84, 255), b=(230, 210, 160, 255), shade=(50, 100, 60, 255), pennant=(230, 210, 160, 255)),
]

GOODS_COLORS = [(210, 70, 64, 255), (232, 176, 60, 255), (120, 168, 70, 255), (168, 90, 168, 255)]

EMERALD = (58, 200, 140, 255)
EMERALD_LIGHT = (120, 232, 180, 255)
EMERALD_DARK = (34, 150, 100, 255)


def s(v):
    return v * SCALE


def _draw_awning(draw, cs_w, top_y, eave_y, scallop_y, x0, x1, palette, stripes):
    """A pitched, striped canopy with a scalloped (wavy) bottom trim."""
    peak_x = (x0 + x1) / 2
    draw.polygon([(x0, eave_y), (peak_x, top_y), (x1, eave_y), (x1, scallop_y), (x0, scallop_y)], fill=palette["a"])

    stripe_w = (x1 - x0) / stripes
    for i in range(stripes):
        if i % 2 == 0:
            continue
        sx0 = x0 + i * stripe_w
        sx1 = sx0 + stripe_w
        frac0 = abs((sx0 - peak_x) / (x1 - peak_x)) if x1 != peak_x else 0
        frac1 = abs((sx1 - peak_x) / (x1 - peak_x)) if x1 != peak_x else 0
        y0 = top_y + (eave_y - top_y) * frac0
        y1 = top_y + (eave_y - top_y) * frac1
        draw.polygon([(sx0, max(y0, y1)), (sx1, max(y0, y1)), (sx1, scallop_y), (sx0, scallop_y)], fill=palette["b"])

    # scalloped bottom trim: little triangular flaps
    flap_w = (x1 - x0) / (stripes * 2)
    for i in range(stripes * 2):
        fx0 = x0 + i * flap_w
        color = palette["a"] if (i // 2) % 2 == 0 else palette["b"]
        draw.polygon([(fx0, scallop_y), (fx0 + flap_w, scallop_y), (fx0 + flap_w / 2, scallop_y + flap_w * 0.8)],
                     fill=color)

    # underside shade near the peak for depth
    draw.polygon([(peak_x, top_y), (x1, eave_y), (x1, eave_y - (eave_y - top_y) * 0.18),
                  (peak_x, top_y + (eave_y - top_y) * 0.1)], fill=palette["shade"])


def _draw_pennant(draw, cx, pole_top_y, pole_bottom_y, color, pole_w):
    draw.rectangle([cx - pole_w / 2, pole_top_y, cx + pole_w / 2, pole_bottom_y], fill=POST_SHADE)
    draw.polygon([(cx + pole_w / 2, pole_top_y), (cx + pole_w / 2 + pole_w * 3.2, pole_top_y + pole_w * 1.6),
                  (cx + pole_w / 2, pole_top_y + pole_w * 3.2)], fill=color)


def _draw_hanging_goods(draw, cx, string_top_y, bunch_y, rng_colors, r):
    draw.line([(cx, string_top_y), (cx, bunch_y)], fill=(90, 66, 42, 255), width=max(1, int(r * 0.25)))
    for dx, dy, color in rng_colors:
        draw.ellipse([cx + dx - r, bunch_y + dy - r, cx + dx + r, bunch_y + dy + r], fill=color)


def _draw_crate(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=CRATE)
    draw.rectangle([x0, y0 + (y1 - y0) * 0.6, x1, y1], fill=CRATE_SHADE)
    draw.line([(x0, y0), (x1, y1)], fill=CRATE_SHADE, width=max(1, int((x1 - x0) * 0.06)))
    draw.line([(x1, y0), (x0, y1)], fill=CRATE_SHADE, width=max(1, int((x1 - x0) * 0.06)))


def _draw_barrel(draw, x0, y0, x1, y1):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=(x1 - x0) * 0.22, fill=BARREL)
    for frac in (0.28, 0.72):
        draw.line([(x0, y0 + (y1 - y0) * frac), (x1, y0 + (y1 - y0) * frac)], fill=BARREL_BAND,
                  width=max(1, int((y1 - y0) * 0.08)))


def make_outpost(palette, goods_seed):
    w, h = CELL, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    draw.rectangle([cs_w * 0.14, cs_h * 0.34, cs_w * 0.24, cs_h], fill=POST)
    draw.rectangle([cs_w * 0.76, cs_h * 0.34, cs_w * 0.86, cs_h], fill=POST)
    draw.rectangle([cs_w * 0.14, cs_h * 0.34, cs_w * 0.19, cs_h], fill=POST_SHADE)
    draw.rectangle([cs_w * 0.76, cs_h * 0.34, cs_w * 0.81, cs_h], fill=POST_SHADE)

    _draw_pennant(draw, cs_w * 0.5, cs_h * 0.02, cs_h * 0.15, palette["pennant"], cs_w * 0.02)
    _draw_awning(draw, cs_w, cs_h * 0.16, cs_h * 0.42, cs_h * 0.52, cs_w * 0.02, cs_w * 0.98, palette, stripes=5)

    draw.rectangle([cs_w * 0.1, cs_h * 0.7, cs_w * 0.9, cs_h * 0.92], fill=COUNTER)
    draw.rectangle([cs_w * 0.1, cs_h * 0.84, cs_w * 0.9, cs_h * 0.92], fill=COUNTER_SHADE)

    _draw_crate(draw, cs_w * 0.36, cs_h * 0.58, cs_w * 0.6, cs_h * 0.72)

    goods = [(-cs_w * 0.05, 0, GOODS_COLORS[goods_seed % 4]), (cs_w * 0.05, cs_w * 0.02, GOODS_COLORS[(goods_seed + 1) % 4])]
    _draw_hanging_goods(draw, cs_w * 0.5, cs_h * 0.4, cs_h * 0.52, goods, cs_w * 0.045)

    return canvas.resize((w, h), Image.NEAREST)


def make_marketplace(palette, goods_seed):
    w, h = CELL * 2, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    for px in (0.06, 0.30, 0.70, 0.94):
        draw.rectangle([cs_w * px, cs_h * 0.36, cs_w * (px + 0.05), cs_h], fill=POST)
        draw.rectangle([cs_w * px, cs_h * 0.36, cs_w * (px + 0.02), cs_h], fill=POST_SHADE)

    _draw_pennant(draw, cs_w * 0.15, cs_h * 0.01, cs_h * 0.12, palette["pennant"], cs_w * 0.012)
    _draw_pennant(draw, cs_w * 0.85, cs_h * 0.01, cs_h * 0.12, palette["pennant"], cs_w * 0.012)
    _draw_awning(draw, cs_w, cs_h * 0.1, cs_h * 0.4, cs_h * 0.5, cs_w * 0.0, cs_w * 1.0, palette, stripes=8)

    draw.rectangle([cs_w * 0.03, cs_h * 0.66, cs_w * 0.97, cs_h * 0.9], fill=COUNTER)
    draw.rectangle([cs_w * 0.03, cs_h * 0.8, cs_w * 0.97, cs_h * 0.9], fill=COUNTER_SHADE)

    _draw_crate(draw, cs_w * 0.1, cs_h * 0.52, cs_w * 0.26, cs_h * 0.68)
    _draw_barrel(draw, cs_w * 0.42, cs_h * 0.5, cs_w * 0.58, cs_h * 0.68)
    _draw_crate(draw, cs_w * 0.72, cs_h * 0.52, cs_w * 0.88, cs_h * 0.68)

    goods = [(0, 0, GOODS_COLORS[goods_seed % 4]), (cs_w * 0.045, cs_w * 0.02, GOODS_COLORS[(goods_seed + 2) % 4]),
             (-cs_w * 0.045, cs_w * 0.015, GOODS_COLORS[(goods_seed + 3) % 4])]
    _draw_hanging_goods(draw, cs_w * 0.5, cs_h * 0.36, cs_h * 0.5, goods, cs_w * 0.03)

    return canvas.resize((w, h), Image.NEAREST)


def make_emerald():
    cs = CELL * SCALE
    canvas = Image.new("RGBA", (cs, cs), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    cx, cy = cs * 0.5, cs * 0.52
    pts = [(cx, cy - cs * 0.32), (cx + cs * 0.26, cy - cs * 0.12), (cx + cs * 0.18, cy + cs * 0.3),
           (cx - cs * 0.18, cy + cs * 0.3), (cx - cs * 0.26, cy - cs * 0.12)]
    draw.polygon(pts, fill=EMERALD_DARK)
    inset = [(cx, cy - cs * 0.24), (cx + cs * 0.19, cy - cs * 0.08), (cx + cs * 0.13, cy + cs * 0.22),
             (cx - cs * 0.13, cy + cs * 0.22), (cx - cs * 0.19, cy - cs * 0.08)]
    draw.polygon(inset, fill=EMERALD)
    draw.polygon([(cx, cy - cs * 0.24), (cx + cs * 0.06, cy - cs * 0.05), (cx - cs * 0.02, cy + cs * 0.05),
                  (cx - cs * 0.1, cy - cs * 0.08)], fill=EMERALD_LIGHT)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def main():
    for i, palette in enumerate(CANOPY_PALETTES, start=1):
        make_outpost(palette, goods_seed=i).save(os.path.join(OUT_DIR, f"Outpost{i}.png"))
        print(f"wrote Outpost{i}.png")

    for i, palette in enumerate(CANOPY_PALETTES[:3], start=1):
        make_marketplace(palette, goods_seed=i).save(os.path.join(OUT_DIR, f"Marketplace{i}.png"))
        print(f"wrote Marketplace{i}.png")

    make_emerald().save(os.path.join(OUT_DIR, "Emerald.png"))
    print("wrote Emerald.png")


if __name__ == "__main__":
    main()
