"""Generates a large batch of ripe-crop icons (Potato.png, Wheat.png,
Strawberry.png, Blueberry.png, Watermelon.png, Cabbage.png, Lettuce.png,
Eggplant.png, Chili.png, Cucumber.png, Onion.png, Grape.png, Apple.png,
Sunflower.png). Each is 32x32, drawn at higher internal resolution then
downsampled with NEAREST for crisp pixel-art edges — same pipeline as
the existing Corn/Tomato/Pumpkin/Carrot art. Re-run to tweak.
"""
import os

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
CS = CELL * SCALE
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")


def s(v):
    return v * SCALE


def canvas():
    return Image.new("RGBA", (CS, CS), (0, 0, 0, 0))


def save(img, name):
    img.resize((CELL, CELL), Image.NEAREST).save(os.path.join(OUT_DIR, name))


# ------------------------------------------------------------------ Potato --
def make_potato():
    c = canvas()
    d = ImageDraw.Draw(c)
    body = (170, 130, 84, 255)
    body_dark = (128, 96, 60, 255)
    eye = (72, 52, 32, 255)
    d.ellipse([s(6), s(10), s(26), s(24)], fill=body)
    d.ellipse([s(6), s(18), s(26), s(24)], fill=body_dark)
    for (ex, ey) in ((10, 14), (18, 13), (14, 18), (21, 17)):
        d.ellipse([s(ex), s(ey), s(ex + 1.5), s(ey + 1.5)], fill=eye)
    return c


# ------------------------------------------------------------------- Wheat --
def make_wheat():
    c = canvas()
    d = ImageDraw.Draw(c)
    stalk = (188, 150, 60, 255)
    head = (232, 200, 96, 255)
    head_shade = (196, 168, 74, 255)
    # stalk
    d.rectangle([s(15), s(14), s(17), s(28)], fill=stalk)
    # grain kernels arranged in a spike pattern
    for i, y in enumerate((4, 7, 10, 13)):
        offset = 3 if i % 2 == 0 else -3
        d.ellipse([s(16 + offset - 2), s(y), s(16 + offset + 2), s(y + 4)], fill=head)
        d.ellipse([s(16 - offset - 2), s(y + 1), s(16 - offset + 2), s(y + 5)], fill=head_shade)
    # tip
    d.polygon([(s(16), s(2)), (s(14), s(6)), (s(18), s(6))], fill=head)
    return c


# ------------------------------------------------------------- Strawberry --
def make_strawberry():
    c = canvas()
    d = ImageDraw.Draw(c)
    berry = (222, 60, 68, 255)
    berry_shade = (168, 40, 48, 255)
    seed = (255, 220, 120, 255)
    leaf = (86, 160, 76, 255)
    # heart-ish berry
    d.polygon([(s(16), s(28)), (s(6), s(14)), (s(10), s(9)), (s(16), s(13)),
               (s(22), s(9)), (s(26), s(14))], fill=berry)
    d.polygon([(s(16), s(28)), (s(9), s(18)), (s(23), s(18))], fill=berry_shade)
    # seeds
    for (sx, sy) in ((10, 17), (14, 15), (18, 15), (22, 17), (12, 21), (16, 22), (20, 21)):
        d.ellipse([s(sx), s(sy), s(sx + 1), s(sy + 1)], fill=seed)
    # leafy cap
    d.polygon([(s(11), s(11)), (s(16), s(5)), (s(21), s(11)), (s(16), s(14))], fill=leaf)
    return c


# -------------------------------------------------------------- Blueberry --
def make_blueberry():
    c = canvas()
    d = ImageDraw.Draw(c)
    blue = (68, 96, 176, 255)
    blue_light = (128, 154, 216, 255)
    stem = (108, 76, 52, 255)
    leaf = (86, 160, 76, 255)
    # cluster of 4 berries
    for (bx, by, r) in ((10, 14, 5), (20, 14, 5), (13, 21, 5), (21, 21, 5)):
        d.ellipse([s(bx - r), s(by - r), s(bx + r), s(by + r)], fill=blue)
        d.ellipse([s(bx - r + 1), s(by - r + 1), s(bx - r + 3), s(by - r + 3)], fill=blue_light)
    # stem + tiny leaf
    d.rectangle([s(15), s(4), s(17), s(11)], fill=stem)
    d.polygon([(s(17), s(8)), (s(22), s(6)), (s(20), s(11))], fill=leaf)
    return c


