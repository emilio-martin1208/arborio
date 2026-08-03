"""Generates peaceful animal mobs: FarmImg/Rabbit.png and FarmImg/Bird.png
(32x32, single sprite each — animated in-game via a simple hop/bob and
horizontal flip rather than a walk-cycle sheet). Drawn at higher internal
resolution then downsampled with NEAREST for crisp pixel-art edges.
Re-run to tweak.
"""
import os

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
CS = CELL * SCALE
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

RABBIT_BODY = (222, 208, 194, 255)
RABBIT_SHADE = (192, 176, 162, 255)
RABBIT_INNER_EAR = (232, 176, 178, 255)
RABBIT_EYE = (40, 32, 28, 255)
RABBIT_TAIL = (240, 234, 226, 255)

BIRD_BODY = (92, 132, 168, 255)
BIRD_SHADE = (68, 102, 136, 255)
BIRD_BELLY = (230, 214, 170, 255)
BIRD_BEAK = (232, 158, 60, 255)
BIRD_EYE = (30, 26, 24, 255)

FOX_BODY = (206, 108, 52, 255)
FOX_SHADE = (170, 84, 38, 255)
FOX_BELLY = (240, 226, 204, 255)
FOX_EYE = (30, 26, 24, 255)
FOX_EAR_INNER = (40, 30, 26, 255)

DEER_BODY = (168, 124, 84, 255)
DEER_SHADE = (138, 100, 66, 255)
DEER_BELLY = (232, 218, 196, 255)
DEER_ANTLER = (196, 176, 150, 255)
DEER_EYE = (30, 26, 24, 255)

HEDGEHOG_SPIKE = (120, 100, 74, 255)
HEDGEHOG_SPIKE_SHADE = (94, 78, 56, 255)
HEDGEHOG_FACE = (214, 196, 172, 255)
HEDGEHOG_EYE = (30, 26, 24, 255)
HEDGEHOG_NOSE = (50, 40, 34, 255)

SQUIRREL_BODY = (176, 96, 54, 255)
SQUIRREL_SHADE = (144, 76, 42, 255)
SQUIRREL_BELLY = (236, 220, 196, 255)
SQUIRREL_EYE = (30, 26, 24, 255)


def s(v):
    return v * SCALE


