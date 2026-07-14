"""Generates FarmImg/Stable.png (2 tiles wide x 2 tall, anchored at the
bottom like the house) and FarmImg/Horse.png (a rideable horse, single
side-view sprite flipped in-game for left/right travel). Drawn at higher
internal resolution then downsampled with NEAREST for crisp pixel-art
edges. Re-run to tweak.
"""
import os

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

WOOD = (150, 106, 62, 255)
WOOD_SHADE = (118, 80, 44, 255)
WOOD_DARK = (92, 62, 34, 255)
ROOF = (128, 62, 46, 255)
ROOF_SHADE = (100, 46, 34, 255)
HAY = (222, 188, 96, 255)
HAY_SHADE = (194, 158, 70, 255)
DOOR_GAP = (48, 34, 26, 255)

HORSE_BODY = (120, 80, 52, 255)
HORSE_SHADE = (92, 58, 36, 255)
HORSE_MANE = (58, 40, 28, 255)
HORSE_HOOF = (40, 30, 24, 255)
HORSE_SADDLE = (150, 60, 50, 255)


def s(v):
    return v * SCALE


def make_stable():
    w, h = CELL * 2, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    roof_h = cs_h * 0.36
    draw.polygon([(0, roof_h), (cs_w / 2, cs_h * 0.06), (cs_w, roof_h), (cs_w, roof_h * 1.1), (0, roof_h * 1.1)],
                 fill=ROOF)
    draw.polygon([(0, roof_h), (cs_w / 2, cs_h * 0.06), (cs_w / 2, roof_h * 0.5), (0, roof_h * 1.1)], fill=ROOF_SHADE)

    draw.rectangle([0, roof_h, cs_w, cs_h], fill=WOOD)
    for i in range(6):
        x = cs_w * (i / 6)
        draw.line([(x, roof_h), (x, cs_h)], fill=WOOD_SHADE, width=max(1, int(cs_w * 0.01)))
    draw.rectangle([0, cs_h * 0.88, cs_w, cs_h], fill=WOOD_DARK)

    # hayloft opening near the top with hay poking out
    loft_x0, loft_x1 = cs_w * 0.36, cs_w * 0.64
    draw.rectangle([loft_x0, roof_h * 1.15, loft_x1, roof_h * 1.15 + cs_h * 0.14], fill=DOOR_GAP)
    for i in range(5):
        hx = loft_x0 + (loft_x1 - loft_x0) * (i / 4)
        draw.polygon([(hx, roof_h * 1.15 + cs_h * 0.14), (hx + cs_w * 0.02, roof_h * 1.15 + cs_h * 0.02),
                      (hx + cs_w * 0.04, roof_h * 1.15 + cs_h * 0.14)], fill=HAY if i % 2 == 0 else HAY_SHADE)

    # big double doors
    door_y0 = cs_h * 0.6
    draw.rectangle([cs_w * 0.16, door_y0, cs_w * 0.47, cs_h * 0.92], fill=WOOD_SHADE)
    draw.rectangle([cs_w * 0.53, door_y0, cs_w * 0.84, cs_h * 0.92], fill=WOOD_SHADE)
    draw.rectangle([cs_w * 0.47, door_y0, cs_w * 0.53, cs_h * 0.92], fill=DOOR_GAP)
    for dx in (0.16, 0.53):
        draw.line([(cs_w * dx, door_y0), (cs_w * (dx + 0.155), cs_h * 0.92)], fill=WOOD_DARK, width=max(1, int(cs_w * 0.008)))

    # a bale of hay out front
    draw.ellipse([cs_w * 0.02, cs_h * 0.82, cs_w * 0.15, cs_h * 0.94], fill=HAY)
    draw.ellipse([cs_w * 0.02, cs_h * 0.88, cs_w * 0.15, cs_h * 0.94], fill=HAY_SHADE)

    return canvas.resize((w, h), Image.NEAREST)


def make_horse_frame(stride):
    """stride: -1, 0, 1 — back and front leg pairs shift oppositely to
    simulate a running gait, with a slight body bob mid-stride."""
    w, h = CELL, CELL
    cs = CELL * SCALE
    canvas = Image.new("RGBA", (cs, cs), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # body (side view, facing right)
    draw.ellipse([cs * 0.16, cs * 0.36, cs * 0.86, cs * 0.68], fill=HORSE_BODY)
    draw.ellipse([cs * 0.16, cs * 0.54, cs * 0.86, cs * 0.68], fill=HORSE_SHADE)

    # neck (thick wedge connecting body to head) + head (elongated muzzle)
    draw.polygon([(cs * 0.68, cs * 0.48), (cs * 0.76, cs * 0.16), (cs * 0.92, cs * 0.14),
                  (cs * 0.88, cs * 0.46)], fill=HORSE_BODY)
    draw.polygon([(cs * 0.76, cs * 0.18), (cs * 1.0, cs * 0.22), (cs * 0.98, cs * 0.32),
                  (cs * 0.9, cs * 0.34), (cs * 0.78, cs * 0.28)], fill=HORSE_BODY)
    draw.polygon([(cs * 0.9, cs * 0.34), (cs * 0.98, cs * 0.32), (cs * 0.94, cs * 0.4),
                  (cs * 0.86, cs * 0.4)], fill=HORSE_SHADE)
    # ear
    draw.polygon([(cs * 0.78, cs * 0.18), (cs * 0.76, cs * 0.08), (cs * 0.84, cs * 0.16)], fill=HORSE_BODY)

    # mane running down the neck
    draw.line([(cs * 0.78, cs * 0.16), (cs * 0.68, cs * 0.46)], fill=HORSE_MANE, width=max(1, int(cs * 0.055)))

    # saddle
    draw.rectangle([cs * 0.42, cs * 0.34, cs * 0.62, cs * 0.44], fill=HORSE_SADDLE)

    # tail
    draw.polygon([(cs * 0.16, cs * 0.44), (cs * 0.02, cs * 0.5), (cs * 0.08, cs * 0.68), (cs * 0.2, cs * 0.58)],
                  fill=HORSE_MANE)

    # legs: back pair and front pair shift oppositely for a running stride
    leg_shift = stride * cs * 0.05
    for lx, shift in ((0.28, leg_shift), (0.4, leg_shift), (0.6, -leg_shift), (0.72, -leg_shift)):
        draw.rectangle([cs * lx + shift, cs * 0.62, cs * (lx + 0.07) + shift, cs * 0.86], fill=HORSE_BODY)
        draw.rectangle([cs * lx + shift, cs * 0.8, cs * (lx + 0.07) + shift, cs * 0.86], fill=HORSE_HOOF)

    frame = canvas.resize((w, h), Image.NEAREST)
    if stride != 0:
        # a 1px body bob mid-stride
        bobbed = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bobbed.paste(frame, (0, -1), frame)
        frame = bobbed
    return frame


def make_horse_strip():
    strip = Image.new("RGBA", (CELL * 3, CELL), (0, 0, 0, 0))
    for i, stride in enumerate((0, -1, 1)):  # neutral, stride-A, stride-B
        strip.paste(make_horse_frame(stride), (i * CELL, 0))
    return strip


def main():
    make_stable().save(os.path.join(OUT_DIR, "Stable.png"))
    make_horse_strip().save(os.path.join(OUT_DIR, "Horse.png"))
    print("wrote Stable.png, Horse.png (3-frame gallop strip)")


if __name__ == "__main__":
    main()