# -------------------------------------------------------------- Watermelon --
def make_watermelon():
    c = canvas()
    d = ImageDraw.Draw(c)
    rind = (86, 150, 66, 255)
    rind_dark = (50, 108, 50, 255)
    flesh = (222, 74, 82, 255)
    seed = (40, 32, 28, 255)
    d.ellipse([s(4), s(6), s(28), s(28)], fill=rind)
    # rind stripes
    for i in range(3):
        d.arc([s(4), s(6), s(28), s(28)], 200 + i * 20, 340 - i * 20, fill=rind_dark, width=max(1, int(s(0.4))))
    # pink flesh slice at top
    d.pieslice([s(4), s(6), s(28), s(28)], 180, 360, fill=flesh)
    d.arc([s(4), s(6), s(28), s(28)], 180, 360, fill=rind_dark, width=max(1, int(s(0.5))))
    for (sx, sy) in ((10, 12), (14, 10), (18, 10), (22, 12), (12, 15), (20, 15)):
        d.polygon([(s(sx), s(sy)), (s(sx + 1.5), s(sy + 3)), (s(sx - 1), s(sy + 3))], fill=seed)
    return c


# ----------------------------------------------------------------- Cabbage --
def make_cabbage():
    c = canvas()
    d = ImageDraw.Draw(c)
    outer = (108, 172, 92, 255)
    middle = (140, 196, 120, 255)
    inner = (176, 216, 148, 255)
    vein = (60, 108, 60, 255)
    d.ellipse([s(4), s(6), s(28), s(28)], fill=outer)
    d.ellipse([s(7), s(9), s(25), s(26)], fill=middle)
    d.ellipse([s(10), s(12), s(22), s(24)], fill=inner)
    for i in range(-2, 3):
        d.line([(s(16 + i * 2), s(9)), (s(16), s(20))], fill=vein, width=max(1, int(s(0.3))))
    return c


# ----------------------------------------------------------------- Lettuce --
def make_lettuce():
    c = canvas()
    d = ImageDraw.Draw(c)
    outer = (128, 200, 108, 255)
    middle = (168, 220, 128, 255)
    inner = (208, 236, 148, 255)
    # frilly ruffled shape via overlapping ellipses
    for (cx, cy, w, h, col) in ((16, 22, 12, 6, outer), (16, 18, 11, 7, outer), (16, 14, 10, 6, middle),
                                  (16, 11, 8, 5, inner)):
        d.ellipse([s(cx - w), s(cy - h), s(cx + w), s(cy + h)], fill=col)
    return c


# --------------------------------------------------------------- Eggplant --
def make_eggplant():
    c = canvas()
    d = ImageDraw.Draw(c)
    purple = (108, 62, 128, 255)
    purple_light = (150, 96, 172, 255)
    stem = (86, 128, 60, 255)
    d.ellipse([s(9), s(11), s(23), s(28)], fill=purple)
    d.ellipse([s(11), s(19), s(21), s(27)], fill=purple_light)
    # curve stem
    d.polygon([(s(11), s(11)), (s(21), s(11)), (s(21), s(8)), (s(17), s(4)), (s(15), s(4)), (s(11), s(8))], fill=stem)
    return c


# ------------------------------------------------------------------ Chili --
def make_chili():
    c = canvas()
    d = ImageDraw.Draw(c)
    red = (222, 52, 40, 255)
    red_dark = (168, 32, 24, 255)
    stem = (86, 128, 60, 255)
    d.polygon([(s(10), s(8)), (s(22), s(8)), (s(20), s(28)), (s(15), s(28)), (s(12), s(24))], fill=red)
    d.polygon([(s(15), s(28)), (s(20), s(28)), (s(20), s(20))], fill=red_dark)
    d.polygon([(s(10), s(8)), (s(22), s(8)), (s(20), s(4)), (s(12), s(4))], fill=stem)
    return c


# --------------------------------------------------------------- Cucumber --
def make_cucumber():
    c = canvas()
    d = ImageDraw.Draw(c)
    green = (86, 148, 68, 255)
    green_dark = (56, 108, 48, 255)
    highlight = (150, 200, 108, 255)
    d.rectangle([s(6), s(13), s(26), s(19)], fill=green)
    d.ellipse([s(2), s(13), s(10), s(19)], fill=green)
    d.ellipse([s(22), s(13), s(30), s(19)], fill=green)
    d.rectangle([s(6), s(17), s(26), s(19)], fill=green_dark)
    # tiny bumps/highlight
    for x in (8, 14, 20):
        d.ellipse([s(x), s(14), s(x + 1.5), s(15.5)], fill=highlight)
    return c


