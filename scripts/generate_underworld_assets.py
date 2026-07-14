"""Generates art for the underworld: ancient ruin entrances (desert surface
side), the underground floor/obstacle/decor sets for its three zones
(infernal forge, cursed catacombs, corrupted temple), the return portal,
a demon enemy, and the Hellsteel currency icon. Drawn at higher internal
resolution then downsampled with NEAREST for crisp pixel-art edges,
matching the rest of the game's art pipeline. Re-run to tweak.
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter

CELL = 32
SCALE = 8
CS = CELL * SCALE
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

random.seed(7)


def s(v):
    return v * SCALE


# ---------------------------------------------------------------- ground --
# Each zone gets a base stone color, a crack/mortar color, and an accent
# (lava glow / bone flecks / mossy glow) scattered as small blobs so tiles
# read as worn and irregular rather than flat painted squares.
ZONE_PALETTES = {
    "forge": dict(base=(58, 40, 40, 255), base2=(70, 46, 44, 255), crack=(30, 18, 18, 255),
                  accent=(232, 120, 40, 255), accent2=(255, 176, 60, 255)),
    "catacombs": dict(base=(54, 48, 60, 255), base2=(62, 54, 68, 255), crack=(28, 24, 32, 255),
                       accent=(210, 200, 188, 255), accent2=(150, 90, 170, 255)),
    "temple": dict(base=(44, 56, 46, 255), base2=(52, 64, 54, 255), crack=(24, 32, 26, 255),
                   accent=(96, 168, 120, 255), accent2=(150, 220, 150, 255)),
}


def make_ground_tile(zone, variant_seed):
    rng = random.Random(variant_seed)
    p = ZONE_PALETTES[zone]
    canvas = Image.new("RGBA", (CS, CS), p["base"])
    draw = ImageDraw.Draw(canvas)

    # mottled patches of the secondary base color
    for _ in range(14):
        bx, by = rng.uniform(0, CS), rng.uniform(0, CS)
        r = rng.uniform(CS * 0.05, CS * 0.14)
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=p["base2"])

    # mortar/crack lines, a jagged connected network rather than straight cuts
    for _ in range(rng.randint(4, 6)):
        x, y = rng.uniform(0, CS), rng.uniform(0, CS)
        for _seg in range(rng.randint(3, 5)):
            nx = max(0, min(CS, x + rng.uniform(-CS * 0.22, CS * 0.22)))
            ny = max(0, min(CS, y + rng.uniform(-CS * 0.22, CS * 0.22)))
            draw.line([(x, y), (nx, ny)], fill=p["crack"], width=max(1, int(CS * 0.012)))
            x, y = nx, ny

    # glowing accent flecks (embers / bone shards / moss-light)
    for _ in range(rng.randint(5, 9)):
        ax, ay = rng.uniform(CS * 0.1, CS * 0.9), rng.uniform(CS * 0.1, CS * 0.9)
        r = rng.uniform(CS * 0.01, CS * 0.025)
        draw.ellipse([ax - r, ay - r, ax + r, ay + r], fill=rng.choice([p["accent"], p["accent2"]]))

    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=SCALE * 0.15))
    return canvas.resize((CELL, CELL), Image.NEAREST)


# ------------------------------------------------------------- obstacles --
def make_forge_spike():
    """Jagged obsidian spike, glowing at the cracks."""
    w, h = CELL, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    base_y = cs_h * 0.94
    draw.polygon([(cs_w * 0.5, cs_h * 0.32), (cs_w * 0.72, base_y), (cs_w * 0.28, base_y)],
                 fill=(30, 26, 30, 255))
    draw.polygon([(cs_w * 0.5, cs_h * 0.32), (cs_w * 0.6, base_y), (cs_w * 0.5, base_y)],
                 fill=(44, 38, 44, 255))
    for _ in range(6):
        t = random.uniform(0.4, 0.9)
        cx = cs_w * 0.5 + (random.uniform(-0.12, 0.12)) * cs_w
        cy = cs_h * 0.32 + t * (base_y - cs_h * 0.32)
        draw.line([(cx, cy), (cx + random.uniform(-8, 8), cy + random.uniform(6, 14))],
                  fill=(240, 130, 40, 255), width=max(1, int(cs_w * 0.02)))
    return canvas.resize((w, h), Image.NEAREST)


def make_bone_pile():
    """A jumbled heap of long bones topped with a skull, staked on a post
    like a grim catacomb waymarker — reads clearly at 32px unlike a soft
    rounded pile, which tended to blob into an indistinct shape."""
    w, h = CELL, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    bone = (222, 214, 196, 255)
    bone_shade = (182, 172, 156, 255)
    dark = (30, 20, 24, 255)
    base_y = cs_h * 0.94

    # crossed long bones leaning against the ground, knobbly ends
    for angle in (-1, 1):
        x0, y0 = cs_w * 0.5, base_y
        x1, y1 = cs_w * 0.5 + angle * cs_w * 0.26, cs_h * 0.5
        draw.line([(x0, y0), (x1, y1)], fill=bone, width=max(1, int(cs_w * 0.075)))
        for (ex, ey) in ((x0, y0), (x1, y1)):
            draw.ellipse([ex - cs_w * 0.055, ey - cs_w * 0.055, ex + cs_w * 0.055, ey + cs_w * 0.055],
                          fill=bone_shade)

    # skull perched at the crossing point
    sx0, sy0, sx1, sy1 = cs_w * 0.3, cs_h * 0.3, cs_w * 0.7, cs_h * 0.58
    draw.ellipse([sx0, sy0, sx1, sy1], fill=bone)
    draw.ellipse([sx0, sy0 + (sy1 - sy0) * 0.55, sx1, sy1], fill=bone_shade)
    draw.rectangle([cs_w * 0.42, sy1 - cs_h * 0.03, cs_w * 0.58, sy1 + cs_h * 0.08], fill=bone)
    draw.ellipse([cs_w * 0.38, cs_h * 0.4, cs_w * 0.47, cs_h * 0.49], fill=dark)
    draw.ellipse([cs_w * 0.53, cs_h * 0.4, cs_w * 0.62, cs_h * 0.49], fill=dark)
    draw.polygon([(cs_w * 0.47, cs_h * 0.5), (cs_w * 0.53, cs_h * 0.5), (cs_w * 0.5, cs_h * 0.54)], fill=dark)

    # a couple of loose bones scattered at the base
    draw.line([(cs_w * 0.2, base_y - cs_h * 0.02), (cs_w * 0.36, base_y + cs_h * 0.02)], fill=bone,
              width=max(1, int(cs_w * 0.05)))
    draw.line([(cs_w * 0.64, base_y + cs_h * 0.02), (cs_w * 0.82, base_y - cs_h * 0.02)], fill=bone_shade,
              width=max(1, int(cs_w * 0.05)))

    return canvas.resize((w, h), Image.NEAREST)


def make_broken_pillar():
    """A crumbling, moss/rune-corrupted temple column."""
    w, h = CELL, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    stone = (120, 118, 108, 255)
    stone_shade = (90, 90, 82, 255)
    moss = (90, 160, 100, 255)
    draw.rectangle([cs_w * 0.28, cs_h * 0.16, cs_w * 0.72, cs_h * 0.94], fill=stone)
    draw.rectangle([cs_w * 0.28, cs_h * 0.7, cs_w * 0.72, cs_h * 0.94], fill=stone_shade)
    draw.polygon([(cs_w * 0.22, cs_h * 0.16), (cs_w * 0.78, cs_h * 0.16),
                  (cs_w * 0.7, cs_h * 0.3), (cs_w * 0.3, cs_h * 0.3)], fill=stone)
    for frac in (0.3, 0.46, 0.62):
        draw.line([(cs_w * 0.28, cs_h * frac), (cs_w * 0.72, cs_h * frac)], fill=stone_shade,
                   width=max(1, int(cs_w * 0.02)))
    # a jagged broken top instead of a clean cap
    draw.polygon([(cs_w * 0.3, cs_h * 0.3), (cs_w * 0.42, cs_h * 0.16), (cs_w * 0.5, cs_h * 0.26),
                  (cs_w * 0.6, cs_h * 0.14), (cs_w * 0.7, cs_h * 0.3)], fill=(0, 0, 0, 0))
    draw.polygon([(cs_w * 0.32, cs_h * 0.3), (cs_w * 0.4, cs_h * 0.2), (cs_w * 0.5, cs_h * 0.28),
                  (cs_w * 0.62, cs_h * 0.18), (cs_w * 0.68, cs_h * 0.3)], fill=stone)
    draw.ellipse([cs_w * 0.32, cs_h * 0.4, cs_w * 0.48, cs_h * 0.54], fill=moss)
    draw.ellipse([cs_w * 0.5, cs_h * 0.55, cs_w * 0.68, cs_h * 0.68], fill=moss)
    return canvas.resize((w, h), Image.NEAREST)


# ------------------------------------------------------------------ decor --
def make_ember_cracks():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    x, y = CS * 0.2, CS * 0.8
    for _ in range(4):
        nx = x + random.uniform(CS * 0.1, CS * 0.2)
        ny = y - random.uniform(CS * 0.1, CS * 0.25)
        draw.line([(x, y), (nx, ny)], fill=(255, 150, 50, 230), width=max(1, int(CS * 0.02)))
        x, y = nx, ny
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_skull_decor():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    bone = (222, 214, 196, 255)
    draw.ellipse([CS * 0.32, CS * 0.34, CS * 0.68, CS * 0.62], fill=bone)
    draw.rectangle([CS * 0.4, CS * 0.56, CS * 0.6, CS * 0.68], fill=bone)
    draw.ellipse([CS * 0.38, CS * 0.44, CS * 0.46, CS * 0.52], fill=(30, 20, 24, 255))
    draw.ellipse([CS * 0.54, CS * 0.44, CS * 0.62, CS * 0.52], fill=(30, 20, 24, 255))
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_moss_glow():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    for _ in range(5):
        gx, gy = random.uniform(CS * 0.2, CS * 0.8), random.uniform(CS * 0.2, CS * 0.8)
        r = random.uniform(CS * 0.03, CS * 0.06)
        draw.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(140, 230, 150, 200))
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=SCALE * 0.3))
    return canvas.resize((CELL, CELL), Image.NEAREST)


# ------------------------------------------------------------- ruin/portal --
def make_ruin_entrance():
    """Weathered stone archway sunk into the desert, 2 tiles wide x 2 tall,
    with a dark portal glow inside — the surface-side entrance."""
    w, h = CELL * 2, CELL * 2
    cs_w, cs_h = w * SCALE, h * SCALE
    canvas = Image.new("RGBA", (cs_w, cs_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    stone = (168, 140, 96, 255)
    stone_shade = (130, 106, 70, 255)
    rune = (120, 220, 200, 255)

    # arch frame
    draw.polygon([(cs_w * 0.08, cs_h), (cs_w * 0.08, cs_h * 0.4), (cs_w * 0.5, cs_h * 0.08),
                  (cs_w * 0.92, cs_h * 0.4), (cs_w * 0.92, cs_h),
                  (cs_w * 0.78, cs_h), (cs_w * 0.78, cs_h * 0.46), (cs_w * 0.5, cs_h * 0.26),
                  (cs_w * 0.22, cs_h * 0.46), (cs_w * 0.22, cs_h)], fill=stone)
    draw.polygon([(cs_w * 0.08, cs_h), (cs_w * 0.08, cs_h * 0.4), (cs_w * 0.5, cs_h * 0.08),
                  (cs_w * 0.5, cs_h * 0.2), (cs_w * 0.18, cs_h * 0.46), (cs_w * 0.18, cs_h)],
                 fill=stone_shade)

    # dark portal void inside the arch
    draw.polygon([(cs_w * 0.22, cs_h), (cs_w * 0.22, cs_h * 0.46), (cs_w * 0.5, cs_h * 0.26),
                  (cs_w * 0.78, cs_h * 0.46), (cs_w * 0.78, cs_h)], fill=(14, 10, 16, 255))

    # glowing runes along the arch
    for t in (0.15, 0.32, 0.68, 0.85):
        rx = cs_w * (0.08 + t * 0.84)
        ry = cs_h * (0.4 + abs(t - 0.5) * 0.9) if t < 0.5 or t > 0.5 else cs_h * 0.16
        ry = cs_h * 0.4 - (0.5 - abs(t - 0.5)) * cs_h * 0.5
        draw.ellipse([rx - cs_w * 0.02, ry - cs_w * 0.02, rx + cs_w * 0.02, ry + cs_w * 0.02], fill=rune)

    # cracks in the stone
    for _ in range(5):
        cx, cy = random.uniform(cs_w * 0.1, cs_w * 0.9), random.uniform(cs_h * 0.5, cs_h * 0.95)
        draw.line([(cx, cy), (cx + random.uniform(-14, 14), cy + random.uniform(10, 26))],
                   fill=stone_shade, width=max(1, int(cs_w * 0.008)))

    return canvas.resize((w, h), Image.NEAREST)


def make_portal_frame(pulse):
    """pulse: 0 or 1 — a soft glowing rune circle marking the return point,
    two frames for a gentle flicker."""
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    outer = (120, 220, 200, 160 + pulse * 50)
    inner = (200, 250, 235, 200 + pulse * 40)
    r1 = CS * (0.34 + pulse * 0.02)
    r2 = CS * (0.2 + pulse * 0.015)
    cx, cy = CS * 0.5, CS * 0.5
    draw.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], outline=outer, width=max(1, int(CS * 0.03)))
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=inner, width=max(1, int(CS * 0.025)))
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=SCALE * 0.2))
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_portal_strip():
    strip = Image.new("RGBA", (CELL * 2, CELL), (0, 0, 0, 0))
    for i, pulse in enumerate((0, 1)):
        strip.paste(make_portal_frame(pulse), (i * CELL, 0))
    return strip


# ------------------------------------------------------------------ demon --
def make_demon():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    skin = (168, 46, 40, 255)
    skin_shade = (128, 30, 28, 255)
    horn = (60, 50, 54, 255)
    eye = (255, 220, 60, 255)
    claw = (40, 34, 36, 255)

    # legs
    draw.rectangle([s(11), s(24), s(15), s(29)], fill=skin_shade)
    draw.rectangle([s(17), s(24), s(21), s(29)], fill=skin_shade)
    draw.polygon([(s(10), s(29)), (s(16), s(29)), (s(13), s(31))], fill=claw)
    draw.polygon([(s(16), s(29)), (s(22), s(29)), (s(19), s(31))], fill=claw)

    # body
    draw.ellipse([s(8), s(13), s(24), s(27)], fill=skin)
    draw.ellipse([s(8), s(21), s(24), s(27)], fill=skin_shade)

    # arms + claws
    draw.line([(s(8), s(17)), (s(3), s(23))], fill=skin, width=max(1, int(s(2.4))))
    draw.line([(s(24), s(17)), (s(29), s(23))], fill=skin, width=max(1, int(s(2.4))))
    draw.polygon([(s(1), s(22)), (s(5), s(20)), (s(4), s(25))], fill=claw)
    draw.polygon([(s(31), s(22)), (s(27), s(20)), (s(28), s(25))], fill=claw)

    # head + horns
    draw.ellipse([s(10), s(4), s(22), s(15)], fill=skin)
    draw.polygon([(s(11), s(6)), (s(8), s(0)), (s(13), s(5))], fill=horn)
    draw.polygon([(s(21), s(6)), (s(24), s(0)), (s(19), s(5))], fill=horn)

    # glowing eyes + snarl
    draw.ellipse([s(12.5), s(8), s(15), s(10.2)], fill=eye)
    draw.ellipse([s(17), s(8), s(19.5), s(10.2)], fill=eye)
    for i in range(3):
        tx = s(12.5 + i * 2.3)
        draw.polygon([(tx, s(11.5)), (tx + s(1), s(11.5)), (tx + s(0.5), s(13))], fill=(240, 240, 232, 255))

    return canvas.resize((CELL, CELL), Image.NEAREST)


# --------------------------------------------------------------- currency --
def make_hellsteel():
    canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    dark = (54, 40, 42, 255)
    mid = (92, 58, 56, 255)
    glow = (232, 110, 46, 255)
    draw.polygon([(s(6), s(12)), (s(26), s(10)), (s(24), s(22)), (s(8), s(24))], fill=dark)
    draw.polygon([(s(6), s(12)), (s(26), s(10)), (s(25), s(14)), (s(7), s(16))], fill=mid)
    draw.line([(s(9), s(15)), (s(22), s(13.5))], fill=glow, width=max(1, int(s(0.9))))
    draw.line([(s(9), s(19)), (s(21), s(17.5))], fill=glow, width=max(1, int(s(0.6))))
    return canvas.resize((CELL, CELL), Image.NEAREST)


def main():
    for zone in ZONE_PALETTES:
        pass

    idx = 1
    for zone in ("forge", "catacombs", "temple"):
        for variant in range(2):
            make_ground_tile(zone, variant_seed=idx * 13 + variant).save(
                os.path.join(OUT_DIR, f"UnderworldGround{idx}.png"))
            print(f"wrote UnderworldGround{idx}.png ({zone})")
            idx += 1

    make_forge_spike().save(os.path.join(OUT_DIR, "UnderworldObstacle1.png"))
    make_bone_pile().save(os.path.join(OUT_DIR, "UnderworldObstacle2.png"))
    make_broken_pillar().save(os.path.join(OUT_DIR, "UnderworldObstacle3.png"))
    print("wrote UnderworldObstacle1-3.png")

    make_ember_cracks().save(os.path.join(OUT_DIR, "UnderworldDecor1.png"))
    make_skull_decor().save(os.path.join(OUT_DIR, "UnderworldDecor2.png"))
    make_moss_glow().save(os.path.join(OUT_DIR, "UnderworldDecor3.png"))
    print("wrote UnderworldDecor1-3.png")

    make_ruin_entrance().save(os.path.join(OUT_DIR, "RuinEntrance.png"))
    print("wrote RuinEntrance.png")

    make_portal_strip().save(os.path.join(OUT_DIR, "Portal.png"))
    print("wrote Portal.png (2-frame pulse strip)")

    make_demon().save(os.path.join(OUT_DIR, "Demon.png"))
    print("wrote Demon.png")

    make_hellsteel().save(os.path.join(OUT_DIR, "Hellsteel.png"))
    print("wrote Hellsteel.png")


if __name__ == "__main__":
    main()
