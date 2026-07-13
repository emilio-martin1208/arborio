"""Generates the house exterior (FarmImg/House.png, 2 tiles wide x 2 tiles
tall — the bottom tile row is the solid/collidable footprint, the top row
is roof/chimney overhang) and the interior room tiles (FarmImg/Floor.png,
FarmImg/Wall.png). Drawn at higher internal resolution then downsampled
with NEAREST to match the rest of the game's crisp pixel-art style.
Re-run to tweak.
"""
import os

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

ROOF = (150, 68, 48, 255)
ROOF_SHADE = (118, 50, 36, 255)
ROOF_LINE = (100, 42, 30, 255)
CHIMNEY = (128, 80, 58, 255)
CHIMNEY_SHADE = (100, 60, 42, 255)
SMOKE = (232, 232, 232, 130)

WALL = (200, 154, 100, 255)
WALL_SHADE = (172, 128, 78, 255)
WALL_LINE = (150, 108, 62, 255)

BASE = (150, 142, 128, 255)
BASE_SHADE = (120, 112, 100, 255)

DOOR = (92, 60, 36, 255)
DOOR_PANEL = (112, 76, 46, 255)
DOOR_KNOB = (224, 198, 92, 255)
AWNING = (120, 52, 38, 255)

WINDOW = (156, 206, 214, 255)
WINDOW_FRAME = (100, 70, 42, 255)
FLOWERBOX = (96, 74, 48, 255)
FLOWER_COLORS = [(214, 90, 96, 255), (238, 198, 80, 255), (206, 120, 190, 255)]

FLOOR_BASE = (168, 122, 76, 255)
FLOOR_PLANK = (146, 104, 62, 255)
FLOOR_PLANK_DARK = (128, 90, 52, 255)

WALL_PAPER = (176, 138, 104, 255)
WALL_PAPER_SHADE = (152, 116, 84, 255)


def s(v):
    return v * SCALE


