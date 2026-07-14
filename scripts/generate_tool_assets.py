"""Generates hand-held tool/weapon sprites: FarmImg/Tool_Pick.png,
Tool_Hoe.png, Tool_Axe.png, Tool_Sword.png. Each is drawn diagonally (head/
blade pointing up-right, handle down-left) so it reads naturally both as an
idle carried pose and mid-rotation during the swing animation. Drawn at
higher internal resolution then downsampled with NEAREST for crisp
pixel-art edges, matching the rest of the game's art pipeline. Re-run to
tweak.
"""
import os

from PIL import Image, ImageDraw

CELL = 24
SCALE = 8
CS = CELL * SCALE
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

HANDLE = (120, 84, 52, 255)
HANDLE_SHADE = (92, 62, 38, 255)


def s(v):
    return v * SCALE


def _handle(draw, x0, y0, x1, y1, width_frac=0.16):
    w = CS * width_frac
    draw.line([(x0, y0), (x1, y1)], fill=HANDLE, width=int(w))
    draw.line([(x0, y0), (x0 + (x1 - x0) * 0.4, y0 + (y1 - y0) * 0.4)], fill=HANDLE_SHADE, width=int(w * 0.5))


def make_pick():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    head = (150, 150, 158, 255)
    head_shade = (110, 110, 120, 255)
    _handle(draw, CS * 0.18, CS * 0.9, CS * 0.68, CS * 0.32)
    # pickaxe head: a curved double point crossing the handle near the top
    draw.polygon([(CS * 0.5, CS * 0.06), (CS * 0.92, CS * 0.22), (CS * 0.7, CS * 0.42),
                  (CS * 0.42, CS * 0.3)], fill=head)
    draw.polygon([(CS * 0.5, CS * 0.06), (CS * 0.12, CS * 0.2), (CS * 0.36, CS * 0.42),
                  (CS * 0.6, CS * 0.28)], fill=head_shade)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_hoe():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    head = (170, 150, 130, 255)
    head_shade = (130, 112, 96, 255)
    _handle(draw, CS * 0.2, CS * 0.92, CS * 0.62, CS * 0.28)
    # flat blade perpendicular to the handle top
    draw.polygon([(CS * 0.5, CS * 0.1), (CS * 0.9, CS * 0.28), (CS * 0.8, CS * 0.46),
                  (CS * 0.42, CS * 0.28)], fill=head)
    draw.polygon([(CS * 0.5, CS * 0.1), (CS * 0.42, CS * 0.28), (CS * 0.48, CS * 0.32),
                  (CS * 0.56, CS * 0.16)], fill=head_shade)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_axe():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    head = (168, 172, 178, 255)
    head_shade = (124, 128, 136, 255)
    _handle(draw, CS * 0.22, CS * 0.92, CS * 0.62, CS * 0.26)
    # wide curved axe head at the top of the handle
    draw.polygon([(CS * 0.58, CS * 0.06), (CS * 0.98, CS * 0.16), (CS * 0.94, CS * 0.42),
                  (CS * 0.68, CS * 0.5), (CS * 0.52, CS * 0.3)], fill=head)
    draw.polygon([(CS * 0.58, CS * 0.06), (CS * 0.68, CS * 0.5), (CS * 0.6, CS * 0.46),
                  (CS * 0.5, CS * 0.14)], fill=head_shade)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_sword():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    blade = (206, 210, 216, 255)
    blade_shade = (162, 168, 176, 255)
    guard = (196, 160, 60, 255)
    grip = (74, 52, 34, 255)

    # grip + pommel at the bottom-left
    draw.line([(CS * 0.12, CS * 0.96), (CS * 0.3, CS * 0.74)], fill=grip, width=int(CS * 0.13))
    draw.ellipse([CS * 0.06, CS * 0.9, CS * 0.2, CS * 1.02], fill=grip)
    # crossguard
    draw.line([(CS * 0.2, CS * 0.82), (CS * 0.42, CS * 0.62)], fill=guard, width=int(CS * 0.1))
    # blade tapering to a point at the top-right
    draw.polygon([(CS * 0.32, CS * 0.72), (CS * 0.42, CS * 0.62), (CS * 0.98, CS * 0.08),
                  (CS * 0.9, CS * 0.02), (CS * 0.5, CS * 0.5)], fill=blade)
    draw.polygon([(CS * 0.32, CS * 0.72), (CS * 0.42, CS * 0.62), (CS * 0.74, CS * 0.32),
                  (CS * 0.68, CS * 0.32)], fill=blade_shade)
    return canvas.resize((CELL, CELL), Image.NEAREST)


def main():
    make_pick().save(os.path.join(OUT_DIR, "Tool_Pick.png"))
    make_hoe().save(os.path.join(OUT_DIR, "Tool_Hoe.png"))
    make_axe().save(os.path.join(OUT_DIR, "Tool_Axe.png"))
    make_sword().save(os.path.join(OUT_DIR, "Tool_Sword.png"))
    print("wrote Tool_Pick.png, Tool_Hoe.png, Tool_Axe.png, Tool_Sword.png")


if __name__ == "__main__":
    main()