# ------------------------------------------------------------------ Onion --
def make_onion():
    c = canvas()
    d = ImageDraw.Draw(c)
    skin = (222, 178, 108, 255)
    skin_dark = (176, 130, 72, 255)
    green = (86, 148, 68, 255)
    d.ellipse([s(6), s(11), s(26), s(28)], fill=skin)
    d.ellipse([s(6), s(19), s(26), s(28)], fill=skin_dark)
    # vertical stripe lines
    for x in (12, 16, 20):
        d.line([(s(x), s(13)), (s(x), s(26))], fill=skin_dark, width=max(1, int(s(0.3))))
    # green tops
    d.polygon([(s(12), s(11)), (s(16), s(4)), (s(20), s(11))], fill=green)
    d.polygon([(s(14), s(11)), (s(18), s(6)), (s(20), s(11))], fill=green)
    return c


# ------------------------------------------------------------------ Grape --
def make_grape():
    c = canvas()
    d = ImageDraw.Draw(c)
    grape = (128, 74, 168, 255)
    grape_light = (172, 118, 208, 255)
    leaf = (86, 160, 76, 255)
    stem = (108, 76, 52, 255)
    # top row 3 grapes, then 2, then 1
    layers = ((8, 12), (12, 15), (16, 12), (10, 18), (14, 18), (18, 18), (12, 22), (16, 22), (14, 26))
    for (gx, gy) in layers:
        d.ellipse([s(gx - 2.5), s(gy - 2.5), s(gx + 2.5), s(gy + 2.5)], fill=grape)
        d.ellipse([s(gx - 2), s(gy - 2), s(gx - 0.5), s(gy - 0.5)], fill=grape_light)
    d.rectangle([s(15), s(4), s(17), s(10)], fill=stem)
    d.polygon([(s(17), s(6)), (s(24), s(4)), (s(22), s(10))], fill=leaf)
    return c


# ------------------------------------------------------------------ Apple --
def make_apple():
    c = canvas()
    d = ImageDraw.Draw(c)
    red = (220, 60, 60, 255)
    red_dark = (168, 42, 42, 255)
    highlight = (255, 168, 156, 255)
    stem = (108, 76, 52, 255)
    leaf = (86, 160, 76, 255)
    d.ellipse([s(6), s(9), s(26), s(28)], fill=red)
    d.ellipse([s(6), s(19), s(26), s(28)], fill=red_dark)
    d.ellipse([s(10), s(12), s(14), s(16)], fill=highlight)
    d.rectangle([s(15), s(5), s(17), s(10)], fill=stem)
    d.polygon([(s(17), s(6)), (s(22), s(4)), (s(21), s(9))], fill=leaf)
    return c


# -------------------------------------------------------------- Sunflower --
def make_sunflower():
    c = canvas()
    d = ImageDraw.Draw(c)
    petal = (250, 208, 60, 255)
    petal_dark = (208, 170, 40, 255)
    center = (86, 56, 32, 255)
    center_hi = (140, 92, 52, 255)
    stem = (86, 128, 60, 255)
    # petals as a ring
    import math
    for i in range(12):
        angle = i * (math.pi / 6)
        px = 16 + math.cos(angle) * 8
        py = 14 + math.sin(angle) * 8
        d.ellipse([s(px - 3), s(py - 3), s(px + 3), s(py + 3)],
                  fill=petal if i % 2 == 0 else petal_dark)
    d.ellipse([s(11), s(9), s(21), s(19)], fill=center)
    d.ellipse([s(13), s(11), s(19), s(17)], fill=center_hi)
    d.rectangle([s(15), s(19), s(17), s(28)], fill=stem)
    return c


CROPS = {
    "Potato.png": make_potato,
    "Wheat.png": make_wheat,
    "Strawberry.png": make_strawberry,
    "Blueberry.png": make_blueberry,
    "Watermelon.png": make_watermelon,
    "Cabbage.png": make_cabbage,
    "Lettuce.png": make_lettuce,
    "Eggplant.png": make_eggplant,
    "Chili.png": make_chili,
    "Cucumber.png": make_cucumber,
    "Onion.png": make_onion,
    "Grape.png": make_grape,
    "Apple.png": make_apple,
    "Sunflower.png": make_sunflower,
}


def main():
    for name, maker in CROPS.items():
        save(maker(), name)
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