def make_house():
    w, h = CELL * 2, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    peak_y = cs_h * 0.20
    eaves_y = cs_h * 0.56
    base_y = cs_h * 0.94

    # chimney (drawn first so the roof overlaps its base, leaving the top poking out)
    chim_top = cs_h * 0.16
    chim_x0, chim_x1 = cs_w * 0.66, cs_w * 0.80
    draw.rectangle([chim_x0, chim_top, chim_x1, eaves_y * 0.82], fill=CHIMNEY)
    draw.rectangle([chim_x0, chim_top, (chim_x0 + chim_x1) / 2, eaves_y * 0.82], fill=CHIMNEY_SHADE)
    # smoke puffs, drifting up and to the side above the chimney
    for dx, y_frac, r in [(0.0, 0.12, 0.032), (0.05, 0.075, 0.042), (0.0, 0.035, 0.05)]:
        cx, cy = (chim_x0 + chim_x1) / 2 + cs_w * dx, cs_h * y_frac
        draw.ellipse([cx - cs_w * r, cy - cs_w * r, cx + cs_w * r, cy + cs_w * r], fill=SMOKE)

    # roof (gabled)
    draw.polygon([(0, eaves_y), (cs_w / 2, peak_y), (cs_w, eaves_y), (cs_w, eaves_y * 1.08), (0, eaves_y * 1.08)], fill=ROOF)
    draw.polygon([(0, eaves_y), (cs_w / 2, peak_y), (cs_w / 2, peak_y + (eaves_y - peak_y) * 0.4), (0, eaves_y * 1.08)], fill=ROOF_SHADE)
    # shingle course lines
    for frac in (0.35, 0.6, 0.82):
        y0 = peak_y + (eaves_y - peak_y) * frac
        spread = frac
        draw.line([(cs_w / 2 - (cs_w / 2) * spread, y0), (cs_w / 2 + (cs_w / 2) * spread, y0)], fill=ROOF_LINE, width=max(1, int(s(0.06))))

    # walls (log-cabin banding)
    draw.rectangle([0, eaves_y, cs_w, base_y], fill=WALL)
    band_h = (base_y - eaves_y) / 5
    for i in range(5):
        y0 = eaves_y + i * band_h
        draw.line([(0, y0 + band_h - s(0.15)), (cs_w, y0 + band_h - s(0.15))], fill=WALL_LINE, width=max(1, int(s(0.1))))
    draw.rectangle([0, eaves_y, cs_w, eaves_y + s(0.3)], fill=WALL_LINE)

    # stone foundation
    draw.rectangle([0, base_y, cs_w, cs_h], fill=BASE)
    draw.rectangle([0, base_y + (cs_h - base_y) * 0.5, cs_w, cs_h], fill=BASE_SHADE)

    # windows with flower boxes
    win_y0, win_y1 = eaves_y + cs_h * 0.06, eaves_y + cs_h * 0.22
    for wx in (cs_w * 0.09, cs_w * 0.67):
        ww = cs_w * 0.24
        draw.rectangle([wx, win_y0, wx + ww, win_y1], fill=WINDOW_FRAME)
        pad = cs_w * 0.02
        draw.rectangle([wx + pad, win_y0 + pad, wx + ww - pad, win_y1 - pad], fill=WINDOW)
        mid_x, mid_y = wx + ww / 2, (win_y0 + win_y1) / 2
        draw.line([(mid_x, win_y0 + pad), (mid_x, win_y1 - pad)], fill=WINDOW_FRAME, width=max(1, int(s(0.08))))
        draw.line([(wx + pad, mid_y), (wx + ww - pad, mid_y)], fill=WINDOW_FRAME, width=max(1, int(s(0.08))))
        # flower box beneath
        box_y0 = win_y1 + cs_h * 0.01
        draw.rectangle([wx - cs_w * 0.01, box_y0, wx + ww + cs_w * 0.01, box_y0 + cs_h * 0.045], fill=FLOWERBOX)
        for i in range(4):
            fx = wx + ww * (0.08 + i * 0.28)
            fr = cs_w * 0.018
            color = FLOWER_COLORS[i % len(FLOWER_COLORS)]
            draw.ellipse([fx - fr, box_y0 - fr * 0.6, fx + fr, box_y0 + fr * 0.6], fill=color)

    # door with awning
    door_w, door_x = cs_w * 0.24, cs_w * 0.38
    door_y0 = eaves_y + cs_h * 0.14
    draw.polygon([(door_x - cs_w * 0.03, door_y0), (door_x + door_w / 2, door_y0 - cs_h * 0.06),
                  (door_x + door_w + cs_w * 0.03, door_y0)], fill=AWNING)
    draw.rectangle([door_x, door_y0, door_x + door_w, base_y], fill=DOOR)
    panel_pad = door_w * 0.16
    draw.rectangle([door_x + panel_pad, door_y0 + (base_y - door_y0) * 0.12,
                    door_x + door_w - panel_pad, door_y0 + (base_y - door_y0) * 0.48], fill=DOOR_PANEL)
    draw.rectangle([door_x + panel_pad, door_y0 + (base_y - door_y0) * 0.56,
                    door_x + door_w - panel_pad, door_y0 + (base_y - door_y0) * 0.92], fill=DOOR_PANEL)
    draw.ellipse([door_x + door_w * 0.74, door_y0 + (base_y - door_y0) * 0.68,
                  door_x + door_w * 0.86, door_y0 + (base_y - door_y0) * 0.76], fill=DOOR_KNOB)

    return canvas.resize((w, h), Image.NEAREST)


def make_floor():
    canvas = Image.new("RGBA", (s(CELL), s(CELL)), FLOOR_BASE)
    draw = ImageDraw.Draw(canvas)
    plank_h = s(CELL) / 4
    for i in range(4):
        y = i * plank_h
        color = FLOOR_PLANK if i % 2 == 0 else FLOOR_PLANK_DARK
        draw.rectangle([0, y, s(CELL), y + plank_h - s(0.15)], fill=color)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_wall():
    canvas = Image.new("RGBA", (s(CELL), s(CELL)), WALL_PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, s(CELL) - s(2.5), s(CELL), s(CELL)], fill=WALL_PAPER_SHADE)
    draw.rectangle([0, 0, s(CELL), s(1.5)], fill=WALL_PAPER_SHADE)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def main():
    house = make_house()
    house.save(os.path.join(OUT_DIR, "House.png"))
    print("wrote House.png", house.size)

    floor = make_floor()
    floor.save(os.path.join(OUT_DIR, "Floor.png"))
    print("wrote Floor.png", floor.size)

    wall = make_wall()
    wall.save(os.path.join(OUT_DIR, "Wall.png"))
    print("wrote Wall.png", wall.size)


if __name__ == "__main__":
    main()
