"""Generates one 4-direction, 4-frame walk sprite sheet per playable
character into FarmImg/Player_<Name>.png. Drawn at higher internal
resolution then downsampled with NEAREST so edges stay crisp (matching
the hand-drawn crop art) instead of soft/anti-aliased. Re-run this
script to regenerate/tweak any character's design.

Sheet layout (32x32 cells): rows = down, left, right, up. columns = idle,
step-A, mid, step-B.
"""
import os
from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
CS = CELL * SCALE
DIRECTIONS = ["down", "left", "right", "up"]
FRAMES_PER_DIR = 4

EYE = (48, 34, 30, 255)

# Each character is defined purely by a color palette + hair style so the
# silhouette/animation code stays shared. hair_style "short" hides hair
# under the hat; "long" shows strands at the sides and fuller hair from behind.
CHARACTERS = {
    "Hank": dict(
        skin=(255, 214, 173, 255),
        hat_brim=(219, 178, 84, 255), hat_band=(168, 122, 58, 255), hat_top=(236, 197, 110, 255),
        shirt=(219, 90, 74, 255), shirt_shade=(185, 70, 58, 255),
        overalls=(69, 103, 148, 255), overalls_shade=(56, 85, 123, 255), strap=(48, 74, 108, 255),
        shoe=(91, 60, 33, 255), hair=(139, 94, 60, 255), hair_style="short",
    ),
    "Jeff": dict(
        skin=(222, 178, 135, 255),
        hat_brim=(120, 140, 90, 255), hat_band=(80, 96, 60, 255), hat_top=(140, 160, 104, 255),
        shirt=(224, 158, 60, 255), shirt_shade=(188, 128, 44, 255),
        overalls=(95, 110, 64, 255), overalls_shade=(74, 88, 48, 255), strap=(60, 72, 38, 255),
        shoe=(74, 50, 30, 255), hair=(40, 32, 28, 255), hair_style="short",
    ),
    "Martha": dict(
        skin=(255, 224, 189, 255),
        hat_brim=(196, 74, 74, 255), hat_band=(150, 50, 50, 255), hat_top=(214, 100, 100, 255),
        shirt=(230, 200, 80, 255), shirt_shade=(196, 168, 60, 255),
        overalls=(86, 130, 90, 255), overalls_shade=(66, 105, 72, 255), strap=(52, 84, 58, 255),
        shoe=(96, 66, 40, 255), hair=(112, 66, 40, 255), hair_style="long",
    ),
    "Marin": dict(
        skin=(198, 150, 110, 255),
        hat_brim=(210, 196, 150, 255), hat_band=(168, 150, 104, 255), hat_top=(226, 214, 176, 255),
        shirt=(60, 150, 150, 255), shirt_shade=(46, 122, 122, 255),
        overalls=(50, 70, 110, 255), overalls_shade=(38, 55, 88, 255), strap=(30, 44, 72, 255),
        shoe=(60, 44, 32, 255), hair=(30, 26, 26, 255), hair_style="long",
    ),
}


def s(v):
    return v * SCALE


def leg_offset(col):
    return {0: 0, 1: -1.6, 2: 0, 3: 1.6}[col]


def arm_offset(col):
    return {0: 0, 1: 0.8, 2: 0, 3: -0.8}[col]


def draw_legs(draw, col, p):
    o = leg_offset(col)
    draw.rectangle([s(17 + o), s(23), s(19.5 + o), s(28)], fill=p["shoe"])
    draw.rectangle([s(12.5 - o), s(23), s(15 - o), s(28)], fill=p["shoe"])


def draw_torso(draw, p):
    draw.rectangle([s(11.5), s(15), s(20.5), s(23)], fill=p["overalls"])
    draw.rectangle([s(11.5), s(15), s(20.5), s(17.2)], fill=p["shirt"])
    draw.rectangle([s(11.5), s(20.5), s(20.5), s(23)], fill=p["overalls_shade"])
    draw.rectangle([s(13.3), s(15), s(14.6), s(19)], fill=p["strap"])
    draw.rectangle([s(17.4), s(15), s(18.7), s(19)], fill=p["strap"])