def make_rabbit():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # tail
    draw.ellipse([s(20), s(17), s(25), s(22)], fill=RABBIT_TAIL)
    # body
    draw.ellipse([s(9), s(14), s(23), s(25)], fill=RABBIT_BODY)
    draw.ellipse([s(9), s(19), s(23), s(25)], fill=RABBIT_SHADE)
    # head
    draw.ellipse([s(15), s(9), s(25), s(18)], fill=RABBIT_BODY)
    # ears
    draw.ellipse([s(15.5), s(1), s(18.5), s(10)], fill=RABBIT_BODY)
    draw.ellipse([s(16.2), s(2.5), s(17.8), s(8.5)], fill=RABBIT_INNER_EAR)
    draw.ellipse([s(20.5), s(1.5), s(23.5), s(10.2)], fill=RABBIT_BODY)
    draw.ellipse([s(21.2), s(3), s(22.8), s(9)], fill=RABBIT_INNER_EAR)
    # face
    draw.ellipse([s(22.5), s(11.5), s(24), s(13)], fill=RABBIT_EYE)
    # front feet
    draw.ellipse([s(14), s(23), s(18), s(26.5)], fill=RABBIT_BODY)
    draw.ellipse([s(19), s(23), s(23), s(26.5)], fill=RABBIT_BODY)

    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_bird():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # tail feathers
    draw.polygon([(s(8), s(15)), (s(2), s(11)), (s(2), s(18))], fill=BIRD_SHADE)
    # body
    draw.ellipse([s(8), s(11), s(24), s(24)], fill=BIRD_BODY)
    draw.ellipse([s(8), s(18), s(24), s(24)], fill=BIRD_SHADE)
    # belly
    draw.ellipse([s(12), s(17), s(22), s(24)], fill=BIRD_BELLY)
    # head
    draw.ellipse([s(19), s(6), s(29), s(16)], fill=BIRD_BODY)
    # beak
    draw.polygon([(s(28), s(10)), (s(32), s(11.5)), (s(28), s(13.5))], fill=BIRD_BEAK)
    # eye
    draw.ellipse([s(25), s(9), s(26.5), s(10.5)], fill=BIRD_EYE)
    # feet
    draw.line([(s(15), s(24)), (s(14), s(27))], fill=BIRD_BEAK, width=max(1, int(s(0.3))))
    draw.line([(s(19), s(24)), (s(19.5), s(27))], fill=BIRD_BEAK, width=max(1, int(s(0.3))))

    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_fox():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # bushy tail
    draw.polygon([(s(3), s(20)), (s(11), s(14)), (s(12), s(24)), (s(4), s(27))], fill=FOX_BODY)
    draw.ellipse([s(2), s(22), s(8), s(28)], fill=(255, 255, 255, 255))
    # body
    draw.ellipse([s(9), s(14), s(24), s(25)], fill=FOX_BODY)
    draw.ellipse([s(9), s(19), s(24), s(25)], fill=FOX_SHADE)
    # belly
    draw.ellipse([s(13), s(18), s(21), s(25)], fill=FOX_BELLY)
    # head
    draw.ellipse([s(18), s(8), s(29), s(19)], fill=FOX_BODY)
    draw.polygon([(s(26), s(13)), (s(30), s(14.5)), (s(26), s(16.5))], fill=FOX_BELLY)
    # ears
    draw.polygon([(s(19), s(9)), (s(21), s(2)), (s(23), s(9))], fill=FOX_BODY)
    draw.polygon([(s(19.7), s(8)), (s(21), s(4)), (s(22.3), s(8))], fill=FOX_EAR_INNER)
    draw.polygon([(s(24), s(9)), (s(26), s(2.5)), (s(28), s(9))], fill=FOX_BODY)
    draw.polygon([(s(24.7), s(8)), (s(26), s(4.5)), (s(27.3), s(8))], fill=FOX_EAR_INNER)
    # eye
    draw.ellipse([s(25), s(11.5), s(26.5), s(13)], fill=FOX_EYE)
    # feet
    draw.ellipse([s(12), s(23), s(16), s(26.5)], fill=FOX_SHADE)
    draw.ellipse([s(19), s(23), s(23), s(26.5)], fill=FOX_SHADE)

    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_deer():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # legs (drawn first so the body sits over the top of them)
    for lx in (12, 16, 20, 24):
        draw.line([(s(lx), s(23)), (s(lx), s(30))], fill=DEER_SHADE, width=max(1, int(s(0.6))))
    # body
    draw.ellipse([s(8), s(13), s(25), s(24)], fill=DEER_BODY)
    draw.ellipse([s(8), s(18), s(25), s(24)], fill=DEER_SHADE)
    # belly
    draw.ellipse([s(12), s(18), s(21), s(24)], fill=DEER_BELLY)
    # head + neck
    draw.polygon([(s(20), s(19)), (s(24), s(8)), (s(28), s(19))], fill=DEER_BODY)
    draw.ellipse([s(22), s(6), s(30), s(14)], fill=DEER_BODY)
    # antlers
    draw.line([(s(23), s(7)), (s(21), s(1))], fill=DEER_ANTLER, width=max(1, int(s(0.4))))
    draw.line([(s(21), s(4)), (s(19), s(3))], fill=DEER_ANTLER, width=max(1, int(s(0.3))))
    draw.line([(s(26), s(6)), (s(28), s(0.5))], fill=DEER_ANTLER, width=max(1, int(s(0.4))))
    draw.line([(s(27), s(3)), (s(29), s(2))], fill=DEER_ANTLER, width=max(1, int(s(0.3))))
    # eye + tail
    draw.ellipse([s(27), s(9), s(28.5), s(10.5)], fill=DEER_EYE)
    draw.ellipse([s(6), s(16), s(9), s(20)], fill=DEER_BELLY)

    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_hedgehog():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # spiky back — a dome of little triangles over a base ellipse
    draw.ellipse([s(7), s(13), s(26), s(26)], fill=HEDGEHOG_SPIKE)
    for i, sx in enumerate(range(8, 25, 3)):
        h = 6 if i % 2 == 0 else 8
        draw.polygon([(s(sx), s(15)), (s(sx + 1.5), s(15 - h)), (s(sx + 3), s(15))],
                     fill=HEDGEHOG_SPIKE if i % 2 == 0 else HEDGEHOG_SPIKE_SHADE)
    # face
    draw.ellipse([s(6), s(17), s(15), s(25)], fill=HEDGEHOG_FACE)
    draw.ellipse([s(5.5), s(20), s(8.5), s(23)], fill=HEDGEHOG_NOSE)
    draw.ellipse([s(10), s(19), s(11.5), s(20.5)], fill=HEDGEHOG_EYE)
    # feet
    draw.ellipse([s(11), s(24), s(15), s(27)], fill=HEDGEHOG_SPIKE_SHADE)
    draw.ellipse([s(19), s(24), s(23), s(27)], fill=HEDGEHOG_SPIKE_SHADE)

    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_squirrel():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # big curled tail behind the body
    draw.polygon([(s(4), s(26)), (s(2), s(14)), (s(10), s(6)), (s(16), s(10)),
                  (s(11), s(12)), (s(8), s(20)), (s(9), s(27))], fill=SQUIRREL_BODY)
    draw.polygon([(s(5), s(24)), (s(4), s(15)), (s(9), s(9)), (s(12), s(11)),
                  (s(8), s(18)), (s(8), s(25))], fill=SQUIRREL_SHADE)
    # body + head
    draw.ellipse([s(12), s(15), s(24), s(26)], fill=SQUIRREL_BODY)
    draw.ellipse([s(14), s(20), s(24), s(26)], fill=SQUIRREL_BELLY)
    draw.ellipse([s(19), s(10), s(28), s(19)], fill=SQUIRREL_BODY)
    draw.ellipse([s(20), s(8), s(23), s(12)], fill=SQUIRREL_BODY)
    draw.ellipse([s(24), s(8), s(27), s(12)], fill=SQUIRREL_BODY)
    draw.ellipse([s(26), s(13), s(27.5), s(14.5)], fill=SQUIRREL_EYE)
    # acorn held in front paws
    draw.ellipse([s(18), s(19), s(22), s(23)], fill=(150, 100, 56, 255))

    return canvas.resize((CELL, CELL), Image.NEAREST)


def main():
    make_rabbit().save(os.path.join(OUT_DIR, "Rabbit.png"))
    make_bird().save(os.path.join(OUT_DIR, "Bird.png"))
    make_fox().save(os.path.join(OUT_DIR, "Fox.png"))
    make_deer().save(os.path.join(OUT_DIR, "Deer.png"))
    make_hedgehog().save(os.path.join(OUT_DIR, "Hedgehog.png"))
    make_squirrel().save(os.path.join(OUT_DIR, "Squirrel.png"))
    print("wrote Rabbit.png, Bird.png, Fox.png, Deer.png, Hedgehog.png, Squirrel.png")


if __name__ == "__main__":
    main()
