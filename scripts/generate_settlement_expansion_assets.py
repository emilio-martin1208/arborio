"""Generates the settlement-expansion art: biome-flavor village centerpiece
houses (SakuraHouse, DesertHouse, SnowHouse — 2 tiles wide x 2 tall, anchored
at the bottom like the farmhouse) and the walled-kingdom set (WallStone, a
1-tile flush, tileable wall segment, and KingdomGate, a 2-tile-wide toll
archway). Drawn at higher internal resolution then downsampled with NEAREST
for crisp pixel-art edges, matching the rest of the game's art pipeline.
Re-run to tweak.
"""
import os
import random

from PIL import Image, ImageDraw

CELL = 32
SCALE = 8
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")

random.seed(23)


def s(v):
    return v * SCALE


def canvas2x2():
    w, h = CELL * 2, CELL * 2
    return Image.new("RGBA", (w * SCALE, h * SCALE), (0, 0, 0, 0)), w, h


# --------------------------------------------------------- Sakura House --
def make_sakura_house():
    """Pagoda-style: dark timber frame, white plaster, a curved multi-tier
    roof, and a paper-screen (shoji) grid window."""
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    plaster = (238, 230, 216, 255)
    plaster_shade = (206, 196, 180, 255)
    timber = (54, 40, 34, 255)
    roof = (120, 40, 40, 255)
    roof_shade = (86, 26, 26, 255)
    roof_dark = (58, 44, 40, 255)
    paper = (222, 214, 192, 255)
    lantern = (222, 90, 60, 255)

    # walls
    d.rectangle([cs_w * 0.12, cs_h * 0.48, cs_w * 0.88, cs_h], fill=plaster)
    d.rectangle([cs_w * 0.12, cs_h * 0.84, cs_w * 0.88, cs_h], fill=plaster_shade)
    for x in (0.12, 0.32, 0.5, 0.68, 0.88):
        d.rectangle([cs_w * x, cs_h * 0.48, cs_w * x + cs_w * 0.015, cs_h], fill=timber)

    # shoji window
    d.rectangle([cs_w * 0.38, cs_h * 0.58, cs_w * 0.62, cs_h * 0.76], fill=paper)
    d.line([(cs_w * 0.5, cs_h * 0.58), (cs_w * 0.5, cs_h * 0.76)], fill=timber, width=max(1, int(cs_w * 0.012)))
    d.line([(cs_w * 0.38, cs_h * 0.67), (cs_w * 0.62, cs_h * 0.67)], fill=timber, width=max(1, int(cs_w * 0.012)))

    # lower roof tier (wide eave)
    d.polygon([(cs_w * 0.0, cs_h * 0.5), (cs_w * 0.5, cs_h * 0.3), (cs_w * 1.0, cs_h * 0.5),
               (cs_w * 0.94, cs_h * 0.56), (cs_w * 0.5, cs_h * 0.38), (cs_w * 0.06, cs_h * 0.56)], fill=roof)
    d.polygon([(cs_w * 0.5, cs_h * 0.3), (cs_w * 1.0, cs_h * 0.5), (cs_w * 0.94, cs_h * 0.56),
               (cs_w * 0.5, cs_h * 0.38)], fill=roof_shade)
    # upturned eave corners
    d.polygon([(cs_w * 0.0, cs_h * 0.5), (cs_w * 0.06, cs_h * 0.56), (cs_w * -0.06, cs_h * 0.58)], fill=roof)
    d.polygon([(cs_w * 1.0, cs_h * 0.5), (cs_w * 0.94, cs_h * 0.56), (cs_w * 1.06, cs_h * 0.58)], fill=roof)

    # upper roof tier + finial
    d.polygon([(cs_w * 0.2, cs_h * 0.3), (cs_w * 0.5, cs_h * 0.08), (cs_w * 0.8, cs_h * 0.3),
               (cs_w * 0.74, cs_h * 0.35), (cs_w * 0.5, cs_h * 0.18), (cs_w * 0.26, cs_h * 0.35)], fill=roof_dark)
    d.rectangle([cs_w * 0.485, cs_h * 0.02, cs_w * 0.515, cs_h * 0.1], fill=roof_dark)

    # a small red lantern by the door
    d.line([(cs_w * 0.2, cs_h * 0.6), (cs_w * 0.2, cs_h * 0.7)], fill=timber, width=max(1, int(cs_w * 0.01)))
    d.ellipse([cs_w * 0.16, cs_h * 0.7, cs_w * 0.24, cs_h * 0.78], fill=lantern)

    return c.resize((w, h), Image.NEAREST)