def draw_arms(draw, col, side, p):
    o = arm_offset(col)
    if side in ("both", "left"):
        draw.rectangle([s(8.3), s(15.8 + o), s(11.3), s(20.5 + o)], fill=p["skin"])
    if side in ("both", "right"):
        draw.rectangle([s(20.7), s(15.8 - o), s(23.7), s(20.5 - o)], fill=p["skin"])


def draw_hat(draw, brim_box, band_box, top_box, p):
    draw.ellipse(brim_box, fill=p["hat_brim"])
    draw.rectangle(band_box, fill=p["hat_band"])
    draw.ellipse(top_box, fill=p["hat_top"])


def draw_frame(direction, col, p):
    frame = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    long_hair = p["hair_style"] == "long"

    if direction == "down":
        draw_legs(draw, col, p)
        draw_arms(draw, col, "both", p)
        draw_torso(draw, p)
        if long_hair:
            draw.rectangle([s(10.3), s(9), s(12), s(13.5)], fill=p["hair"])
            draw.rectangle([s(20), s(9), s(21.7), s(13.5)], fill=p["hair"])
        draw.ellipse([s(11.5), s(6), s(20.5), s(15)], fill=p["skin"])
        draw.rectangle([s(13.3), s(11), s(14.3), s(12)], fill=EYE)
        draw.rectangle([s(17.7), s(11), s(18.7), s(12)], fill=EYE)
        draw_hat(draw, [s(8.5), s(3.5), s(23.5), s(9)], [s(10.5), s(6.2), s(21.5), s(8)], [s(12.5), s(1.5), s(19.5), s(6.5)], p)

    elif direction == "up":
        draw_legs(draw, col, p)
        draw_arms(draw, col, "both", p)
        draw_torso(draw, p)
        draw.ellipse([s(11.5), s(6), s(20.5), s(15)], fill=p["skin"])
        hair_bottom = s(14.5) if long_hair else s(13)
        draw.pieslice([s(11.5), s(6), s(20.5), hair_bottom], 180, 360, fill=p["hair"])
        if long_hair:
            draw.rectangle([s(11), s(10), s(13), s(16)], fill=p["hair"])
            draw.rectangle([s(19), s(10), s(21), s(16)], fill=p["hair"])
        draw_hat(draw, [s(8.5), s(3.5), s(23.5), s(9)], [s(10.5), s(6.2), s(21.5), s(8)], [s(12.5), s(1.5), s(19.5), s(6.5)], p)

    else:  # left / right — draw facing "left", flip for right
        draw_legs(draw, col, p)
        draw_arms(draw, col, "left", p)
        draw_torso(draw, p)
        if long_hair:
            draw.rectangle([s(19.5), s(9), s(21.3), s(14)], fill=p["hair"])
        draw.ellipse([s(12), s(6), s(19.5), s(15)], fill=p["skin"])
        draw.rectangle([s(12.7), s(11), s(13.7), s(12)], fill=EYE)
        draw_hat(draw, [s(9), s(3.5), s(22.5), s(9)], [s(10.5), s(6.2), s(20.5), s(8)], [s(12), s(1.5), s(19), s(6.5)], p)
        draw_arms(draw, col, "right", p)

        if direction == "right":
            frame = frame.transpose(Image.FLIP_LEFT_RIGHT)

    return frame.resize((CELL, CELL), Image.NEAREST)


def render_sheet(palette):
    sheet = Image.new("RGBA", (CELL * FRAMES_PER_DIR, CELL * len(DIRECTIONS)), (0, 0, 0, 0))
    for row, direction in enumerate(DIRECTIONS):
        for col in range(FRAMES_PER_DIR):
            frame = draw_frame(direction, col, palette)
            sheet.paste(frame, (col * CELL, row * CELL), frame)
    return sheet


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "FarmImg")
    for name, palette in CHARACTERS.items():
        sheet = render_sheet(palette)
        out_path = os.path.join(out_dir, f"Player_{name}.png")
        sheet.save(out_path)
        print(f"wrote {out_path} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