# --------------------------------------------------------- Desert House --
def make_desert_house():
    """Flat-roofed adobe: rounded sandstone walls, a deep-set shadowed
    window, and a woven wind-catch on the roof."""
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    adobe = (214, 176, 128, 255)
    adobe_shade = (182, 144, 100, 255)
    adobe_dark = (150, 116, 78, 255)
    window = (58, 42, 34, 255)
    beam = (120, 88, 56, 255)
    cloth = (196, 100, 70, 255)

    d.rounded_rectangle([cs_w * 0.08, cs_h * 0.38, cs_w * 0.92, cs_h], radius=cs_w * 0.06, fill=adobe)
    d.rectangle([cs_w * 0.08, cs_h * 0.78, cs_w * 0.92, cs_h], fill=adobe_shade)
    d.rounded_rectangle([cs_w * 0.08, cs_h * 0.38, cs_w * 0.92, cs_h * 0.5], radius=cs_w * 0.06, fill=adobe_dark)

    # roofline beam stubs poking out (classic adobe look)
    for bx in (0.14, 0.32, 0.68, 0.86):
        d.rectangle([cs_w * bx, cs_h * 0.36, cs_w * (bx + 0.04), cs_h * 0.46], fill=beam)

    # deep window
    d.rounded_rectangle([cs_w * 0.36, cs_h * 0.56, cs_w * 0.64, cs_h * 0.78], radius=cs_w * 0.03, fill=window)
    d.rectangle([cs_w * 0.36, cs_h * 0.56, cs_w * 0.64, cs_h * 0.6], fill=adobe_shade)

    # woven cloth wind-catch on the roof
    d.polygon([(cs_w * 0.62, cs_h * 0.36), (cs_w * 0.78, cs_h * 0.36), (cs_w * 0.74, cs_h * 0.18),
               (cs_w * 0.66, cs_h * 0.18)], fill=cloth)
    d.line([(cs_w * 0.66, cs_h * 0.22), (cs_w * 0.74, cs_h * 0.22)], fill=adobe_dark, width=max(1, int(cs_w * 0.01)))

    return c.resize((w, h), Image.NEAREST)


# ----------------------------------------------------------- Snow House --
def make_snow_house():
    """Timber cabin with a steep, thick snow-capped roof and icicles."""
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    log = (108, 78, 54, 255)
    log_shade = (82, 58, 40, 255)
    snow = (240, 246, 250, 255)
    snow_shade = (206, 220, 230, 255)
    window = (232, 190, 96, 255)
    ice = (200, 226, 236, 230)

    d.rectangle([cs_w * 0.1, cs_h * 0.44, cs_w * 0.9, cs_h], fill=log)
    for y in (0.52, 0.62, 0.72, 0.82, 0.92):
        d.line([(cs_w * 0.1, cs_h * y), (cs_w * 0.9, cs_h * y)], fill=log_shade, width=max(1, int(cs_h * 0.015)))

    # warm-lit window
    d.rectangle([cs_w * 0.38, cs_h * 0.58, cs_w * 0.62, cs_h * 0.76], fill=window)
    d.rectangle([cs_w * 0.38, cs_h * 0.58, cs_w * 0.62, cs_h * 0.61], fill=(255, 224, 140, 255))

    # steep roof, heavily snow-capped
    d.polygon([(cs_w * 0.0, cs_h * 0.46), (cs_w * 0.5, cs_h * 0.12), (cs_w * 1.0, cs_h * 0.46)], fill=log_shade)
    d.polygon([(cs_w * 0.02, cs_h * 0.42), (cs_w * 0.5, cs_h * 0.1), (cs_w * 0.98, cs_h * 0.42),
               (cs_w * 0.98, cs_h * 0.34), (cs_w * 0.5, cs_h * 0.04), (cs_w * 0.02, cs_h * 0.34)], fill=snow)
    d.polygon([(cs_w * 0.5, cs_h * 0.04), (cs_w * 0.98, cs_h * 0.34), (cs_w * 0.98, cs_h * 0.42),
               (cs_w * 0.5, cs_h * 0.12)], fill=snow_shade)

    # icicles along the eave
    for ix in (0.1, 0.22, 0.36, 0.5, 0.64, 0.78, 0.9):
        d.polygon([(cs_w * ix, cs_h * 0.42), (cs_w * (ix + 0.02), cs_h * 0.42), (cs_w * (ix + 0.01), cs_h * 0.49)],
                   fill=ice)

    return c.resize((w, h), Image.NEAREST)


# ------------------------------------------------------------- Wall/Gate --
def make_wall_stone():
    """1-tile flush stone wall block — repeats to form a perimeter."""
    canvas = Image.new("RGBA", (CELL * SCALE, CELL * SCALE), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    cs = CELL * SCALE
    stone = (150, 144, 138, 255)
    stone_shade = (114, 108, 102, 255)
    mortar = (176, 170, 164, 255)

    d.rectangle([0, 0, cs, cs], fill=mortar)
    rows = [(0.0, 0), (0.34, 1), (0.68, 0)]
    for y_frac, offset in rows:
        bw = cs * 0.34
        x = -bw / 2 if offset else 0
        while x < cs:
            x0, x1 = max(x, 0), min(x + bw - cs * 0.02, cs)
            if x1 > x0:
                d.rectangle([x0, cs * y_frac, x1, cs * (y_frac + 0.32)], fill=stone)
                d.rectangle([x0, cs * (y_frac + 0.24), x1, cs * (y_frac + 0.32)], fill=stone_shade)
            x += bw
    return canvas.resize((CELL, CELL), Image.NEAREST)


def make_kingdom_gate():
    """2-tile-wide toll archway: stone frame, heavy wooden doors, a
    battlement-style top, and a small toll sign."""
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    stone = (150, 144, 138, 255)
    stone_shade = (110, 104, 98, 255)
    door = (96, 66, 42, 255)
    door_shade = (72, 48, 30, 255)
    banding = (58, 50, 40, 255)
    sign = (196, 160, 90, 255)

    # side towers
    d.rectangle([cs_w * 0.0, cs_h * 0.2, cs_w * 0.24, cs_h], fill=stone)
    d.rectangle([cs_w * 0.76, cs_h * 0.2, cs_w * 1.0, cs_h], fill=stone)
    d.rectangle([cs_w * 0.0, cs_h * 0.82, cs_w * 0.24, cs_h], fill=stone_shade)
    d.rectangle([cs_w * 0.76, cs_h * 0.82, cs_w * 1.0, cs_h], fill=stone_shade)
    # battlements
    for bx in (0.02, 0.1, 0.18, 0.78, 0.86, 0.94):
        d.rectangle([cs_w * bx, cs_h * 0.12, cs_w * (bx + 0.06), cs_h * 0.22], fill=stone)

    # archway lintel connecting the towers
    d.rectangle([cs_w * 0.18, cs_h * 0.3, cs_w * 0.82, cs_h * 0.42], fill=stone)
    d.rectangle([cs_w * 0.18, cs_h * 0.36, cs_w * 0.82, cs_h * 0.42], fill=stone_shade)

    # double doors
    d.rectangle([cs_w * 0.26, cs_h * 0.42, cs_w * 0.52, cs_h], fill=door)
    d.rectangle([cs_w * 0.52, cs_h * 0.42, cs_w * 0.76, cs_h], fill=door_shade)
    for dx in (0.32, 0.44, 0.58, 0.7):
        d.line([(cs_w * dx, cs_h * 0.46), (cs_w * dx, cs_h * 0.96)], fill=banding, width=max(1, int(cs_w * 0.012)))
    d.line([(cs_w * 0.26, cs_h * 0.6), (cs_w * 0.76, cs_h * 0.6)], fill=banding, width=max(1, int(cs_w * 0.02)))
    d.ellipse([cs_w * 0.48, cs_h * 0.68, cs_w * 0.54, cs_h * 0.76], fill=(220, 190, 100, 255))

    # toll sign hanging beside the gate
    d.rectangle([cs_w * 0.02, cs_h * 0.5, cs_w * 0.16, cs_h * 0.66], fill=sign)
    d.rectangle([cs_w * 0.02, cs_h * 0.5, cs_w * 0.16, cs_h * 0.54], fill=(150, 116, 60, 255))

    return c.resize((w, h), Image.NEAREST)


# --------------------------------------------------------- Tribal Hut --
def make_tribal_hut():
    """Archipelago village centerpiece: round wattle-and-daub walls, a
    conical dried-palm-thatch roof, and a totem pole with a carved mask
    out front."""
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    wall = (196, 156, 104, 255)
    wall_shade = (162, 126, 80, 255)
    thatch = (188, 148, 66, 255)
    thatch_shade = (150, 114, 48, 255)
    thatch_dark = (120, 90, 38, 255)
    door = (70, 48, 32, 255)
    totem_wood = (120, 84, 52, 255)
    totem_mask = (196, 70, 56, 255)
    totem_eyes = (250, 236, 200, 255)

    # round hut base
    d.ellipse([cs_w * 0.14, cs_h * 0.5, cs_w * 0.86, cs_h], fill=wall)
    d.ellipse([cs_w * 0.14, cs_h * 0.78, cs_w * 0.86, cs_h], fill=wall_shade)
    for x in (0.28, 0.5, 0.72):
        d.line([(cs_w * x, cs_h * 0.54), (cs_w * x, cs_h)], fill=wall_shade, width=max(1, int(cs_w * 0.012)))

    # doorway
    d.rounded_rectangle([cs_w * 0.44, cs_h * 0.7, cs_w * 0.58, cs_h], radius=cs_w * 0.06, fill=door)

    # conical thatched roof, built from stacked rings for a shaggy texture
    d.polygon([(cs_w * 0.06, cs_h * 0.52), (cs_w * 0.5, cs_h * 0.06), (cs_w * 0.94, cs_h * 0.52)], fill=thatch_dark)
    for i, frac in enumerate((0.0, 0.16, 0.32)):
        top = cs_h * (0.06 + frac)
        span = 0.94 - frac * 1.5
        d.polygon([(cs_w * (0.5 - span / 2), cs_h * 0.52), (cs_w * 0.5, top),
                   (cs_w * (0.5 + span / 2), cs_h * 0.52)], fill=thatch if i % 2 == 0 else thatch_shade)

    # totem pole beside the hut
    d.rectangle([cs_w * 0.02, cs_h * 0.42, cs_w * 0.11, cs_h], fill=totem_wood)
    d.rounded_rectangle([cs_w * 0.005, cs_h * 0.34, cs_w * 0.125, cs_h * 0.5], radius=cs_w * 0.02, fill=totem_mask)
    d.ellipse([cs_w * 0.02, cs_h * 0.39, cs_w * 0.05, cs_h * 0.42], fill=totem_eyes)
    d.ellipse([cs_w * 0.08, cs_h * 0.39, cs_w * 0.11, cs_h * 0.42], fill=totem_eyes)

    return c.resize((w, h), Image.NEAREST)


# -------------------------------------------------------- Monk Temple --
def make_monk_temple():
    """A distant, sacred landmark: pale stone base, a tiered gilded roof,
    a hanging bronze gong, and prayer flags strung to one side — meant to
    read as clearly grander/rarer than an ordinary village building."""
    c, w, h = canvas2x2()
    d = ImageDraw.Draw(c)
    cs_w, cs_h = w * SCALE, h * SCALE
    stone = (222, 214, 196, 255)
    stone_shade = (188, 178, 158, 255)
    roof = (150, 40, 44, 255)
    roof_shade = (110, 26, 30, 255)
    gold = (222, 184, 90, 255)
    gold_dark = (176, 138, 58, 255)
    gong = (198, 150, 78, 255)
    gong_dark = (150, 108, 52, 255)
    flag_colors = [(196, 70, 60, 255), (222, 184, 90, 255), (70, 120, 160, 255), (90, 150, 90, 255)]

    # stone base
    d.rectangle([cs_w * 0.1, cs_h * 0.5, cs_w * 0.9, cs_h], fill=stone)
    d.rectangle([cs_w * 0.1, cs_h * 0.84, cs_w * 0.9, cs_h], fill=stone_shade)
    for x in (0.1, 0.34, 0.5, 0.66, 0.9):
        d.rectangle([cs_w * x, cs_h * 0.5, cs_w * x + cs_w * 0.015, cs_h], fill=stone_shade)

    # gilded doorway arch
    d.rounded_rectangle([cs_w * 0.4, cs_h * 0.6, cs_w * 0.6, cs_h], radius=cs_w * 0.1, fill=gold_dark)
    d.rounded_rectangle([cs_w * 0.42, cs_h * 0.64, cs_w * 0.58, cs_h], radius=cs_w * 0.08, fill=(40, 30, 24, 255))

    # tiered pagoda roof
    d.polygon([(cs_w * -0.02, cs_h * 0.5), (cs_w * 0.5, cs_h * 0.22), (cs_w * 1.02, cs_h * 0.5),
               (cs_w * 0.94, cs_h * 0.56), (cs_w * 0.5, cs_h * 0.3), (cs_w * 0.06, cs_h * 0.56)], fill=roof)
    d.polygon([(cs_w * 0.5, cs_h * 0.22), (cs_w * 1.02, cs_h * 0.5), (cs_w * 0.94, cs_h * 0.56),
               (cs_w * 0.5, cs_h * 0.3)], fill=roof_shade)
    d.polygon([(cs_w * 0.22, cs_h * 0.22), (cs_w * 0.5, cs_h * 0.02), (cs_w * 0.78, cs_h * 0.22),
               (cs_w * 0.7, cs_h * 0.27), (cs_w * 0.5, cs_h * 0.1), (cs_w * 0.3, cs_h * 0.27)], fill=gold_dark)
    d.rectangle([cs_w * 0.485, cs_h * -0.02, cs_w * 0.515, cs_h * 0.05], fill=gold)

    # hanging bronze gong beside the doorway
    d.rectangle([cs_w * 0.24, cs_h * 0.48, cs_w * 0.26, cs_h * 0.66], fill=gold_dark)
    d.ellipse([cs_w * 0.16, cs_h * 0.6, cs_w * 0.32, cs_h * 0.76], fill=gong)
    d.ellipse([cs_w * 0.2, cs_h * 0.64, cs_w * 0.28, cs_h * 0.72], fill=gong_dark)

    # prayer flags strung from the roof eave
    flag_y = cs_h * 0.56
    d.line([(cs_w * 0.7, flag_y), (cs_w * 0.98, flag_y - cs_h * 0.04)], fill=(210, 200, 180, 255), width=max(1, int(cs_w * 0.006)))
    for i, fx in enumerate((0.74, 0.81, 0.88, 0.95)):
        fy = flag_y - cs_h * 0.04 * (fx - 0.7) / 0.28
        d.polygon([(cs_w * fx, fy), (cs_w * (fx + 0.04), fy), (cs_w * (fx + 0.02), fy + cs_h * 0.07)],
                   fill=flag_colors[i % len(flag_colors)])

    return c.resize((w, h), Image.NEAREST)


def main():
    make_sakura_house().save(os.path.join(OUT_DIR, "SakuraHouse.png"))
    make_desert_house().save(os.path.join(OUT_DIR, "DesertHouse.png"))
    make_snow_house().save(os.path.join(OUT_DIR, "SnowHouse.png"))
    print("wrote SakuraHouse.png, DesertHouse.png, SnowHouse.png")

    make_wall_stone().save(os.path.join(OUT_DIR, "WallStone.png"))
    make_kingdom_gate().save(os.path.join(OUT_DIR, "KingdomGate.png"))
    print("wrote WallStone.png, KingdomGate.png")

    make_tribal_hut().save(os.path.join(OUT_DIR, "TribalHut.png"))
    make_monk_temple().save(os.path.join(OUT_DIR, "MonkTemple.png"))
    print("wrote TribalHut.png, MonkTemple.png")


if __name__ == "__main__":
    main()
