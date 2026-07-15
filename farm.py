import math
import os
import random

import pygame
from PIL import Image, ImageDraw, ImageFilter

pygame.init()

# Display must come first
TILE_SIZE = 50
INITIAL_VIEW_TILES = 10
UI_BAR_HEIGHT = 120

WORLD_W, WORLD_H = 320, 320
WIDTH = INITIAL_VIEW_TILES * TILE_SIZE
HEIGHT = INITIAL_VIEW_TILES * TILE_SIZE + UI_BAR_HEIGHT
#SCALED renders at the internal WIDTH x HEIGHT then scales the whole
#surface up to the largest whole-number multiple that fits the display,
#preserving pixel-art crispness. RESIZABLE lets the user drag the window
#(the internal resolution stays the same; only the display size changes).
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("Arborio - Tile Farming")

# Path to assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_PATH = os.path.join(BASE_DIR, "FarmImg")

# Image loader
def load_image(name):
    return pygame.image.load(os.path.join(ASSET_PATH, name)).convert_alpha()

# Now it’s safe to load images

IMG_CORN = load_image("Corn.png")
IMG_TOMATO = load_image("Tomato.png")
IMG_PUMPKIN = load_image("pumpkin.png")
IMG_CARROT = load_image("Carrot.png")
IMG_POTATO = load_image("Potato.png")
IMG_WHEAT = load_image("Wheat.png")
IMG_STRAWBERRY = load_image("Strawberry.png")
IMG_BLUEBERRY = load_image("Blueberry.png")
IMG_WATERMELON = load_image("Watermelon.png")
IMG_CABBAGE = load_image("Cabbage.png")
IMG_LETTUCE = load_image("Lettuce.png")
IMG_EGGPLANT = load_image("Eggplant.png")
IMG_CHILI = load_image("Chili.png")
IMG_CUCUMBER = load_image("Cucumber.png")
IMG_ONION = load_image("Onion.png")
IMG_GRAPE = load_image("Grape.png")
IMG_APPLE = load_image("Apple.png")
IMG_SUNFLOWER = load_image("Sunflower.png")
IMG_FISH = load_image("Fish.png")
IMG_FISH_FLIPPED = pygame.transform.flip(IMG_FISH, True, False)
CROP_IMAGES = {
    "corn": IMG_CORN, "tomato": IMG_TOMATO, "pumpkin": IMG_PUMPKIN, "carrot": IMG_CARROT,
    "potato": IMG_POTATO, "wheat": IMG_WHEAT, "strawberry": IMG_STRAWBERRY, "blueberry": IMG_BLUEBERRY,
    "watermelon": IMG_WATERMELON, "cabbage": IMG_CABBAGE, "lettuce": IMG_LETTUCE,
    "eggplant": IMG_EGGPLANT, "chili": IMG_CHILI, "cucumber": IMG_CUCUMBER, "onion": IMG_ONION,
    "grape": IMG_GRAPE, "apple": IMG_APPLE, "sunflower": IMG_SUNFLOWER,
}

IMG_BED = load_image("Bed.png")
IMG_HOUSE = load_image("House.png")  # 2 tiles wide x 2 tiles tall; only the bottom row is solid
IMG_FLOOR = load_image("Floor.png")
IMG_WALL = load_image("Wall.png")

# Grass ground variants: each is a 3-frame wind-sway strip (neutral, lean-left,
# lean-right) with its own subtly-different natural color palette. Each frame
# is drawn oversized (see OVERFLOW in generate_ground_tiles.py) and rendered
# overlapping its neighbors so blade tips spill across tile boundaries
# instead of every tile reading as a hard perfect square.
GRASS_FRAME_SIZE = 46  # must match EXPORT_CELL in scripts/generate_ground_tiles.py
GRASS_OVERFLOW_SCALE = GRASS_FRAME_SIZE / 32  # 32 = the nominal 1-tile size
# Ground1-12 meadow/maple, 13-24 sakura, 25-36 jungle, 37-48 desert (see BIOME_GROUND_INDICES)
GROUND_VARIANT_COUNT = 60


def load_grass_frames(name):
    sheet = load_image(name)
    return [sheet.subsurface(pygame.Rect(col * GRASS_FRAME_SIZE, 0, GRASS_FRAME_SIZE, GRASS_FRAME_SIZE))
            for col in range(3)]


GROUND_FRAMES = [load_grass_frames(f"Ground{i}.png") for i in range(1, GROUND_VARIANT_COUNT + 1)]

# Water: 4 shape variants (like the grass ground variants), each a 3-frame
# ripple strip in the same 46px oversized-tile format with its own irregular
# soft-alpha edge so lake tiles blend into each other and into the shore
# instead of reading as a grid of flat blue squares. farm.py assigns a
# variant per tile via coherent noise so a whole lake doesn't repeat one
# shape identically tile after tile.
WATER_VARIANT_COUNT = 12
WATER_FRAMES = [load_grass_frames(f"Water{i}.png") for i in range(1, WATER_VARIANT_COUNT + 1)]


def water_frame_for(x, y, ticks):
    """Slower cycle than grass sway — ripples roll gently across still water."""
    wave = math.sin(ticks * 0.0006 + (x * 0.7 + y * 0.4))
    if wave > 0.33:
        return 2
    if wave < -0.33:
        return 1
    return 0


def grass_frame_for(x, y, ticks):
    """Per-tile phased sway so wind rolls across the field like a wave,
    rather than every blade of grass swaying in perfect unison."""
    wave = math.sin(ticks * 0.0009 + (x * 0.9 + y * 0.5))
    if wave > 0.33:
        return 2  # lean right
    if wave < -0.33:
        return 1  # lean left
    return 0  # neutral
IMG_DECOR1 = load_image("Decor1.png")
IMG_DECOR2 = load_image("Decor2.png")
IMG_DECOR3 = load_image("Decor3.png")
IMG_DECOR4 = load_image("Decor4.png")
DECOR_IMAGES = [IMG_DECOR1, IMG_DECOR2, IMG_DECOR3, IMG_DECOR4]
DECOR_CHANCE = 0.06  # fraction of grass tiles that get a sparse flower/rock/bush decoration

# Biome-specific decor so each biome reads as visually distinct rather than
# every biome scattering the same generic flowers/rocks/bushes. Meadow/maple
# keep the original generic set (a fresh grassy-field look suits both).
BIOME_DECOR_IMAGES = {
    "meadow": DECOR_IMAGES,
    "maple": DECOR_IMAGES + [load_image("MapleDecor1.png"), load_image("MapleDecor2.png")],
    "sakura": [load_image("SakuraDecor1.png"), load_image("SakuraDecor2.png")],
    "jungle": [load_image("JungleDecor1.png"), load_image("JungleDecor2.png")],
    "desert": [load_image("DesertDecor1.png"), load_image("DesertDecor2.png")],
    "tundra": [load_image("TundraDecor1.png"), load_image("TundraDecor2.png")],
}

IMG_PATH = load_image("Path.png")

# Trees: 1 tile wide x 2 tiles tall, anchored at the bottom like the house.
# 6 species (oak, tall_oak, pine, bushy, maple, sapling) for a mixed forest.
TREE_IMAGES = [load_image(f"Tree{i}.png") for i in range(1, 11)]

# Peaceful wandering animal mobs (no combat, just ambiance)
ANIMAL_IMAGES = {"rabbit": load_image("Rabbit.png"), "bird": load_image("Bird.png")}
ANIMAL_IMAGES_FLIPPED = {k: pygame.transform.flip(v, True, False) for k, v in ANIMAL_IMAGES.items()}
ANIMAL_SPEED = {"rabbit": 1.3, "bird": 1.8}

# Marketplace structures
OUTPOST_IMAGES = [load_image(f"Outpost{i}.png") for i in range(1, 5)]        # small stall: 1 tile wide x 2 tall
MARKETPLACE_IMAGES = [load_image(f"Marketplace{i}.png") for i in range(1, 4)]  # larger stall: 2 tiles wide x 2 tall

IMG_STABLE = load_image("Stable.png")  # 2 tiles wide x 2 tall, anchored like the house
IMG_WELL = load_image("Well.png")  # 1 tile, sits flush (no overhang)
IMG_SHRINE = load_image("Shrine.png")  # 2 tiles wide x 2 tall, anchored like the house
IMG_BLACKSMITH = load_image("Blacksmith.png")  # 2 tiles wide x 2 tall
IMG_FISHERMAN_SHACK = load_image("FishermanShack.png")  # 2 tiles wide x 2 tall

# Biome-flavor village centerpieces + walled-kingdom set
FLAVOR_HOUSE_IMAGES = {
    "sakura": load_image("SakuraHouse.png"),
    "desert": load_image("DesertHouse.png"),
    "snow": load_image("SnowHouse.png"),
}
BIOME_TO_FLAVOR = {"sakura": "sakura", "desert": "desert", "tundra": "snow"}
IMG_WALL_STONE = load_image("WallStone.png")  # 1 tile, flush
IMG_KINGDOM_GATE = load_image("KingdomGate.png")  # 2 tiles wide x 2 tall, anchored like the house
KINGDOM_NAMES = ["Ashenfall", "Rivenhall", "Goldmere", "Stonewatch", "Emberkeep", "Thornwall"]
HORSE_SHEET = load_image("Horse.png")  # 3-frame gallop strip: neutral, stride-A, stride-B
HORSE_FRAME_SIZE = 32
HORSE_FRAMES = [HORSE_SHEET.subsurface(pygame.Rect(col * HORSE_FRAME_SIZE, 0, HORSE_FRAME_SIZE, HORSE_FRAME_SIZE))
                for col in range(3)]
HORSE_FRAMES_FLIPPED = [pygame.transform.flip(f, True, False) for f in HORSE_FRAMES]
HORSE_SPEED_MULT = 2  # tiles moved per keypress while mounted

# Farm base-building: a mineable boulder (surface stone/iron node), raw
# resource icons, processed-goods icons, a construction-site overlay, and
# every player-constructible building sprite.
IMG_BOULDER = load_image("Boulder.png")
RESOURCE_IMAGES = {
    "wood": load_image("Wood.png"),
    "stone": load_image("Stone.png"),
    "iron": load_image("Iron.png"),
}
GOODS_IMAGES = {
    "flour": load_image("Flour.png"),
    "feed": load_image("Feed.png"),
    "jam": load_image("Jam.png"),
    "pickles": load_image("Pickles.png"),
    "honey": load_image("Honey.png"),
    "cider": load_image("Cider.png"),
    "lumber": load_image("Lumber.png"),
    "bricks": load_image("Bricks.png"),
    "ingot": load_image("Ingot.png"),
}
IMG_CONSTRUCTION_SITE = load_image("ConstructionSite.png")  # 2x2 scaffolding overlay
FARM_BUILDING_IMAGES = {
    "mill": load_image("Mill.png"),
    "preserving_shed": load_image("PreservingShed.png"),
    "brewery": load_image("Brewery.png"),
    "workshop": load_image("Workshop.png"),
    "barn": load_image("Barn.png"),
    "silo": load_image("Silo.png"),
    "warehouse": load_image("Warehouse.png"),
    "farm_well": load_image("FarmWell.png"),
    "windmill": load_image("Windmill.png"),
    "greenhouse": load_image("Greenhouse.png"),
    "beehive": load_image("BeeHive.png"),
    "orchard_marker": load_image("OrchardMarker.png"),
    "watchtower": load_image("Watchtower.png"),
    "magic_ward": load_image("MagicWard.png"),
}

# Underworld: ancient ruins hidden in the desert lead down into a dangerous
# underground realm. Ground tiles are static (no wind-sway needed for stone),
# grouped 2-per-zone like the biome ground variants above.
UNDERWORLD_ZONES = ["forge", "catacombs", "temple"]
UNDERWORLD_GROUND_IMAGES = [load_image(f"UnderworldGround{i}.png") for i in range(1, 37)]
UNDERWORLD_GROUND_INDICES = {
    "forge": list(range(0, 12)), "catacombs": list(range(12, 24)), "temple": list(range(24, 36)),
}
UNDERWORLD_OBSTACLE_IMAGES = [load_image(f"UnderworldObstacle{i}.png") for i in range(1, 4)]
UNDERWORLD_OBSTACLE_INDEX = {"forge": 0, "catacombs": 1, "temple": 2}
UNDERWORLD_DECOR_IMAGES = [load_image(f"UnderworldDecor{i}.png") for i in range(1, 4)]
UNDERWORLD_DECOR_INDEX = {"forge": 0, "catacombs": 1, "temple": 2}
UNDERWORLD_DECOR_CHANCE = 0.05

IMG_RUIN = load_image("RuinEntrance.png")  # 2 tiles wide x 2 tall, anchored like the house/stable
PORTAL_SHEET = load_image("Portal.png")  # 2-frame glow-pulse strip
PORTAL_FRAMES = [PORTAL_SHEET.subsurface(pygame.Rect(col * 32, 0, 32, 32)) for col in range(2)]
IMG_DEMON = load_image("Demon.png")
IMG_DEMON_FLIPPED = pygame.transform.flip(IMG_DEMON, True, False)
IMG_HELLSTEEL = load_image("Hellsteel.png")
DEMON_SPEED = 0.9  # tiles per second, slower and more deliberate than the peaceful animals
DEMON_MAX_HP = 3
DEMON_ATTACK_RANGE = 0.75  # tiles
DEMON_ATTACK_DAMAGE = 1
DEMON_ATTACK_COOLDOWN = 1.2  # seconds between hits from the same demon
PLAYER_HURT_FLASH_DURATION = 0.35
SWORD_REACH = 1.1  # tiles; nearest demon within this radius takes the hit
PURIFY_KILLS_NEEDED = 6  # demons defeated (per ruin) before its surroundings start to purify
PURIFY_RADIUS = 6

# Hand-held tool/weapon sprites, drawn diagonally (see generate_tool_assets.py)
# so they read naturally both idle-carried and mid-rotation during a swing.
TOOL_IMAGES = {
    "Pick": load_image("Tool_Pick.png"),
    "Hoe": load_image("Tool_Hoe.png"),
    "Axe": load_image("Tool_Axe.png"),
    "Sword": load_image("Tool_Sword.png"),
}
SWING_DURATION = 0.22  # seconds a swing animation takes to complete
# Per-facing (idle carry angle, swing arc sweep, anchor x-frac, anchor y-frac)
# in player-sprite-relative coordinates. Angles are degrees, counter-clockwise.
TOOL_POSE = {
    "down":  (-20, -100, 0.66, 0.62),
    "up":    (160, 100, 0.85, 0.46),
    "left":  (100, 100, 0.02, 0.58),
    "right": (-100, -100, 0.98, 0.58),
}

VILLAGER_NAMES = ["Elin", "Tomas", "Greta", "Oskar", "Nia", "Bram"]
VILLAGER_GREETINGS = [
    "Lovely day at the market, isn't it?",
    "Welcome to the village! Stop by the stable if you need a horse.",
    "Business has been good around here lately.",
    "Haven't seen you before — new to these parts?",
]
IMG_EMERALD = load_image("Emerald.png")

# Irregular tilled-soil patches (chosen per plot so plots don't look gridded)
SOIL_IMAGES = [load_image(f"Soil{i}.png") for i in range(1, 13)]

# Generic growth-stage art shared by all crop types before they mature,
# plus the withered/dead stage shown if a ripe crop isn't harvested in time.
STAGE_IMAGES = {
    "planted": load_image("Stage_Seedling.png"),
    "sprout": load_image("Stage_Sprout.png"),
    "growing": load_image("Stage_Growing.png"),
    "withered": load_image("Stage_Withered.png"),
}
STAGE_POP_DURATION = 0.4  # seconds for a new stage to "pop" in to full size

# Player sprite sheets: rows = down/left/right/up, columns = 4 walk frames
PLAYER_FRAME_SIZE = 32
PLAYER_DIRECTIONS = ["down", "left", "right", "up"]
CHARACTER_NAMES = ["Hank", "Jeff", "Martha", "Marin"]
CHARACTER_BIOS = {
    "Hank": "A steady hand who's worked this land his whole life — patient, practical, and up before sunrise.",
    "Jeff": "A restless wanderer who took up farming to slow down, though he still can't sit still for long.",
    "Martha": "Sharp-tongued and sharper-minded, she treats every harvest like a puzzle worth solving.",
    "Marin": "Quiet and observant, with a well-worn atlas in her pack and a soft spot for anything wild and growing.",
}


def load_character_frames(name):
    sheet = load_image(f"Player_{name}.png")
    return {
        direction: [
            sheet.subsurface(pygame.Rect(col * PLAYER_FRAME_SIZE, row * PLAYER_FRAME_SIZE,
                                          PLAYER_FRAME_SIZE, PLAYER_FRAME_SIZE))
            for col in range(4)
        ]
        for row, direction in enumerate(PLAYER_DIRECTIONS)
    }


PLAYER_FRAMES_BY_CHARACTER = {name: load_character_frames(name) for name in CHARACTER_NAMES}
CHARACTER_PORTRAITS = {
    name: pygame.transform.scale(frames["down"][0], (96, 96))
    for name, frames in PLAYER_FRAMES_BY_CHARACTER.items()
}
PLAYER_FRAMES = PLAYER_FRAMES_BY_CHARACTER["Hank"]  # overwritten once a character is chosen

# Villagers aren't player-selectable, so their frames are loaded separately
# (after CHARACTER_PORTRAITS above) rather than joining the character-select pool.
VILLAGER_FRAMES_BY_NAME = {name: load_character_frames(name) for name in VILLAGER_NAMES}







clock = pygame.time.Clock()
FONT_NAME = "rockwell"  # falls back to the default system font if unavailable
font = pygame.font.SysFont(FONT_NAME, 26, bold=True)
ui_font = pygame.font.SysFont(FONT_NAME, 19, bold=True)  # smaller font for in-game UI
tool_font = pygame.font.SysFont(FONT_NAME, 16, bold=True)  # compact label for the HUD tool slot
micro_font = pygame.font.SysFont(FONT_NAME, 12, bold=True)  # crop journal cells — tight space

#Text colors and drop-shadow rendering, for a warmer, more readable look
TEXT_CREAM = (250, 240, 218)
TEXT_GOLD = (255, 205, 92)
TEXT_SHADOW = (46, 30, 20)


def render_text(font_obj, text, color, shadow=TEXT_SHADOW):
    shadow_surf = font_obj.render(text, True, shadow)
    main_surf = font_obj.render(text, True, color)
    combined = pygame.Surface((main_surf.get_width() + 2, main_surf.get_height() + 2), pygame.SRCALPHA)
    combined.blit(shadow_surf, (2, 2))
    combined.blit(main_surf, (0, 0))
    return combined


def wrap_text(font_obj, text, max_width):
    """Greedy word-wrap: returns a list of lines, each rendering no wider
    than max_width in font_obj."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font_obj.size(candidate)[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped_centered(surface, font_obj, text, color, center_x, top_y, max_width, line_gap=4, alpha=None):
    """Word-wraps text to max_width and draws it horizontally centered on
    center_x, stacked top-to-bottom from top_y. Since every line is at most
    max_width wide and centered on center_x, as long as center_x/max_width
    keep the whole block within the screen this can never run off either
    edge — unlike a single unwrapped render_text call, which just keeps
    growing wider until it does. Returns the total height drawn, so callers
    stacking multiple messages can offset the next one below it."""
    lines = wrap_text(font_obj, text, max_width)
    y = top_y
    for line in lines:
        surf = render_text(font_obj, line, color)
        if alpha is not None:
            surf.set_alpha(alpha)
        surface.blit(surf, (center_x - surf.get_width() // 2, y))
        y += surf.get_height() + line_gap
    return y - top_y


def draw_clock(surface, center, radius, progress, color=TEXT_CREAM):
    """progress: 0..1 fraction through the current day."""
    pygame.draw.circle(surface, color, center, radius, 2)
    for tick in range(4):
        angle = tick * (math.pi / 2)
        x1 = center[0] + math.cos(angle) * radius * 0.78
        y1 = center[1] + math.sin(angle) * radius * 0.78
        x2 = center[0] + math.cos(angle) * radius
        y2 = center[1] + math.sin(angle) * radius
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)

    minute_angle = progress * 2 * math.pi - math.pi / 2
    mx = center[0] + math.cos(minute_angle) * radius * 0.8
    my = center[1] + math.sin(minute_angle) * radius * 0.8
    pygame.draw.line(surface, color, center, (mx, my), 2)

    hour_angle = (progress * 0.5) * 2 * math.pi - math.pi / 2
    hx = center[0] + math.cos(hour_angle) * radius * 0.48
    hy = center[1] + math.sin(hour_angle) * radius * 0.48
    pygame.draw.line(surface, color, center, (hx, hy), 3)


def draw_bar(surface, rect, fraction, fill_color, bg_color=(60, 48, 38), border_color=TEXT_CREAM):
    pygame.draw.rect(surface, bg_color, rect)
    fraction = max(0.0, min(1.0, fraction))
    fill_w = int(rect.width * fraction)
    if fill_w > 0:
        pygame.draw.rect(surface, fill_color, (rect.x, rect.y, fill_w, rect.height))
    pygame.draw.rect(surface, border_color, rect, 2)


#Hotbar slot geometry, shared by hit-testing (mouse events) and drawing
BAR_TOP = HEIGHT - UI_BAR_HEIGHT
HOTBAR_ROW_Y = BAR_TOP + 10 + 52
HOTBAR_ICON_SIZE = 28
HOTBAR_SLOT_W = 78
HOTBAR_X = 12


def hotbar_slot_rect(i):
    x = HOTBAR_X + i * HOTBAR_SLOT_W
    return pygame.Rect(x - 3, HOTBAR_ROW_Y - 3, HOTBAR_ICON_SIZE + 6, HOTBAR_ICON_SIZE + 6)


def hotbar_slot_at(pos):
    for i in range(len(hotbar_slots)):
        if hotbar_slot_rect(i).collidepoint(pos):
            return i
    return None


#Colors
COLORS = {
    "grass": (80, 160, 80),
    "planted": (120, 80, 40),
    "sprout": (120, 180, 80),
    "grown": (60, 180, 60),
    "player": (200, 200, 255),
    "bed": (100, 100, 200),
    "tree": (34, 139, 34)
}

#Seeds — the master catalog of every crop in the game. Everything with an
#unlock_hint is locked at start; the crop journal (X key) shows locked ones
#as grayed-out silhouettes with the hint underneath. Seeds appear in
#seed_inventory only once discovered.
# wither_time: how long a ripe/grown crop stays harvestable before it dies.
SEEDS = {
    "corn":       {"name": "Corn",       "color": (230, 220, 40), "grow_time": 5.0,  "xp": 0.5, "wither_time": 10.0, "value": 2},
    "carrot":     {"name": "Carrot",     "color": (255, 140, 40), "grow_time": 3.0,  "xp": 1.0, "wither_time": 6.0,  "value": 3},
    "tomato":     {"name": "Tomato",     "color": (255, 50, 50),  "grow_time": 4.0,  "xp": 1.2, "wither_time": 8.0,  "value": 4, "unlock_hint": "Reach level 5"},
    "pumpkin":    {"name": "Pumpkin",    "color": (255, 100, 0),  "grow_time": 60.0, "xp": 10,  "wither_time": 40.0, "value": 20, "unlock_hint": "Reach level 3"},
    "potato":     {"name": "Potato",     "color": (170, 130, 84), "grow_time": 4.0,  "xp": 0.8, "wither_time": 12.0, "value": 3, "unlock_hint": "Marketplace"},
    "wheat":      {"name": "Wheat",      "color": (232, 200, 96), "grow_time": 5.0,  "xp": 0.6, "wither_time": 20.0, "value": 2, "unlock_hint": "Fisherman"},
    "strawberry": {"name": "Strawberry", "color": (222, 60, 68),  "grow_time": 6.0,  "xp": 1.6, "wither_time": 8.0,  "value": 5, "unlock_hint": "Marketplace"},
    "blueberry":  {"name": "Blueberry",  "color": (68, 96, 176),  "grow_time": 7.0,  "xp": 2.0, "wither_time": 8.0,  "value": 6, "unlock_hint": "Marketplace"},
    "watermelon": {"name": "Watermelon", "color": (222, 74, 82),  "grow_time": 10.0, "xp": 3.0, "wither_time": 12.0, "value": 8, "unlock_hint": "Reach level 8"},
    "cabbage":    {"name": "Cabbage",    "color": (108, 172, 92), "grow_time": 5.0,  "xp": 1.2, "wither_time": 14.0, "value": 4, "unlock_hint": "Marketplace"},
    "lettuce":    {"name": "Lettuce",    "color": (128, 200, 108),"grow_time": 3.5,  "xp": 0.9, "wither_time": 7.0,  "value": 3, "unlock_hint": "Marketplace"},
    "eggplant":   {"name": "Eggplant",   "color": (108, 62, 128), "grow_time": 6.0,  "xp": 1.6, "wither_time": 10.0, "value": 5, "unlock_hint": "Reach level 6"},
    "chili":      {"name": "Chili",      "color": (222, 52, 40),  "grow_time": 5.5,  "xp": 1.5, "wither_time": 9.0,  "value": 5, "unlock_hint": "Blacksmith"},
    "cucumber":   {"name": "Cucumber",   "color": (86, 148, 68),  "grow_time": 4.5,  "xp": 1.1, "wither_time": 9.0,  "value": 4, "unlock_hint": "Marketplace"},
    "onion":      {"name": "Onion",      "color": (222, 178, 108),"grow_time": 4.0,  "xp": 1.0, "wither_time": 11.0, "value": 3, "unlock_hint": "Marketplace"},
    "grape":      {"name": "Grape",      "color": (128, 74, 168), "grow_time": 9.0,  "xp": 2.4, "wither_time": 12.0, "value": 7, "unlock_hint": "Reach level 7"},
    "apple":      {"name": "Apple",      "color": (220, 60, 60),  "grow_time": 12.0, "xp": 3.5, "wither_time": 15.0, "value": 9, "unlock_hint": "Reach level 9"},
    "sunflower":  {"name": "Sunflower",  "color": (250, 208, 60), "grow_time": 5.0,  "xp": 2.0, "wither_time": 12.0, "value": 4, "unlock_hint": "Reach level 10"},
}
# Which seeds the player has actually discovered (unlocked) — starts with the
# two freely available at spawn, everything else is added by leveling up,
# marketplace unlocks, or NPC trades.
DISCOVERED_SEEDS = {"corn", "carrot"}
selected_seed = "corn"
seed_inventory = {"corn": 5, "carrot": 3}
inventory_open = False
emeralds = 15  # starting currency for the marketplace

#Tools
pick_tool = {"name": "Pick", "level": 1, "color": (200, 180, 50)}
hoe_tool = None
axe_tool = None
sword_tool = {"name": "Sword", "level": 1, "color": (190, 194, 200)}
unlocked_tools = [pick_tool, sword_tool]
equipped_tool = pick_tool

#Hotbar: an ordered, drag-and-drop-reorderable arrangement of seeds/tools.
#Reordering only changes visual slot order; selection still points at the
#same seed_inventory / unlocked_tools entries.
hotbar_slots = [{"kind": "seed", "key": k} for k in seed_inventory] + \
               [{"kind": "tool", "tool": t} for t in unlocked_tools]
drag_slot = None  # index into hotbar_slots currently being dragged, or None

# ============================================================================
# Farm base-building system: raw resources, a build-your-own set of
# buildings (storage/production/infrastructure/defense), construction and
# decay over time, a farming skill track, and periodic underworld raids.
# The farm starts ruined — a few tiles near the house carry broken-fence/
# rubble decor that clears as the farm is restored (see FARM_TIERS).
# ============================================================================

#Raw resources gathered from the surface: wood from chopping trees, stone
#and iron from mining boulders. A small starting stash reflects the
#"ruined farm has scraps lying around" framing rather than starting at zero.
resources = {"wood": 15, "stone": 8, "iron": 0}

#Processed goods produced by production buildings, sellable at markets for
#more than their raw ingredients.
goods_inventory = {}

GOODS_INFO = {
    "flour":   {"name": "Flour",       "image": "flour",   "value": 6},
    "feed":    {"name": "Animal Feed", "image": "feed",     "value": 5},
    "jam":     {"name": "Jam",         "image": "jam",      "value": 10},
    "pickles": {"name": "Pickles",     "image": "pickles",  "value": 9},
    "honey":   {"name": "Honey",       "image": "honey",    "value": 11},
    "cider":   {"name": "Cider",       "image": "cider",    "value": 14},
    "lumber":  {"name": "Lumber",      "image": "lumber",   "value": 4},
    "bricks":  {"name": "Bricks",      "image": "bricks",   "value": 4},
    "ingot":   {"name": "Ingot",       "image": "ingot",    "value": 12},
}

#Farm restoration tiers: a meta-progression readout of how far the farm has
#come from "abandoned ruin" to "legendary base", driven by how many player
#buildings are actually finished and standing (see recompute_farm_tier()).
FARM_TIERS = ["Abandoned Farm", "Basic Homestead", "Functional Farm",
              "Advanced Agricultural Base", "Legendary Farmstead"]
farm_tier = 0

#Farming skill: a second, slower XP track fed by the same harvests that
#drive the main level, unlocking passive farm-wide bonuses at milestones
#instead of one-off rewards.
farming_skill_xp = 0.0
farming_skill_level = 1


def farming_skill_xp_needed(lvl):
    return 20.0 * lvl


def farming_skill_growth_mult():
    """Stacking passive growth-speed bonus from skill milestones."""
    mult = 1.0
    if farming_skill_level >= 5:
        mult *= 1.2
    if farming_skill_level >= 20:
        mult *= 1.25
    return mult


def farming_skill_bypasses_winter():
    """Level 20 'ancient farming technology' — acts like a permanent,
    farm-wide Greenhouse for winter growth."""
    return farming_skill_level >= 20


def farming_skill_build_discount():
    """Level 10 'animal breeding' know-how shaves a bit off every build/
    repair cost rather than simulating full livestock breeding mechanics."""
    return 0.9 if farming_skill_level >= 10 else 1.0


#Winter is the one season that actually slows crop growth (a real reason for
#the Greenhouse/Well/skill-tree bonuses to matter) — other seasons are
#neutral. Bypassed by a nearby active Greenhouse or the level-20 skill.
WINTER_GROWTH_MULT = 0.7

#Every buildable building type: category (for the build menu), footprint in
#tiles, resource + emerald cost, and how many in-game days construction
#takes. "days" are measured the same way the rest of the game already
#measures a day (DAY_LENGTH seconds of real time), not a discrete sleep-to-
#advance event, so construction quietly progresses whether or not you sleep.
FARM_BUILDING_TYPES = {
    "mill":            {"label": "Mill",            "category": "Production",     "footprint": (2, 2), "cost": {"wood": 60, "stone": 20, "emeralds": 40}, "build_days": 2},
    "preserving_shed": {"label": "Preserving Shed",  "category": "Production",     "footprint": (2, 2), "cost": {"wood": 50, "stone": 15, "emeralds": 35}, "build_days": 2},
    "brewery":         {"label": "Brewery",          "category": "Production",     "footprint": (2, 2), "cost": {"wood": 40, "stone": 40, "emeralds": 55}, "build_days": 3},
    "workshop":        {"label": "Workshop",         "category": "Production",     "footprint": (2, 2), "cost": {"wood": 70, "stone": 30, "emeralds": 45}, "build_days": 2},
    "barn":            {"label": "Barn",             "category": "Storage",       "footprint": (2, 2), "cost": {"wood": 90, "stone": 20, "emeralds": 50}, "build_days": 3},
    "silo":            {"label": "Silo",             "category": "Storage",       "footprint": (2, 2), "cost": {"wood": 20, "stone": 60, "emeralds": 40}, "build_days": 2},
    "warehouse":       {"label": "Warehouse",        "category": "Storage",       "footprint": (2, 2), "cost": {"wood": 80, "stone": 50, "emeralds": 60}, "build_days": 3},
    "farm_well":       {"label": "Well",             "category": "Infrastructure","footprint": (1, 1), "cost": {"stone": 30, "emeralds": 20}, "build_days": 1},
    "windmill":        {"label": "Windmill",         "category": "Infrastructure","footprint": (2, 2), "cost": {"wood": 70, "stone": 30, "emeralds": 50}, "build_days": 3},
    "greenhouse":      {"label": "Greenhouse",       "category": "Infrastructure","footprint": (2, 2), "cost": {"wood": 50, "stone": 10, "emeralds": 70}, "build_days": 3},
    "beehive":         {"label": "Bee Hive",         "category": "Infrastructure","footprint": (1, 1), "cost": {"wood": 15, "emeralds": 15}, "build_days": 1},
    "orchard_marker":  {"label": "Orchard Plot",     "category": "Infrastructure","footprint": (1, 1), "cost": {"wood": 10, "emeralds": 10}, "build_days": 1},
    "watchtower":      {"label": "Watchtower",       "category": "Defense",       "footprint": (2, 2), "cost": {"wood": 60, "stone": 20, "emeralds": 45}, "build_days": 2},
    "magic_ward":      {"label": "Magic Ward",       "category": "Defense",       "footprint": (2, 2), "cost": {"stone": 40, "iron": 15, "emeralds": 60}, "build_days": 2},
}
BUILD_MENU_ORDER = list(FARM_BUILDING_TYPES.keys())

#Production recipes: each production building offers a small menu of
#conversions from raw crops/materials into a higher-value good.
PRODUCTION_RECIPES = {
    "mill": [
        {"name": "Flour (from Wheat)", "input": {"wheat": 4}, "output": "flour", "qty": 2, "time": 8.0},
        {"name": "Animal Feed (from Corn)", "input": {"corn": 4}, "output": "feed", "qty": 2, "time": 8.0},
    ],
    "preserving_shed": [
        {"name": "Strawberry Jam", "input": {"strawberry": 3}, "output": "jam", "qty": 2, "time": 10.0},
        {"name": "Blueberry Jam", "input": {"blueberry": 3}, "output": "jam", "qty": 2, "time": 10.0},
        {"name": "Pickles (from Cucumber)", "input": {"cucumber": 4}, "output": "pickles", "qty": 2, "time": 10.0},
    ],
    "brewery": [
        {"name": "Apple Cider", "input": {"apple": 3}, "output": "cider", "qty": 2, "time": 14.0},
        {"name": "Grape Cider", "input": {"grape": 4}, "output": "cider", "qty": 2, "time": 14.0},
    ],
    "workshop": [
        {"name": "Lumber (from Wood)", "input": {"wood": 10}, "output": "lumber", "qty": 4, "time": 6.0},
        {"name": "Bricks (from Stone)", "input": {"stone": 10}, "output": "bricks", "qty": 4, "time": 6.0},
        {"name": "Ingot (from Iron)", "input": {"iron": 6}, "output": "ingot", "qty": 2, "time": 10.0},
    ],
}

#Player-constructed building instances. Each is:
# {"type", "x", "y", "stage": "building"|"active", "progress_days", "condition"
#  (0..100), "processing": None or {"recipe_name","time_left","output","qty"}}
farm_buildings = []

CONDITION_DECAY_PER_DAY = 2.2  # condition points lost per in-game day while active
CONDITION_WORN = 50
CONDITION_POOR = 20
REPAIR_COST_FRACTION = 0.35  # fraction of the original build cost to fully repair
REPAIR_DAYS = 0.4

build_menu_open = False
build_menu_selection = 0
build_message = ""
build_message_timer = 0.0

building_panel_open = False
active_building = None
building_panel_selection = 0

farm_status_open = False

#Ancient-farmstead orchard tiles: once an Orchard Plot is built, apple/grape
#planted on its own footprint auto-replant on harvest instead of consuming
#another seed — populated with the marker's footprint tiles.
orchard_tiles = set()

#Farm defense: once the player has been to the underworld at least once,
#the surface farm can be raided by demons that wandered up through a ruin.
has_visited_underworld = False
farm_demons = []
RAID_CHECK_INTERVAL = 45.0  # seconds of real time between raid rolls
RAID_CHANCE = 0.35
raid_timer = 0.0
raid_warning_timer = 0.0  # counts down after a Watchtower spots something, before the raid actually spawns


#Assigns grass color variants in smooth, organic patches (like natural
#sun/shade/moisture variation) via 2D value noise, instead of per-tile
#randomness (a checkerboard) or a symmetric formula (ring artifacts).
NOISE_CELL = 7  # tiles per noise grid cell


def _noise_value(gx, gy):
    h = (gx * 374761393 + gy * 668265263) & 0xffffffff
    h = (h ^ (h >> 13)) * 1274126177 & 0xffffffff
    h = h ^ (h >> 16)
    return (h & 0xffffffff) / 0xffffffff


def _smoothstep(t):
    return t * t * (3 - 2 * t)


def _smooth_noise(x, y, cell):
    """Continuous 2D value noise in [0, 1) — the same interpolated-hash
    technique region_variant bins into a discrete variant index, exposed
    here as a raw float for anything that needs a smooth wiggle (like a
    lake's coastline) rather than a bucketed choice."""
    gx, gy = x / cell, y / cell
    gx0, gy0 = int(gx), int(gy)
    tx, ty = _smoothstep(gx - gx0), _smoothstep(gy - gy0)
    v00, v10 = _noise_value(gx0, gy0), _noise_value(gx0 + 1, gy0)
    v01, v11 = _noise_value(gx0, gy0 + 1), _noise_value(gx0 + 1, gy0 + 1)
    top = v00 * (1 - tx) + v10 * tx
    bottom = v01 * (1 - tx) + v11 * tx
    return top * (1 - ty) + bottom * ty


def region_variant(x, y, cell=NOISE_CELL, bins=GROUND_VARIANT_COUNT):
    value = _smooth_noise(x, y, cell)
    return max(0, min(bins - 1, int(value * bins)))


#House: a solid 2-wide x 1-tall building footprint on the farm (the sprite
#itself is drawn 2 tiles tall so the roof/chimney overhang above it), with
#a walkable doorway row beneath it. Stepping onto a door tile enters the interior.
HOUSE_POS = (1, 1)  # kept off the world edge so the roof overhang has room to render
HOUSE_TILES = {(HOUSE_POS[0] + dx, HOUSE_POS[1]) for dx in range(2)}
DOOR_ROW = HOUSE_POS[1] + 1
DOOR_TILES = {(HOUSE_POS[0] + dx, DOOR_ROW) for dx in range(2)}
HOUSE_OVERHANG_TILES = {(x, HOUSE_POS[1] - 1) for x in range(HOUSE_POS[0], HOUSE_POS[0] + 2)}
FARM_BLOCKED_TILES = HOUSE_TILES | DOOR_TILES | HOUSE_OVERHANG_TILES  # kept clear of trees/crops

#Biomes: large, coarse-noise regions (much bigger than the fine grass-color
#patches above) assign each part of the world to a distinct biome. The area
#around the house is always kept as meadow so the starting farm feels stable.
BIOME_NAMES = ["meadow", "maple", "sakura", "jungle", "desert", "tundra"]
BIOME_NOISE_CELL = 40  # large so each biome forms a real, explorable region on the bigger map
BIOME_SAFE_RADIUS = 11  # tiles around the house that are always meadow

# Indices into GROUND_FRAMES / TREE_IMAGES per biome (0-based). 12 variants
# per biome family (see generate_ground_tiles.py) instead of just 2-6, so
# the same handful of textures don't repeat constantly across a big field.
BIOME_GROUND_INDICES = {
    "meadow": list(range(0, 12)),
    "maple": list(range(0, 12)),
    "sakura": list(range(12, 24)),
    "jungle": list(range(24, 36)),
    "desert": list(range(36, 48)),
    "tundra": list(range(48, 60)),
}
BIOME_TREE_INDICES = {
    "meadow": [0, 1, 2, 3, 5],       # oak, tall_oak, pine, bushy, sapling
    "maple": [4, 4, 4, 0, 1],        # mostly maple, some oak/tall_oak
    "sakura": [6, 6, 6, 5],          # mostly sakura, a touch of sapling
    "jungle": [7, 7, 7, 3],          # mostly jungle_tree, a touch of bushy
    "desert": [8],                   # cactus only
    "tundra": [9, 9, 9, 3],          # mostly snow_pine, a touch of bushy
}


def biome_for(x, y):
    if math.hypot(x - HOUSE_POS[0], y - HOUSE_POS[1]) < BIOME_SAFE_RADIUS:
        return "meadow"
    idx = region_variant(x, y, cell=BIOME_NOISE_CELL, bins=len(BIOME_NAMES))
    return BIOME_NAMES[idx]


#Farm Grid
farm = [
    [
        {
            "state": "grass",
            "timer": 0.0,
            "seed": None,
            "biome": (biome := biome_for(x, y)),
            "ground_variant": BIOME_GROUND_INDICES[biome][region_variant(x, y) % len(BIOME_GROUND_INDICES[biome])],
            "ground_static": None,
            "decor": random.choice(BIOME_DECOR_IMAGES[biome]) if random.random() < DECOR_CHANCE else None,
            "soil_variant": None,
            "stage_anim": 0.0,
            "tree_variant": None,
            "market_id": None,
            "stable_id": None,
            "ruin_id": None,
            "smithy_id": None,
            "shack_id": None,
            "water_variant": None,
            "building_id": None,
            "kingdom_id": None
        }
        for x in range(WORLD_W)
    ]
    for y in range(WORLD_H)
]

#Map overlay: biome layout doesn't change, so pre-render it once as a
#WORLD_W x WORLD_H surface (1px per tile) and just scale/overlay markers
#on top whenever the map is opened, rather than rebuilding it every time.
MAP_BIOME_COLORS = {
    "meadow": (94, 153, 64), "maple": (176, 108, 58), "sakura": (232, 158, 186),
    "jungle": (30, 96, 54), "desert": (216, 190, 140), "tundra": (220, 230, 236),
}
MAP_SURFACE = pygame.Surface((WORLD_W, WORLD_H))
for _my in range(WORLD_H):
    for _mx in range(WORLD_W):
        MAP_SURFACE.set_at((_mx, _my), MAP_BIOME_COLORS[farm[_my][_mx]["biome"]])

#A short dirt path leading away from the door, for a hand-designed touch
PATH_LENGTH = 4
PATH_TILES = set()
for _path_i in range(1, PATH_LENGTH + 1):
    _py = DOOR_ROW + _path_i
    if _py < WORLD_H:
        farm[_py][HOUSE_POS[0]]["ground_static"] = IMG_PATH
        farm[_py][HOUSE_POS[0] + 1]["ground_static"] = IMG_PATH
        PATH_TILES.add((HOUSE_POS[0], _py))
        PATH_TILES.add((HOUSE_POS[0] + 1, _py))
FARM_BLOCKED_TILES |= PATH_TILES  # keep the path clear of trees too

#House interior: a small fixed room, no camera scrolling needed
location = "farm"  # or "house"
INTERIOR_W, INTERIOR_H = 6, 5
INTERIOR_TILE_SIZE = 70
INTERIOR_BED = (2, 1)
INTERIOR_DOOR = (INTERIOR_W // 2, INTERIOR_H - 1)
interior_player_x, interior_player_y = INTERIOR_DOOR[0], INTERIOR_DOOR[1] - 1

#Player
player_x, player_y = 1, 3  # just below the house door, clear of it
player_facing = "down"
player_is_walking = False
player_walk_timer = 0.0
WALK_FRAME_TIME = 0.09  # seconds per step frame
swinging = False  # mid tool-swing animation (chop/harvest/plant/strike)
swing_timer = 0.0
PLAYER_MAX_HP = 10
player_hp = PLAYER_MAX_HP
player_hurt_flash = 0.0  # seconds remaining on a brief red damage flash
mounted = False  # riding a rented horse: moves HORSE_SPEED_MULT tiles per keypress
HORSE_RENTAL_COST = 8
MOVE_REPEAT_DELAY = 0.22  # seconds between steps while a direction key is held down
move_repeat_timer = 0.0
surface_return_x, surface_return_y = player_x, player_y  # where to reappear when leaving a ruin
harvested = 0
day = 1

#Seasons: a fixed-length cycle driven purely by day count, shifting the
#farm's mood (a color tint, since re-skinning every tile per season is out
#of scope) and which weather is possible (snow only in winter, rain otherwise).
SEASONS = ["Spring", "Summer", "Fall", "Winter"]
SEASON_LENGTH_DAYS = 7
SEASON_TINTS = {
    "Spring": (255, 200, 220, 22),
    "Summer": (255, 220, 90, 40),
    "Fall": (200, 100, 40, 65),
    "Winter": (205, 225, 248, 75),
}


def season_for_day(d):
    return SEASONS[((d - 1) // SEASON_LENGTH_DAYS) % len(SEASONS)]


xp = 0.0
level = 1
xp_needed = 10 + level**2 * 8  # matches the quadratic level-up curve below
day_timer = 0.0
DAY_LENGTH = 45.0  # seconds of real time the HUD clock treats as one in-game day


#Weather: rain and snow are mutually exclusive periodic events. weather_timer
#counts toward the next event while calm; rain_timer/snow_timer count down
#the active event's remaining duration once one starts.
WEATHER_INTERVAL = 20.0
RAIN_DURATION = 6.0
RAIN_DROP_COUNT = 70
SNOW_DURATION = 10.0
SNOW_FLAKE_COUNT = 60
weather_timer = 0.0
rain_timer = 0.0
raining = False
rain_drops = []
snow_timer = 0.0
snowing = False
snow_flakes = []

#Tree spawn
TREE_INTERVAL = 20.0
tree_timer = 0.0

#Haste mechanic
haste = False
haste_timer = 0.0
HASTE_DURATION = 3.0

#Level system
LEVELS = {
    1: {"reward": None, "achievement": "Fresh Farmer"},
    2: {"reward": ["Upgrade Pick to Lvl2", "Unlock Hoe"], "achievement": "Level 2 Farmer"},
    3: {"reward": ["Unlock Pumpkin Seeds"], "achievement": "Pumpkin Picker"},
    4: {"reward": ["Upgrade Pickaxe"], "achievement": "Garden Helper"},
    5: {"reward": ["Unlock Tomato Seeds"], "achievement": "Tomato Tycoon"},
    6: {"reward": ["Unlock Axe", "Unlock Eggplant Seeds"], "achievement": "Woodcutter"},
    7: {"reward": ["Carrot XP Boost", "Unlock Grape Seeds"], "achievement": "Vintner"},
    8: {"reward": ["Unlock Watermelon Seeds"], "achievement": "Melon Master"},
    9: {"reward": ["Upgrade Pick Lvl3", "Upgrade Hoe Lvl2", "Unlock Apple Seeds"], "achievement": "Orchardist"},
    10: {"reward": ["Unlock Sunflower Seeds"], "achievement": "Grand Farmer"}
}

achievements_unlocked = []
achievement_queue = []
ACHIEVEMENT_DISPLAY_TIME = 3.0

level_popup_queue = []
LEVEL_POPUP_TIME = 2.0

day_popup_queue = []
DAY_POPUP_TIME = 5.0

level_up_pending = False
level_up_message = ""
reward_options = []

#Seed selection keys
SEED_KEYS = [pygame.K_r, pygame.K_t, pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p]

FACING_DELTA = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

#Zoom / View
zoom = 1.2  # start slightly zoomed in for a closer camera, without excessive upscale blur
tile_draw_size = int(TILE_SIZE * zoom)
view_width, view_height = 10, 10  # Initial view

#Player glide: the player's own on-screen position eases toward their real
#(tile-locked) position instead of popping instantly, and the camera tracks
#that same eased value — so the player visually glides tile-to-tile and the
#world scrolls in lockstep underneath, instead of the sprite jumping a full
#tile while the camera trails behind separately (which looked worse, not
#smoother: a jarring pop followed by a catch-up slide).
PLAYER_GLIDE_SMOOTH_SPEED = 12.0  # higher = glide catches up to the tile faster
player_visual_x = float(player_x)
player_visual_y = float(player_y)

VIGNETTE = load_image("Vignette.png")

def start_screen():
    """Runs the title/menu/character-select loop. Returns the chosen character name."""
    state = "menu"  # "menu" | "instructions" | "character_select"
    selected_option = 0
    options = ["Start Game", "Instructions", "Quit"]
    selected_character_index = 0
    blink_timer = 0.0
    blink_on = True

    # Mini farm preview, shown behind the main menu
    preview_w, preview_h = 10, 10
    preview_farm = [[{"state": "grass", "timer": 0.0, "seed": None} for x in range(preview_w)] for y in range(preview_h)]
    preview_seeds = ["corn", "carrot"]

    title_font = pygame.font.SysFont(FONT_NAME, 38, bold=True)
    subtitle_font = pygame.font.SysFont(FONT_NAME, 17, bold=True)

    while True:
        dt = clock.tick(60)/1000.0
        blink_timer += dt
        if blink_timer >= 0.5:  # blink every 0.5 sec
            blink_on = not blink_on
            blink_timer = 0.0

        screen.fill((50,50,100))

        #Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if state == "instructions":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                        state = "menu"

                elif state == "character_select":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        selected_character_index = (selected_character_index - 1) % len(CHARACTER_NAMES)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        selected_character_index = (selected_character_index + 1) % len(CHARACTER_NAMES)
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        return CHARACTER_NAMES[selected_character_index]

                else:  # menu
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_SPACE:
                        if selected_option == 0:
                            state = "character_select"
                        elif selected_option == 1:
                            state = "instructions"
                        elif selected_option == 2:
                            pygame.quit()
                            exit()

            #choose with scroll wheel
            elif event.type == pygame.MOUSEWHEEL:
                if state == "character_select":
                    if event.y > 0:
                        selected_character_index = (selected_character_index - 1) % len(CHARACTER_NAMES)
                    elif event.y < 0:
                        selected_character_index = (selected_character_index + 1) % len(CHARACTER_NAMES)
                elif state == "menu":
                    if event.y > 0:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.y < 0:
                        selected_option = (selected_option + 1) % len(options)

        #Update animated preview farm (menu backdrop only)
        if state == "menu":
            for y in range(preview_h):
                for x in range(preview_w):
                    tile = preview_farm[y][x]
                    rect = pygame.Rect(WIDTH//2 - preview_w*20//2 + x*20, HEIGHT//4 - preview_h*20//2 + y*20, 18, 18)
                    color = COLORS.get(tile["state"], COLORS["grass"])
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0,0,0), rect, 1)

                    if tile["state"] == "grass" and random.random() < 0.002:
                        seed_choice = random.choice(preview_seeds)
                        tile["state"] = "planted"
                        tile["seed"] = seed_choice
                        tile["timer"] = 0.0
                    elif tile["state"] == "planted":
                        tile["timer"] += dt
                        seed = SEEDS[tile["seed"]]
                        if tile["timer"] >= seed["grow_time"]*0.5:
                            tile["state"] = "sprout"
                        if tile["timer"] >= seed["grow_time"]:
                            tile["state"] = "grown"

        #Draw title
        title = render_text(title_font, "Arborio", TEXT_GOLD)
        subtitle = render_text(subtitle_font, "The Tile Farm Game", TEXT_CREAM)

        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 70))

        #Draw menu
        if state == "instructions":
            instructions = [
                "---*Arborio is a high startch rice*---",
                "Controls:",
                "Arrow Keys/WASD - Move",
                "Space - Plant Seed",
                "E - Harvest / Sleep",
                "Q - Inventory",
                "Z - Switch Tool",
                "R-T/Y-U/I-O/P - Select Seed",
                "Mouse Wheel - Zoom In/Out",
                "Enter/Space - Back"
            ]
            for i, line in enumerate(instructions):
                text_surf = render_text(font, line, TEXT_CREAM)
                screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//4 + i*30))

        elif state == "character_select":
            heading = render_text(subtitle_font, "Choose your Farmer", TEXT_GOLD)
            screen.blit(heading, (WIDTH//2 - heading.get_width()//2, 150))

            portrait_size = 96
            gap = 26
            total_w = len(CHARACTER_NAMES) * portrait_size + (len(CHARACTER_NAMES) - 1) * gap
            start_x = WIDTH//2 - total_w//2
            row_y = 200

            for i, name in enumerate(CHARACTER_NAMES):
                x = start_x + i * (portrait_size + gap)
                screen.blit(CHARACTER_PORTRAITS[name], (x, row_y))

                if i == selected_character_index and blink_on:
                    pygame.draw.rect(screen, TEXT_GOLD, (x-4, row_y-4, portrait_size+8, portrait_size+8), 3)

                name_surf = render_text(font, name, TEXT_CREAM)
                screen.blit(name_surf, (x + portrait_size//2 - name_surf.get_width()//2, row_y + portrait_size + 8))

            bio_text = CHARACTER_BIOS[CHARACTER_NAMES[selected_character_index]]
            bio_lines = wrap_text(subtitle_font, bio_text, WIDTH - 40)
            bio_y = row_y + portrait_size + 45
            for line in bio_lines:
                line_surf = render_text(subtitle_font, line, TEXT_GOLD)
                screen.blit(line_surf, (WIDTH//2 - line_surf.get_width()//2, bio_y))
                bio_y += line_surf.get_height() + 2

            prompt = render_text(subtitle_font, "Left/Right to choose, Space to confirm, Esc to go back", TEXT_CREAM)
            screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, bio_y + 12))

        else:
            for i, option in enumerate(options):
                color = TEXT_CREAM
                text_surf = render_text(font, option, color)
                x_pos = WIDTH//2 - text_surf.get_width()//2
                y_pos = HEIGHT//2 + i*40
                screen.blit(text_surf, (x_pos, y_pos))

                # Blinking retro highlight
                if i == selected_option and blink_on:
                    highlight_rect = pygame.Rect(x_pos-5, y_pos-5, text_surf.get_width()+10, text_surf.get_height()+10)
                    pygame.draw.rect(screen, TEXT_GOLD, highlight_rect, 2)

        pygame.display.flip()





#Run Main Menu
chosen_character = start_screen()
PLAYER_FRAMES = PLAYER_FRAMES_BY_CHARACTER[chosen_character]

#NPCs: the 3 characters the player didn't pick, each living in the world on
#their own schedule (walking between waypoints all day, whether or not the
#player is nearby), each with their own role and a small rotating pool of
#helpful tips rather than one static line.
NPC_NAMES = [name for name in CHARACTER_NAMES if name != chosen_character]
NPC_SPEED = 2.2  # tiles per second

# Each NPC's schedule is (day-fraction to be there by, (tile_x, tile_y), activity label)
NPC_DEFS = [
    {
        "schedule": [
            (0.0, (float(HOUSE_POS[0] + 7), float(HOUSE_POS[1] + 3)), "home"),
            (0.3, (float(HOUSE_POS[0] + 18), float(HOUSE_POS[1] + 9)), "field"),
            (0.6, (float(HOUSE_POS[0] + 12), float(HOUSE_POS[1] + 16)), "shop"),
            (0.85, (float(HOUSE_POS[0] + 7), float(HOUSE_POS[1] + 3)), "home"),
        ],
        "tips": {
            "home": [
                "Crops keep growing even while you're away — but so does the clock on withering.",
                "A level-2 Pick doubles both your harvest and the XP from it.",
            ],
            "field": [
                "Watch a planted crop closely: seedling, sprout, growing, then ripe. Don't wait too long after that!",
                "Different crops wither at different rates — corn gives you more grace than carrots.",
            ],
            "shop": [
                "The Hoe lets you replant the same spot the instant you harvest it. Big time saver.",
            ],
        },
    },
    {
        "schedule": [
            (0.0, (float(HOUSE_POS[0] + 22), float(HOUSE_POS[1] + 4)), "home"),
            (0.3, (float(HOUSE_POS[0] + 10), float(HOUSE_POS[1] + 20)), "shop"),
            (0.6, (float(HOUSE_POS[0] - 8), float(HOUSE_POS[1] + 14)), "field"),
            (0.85, (float(HOUSE_POS[0] + 22), float(HOUSE_POS[1] + 4)), "home"),
        ],
        "tips": {
            "home": [
                "Outposts carry a few trades each, but marketplaces are bigger — more trades, and they sometimes sell tools.",
            ],
            "shop": [
                "Emeralds are the only thing marketplaces care about. Sell off crops you've got plenty of.",
                "Prices are different at every stall — worth checking more than one before you sell in bulk.",
            ],
            "field": [
                "I've spotted outposts scattered all over — some are a fair walk from home, so stock up before you go.",
            ],
        },
    },
    {
        "schedule": [
            (0.0, (float(HOUSE_POS[0] + 5), float(HOUSE_POS[1] + 22)), "home"),
            (0.3, (float(HOUSE_POS[0] - 12), float(HOUSE_POS[1] + 10)), "field"),
            (0.6, (float(HOUSE_POS[0] + 20), float(HOUSE_POS[1] + 18)), "shop"),
            (0.85, (float(HOUSE_POS[0] + 5), float(HOUSE_POS[1] + 22)), "home"),
        ],
        "tips": {
            "home": [
                "Press M any time you're outside to pull up the map — this world is huge, it helps to see the shape of it.",
            ],
            "field": [
                "Every biome grows its own trees — maple forests, sakura groves, jungle, even cactus out in the desert.",
                "An Axe lets you chop trees for a clear path. They grow back eventually if you leave the area alone.",
            ],
            "shop": [
                "The animals won't bother you, but get too close and they'll skitter off. Peaceful, just shy.",
            ],
        },
    },
]

npcs = []
for name, npc_def in zip(NPC_NAMES, NPC_DEFS):
    start_x, start_y = npc_def["schedule"][0][1]
    npcs.append({
        "name": name,
        "frames": PLAYER_FRAMES_BY_CHARACTER[name],
        "schedule": npc_def["schedule"],
        "tips": npc_def["tips"],
        "tip_index": 0,
        "x": start_x, "y": start_y,
        "facing": "down",
        "activity": npc_def["schedule"][0][2],
        "is_walking": False,
        "walk_timer": 0.0,
        "frame_index": 0,
    })

dialogue_open = False
dialogue_text = ""

market_open = False
active_outpost = None
market_selection = 0
market_message = ""
market_message_timer = 0.0

map_open = False
journal_open = False  # crop compendium (X key)


def npc_target_for(schedule, day_fraction):
    target, activity = schedule[0][1], schedule[0][2]
    for frac, pos, label in schedule:
        if day_fraction >= frac:
            target, activity = pos, label
        else:
            break
    return target, activity


def next_npc_tip(npc):
    """Cycles through this NPC's tips for their current activity so talking
    again gives something new instead of repeating the same line."""
    lines = npc["tips"].get(npc["activity"], ["..."])
    line = lines[npc["tip_index"] % len(lines)]
    npc["tip_index"] += 1
    return f"{npc['name']}: {line}"

#Helper functions 


#achivment message 
def unlock_achievement(name):
    if name and name not in achievements_unlocked:
        achievements_unlocked.append(name)
        achievement_queue.append({"text": f"Achievement Unlocked: {name}", "timer": 0.0})


#lvl message 
def show_level_popup(lvl):
    level_popup_queue.append({"text": f"Congrats! Level {lvl} reached!", "timer": 0.0})


#wich rewars chosen 
def discover_seed(key, count=5):
    """Adds a seed to the player's inventory + hotbar the first time they
    encounter it (from a level reward, a marketplace unlock, or an NPC trade).
    Repeat calls just top up inventory — the hotbar slot isn't duplicated."""
    DISCOVERED_SEEDS.add(key)
    already = key in seed_inventory
    if not already:
        seed_inventory[key] = 0
        hotbar_slots.append({"kind": "seed", "key": key})
    seed_inventory[key] += count


def apply_reward(reward):
    global pick_tool, hoe_tool, axe_tool, unlocked_tools, equipped_tool
    if reward in ("Upgrade Pickaxe", "Upgrade Pick to Lvl2", "Upgrade Pick Lvl3"):
        pick_tool["level"] += 1
    elif reward in ("Upgrade Hoe", "Upgrade Hoe Lvl1", "Upgrade Hoe Lvl2"):
        if hoe_tool:
            hoe_tool["level"] += 1
    elif reward == "Unlock Hoe":
        if not hoe_tool:
            hoe_tool = {"name": "Hoe", "level": 1, "color": (150, 100, 200)}
            unlocked_tools.append(hoe_tool)
            equipped_tool = hoe_tool
            hotbar_slots.append({"kind": "tool", "tool": hoe_tool})
    elif reward == "Unlock Axe":
        if not axe_tool:
            axe_tool = {"name": "Axe", "level": 1, "color": (139, 69, 19)}
            unlocked_tools.append(axe_tool)
            hotbar_slots.append({"kind": "tool", "tool": axe_tool})
    elif reward == "Unlock Pumpkin Seeds":
        discover_seed("pumpkin")
    elif reward == "Unlock Tomato Seeds":
        discover_seed("tomato")
    elif reward == "Carrot XP Boost":
        SEEDS["carrot"]["xp"] *= 2
    elif reward == "Unlock Cow":
        pass
    elif reward == "Unlock Sunflower Seeds":
        discover_seed("sunflower")
    elif reward == "Unlock Watermelon Seeds":
        discover_seed("watermelon")
    elif reward == "Unlock Eggplant Seeds":
        discover_seed("eggplant")
    elif reward == "Unlock Grape Seeds":
        discover_seed("grape")
    elif reward == "Unlock Apple Seeds":
        discover_seed("apple")
    elif reward == "Skip":
        pass


#Trees: solid, choppable obstacles that populate the landscape.
#Random-sampled with a bounded retry count rather than scanning the whole
#world for every spawn — that scan is fine at 2,500 tiles but not at 40,000.
#Lakes and ponds: irregular-shaped water bodies scattered across the map,
#biased away from the desert (rare) and toward jungle/meadow. Shape is
#organic via a "grow outward from a seed tile, jittered by noise" fill so
#no lake reads as a perfect circle. Water tiles are non-walkable.
water_bodies = []  # list of (center_x, center_y) so villages can be placed near them
water_shapes = []  # {"surface", "x", "y", "w", "h", "tiles"} — one precomputed image per lake/pond

fish = []
FISH_SPEED = 0.7


def spawn_fish_for(water_shape):
    """A few peaceful fish per lake, wandering only within that lake's exact
    tile set (not just its bounding box, which can include non-water bleed
    at odd shape corners) — bigger lakes get more."""
    tiles = list(water_shape["tiles"])
    if not tiles:
        return
    count = max(1, min(6, len(tiles) // 15))
    for _ in range(count):
        x, y = random.choice(tiles)
        fish.append({
            "x": float(x) + random.uniform(-0.3, 0.3), "y": float(y) + random.uniform(-0.3, 0.3),
            "target_x": float(x), "target_y": float(y), "water_tiles": tiles,
            "facing_right": random.random() < 0.5, "state": "idle", "timer": random.uniform(0.0, 3.0),
        })

WATER_SHAPE_CELL = 32  # px per tile at generation resolution


def _pil_to_pygame(img):
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert_alpha()


def _build_water_shape(tile_set):
    """Renders a whole lake/pond as ONE soft-edged image instead of a grid of
    individually-blended water tiles — no per-tile grid can show through
    because there is no per-tile grid. Built from the exact set of tiles
    stamp_water_body claimed: filled rounded blocks per tile, blurred into a
    single smooth silhouette, then a water gradient + a handful of soft
    highlight streaks painted across the WHOLE shape (not per tile, so
    nothing repeats). Returns (surface, x, y, w, h) in tile units, already
    including the margin used for the blur so callers can position/scale it
    directly against the tile grid with no further offset math."""
    xs = [x for x, _ in tile_set]
    ys = [y for _, y in tile_set]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w_tiles = max_x - min_x + 1
    h_tiles = max_y - min_y + 1
    cell = WATER_SHAPE_CELL
    margin = cell  # 1 tile of blur margin on every side
    img_w = w_tiles * cell + margin * 2
    img_h = h_tiles * cell + margin * 2

    mask = Image.new("L", (img_w, img_h), 0)
    mdraw = ImageDraw.Draw(mask)
    pad = cell * 0.14
    for (x, y) in tile_set:
        px = (x - min_x) * cell + margin
        py = (y - min_y) * cell + margin
        mdraw.rounded_rectangle([px - pad, py - pad, px + cell + pad, py + cell + pad],
                                 radius=cell * 0.4, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=cell * 0.4))

    rng = random.Random(hash((min_x, min_y, w_tiles, h_tiles)) & 0xffffffff)
    deep = (46, 90, 150, 255)
    mid = (78, 132, 196, 255)
    shine = (176, 208, 238, 255)

    base = Image.new("RGBA", (img_w, img_h), deep)
    bdraw = ImageDraw.Draw(base)
    for _ in range(max(6, (w_tiles * h_tiles) // 5)):
        bx, by = rng.uniform(0, img_w), rng.uniform(0, img_h)
        r = rng.uniform(cell * 0.7, cell * 1.8)
        bdraw.ellipse([bx - r, by - r, bx + r, by + r], fill=mid)
    base = base.filter(ImageFilter.GaussianBlur(radius=cell * 0.3))

    rdraw = ImageDraw.Draw(base)
    for _ in range(max(3, (w_tiles + h_tiles) // 2)):
        ry = rng.uniform(0, img_h)
        rx0 = rng.uniform(0, img_w * 0.4)
        rw = rng.uniform(img_w * 0.2, img_w * 0.5)
        rdraw.line([(rx0, ry), (rx0 + rw, ry)], fill=shine, width=max(1, int(cell * 0.05)))
    base = base.filter(ImageFilter.GaussianBlur(radius=cell * 0.1))

    base.putalpha(mask)
    return base, min_x - 1, min_y - 1, w_tiles + 2, h_tiles + 2


def stamp_water_body(cx, cy, target_size):
    """BFS-ish organic fill: start at the center, march outward, keep tiles
    that pass a distance-plus-noise threshold. Uses smooth (bilinearly
    interpolated) noise rather than raw per-tile jitter, so the coastline
    forms real coherent coves and headlands instead of a jittery/blocky
    circle — a hash-per-tile perturbation is uncorrelated noise, not a wiggle.
    Skips already-claimed tiles. The claimed tile set is then rendered as one
    single smooth shape (see _build_water_shape) instead of per-tile stamps."""
    stamped_tiles = []
    max_r = int(math.sqrt(target_size / math.pi) + 2)
    for dy in range(-max_r, max_r + 1):
        for dx in range(-max_r, max_r + 1):
            x, y = cx + dx, cy + dy
            if not (0 <= x < WORLD_W and 0 <= y < WORLD_H):
                continue
            if (x, y) in FARM_BLOCKED_TILES:
                continue
            if farm[y][x]["state"] != "grass":
                continue
            r = math.hypot(dx, dy)
            # smooth noise, coherent over a few tiles, perturbs the effective
            # radius so the shoreline curves naturally instead of jittering
            wiggle = _smooth_noise(x, y, cell=3.2) - 0.5
            noise_r = r + wiggle * max_r * 0.7
            if noise_r > max_r:
                continue
            farm[y][x]["state"] = "water"
            farm[y][x]["ground_static"] = None
            MAP_SURFACE.set_at((x, y), (68, 128, 200))  # blue on the world map overlay
            stamped_tiles.append((x, y))
    if stamped_tiles:
        water_bodies.append((cx, cy))
        stamped_set = set(stamped_tiles)

        # A 1-tile shore buffer around every lake: reserved (via
        # FARM_BLOCKED_TILES, so trees/rocks/buildings won't spawn there —
        # this doesn't block player movement, that's governed separately by
        # tile state) so nothing stands close enough to the water to
        # visually bleed into the lake's soft, slightly-overdrawn shore image.
        buffer_ring = set()
        for (x, y) in stamped_tiles:
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    nx, ny = x + ddx, y + ddy
                    if (nx, ny) not in stamped_set:
                        buffer_ring.add((nx, ny))
        FARM_BLOCKED_TILES.update(buffer_ring)

        # Ponds planted later (e.g. next to a village's fisherman shack) can
        # land next to trees/rocks that were already placed earlier in
        # world-gen, before this pond existed — the buffer reservation above
        # only stops *future* spawns, so also clear out anything already
        # sitting in the buffer ring right now.
        for (bx, by) in buffer_ring:
            if 0 <= bx < WORLD_W and 0 <= by < WORLD_H and farm[by][bx]["state"] in ("tree", "rock"):
                farm[by][bx]["state"] = "grass"
                farm[by][bx]["tree_variant"] = None

        img, ox, oy, w_tiles, h_tiles = _build_water_shape(stamped_tiles)
        water_shapes.append({"surface": _pil_to_pygame(img), "x": ox, "y": oy, "w": w_tiles, "h": h_tiles,
                              "tiles": stamped_set})
        spawn_fish_for(water_shapes[-1])
    return len(stamped_tiles)


def spawn_water_body(target_size):
    for _ in range(60):
        x, y = random.randint(6, WORLD_W - 7), random.randint(6, WORLD_H - 7)
        # skip desert (dry biome!) and skip anywhere too close to another lake
        if biome_for(x, y) == "desert":
            continue
        if any(math.hypot(x - wx, y - wy) < 20 for (wx, wy) in water_bodies):
            continue
        if math.hypot(x - HOUSE_POS[0], y - HOUSE_POS[1]) < 8:
            continue  # don't drown the starting farm
        if stamp_water_body(x, y, target_size) > target_size // 3:
            return


# 20 big-ish lakes + 30 small ponds (villages will get their own small ponds
# later) — counts scaled ~2.5x for the larger world so water stays just as
# common per unit area, not diluted across the bigger map.
for _ in range(20):
    spawn_water_body(random.randint(70, 140))
for _ in range(30):
    spawn_water_body(random.randint(14, 30))


def spawn_tree():
    for _ in range(30):
        x, y = random.randint(0, WORLD_W - 1), random.randint(0, WORLD_H - 1)
        if (farm[y][x]["state"] == "grass" and (x, y) not in FARM_BLOCKED_TILES
                and (x, y) != (player_x, player_y)):
            farm[y][x]["state"] = "tree"
            farm[y][x]["tree_variant"] = random.choice(BIOME_TREE_INDICES[farm[y][x]["biome"]])
            return

#Populate the landscape with trees at world-gen (scaled ~2.5x for the larger world)
for _ in range(1500):
    spawn_tree()


def spawn_rock():
    """Mineable boulders (stone + a chance of iron), scattered the same
    bounded-retry way as trees. Slightly rarer than trees."""
    for _ in range(30):
        x, y = random.randint(0, WORLD_W - 1), random.randint(0, WORLD_H - 1)
        if (farm[y][x]["state"] == "grass" and (x, y) not in FARM_BLOCKED_TILES
                and (x, y) != (player_x, player_y)):
            farm[y][x]["state"] = "rock"
            return


for _ in range(550):
    spawn_rock()

#Abandoned-farm flavor: a handful of tiles near the house are forcibly given
#the existing rock/rubble decor image (bypassing the normal sparse chance),
#selling the "ruined farm" starting state. They clear the first time the
#farm tier advances past 0 (see recompute_farm_tier), a small visual payoff
#for actually restoring the place rather than just a number going up.
starting_rubble_tiles = set()
for _ in range(6):
    for _try in range(20):
        rx = HOUSE_POS[0] + random.randint(-5, 5)
        ry = HOUSE_POS[1] + random.randint(-5, 5)
        if (0 <= rx < WORLD_W and 0 <= ry < WORLD_H and (rx, ry) not in FARM_BLOCKED_TILES
                and farm[ry][rx]["state"] == "grass"):
            farm[ry][rx]["decor"] = IMG_DECOR3  # the rock/rubble decor image
            starting_rubble_tiles.add((rx, ry))
            break


def recompute_farm_tier():
    """Farm tier is driven by how many player-constructed buildings are
    actually finished and standing — 2 buildings per tier, capped at the
    top tier. Announces tier-ups the same way achievements are announced,
    and clears the starting rubble the first time the farm is restored
    past "abandoned"."""
    global farm_tier
    active_count = sum(1 for b in farm_buildings if b["stage"] == "active")
    new_tier = min(len(FARM_TIERS) - 1, active_count // 2)
    if new_tier > farm_tier:
        farm_tier = new_tier
        achievement_queue.append({"text": f"Farm restored to: {FARM_TIERS[farm_tier]}", "timer": 0.0})
        if farm_tier >= 1:
            for (rx, ry) in starting_rubble_tiles:
                farm[ry][rx]["decor"] = random.choice(DECOR_IMAGES) if random.random() < DECOR_CHANCE else None


def _has_open_exposure(footprint):
    """At least half of a footprint's cardinal-neighbor tiles must be open
    grass — the Windmill's 'needs open space, wind exposure' requirement."""
    open_count = 0
    total = 0
    for (px, py) in footprint:
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = px + dx, py + dy
            if (nx, ny) in footprint:
                continue
            total += 1
            if 0 <= nx < WORLD_W and 0 <= ny < WORLD_H and farm[ny][nx]["state"] == "grass":
                open_count += 1
    return total > 0 and (open_count / total) >= 0.5


def _nearby_flowers(cx, cy, radius=3):
    """Bee Hive placement bonus check: any flower decor (not rock/bush)
    within radius means nearby flowers to forage, per the design's 'nearby
    flowers increase honey production' rule."""
    flower_images = {IMG_DECOR1, IMG_DECOR2}
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            x, y = cx + dx, cy + dy
            if 0 <= x < WORLD_W and 0 <= y < WORLD_H and farm[y][x]["decor"] in flower_images:
                return True
    return False


def has_recipe_inputs(input_dict):
    for key, amt in input_dict.items():
        available = resources.get(key) if key in resources else seed_inventory.get(key, 0)
        if available is None or available < amt:
            return False
    return True


def consume_recipe_inputs(input_dict):
    for key, amt in input_dict.items():
        if key in resources:
            resources[key] -= amt
        else:
            seed_inventory[key] -= amt


def any_active_building(btype):
    return any(b["type"] == btype and b["stage"] == "active" for b in farm_buildings)


def attempt_place_building(btype):
    """Validates placement (clear ground, in bounds, Windmill's open-space
    rule), checks + deducts cost, and starts construction. Returns True on
    success so the caller can close the build menu / suppress the same
    keypress from also being read as 'open the building I'm now standing
    in front of' (mirrors the just_entered_ruin double-action guard)."""
    global emeralds, build_message, build_message_timer
    info = FARM_BUILDING_TYPES[btype]
    fw, fh = info["footprint"]
    fdx, fdy = FACING_DELTA[player_facing]
    fx, fy = player_x + fdx, player_y + fdy
    footprint = {(fx + i, fy) for i in range(fw)}

    # Only 2-tall buildings (fh > 1) actually overhang into the row above —
    # farm_well/beehive/orchard_marker sit flush, so don't need that extra
    # margin checked or reserved.
    check_region = _full_footprint(footprint) if fh > 1 else footprint

    if any(not (0 <= px < WORLD_W and 0 <= py < WORLD_H) for (px, py) in footprint):
        build_message, build_message_timer = "Can't place a building there!", 2.0
        return False
    if check_region & FARM_BLOCKED_TILES:
        build_message, build_message_timer = "That spot is already in use!", 2.0
        return False
    if any(farm[py][px]["state"] != "grass" for (px, py) in footprint):
        build_message, build_message_timer = "Needs clear, open ground!", 2.0
        return False
    if btype == "windmill" and not _has_open_exposure(footprint):
        build_message, build_message_timer = "The windmill needs more open space around it!", 2.4
        return False

    discount = farming_skill_build_discount()
    scaled_cost = {res: max(1, int(amt * discount)) for res, amt in info["cost"].items()}
    for res, amt in scaled_cost.items():
        available = emeralds if res == "emeralds" else resources.get(res, 0)
        if available < amt:
            build_message, build_message_timer = "Not enough resources!", 2.0
            return False

    for res, amt in scaled_cost.items():
        if res == "emeralds":
            emeralds -= amt
        else:
            resources[res] -= amt

    building_id = len(farm_buildings)
    for (px, py) in footprint:
        farm[py][px]["state"] = "building"
        farm[py][px]["building_id"] = building_id
    FARM_BLOCKED_TILES.update(check_region)
    farm_buildings.append({
        "type": btype, "x": fx, "y": fy, "footprint": footprint, "stage": "building",
        "progress_days": 0.0, "condition": 100.0, "processing": None, "stock": 0,
        "flower_bonus": _nearby_flowers(fx, fy) if btype == "beehive" else False,
        "_honey_timer": 0.0,
    })
    if btype == "orchard_marker":
        orchard_tiles.update(footprint)
    build_message, build_message_timer = f"Construction started: {info['label']}", 2.2
    return True


def get_building_panel_options(b):
    """Returns the building panel's option list for building b, each a dict
    with at least a 'kind' and 'label'. Shared by both the render code and
    the E-key confirm handler so they can never drift out of sync."""
    info = FARM_BUILDING_TYPES[b["type"]]
    options = []
    if b["stage"] == "building":
        pct = int(min(100, 100 * b["progress_days"] / info["build_days"]))
        options.append({"kind": "info", "label": f"Under construction — {pct}%"})
        options.append({"kind": "leave", "label": "Leave"})
        return options

    if b["processing"] is not None:
        if b["processing"]["time_left"] <= 0:
            options.append({"kind": "collect", "label": f"Collect {b['processing']['qty']} {GOODS_INFO[b['processing']['output']]['name']}"})
        else:
            secs = max(0, int(b["processing"]["time_left"]))
            options.append({"kind": "info", "label": f"Processing '{b['processing']['recipe_name']}' — {secs}s left"})
    elif b["type"] in PRODUCTION_RECIPES:
        for recipe in PRODUCTION_RECIPES[b["type"]]:
            need_str = ", ".join(f"{amt} {k.capitalize()}" for k, amt in recipe["input"].items())
            afford = has_recipe_inputs(recipe["input"])
            options.append({"kind": "recipe", "label": f"{recipe['name']} (needs {need_str})",
                             "recipe": recipe, "affordable": afford})
    elif b["type"] == "beehive":
        if b["stock"] > 0:
            options.append({"kind": "collect_stock", "label": f"Collect {b['stock']} Honey"})
        else:
            options.append({"kind": "info", "label": "Bees foraging" + (" (flowers nearby!)" if b["flower_bonus"] else "...")})
    else:
        descriptions = {
            "barn": "Boosts stored livestock happiness & yield.",
            "silo": "Expands feed storage capacity.",
            "warehouse": "Expands crop/material storage capacity.",
            "farm_well": "Speeds crop growth in a small radius.",
            "windmill": "Speeds up every Mill's production.",
            "greenhouse": "Crops planted here ignore winter slowdown.",
            "orchard_marker": "Apple/Grape here auto-replant after harvest.",
            "watchtower": "Warns of and reduces farm raids.",
            "magic_ward": "Wards the whole farm against raids.",
        }
        options.append({"kind": "info", "label": descriptions.get(b["type"], "A working part of the farm.")})

    if b["condition"] < 100:
        cost = FARM_BUILDING_TYPES[b["type"]]["cost"]
        repair_cost = {k: max(1, int(v * REPAIR_COST_FRACTION)) for k, v in cost.items()}
        cost_str = ", ".join(f"{v} {k.capitalize()}" for k, v in repair_cost.items())
        options.append({"kind": "repair", "label": f"Repair ({cost_str}) — condition {int(b['condition'])}%",
                         "repair_cost": repair_cost})

    options.append({"kind": "leave", "label": "Leave"})
    return options


def growth_rate_at(x, y):
    """Combines every growth-speed modifier that applies to a given tile:
    the farming skill tree's passive bonus, winter's slowdown (bypassed by
    a nearby active Greenhouse or the level-20 skill), and a nearby active
    Well's boost — infrastructure and skill progression actually changing
    how the farm behaves, not just cosmetic placement."""
    mult = farming_skill_growth_mult()
    if season_for_day(day) == "Winter" and not farming_skill_bypasses_winter():
        in_greenhouse = any(b["type"] == "greenhouse" and b["stage"] == "active" and (x, y) in b["footprint"]
                            for b in farm_buildings)
        if not in_greenhouse:
            mult *= WINTER_GROWTH_MULT
    for b in farm_buildings:
        if b["type"] == "farm_well" and b["stage"] == "active" and math.hypot(x - b["x"], y - b["y"]) <= 4:
            mult *= 1.3
            break
    return mult


#Peaceful animals: wander idly, flee a little if the player gets close
animals = []


def spawn_animal():
    species = random.choice(list(ANIMAL_IMAGES.keys()))
    for _ in range(50):
        x, y = random.randint(0, WORLD_W - 1), random.randint(0, WORLD_H - 1)
        if farm[y][x]["state"] == "grass" and (x, y) not in FARM_BLOCKED_TILES:
            animals.append({
                "species": species, "x": float(x), "y": float(y),
                "target_x": float(x), "target_y": float(y),
                "state": "idle", "timer": random.uniform(0.0, 3.0),
                "facing_right": True,
            })
            return


for _ in range(125):
    spawn_animal()

#Marketplace: small outposts scattered around, larger marketplaces further
#out, each with a handful of randomly generated buy/sell trades.
outposts = []


def generate_trades(kind):
    """Small outposts get 3 seed trades, marketplaces get 5 + tool offers.
    Prices scale off each seed's own value field, so rare/high-value crops
    (pumpkin, apple, watermelon) cost far more than corn or carrot."""
    trades = []
    seed_pool = list(SEEDS.keys())
    num_trades = 5 if kind == "marketplace" else 3

    for _ in range(num_trades):
        item = random.choice(seed_pool)
        value = SEEDS[item].get("value", 3)
        if random.random() < 0.5:
            qty = random.randint(3, 6)
            price = max(1, round(qty * value * random.uniform(0.7, 1.0)))
            trades.append({"type": "buy", "item": item, "qty": qty, "price": price})
        else:
            qty = random.randint(2, 5)
            price = max(1, round(qty * value * random.uniform(1.1, 1.6)))
            trades.append({"type": "sell", "item": item, "qty": qty, "price": price})

    if kind == "marketplace":
        if not hoe_tool:
            trades.append({"type": "buy_tool", "tool_name": "hoe", "price": 25})
        if not axe_tool:
            trades.append({"type": "buy_tool", "tool_name": "axe", "price": 30})
        # Marketplaces also buy processed goods — the payoff for building a
        # Mill/Preserving Shed/Brewery/Workshop and actually running it.
        for good_key in random.sample(list(GOODS_INFO.keys()), k=2):
            value = GOODS_INFO[good_key]["value"]
            qty = random.randint(2, 4)
            price = max(1, round(qty * value * random.uniform(1.1, 1.5)))
            trades.append({"type": "sell_good", "item": good_key, "qty": qty, "price": price})

    return trades


def spawn_outpost(kind):
    min_dist = 45 if kind == "marketplace" else 10
    footprint_w = 2 if kind == "marketplace" else 1
    for _ in range(150):
        x = random.randint(2, WORLD_W - footprint_w - 2)
        y = random.randint(2, WORLD_H - 3)
        if math.hypot(x - HOUSE_POS[0], y - HOUSE_POS[1]) < min_dist:
            continue
        footprint = {(x + dx, y) for dx in range(footprint_w)}
        if _full_footprint(footprint) & FARM_BLOCKED_TILES:
            continue
        if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
            continue

        market_id = len(outposts)
        for (fx, fy) in footprint:
            farm[fy][fx]["state"] = "market"
            farm[fy][fx]["market_id"] = market_id
        FARM_BLOCKED_TILES.update(_full_footprint(footprint))
        variant_pool = MARKETPLACE_IMAGES if kind == "marketplace" else OUTPOST_IMAGES
        outposts.append({"x": x, "y": y, "kind": kind, "trades": generate_trades(kind),
                          "variant": random.randrange(len(variant_pool))})

        if kind == "marketplace":
            spawn_village(x, y)
        return


#Villages: a stable plus a handful of locally-wandering villagers, placed
#around each marketplace so trading hubs feel like real settlements.
stables = []
villagers = []


def _outside_bounds(footprint, bounds):
    """bounds, if given, is (x0, y0, x1, y1) that every tile in footprint
    must fall within — used to keep a kingdom's interior services
    (stable/smithy/shack/well/shrine/extra stalls) from landing outside its
    own walls, since these 'near a point' helpers otherwise have no idea a
    wall exists."""
    if bounds is None:
        return False
    x0, y0, x1, y1 = bounds
    return any(not (x0 <= fx <= x1 and y0 <= fy <= y1) for (fx, fy) in footprint)


def _full_footprint(footprint):
    """Every 2-tile-tall, bottom-anchored building (stable, shrine, smithy,
    shack, market/outpost, ruin, flavor house, player building, kingdom
    gate) renders one tile taller than its actual collision footprint — the
    roof/overhang spills into the row above. Collision checks must test
    THIS combined region, not just the footprint: checking only the
    footprint (and reserving the overhang purely as an afterthought) still
    lets a structure's own overhang land on top of an earlier structure's
    already-placed footprint, since that placement never re-checks its
    neighbor's footprint against its own overhang. Using the full region
    for both the check and the reservation closes that gap. The overhang
    tiles never have their state changed — they stay walkable grass
    underneath the sprite's overhang, just reserved from further building."""
    return footprint | {(x, y - 1) for (x, y) in footprint}


def spawn_stable_near(cx, cy, bounds=None):
    for _ in range(60):
        ox = cx + random.randint(-5, 5)
        oy = cy + random.randint(-5, 5)
        footprint = {(ox, oy), (ox + 1, oy)}
        if any(not (0 <= fx < WORLD_W and 0 <= fy < WORLD_H) for (fx, fy) in footprint):
            continue
        if _full_footprint(footprint) & FARM_BLOCKED_TILES:
            continue
        if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
            continue
        if _outside_bounds(footprint, bounds):
            continue

        stable_id = len(stables)
        for (fx, fy) in footprint:
            farm[fy][fx]["state"] = "stable"
            farm[fy][fx]["stable_id"] = stable_id
        FARM_BLOCKED_TILES.update(_full_footprint(footprint))
        stables.append({"x": ox, "y": oy})
        return


def spawn_villager_near(cx, cy, bounds=None):
    name = random.choice(VILLAGER_NAMES)
    for _ in range(40):
        vx, vy = cx + random.uniform(-5, 5), cy + random.uniform(-5, 5)
        ix, iy = int(vx), int(vy)
        if _outside_bounds({(ix, iy)}, bounds):
            continue
        if 0 <= ix < WORLD_W and 0 <= iy < WORLD_H and farm[iy][ix]["state"] == "grass":
            villagers.append({
                "name": name, "frames": VILLAGER_FRAMES_BY_NAME[name],
                "home_x": float(cx), "home_y": float(cy),
                "x": vx, "y": vy, "target_x": vx, "target_y": vy,
                "facing": "down", "wandering": False, "timer": random.uniform(0.0, 3.0),
                "walk_timer": 0.0, "frame_index": 0,
                "greeting": random.choice(VILLAGER_GREETINGS),
            })
            return


wells = []
shrines = []


def spawn_well_near(cx, cy, bounds=None):
    for _ in range(40):
        wx = cx + random.randint(-5, 5)
        wy = cy + random.randint(-5, 5)
        if not (0 <= wx < WORLD_W and 0 <= wy < WORLD_H):
            continue
        if (wx, wy) in FARM_BLOCKED_TILES or farm[wy][wx]["state"] != "grass":
            continue
        if _outside_bounds({(wx, wy)}, bounds):
            continue

        farm[wy][wx]["state"] = "well"
        FARM_BLOCKED_TILES.add((wx, wy))
        wells.append({"x": wx, "y": wy})
        return


def spawn_shrine_near(cx, cy, bounds=None):
    for _ in range(40):
        sx = cx + random.randint(-6, 6)
        sy = cy + random.randint(-6, 6)
        footprint = {(sx, sy), (sx + 1, sy)}
        if any(not (0 <= fx < WORLD_W and 0 <= fy < WORLD_H) for (fx, fy) in footprint):
            continue
        if _full_footprint(footprint) & FARM_BLOCKED_TILES:
            continue
        if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
            continue
        if _outside_bounds(footprint, bounds):
            continue

        for (fx, fy) in footprint:
            farm[fy][fx]["state"] = "shrine"
        FARM_BLOCKED_TILES.update(_full_footprint(footprint))
        shrines.append({"x": sx, "y": sy})
        return


#Blacksmith + fisherman: distinct trade buildings, each with their own
#specialty stock. Placed near marketplaces so a "village" reads as a real
#settlement rather than just a stall and a stable.
smithies = []  # list of dicts: {x, y, trades: [...]}
shacks = []    # fisherman shacks, same shape


def make_smithy_trades():
    trades = []
    # Blacksmiths sell tool upgrades and chili seeds; buy back fish
    if not axe_tool:
        trades.append({"type": "buy_tool", "tool_name": "axe", "price": 24})
    if not hoe_tool:
        trades.append({"type": "buy_tool", "tool_name": "hoe", "price": 22})
    trades.append({"type": "buy", "item": "chili", "qty": 5, "price": 18})
    trades.append({"type": "sell", "item": "wheat", "qty": 4, "price": 14})
    trades.append({"type": "buy_pick_upgrade", "price": 32})
    return trades


def make_shack_trades():
    trades = []
    # Fishermen buy your excess corn (bait), sell wheat and specialty seeds
    trades.append({"type": "buy", "item": "wheat", "qty": 4, "price": 10})
    trades.append({"type": "buy", "item": "cucumber", "qty": 3, "price": 12})
    trades.append({"type": "buy", "item": "blueberry", "qty": 3, "price": 18})
    trades.append({"type": "sell", "item": "corn", "qty": 6, "price": 10})
    trades.append({"type": "sell", "item": "carrot", "qty": 5, "price": 12})
    return trades


def spawn_smithy_near(cx, cy, bounds=None):
    for _ in range(60):
        ox = cx + random.randint(-7, 7)
        oy = cy + random.randint(-7, 7)
        footprint = {(ox, oy), (ox + 1, oy)}
        if any(not (0 <= fx < WORLD_W and 0 <= fy < WORLD_H) for (fx, fy) in footprint):
            continue
        if _full_footprint(footprint) & FARM_BLOCKED_TILES:
            continue
        if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
            continue
        if _outside_bounds(footprint, bounds):
            continue
        smithy_id = len(smithies)
        for (fx, fy) in footprint:
            farm[fy][fx]["state"] = "smithy"
            farm[fy][fx]["smithy_id"] = smithy_id
        FARM_BLOCKED_TILES.update(_full_footprint(footprint))
        smithies.append({"x": ox, "y": oy, "trades": make_smithy_trades()})
        return


def spawn_fisherman_shack_near(cx, cy, bounds=None):
    """Places a fisherman shack next to the closest water tile within reach.
    If no water is nearby, plants a small pond first, then puts the shack
    next to it — so villages always get their waterfront even in dry regions.
    bounds, if given (e.g. a kingdom's interior), keeps both the pond and the
    shack itself from landing outside it."""
    # find nearest water tile within a search box
    best = None
    for dy in range(-10, 11):
        for dx in range(-10, 11):
            wx, wy = cx + dx, cy + dy
            if not (0 <= wx < WORLD_W and 0 <= wy < WORLD_H):
                continue
            if _outside_bounds({(wx, wy)}, bounds):
                continue
            if farm[wy][wx]["state"] == "water":
                d = abs(dx) + abs(dy)
                if best is None or d < best[0]:
                    best = (d, wx, wy)
    if best is None:
        # plant a small pond right next to the village
        for _ in range(20):
            pond_x = cx + random.randint(-6, 6)
            pond_y = cy + random.randint(-6, 6)
            if biome_for(pond_x, pond_y) == "desert":
                continue
            if _outside_bounds({(pond_x, pond_y)}, bounds):
                continue
            if stamp_water_body(pond_x, pond_y, random.randint(10, 20)) > 4:
                best = (0, pond_x, pond_y)
                break
    if best is None:
        return
    _, wx, wy = best
    # place the shack in an empty grass tile adjacent to the water
    for radius in range(1, 5):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                ox, oy = wx + dx, wy + dy
                footprint = {(ox, oy), (ox + 1, oy)}
                if any(not (0 <= fx < WORLD_W and 0 <= fy < WORLD_H) for (fx, fy) in footprint):
                    continue
                if _full_footprint(footprint) & FARM_BLOCKED_TILES:
                    continue
                if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
                    continue
                if _outside_bounds(footprint, bounds):
                    continue
                shack_id = len(shacks)
                for (fx, fy) in footprint:
                    farm[fy][fx]["state"] = "shack"
                    farm[fy][fx]["shack_id"] = shack_id
                FARM_BLOCKED_TILES.update(_full_footprint(footprint))
                shacks.append({"x": ox, "y": oy, "trades": make_shack_trades()})
                return


flavor_buildings = []  # {"x","y","flavor": "sakura"|"desert"|"snow"} village centerpieces


def spawn_flavor_house_near(cx, cy, flavor):
    for _ in range(60):
        ox = cx + random.randint(-6, 6)
        oy = cy + random.randint(-6, 6)
        footprint = {(ox, oy), (ox + 1, oy)}
        if any(not (0 <= fx < WORLD_W and 0 <= fy < WORLD_H) for (fx, fy) in footprint):
            continue
        if _full_footprint(footprint) & FARM_BLOCKED_TILES:
            continue
        if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
            continue
        for (fx, fy) in footprint:
            farm[fy][fx]["state"] = "flavor_house"
        FARM_BLOCKED_TILES.update(_full_footprint(footprint))
        flavor_buildings.append({"x": ox, "y": oy, "flavor": flavor})
        return


def spawn_village(cx, cy):
    """Full-scale village: stable, blacksmith, fisherman shack, well, sometimes
    a shrine, and a big crowd of villagers wandering the streets — meant to
    feel like a real settlement, not a lone stall in an empty field. Villages
    in the sakura/desert/tundra biomes also get a themed centerpiece house
    (pagoda, adobe, or snow cabin) so those regions read as their own
    distinct culture rather than the same generic buildings everywhere."""
    spawn_stable_near(cx, cy)
    spawn_smithy_near(cx, cy)
    spawn_fisherman_shack_near(cx, cy)
    for _ in range(random.randint(8, 14)):
        spawn_villager_near(cx, cy)
    if random.random() < 0.9:
        spawn_well_near(cx, cy)
    if random.random() < 0.5:
        spawn_shrine_near(cx, cy)
    flavor = BIOME_TO_FLAVOR.get(biome_for(cx, cy))
    if flavor:
        spawn_flavor_house_near(cx, cy, flavor)


def spawn_outpost_near(cx, cy, kind, bounds=None):
    """Same footprint/collision rules as spawn_outpost, but clustered near a
    given point instead of dropped anywhere — used to bulk up towns and
    kingdoms with extra stalls beyond their central marketplace."""
    footprint_w = 2 if kind == "marketplace" else 1
    for _ in range(80):
        ox = cx + random.randint(-9, 9)
        oy = cy + random.randint(-9, 9)
        footprint = {(ox + dx, oy) for dx in range(footprint_w)}
        if any(not (0 <= fx < WORLD_W and 0 <= fy < WORLD_H) for (fx, fy) in footprint):
            continue
        if _full_footprint(footprint) & FARM_BLOCKED_TILES:
            continue
        if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
            continue
        if _outside_bounds(footprint, bounds):
            continue
        market_id = len(outposts)
        for (fx, fy) in footprint:
            farm[fy][fx]["state"] = "market"
            farm[fy][fx]["market_id"] = market_id
        FARM_BLOCKED_TILES.update(_full_footprint(footprint))
        variant_pool = MARKETPLACE_IMAGES if kind == "marketplace" else OUTPOST_IMAGES
        outposts.append({"x": ox, "y": oy, "kind": kind, "trades": generate_trades(kind),
                          "variant": random.randrange(len(variant_pool))})
        return


def spawn_village_in_biome(target_biome):
    """Guarantees at least an attempt at a village specifically within a
    given biome (sakura/desert/tundra), rather than leaving those small-town
    themes to random chance across the whole map — mirrors how ruins are
    guaranteed to land in the desert."""
    for _ in range(400):
        x = random.randint(4, WORLD_W - 6)
        y = random.randint(4, WORLD_H - 4)
        if biome_for(x, y) != target_biome:
            continue
        if math.hypot(x - HOUSE_POS[0], y - HOUSE_POS[1]) < 30:
            continue
        footprint = {(x, y), (x + 1, y)}
        if _full_footprint(footprint) & FARM_BLOCKED_TILES:
            continue
        if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
            continue
        market_id = len(outposts)
        for (fx, fy) in footprint:
            farm[fy][fx]["state"] = "market"
            farm[fy][fx]["market_id"] = market_id
        FARM_BLOCKED_TILES.update(_full_footprint(footprint))
        outposts.append({"x": x, "y": y, "kind": "marketplace", "trades": generate_trades("marketplace"),
                          "variant": random.randrange(len(MARKETPLACE_IMAGES))})
        spawn_village(x, y)
        return


def spawn_town(target_biome=None):
    """A town is a village turned up a notch: a second wave of stalls, more
    services, and a much bigger crowd — the mid-tier settlement between a
    single trading post and a walled kingdom. No wall; just bigger."""
    for _ in range(400):
        x = random.randint(6, WORLD_W - 8)
        y = random.randint(6, WORLD_H - 6)
        if target_biome and biome_for(x, y) != target_biome:
            continue
        if math.hypot(x - HOUSE_POS[0], y - HOUSE_POS[1]) < 35:
            continue
        footprint = {(x, y), (x + 1, y)}
        if _full_footprint(footprint) & FARM_BLOCKED_TILES:
            continue
        if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
            continue

        market_id = len(outposts)
        for (fx, fy) in footprint:
            farm[fy][fx]["state"] = "market"
            farm[fy][fx]["market_id"] = market_id
        FARM_BLOCKED_TILES.update(_full_footprint(footprint))
        outposts.append({"x": x, "y": y, "kind": "marketplace", "trades": generate_trades("marketplace"),
                          "variant": random.randrange(len(MARKETPLACE_IMAGES))})

        spawn_stable_near(x, y)
        spawn_smithy_near(x, y)
        spawn_fisherman_shack_near(x, y)
        spawn_well_near(x, y)
        if random.random() < 0.7:
            spawn_shrine_near(x, y)
        for _ in range(3):
            spawn_outpost_near(x, y, "outpost")
        for _ in range(random.randint(18, 26)):
            spawn_villager_near(x, y)
        flavor = BIOME_TO_FLAVOR.get(biome_for(x, y))
        if flavor:
            spawn_flavor_house_near(x, y, flavor)
            spawn_flavor_house_near(x, y, flavor)
        return


#Walled kingdoms: the biggest settlement tier — a walled rectangular compound
#with a single gate that costs a one-time toll to pass. Once paid, that
#kingdom's gate stays open for the rest of the game (a "visa", not a repeat
#toll). Trees/rocks caught inside the footprint are cleared as part of
#construction (the land is settled), but existing structures/water are not
#bulldozed — placement just retries elsewhere instead.
kingdoms = []


def spawn_kingdom(target_biome=None):
    kw, kh = random.randint(16, 20), random.randint(12, 14)
    for _ in range(300):
        x0 = random.randint(6, WORLD_W - kw - 6)
        y0 = random.randint(6, WORLD_H - kh - 6)
        cx, cy = x0 + kw // 2, y0 + kh // 2
        if target_biome and biome_for(cx, cy) != target_biome:
            continue
        if math.hypot(cx - HOUSE_POS[0], cy - HOUSE_POS[1]) < 40:
            continue

        region = [(x, y) for y in range(y0, y0 + kh) for x in range(x0, x0 + kw)]
        if any(not (0 <= x < WORLD_W and 0 <= y < WORLD_H) for (x, y) in region):
            continue
        region_set = set(region)
        if region_set & FARM_BLOCKED_TILES:
            continue
        if any(farm[y][x]["state"] == "water" for (x, y) in region):
            continue

        for (x, y) in region:
            if farm[y][x]["state"] in ("tree", "rock"):
                farm[y][x]["state"] = "grass"
                farm[y][x]["tree_variant"] = None

        kingdom_id = len(kingdoms)
        gate_x = x0 + kw // 2
        wall_tiles = set()
        gate_tiles = set()
        for x in range(x0, x0 + kw):
            for y in (y0, y0 + kh - 1):
                if y == y0 + kh - 1 and gate_x <= x <= gate_x + 1:
                    gate_tiles.add((x, y))
                else:
                    wall_tiles.add((x, y))
        for y in range(y0, y0 + kh):
            for x in (x0, x0 + kw - 1):
                wall_tiles.add((x, y))

        for (wx, wy) in wall_tiles:
            farm[wy][wx]["state"] = "wall"
        for (gx, gy) in gate_tiles:
            farm[gy][gx]["state"] = "gate"
            farm[gy][gx]["kingdom_id"] = kingdom_id
        FARM_BLOCKED_TILES.update(wall_tiles)
        FARM_BLOCKED_TILES.update(_full_footprint(gate_tiles))  # the gate sprite is 2 tiles tall too

        toll = random.randint(40, 90)
        name = KINGDOM_NAMES[kingdom_id % len(KINGDOM_NAMES)]
        kingdoms.append({"x": cx, "y": cy, "x0": x0, "y0": y0, "w": kw, "h": kh,
                          "gate_x": gate_x, "gate_y": y0 + kh - 1,
                          "toll": toll, "paid": False, "name": name})

        cfoot = {(cx, cy), (cx + 1, cy)}
        market_id = len(outposts)
        for (fx, fy) in cfoot:
            farm[fy][fx]["state"] = "market"
            farm[fy][fx]["market_id"] = market_id
        FARM_BLOCKED_TILES.update(_full_footprint(cfoot))
        outposts.append({"x": cx, "y": cy, "kind": "marketplace", "trades": generate_trades("marketplace"),
                          "variant": random.randrange(len(MARKETPLACE_IMAGES))})

        # 1-tile clearance inside the walls so nothing gets placed flush
        # against them, and — critically — so the fisherman shack, extra
        # stalls, etc. can never land outside the walls the way an
        # unconstrained "near a point" search otherwise could.
        interior_bounds = (x0 + 1, y0 + 1, x0 + kw - 2, y0 + kh - 2)
        spawn_stable_near(cx, cy, bounds=interior_bounds)
        spawn_smithy_near(cx, cy, bounds=interior_bounds)
        spawn_fisherman_shack_near(cx, cy, bounds=interior_bounds)
        spawn_well_near(cx, cy, bounds=interior_bounds)
        spawn_shrine_near(cx, cy, bounds=interior_bounds)
        for _ in range(4):
            spawn_outpost_near(cx, cy, random.choice(["outpost", "outpost", "marketplace"]), bounds=interior_bounds)
        for _ in range(random.randint(24, 34)):
            spawn_villager_near(cx, cy, bounds=interior_bounds)
        return


#Settlement counts scaled ~2.5x for the larger world, except kingdoms —
#those are meant to stay rare/special, so just a modest bump.
for _ in range(60):
    spawn_outpost("outpost")
for _ in range(17):
    spawn_outpost("marketplace")
for _ in range(3):
    spawn_village_in_biome("sakura")
for _ in range(3):
    spawn_village_in_biome("desert")
for _ in range(3):
    spawn_village_in_biome("tundra")
for _ in range(7):
    spawn_town()
for _ in range(3):
    spawn_kingdom()

#Underworld: a shared underground map reached through ancient desert ruins.
#Zones are assigned with the same coarse value-noise technique as surface
#biomes, just at a smaller scale to fit a smaller map.
UNDERWORLD_W, UNDERWORLD_H = 90, 90
UNDERWORLD_NOISE_CELL = 22


def underworld_zone_for(x, y):
    idx = region_variant(x, y, cell=UNDERWORLD_NOISE_CELL, bins=len(UNDERWORLD_ZONES))
    return UNDERWORLD_ZONES[idx]


underworld = [
    [
        {
            "state": "floor",  # floor | obstacle | portal
            "zone": (uzone := underworld_zone_for(x, y)),
            "ground_variant": UNDERWORLD_GROUND_INDICES[uzone][region_variant(x, y, cell=5, bins=12)],
            "decor": UNDERWORLD_DECOR_IMAGES[UNDERWORLD_DECOR_INDEX[uzone]]
                     if random.random() < UNDERWORLD_DECOR_CHANCE else None,
        }
        for x in range(UNDERWORLD_W)
    ]
    for y in range(UNDERWORLD_H)
]

UNDERWORLD_BLOCKED_TILES = set()


def pick_underworld_arrival():
    for _ in range(200):
        x, y = random.randint(3, UNDERWORLD_W - 4), random.randint(3, UNDERWORLD_H - 4)
        if (x, y) not in UNDERWORLD_BLOCKED_TILES:
            return x, y
    return UNDERWORLD_W // 2, UNDERWORLD_H // 2


#Ancient ruins: scattered in the desert only, each a doorway down into the
#shared underworld map. Defeating enough demons at a ruin's arrival point
#gradually purifies the desert around that specific ruin, back on the surface.
ruins = []


def spawn_ruin():
    for _ in range(300):
        x = random.randint(2, WORLD_W - 4)
        y = random.randint(2, WORLD_H - 3)
        if biome_for(x, y) != "desert":
            continue
        footprint = {(x, y), (x + 1, y)}
        if _full_footprint(footprint) & FARM_BLOCKED_TILES:
            continue
        if any(farm[fy][fx]["state"] != "grass" for (fx, fy) in footprint):
            continue
        if any(math.hypot(x - r["x"], y - r["y"]) < 18 for r in ruins):
            continue

        ruin_id = len(ruins)
        for (fx, fy) in footprint:
            farm[fy][fx]["state"] = "ruin"
            farm[fy][fx]["ruin_id"] = ruin_id
        FARM_BLOCKED_TILES.update(_full_footprint(footprint))

        ux, uy = pick_underworld_arrival()
        underworld[uy][ux]["state"] = "portal"
        UNDERWORLD_BLOCKED_TILES.add((ux, uy))
        ruins.append({"x": x, "y": y, "underworld_x": ux, "underworld_y": uy,
                       "zone": underworld[uy][ux]["zone"], "kills": 0, "purified": False})
        return


for _ in range(12):
    spawn_ruin()


def purify_around_ruin(ruin):
    """Defeating enough demons tied to a ruin gradually restores the desert
    around its entrance back on the surface — the visible payoff linking the
    underworld combat loop back to the farm/overworld it feeds into."""
    cx, cy = ruin["x"], ruin["y"]
    for dy in range(-PURIFY_RADIUS, PURIFY_RADIUS + 1):
        for dx in range(-PURIFY_RADIUS, PURIFY_RADIUS + 1):
            x, y = cx + dx, cy + dy
            if not (0 <= x < WORLD_W and 0 <= y < WORLD_H) or math.hypot(dx, dy) > PURIFY_RADIUS:
                continue
            tile = farm[y][x]
            if tile["biome"] != "desert":
                continue
            tile["biome"] = "meadow"
            tile["ground_variant"] = BIOME_GROUND_INDICES["meadow"][
                region_variant(x, y) % len(BIOME_GROUND_INDICES["meadow"])]
            if tile["state"] == "grass" and random.random() < DECOR_CHANCE * 2:
                tile["decor"] = random.choice(DECOR_IMAGES)
            MAP_SURFACE.set_at((x, y), MAP_BIOME_COLORS["meadow"])


#Underworld obstacles: solid, unchoppable hazards (spikes/bone piles/broken
#pillars) matching each zone's theme, spawned the same bounded-retry way as
#surface trees.
def spawn_underworld_obstacle():
    for _ in range(30):
        x, y = random.randint(0, UNDERWORLD_W - 1), random.randint(0, UNDERWORLD_H - 1)
        if underworld[y][x]["state"] == "floor" and (x, y) not in UNDERWORLD_BLOCKED_TILES:
            underworld[y][x]["state"] = "obstacle"
            return


for _ in range(450):
    spawn_underworld_obstacle()


#Demons: wander the underworld idly. Combat in this first pass is placeholder
#and simple — facing one and pressing E lands a hit — real-time combat and a
#boss roster are a later pass.
demons = []


def spawn_demon():
    for _ in range(50):
        x, y = random.randint(0, UNDERWORLD_W - 1), random.randint(0, UNDERWORLD_H - 1)
        if underworld[y][x]["state"] == "floor" and (x, y) not in UNDERWORLD_BLOCKED_TILES:
            demons.append({
                "x": float(x), "y": float(y), "target_x": float(x), "target_y": float(y),
                "state": "idle", "timer": random.uniform(0.0, 3.0), "facing_right": True,
                "hp": DEMON_MAX_HP, "attack_cooldown": 0.0,
            })
            return


for _ in range(60):
    spawn_demon()

hellsteel = 0
current_ruin_id = None  # which ruin's underworld the player is currently inside, or None

#Camera based on level
def update_camera_view():
    global view_width, view_height, player_visual_x, player_visual_y
    world_w = WORLD_W if location == "farm" else UNDERWORLD_W
    world_h = WORLD_H if location == "farm" else UNDERWORLD_H
    # 10 + (level-1)*2, max WORLD size
    view_width = min(10 + (level-1)*2, world_w)
    view_height = min(10 + (level-1)*2, world_h)

    # Ease the player's on-screen position toward their real tile position
    # (framerate independent), then point the camera at that same eased
    # value so the player glides tile-to-tile and the world scrolls with
    # it in lockstep, rather than the player popping a full tile instantly.
    ease = 1 - math.exp(-PLAYER_GLIDE_SMOOTH_SPEED * dt)
    player_visual_x += (player_x - player_visual_x) * ease
    player_visual_y += (player_y - player_visual_y) * ease

    cam_x = max(0, min(player_visual_x - view_width/2, world_w - view_width))
    cam_y = max(0, min(player_visual_y - view_height/2, world_h - view_height))
    return cam_x, cam_y

#Movement: handles farm/house/underworld bounds, walls, and door/ruin enter/exit
def try_move(dx, dy):
    global player_x, player_y, interior_player_x, interior_player_y, location, player_visual_x, player_visual_y

    if location == "farm":
        nx = max(0, min(WORLD_W - 1, player_x + dx))
        ny = max(0, min(WORLD_H - 1, player_y + dy))
        tile_state = farm[ny][nx]["state"]
        if (nx, ny) in HOUSE_TILES or tile_state in ("tree", "market", "stable", "ruin", "well", "shrine", "water", "smithy", "shack", "rock", "building", "wall", "flavor_house"):
            return False  # solid house wall, tree, market stall, stable, ruin, kingdom wall, etc.
        if tile_state == "gate" and not kingdoms[farm[ny][nx]["kingdom_id"]]["paid"]:
            return False  # kingdom gate — blocked until its toll is paid

        moved = (nx, ny) != (player_x, player_y)
        player_x, player_y = nx, ny
        return moved

    elif location == "underworld":
        nx = max(0, min(UNDERWORLD_W - 1, player_x + dx))
        ny = max(0, min(UNDERWORLD_H - 1, player_y + dy))
        if underworld[ny][nx]["state"] == "obstacle":
            return False

        moved = (nx, ny) != (player_x, player_y)
        player_x, player_y = nx, ny
        return moved

    else:  # house
        nx = max(0, min(INTERIOR_W - 1, interior_player_x + dx))
        ny = max(0, min(INTERIOR_H - 1, interior_player_y + dy))
        on_border = nx == 0 or ny == 0 or nx == INTERIOR_W - 1 or ny == INTERIOR_H - 1
        if on_border and (nx, ny) != INTERIOR_DOOR:
            return False  # wall

        moved = (nx, ny) != (interior_player_x, interior_player_y)
        interior_player_x, interior_player_y = nx, ny
        if (nx, ny) == INTERIOR_DOOR:
            location = "farm"
            player_x, player_y = HOUSE_POS[0], DOOR_ROW + 1
            player_visual_x, player_visual_y = float(player_x), float(player_y)
        return moved


def move_player(dx, dy):
    """Wraps try_move so a rented horse covers HORSE_SPEED_MULT tiles per
    keypress instead of one, stopping early if a step is blocked."""
    moved_any = False
    steps = HORSE_SPEED_MULT if (mounted and location == "farm") else 1
    for _ in range(steps):
        if not try_move(dx, dy):
            break
        moved_any = True
    return moved_any

#Main Game Loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    tree_timer += dt
    day_timer = (day_timer + dt) % DAY_LENGTH
    tile_draw_size = int(TILE_SIZE * zoom)

    #NPCs: each walks toward today's scheduled waypoint, independent of the player
    for npc in npcs:
        npc_target, npc["activity"] = npc_target_for(npc["schedule"], day_timer / DAY_LENGTH)
        npc_dx, npc_dy = npc_target[0] - npc["x"], npc_target[1] - npc["y"]
        npc_dist = math.hypot(npc_dx, npc_dy)
        if npc_dist > 0.05:
            npc_step = min(npc_dist, NPC_SPEED * dt)
            npc["x"] += npc_dx / npc_dist * npc_step
            npc["y"] += npc_dy / npc_dist * npc_step
            npc["is_walking"] = True
            if abs(npc_dx) > abs(npc_dy):
                npc["facing"] = "right" if npc_dx > 0 else "left"
            else:
                npc["facing"] = "down" if npc_dy > 0 else "up"
        else:
            npc["is_walking"] = False

        if npc["is_walking"]:
            npc["walk_timer"] += dt
            npc["frame_index"] = 1 + int(npc["walk_timer"] // WALK_FRAME_TIME) % 3
        else:
            npc["walk_timer"] = 0.0
            npc["frame_index"] = 0

    #Peaceful animals: idle/wander, and skitter away if the player gets close
    for animal in animals:
        adx, ady = animal["x"] - player_x, animal["y"] - player_y
        dist_to_player = math.hypot(adx, ady)
        if location == "farm" and 0.01 < dist_to_player < 1.8 and animal["state"] != "fleeing":
            flee_dist = 3.0
            animal["target_x"] = max(0, min(WORLD_W - 1, animal["x"] + adx / dist_to_player * flee_dist))
            animal["target_y"] = max(0, min(WORLD_H - 1, animal["y"] + ady / dist_to_player * flee_dist))
            animal["state"] = "fleeing"

        if animal["state"] == "idle":
            animal["timer"] -= dt
            if animal["timer"] <= 0:
                animal["target_x"] = max(0, min(WORLD_W - 1, animal["x"] + random.uniform(-2.5, 2.5)))
                animal["target_y"] = max(0, min(WORLD_H - 1, animal["y"] + random.uniform(-2.5, 2.5)))
                animal["state"] = "moving"

        if animal["state"] in ("moving", "fleeing"):
            tdx = animal["target_x"] - animal["x"]
            tdy = animal["target_y"] - animal["y"]
            tdist = math.hypot(tdx, tdy)
            speed = ANIMAL_SPEED[animal["species"]] * (2.2 if animal["state"] == "fleeing" else 1.0)
            if tdist > 0.08:
                step = min(tdist, speed * dt)
                animal["x"] += tdx / tdist * step
                animal["y"] += tdy / tdist * step
                if abs(tdx) > 0.01:
                    animal["facing_right"] = tdx > 0
            else:
                animal["state"] = "idle"
                animal["timer"] = random.uniform(1.5, 4.0)

    #Fish: peaceful, purely ambient — wander only within their own lake's
    #exact tile set (never the surrounding land), no reaction to the player.
    if location == "farm":
        for f in fish:
            if f["state"] == "idle":
                f["timer"] -= dt
                if f["timer"] <= 0:
                    f["target_x"], f["target_y"] = random.choice(f["water_tiles"])
                    f["state"] = "moving"
            if f["state"] == "moving":
                tdx = f["target_x"] - f["x"]
                tdy = f["target_y"] - f["y"]
                tdist = math.hypot(tdx, tdy)
                if tdist > 0.08:
                    step = min(tdist, FISH_SPEED * dt)
                    f["x"] += tdx / tdist * step
                    f["y"] += tdy / tdist * step
                    if abs(tdx) > 0.01:
                        f["facing_right"] = tdx > 0
                else:
                    f["state"] = "idle"
                    f["timer"] = random.uniform(1.0, 3.0)

    #Demons: idle/wander like the peaceful animals, but drift toward the
    #player when close instead of fleeing — a sense of danger even though
    #this first pass keeps combat itself to a simple strike-to-kill.
    if location == "underworld":
        for demon in demons:
            ddx, ddy = player_x - demon["x"], player_y - demon["y"]
            dist_to_player = math.hypot(ddx, ddy)
            if 0.01 < dist_to_player < 4.0 and demon["state"] != "hunting":
                demon["state"] = "hunting"

            if demon["state"] == "hunting":
                if dist_to_player > 5.5:
                    demon["state"] = "idle"
                    demon["timer"] = random.uniform(0.5, 1.5)
                else:
                    demon["target_x"] = player_x
                    demon["target_y"] = player_y

            if demon["state"] == "idle":
                demon["timer"] -= dt
                if demon["timer"] <= 0:
                    demon["target_x"] = max(0, min(UNDERWORLD_W - 1, demon["x"] + random.uniform(-2.5, 2.5)))
                    demon["target_y"] = max(0, min(UNDERWORLD_H - 1, demon["y"] + random.uniform(-2.5, 2.5)))
                    demon["state"] = "moving"

            if demon["state"] in ("moving", "hunting"):
                tdx = demon["target_x"] - demon["x"]
                tdy = demon["target_y"] - demon["y"]
                tdist = math.hypot(tdx, tdy)
                speed = DEMON_SPEED * (1.6 if demon["state"] == "hunting" else 1.0)
                if tdist > 0.08:
                    step = min(tdist, speed * dt)
                    demon["x"] += tdx / tdist * step
                    demon["y"] += tdy / tdist * step
                    if abs(tdx) > 0.01:
                        demon["facing_right"] = tdx > 0
                elif demon["state"] == "moving":
                    demon["state"] = "idle"
                    demon["timer"] = random.uniform(1.5, 4.0)

            #Contact damage: any demon close enough hurts the player on a
            #per-demon cooldown, regardless of aggro state.
            if demon["attack_cooldown"] > 0:
                demon["attack_cooldown"] -= dt
            if location == "underworld" and demon["attack_cooldown"] <= 0 and dist_to_player < DEMON_ATTACK_RANGE:
                demon["attack_cooldown"] = DEMON_ATTACK_COOLDOWN
                player_hp -= DEMON_ATTACK_DAMAGE
                player_hurt_flash = PLAYER_HURT_FLASH_DURATION
                if player_hp <= 0:
                    player_hp = PLAYER_MAX_HP // 2
                    location = "farm"
                    # Dying always sends you home, not just back to whichever
                    # ruin you happened to enter through — one consistent
                    # respawn point rather than scattered "return here" spots.
                    player_x, player_y = HOUSE_POS[0], DOOR_ROW + 1
                    player_visual_x, player_visual_y = float(player_x), float(player_y)
                    current_ruin_id = None
                    mounted = False
                    achievement_queue.append({
                        "text": "Overwhelmed! You wake up back at the farmhouse...",
                        "timer": 0.0,
                    })

    #Farm raids: once the player has been to the underworld at least once,
    #demons occasionally wander up through a ruin and raid the surface farm.
    #A Watchtower gives an early warning and halves the odds; a Magic Ward
    #stops raids outright. Same wander/hunt AI and contact damage as
    #underworld demons, just running on the WORLD_W/H surface map instead.
    if location == "farm" and has_visited_underworld:
        if raid_warning_timer > 0:
            raid_warning_timer -= dt
            if raid_warning_timer <= 0:
                spawn_count = random.randint(2, 4)
                for _ in range(spawn_count):
                    for _try in range(40):
                        rx = HOUSE_POS[0] + random.randint(-25, 25)
                        ry = HOUSE_POS[1] + random.randint(-25, 25)
                        if (0 <= rx < WORLD_W and 0 <= ry < WORLD_H and (rx, ry) not in FARM_BLOCKED_TILES
                                and farm[ry][rx]["state"] == "grass"
                                and math.hypot(rx - HOUSE_POS[0], ry - HOUSE_POS[1]) > 10):
                            farm_demons.append({
                                "x": float(rx), "y": float(ry), "target_x": float(rx), "target_y": float(ry),
                                "state": "idle", "timer": random.uniform(0.0, 2.0), "facing_right": True,
                                "hp": DEMON_MAX_HP, "attack_cooldown": 0.0,
                            })
                            break
                achievement_queue.append({"text": "Monsters are attacking the farm!", "timer": 0.0})
        else:
            raid_timer += dt
            if raid_timer >= RAID_CHECK_INTERVAL:
                raid_timer = 0.0
                if not any_active_building("magic_ward") and not farm_demons:
                    chance = RAID_CHANCE
                    has_tower = any_active_building("watchtower")
                    if has_tower:
                        chance *= 0.5
                    if random.random() < chance:
                        if has_tower:
                            raid_warning_timer = 4.0
                            achievement_queue.append({"text": "The watchtower spots movement near the farm...",
                                                       "timer": 0.0})
                        else:
                            raid_warning_timer = 0.01  # spawn on the very next tick, no warning available

        for demon in farm_demons:
            ddx, ddy = player_x - demon["x"], player_y - demon["y"]
            dist_to_player = math.hypot(ddx, ddy)
            if 0.01 < dist_to_player < 4.0 and demon["state"] != "hunting":
                demon["state"] = "hunting"

            if demon["state"] == "hunting":
                if dist_to_player > 5.5:
                    demon["state"] = "idle"
                    demon["timer"] = random.uniform(0.5, 1.5)
                else:
                    demon["target_x"] = player_x
                    demon["target_y"] = player_y

            if demon["state"] == "idle":
                demon["timer"] -= dt
                if demon["timer"] <= 0:
                    demon["target_x"] = max(0, min(WORLD_W - 1, demon["x"] + random.uniform(-2.5, 2.5)))
                    demon["target_y"] = max(0, min(WORLD_H - 1, demon["y"] + random.uniform(-2.5, 2.5)))
                    demon["state"] = "moving"

            if demon["state"] in ("moving", "hunting"):
                tdx = demon["target_x"] - demon["x"]
                tdy = demon["target_y"] - demon["y"]
                tdist = math.hypot(tdx, tdy)
                speed = DEMON_SPEED * (1.6 if demon["state"] == "hunting" else 1.0)
                if tdist > 0.08:
                    step = min(tdist, speed * dt)
                    demon["x"] += tdx / tdist * step
                    demon["y"] += tdy / tdist * step
                    if abs(tdx) > 0.01:
                        demon["facing_right"] = tdx > 0
                elif demon["state"] == "moving":
                    demon["state"] = "idle"
                    demon["timer"] = random.uniform(1.5, 4.0)

            if demon["attack_cooldown"] > 0:
                demon["attack_cooldown"] -= dt
            if demon["attack_cooldown"] <= 0 and dist_to_player < DEMON_ATTACK_RANGE:
                demon["attack_cooldown"] = DEMON_ATTACK_COOLDOWN
                player_hp -= DEMON_ATTACK_DAMAGE
                player_hurt_flash = PLAYER_HURT_FLASH_DURATION
                if player_hp <= 0:
                    player_hp = PLAYER_MAX_HP // 2
                    player_x, player_y = HOUSE_POS[0], DOOR_ROW + 1
                    player_visual_x, player_visual_y = float(player_x), float(player_y)
                    mounted = False
                    achievement_queue.append({"text": "Beaten back! You retreat to the farmhouse...", "timer": 0.0})

    #Villagers: wander locally around their village center
    VILLAGER_SPEED = 1.1
    for villager in villagers:
        if not villager["wandering"]:
            villager["timer"] -= dt
            if villager["timer"] <= 0:
                villager["target_x"] = max(0, min(WORLD_W - 1, villager["home_x"] + random.uniform(-4, 4)))
                villager["target_y"] = max(0, min(WORLD_H - 1, villager["home_y"] + random.uniform(-4, 4)))
                villager["wandering"] = True
        else:
            vdx = villager["target_x"] - villager["x"]
            vdy = villager["target_y"] - villager["y"]
            vdist = math.hypot(vdx, vdy)
            if vdist > 0.08:
                step = min(vdist, VILLAGER_SPEED * dt)
                villager["x"] += vdx / vdist * step
                villager["y"] += vdy / vdist * step
                if abs(vdx) > abs(vdy):
                    villager["facing"] = "right" if vdx > 0 else "left"
                else:
                    villager["facing"] = "down" if vdy > 0 else "up"
            else:
                villager["wandering"] = False
                villager["timer"] = random.uniform(2.0, 5.0)

        if villager["wandering"]:
            villager["walk_timer"] += dt
            villager["frame_index"] = 1 + int(villager["walk_timer"] // WALK_FRAME_TIME) % 3
        else:
            villager["walk_timer"] = 0.0
            villager["frame_index"] = 0

    #Rain / snow: mutually exclusive periodic weather with real falling
    #particles (rendered in the farm scene further down), instead of just a
    #background timer with no visible effect.
    farm_view_h = HEIGHT - UI_BAR_HEIGHT
    if raining:
        rain_timer += dt
        if rain_timer >= RAIN_DURATION:
            raining = False
            rain_timer = 0.0
    elif snowing:
        snow_timer += dt
        if snow_timer >= SNOW_DURATION:
            snowing = False
            snow_timer = 0.0
    else:
        weather_timer += dt
        if weather_timer >= WEATHER_INTERVAL:
            weather_timer = 0.0
            if season_for_day(day) == "Winter":
                snowing = True
                snow_flakes = [
                    {"x": random.uniform(0, WIDTH), "y": random.uniform(-farm_view_h, farm_view_h),
                     "speed": random.uniform(40, 90), "drift": random.uniform(-20, 20),
                     "size": random.uniform(2, 4), "phase": random.uniform(0, 6.28)}
                    for _ in range(SNOW_FLAKE_COUNT)
                ]
            else:
                raining = True
                rain_drops = [
                    {"x": random.uniform(0, WIDTH), "y": random.uniform(-farm_view_h, farm_view_h),
                     "speed": random.uniform(420, 620), "length": random.uniform(10, 18)}
                    for _ in range(RAIN_DROP_COUNT)
                ]

    if raining:
        for drop in rain_drops:
            drop["y"] += drop["speed"] * dt
            drop["x"] -= drop["speed"] * 0.12 * dt
            if drop["y"] > farm_view_h:
                drop["y"] = random.uniform(-40, -5)
                drop["x"] = random.uniform(0, WIDTH)
            if drop["x"] < -20:
                drop["x"] = WIDTH + 20

    if snowing:
        for flake in snow_flakes:
            flake["y"] += flake["speed"] * dt
            flake["x"] += math.sin(flake["phase"] + flake["y"] * 0.02) * flake["drift"] * dt
            if flake["y"] > farm_view_h:
                flake["y"] = random.uniform(-40, -5)
                flake["x"] = random.uniform(0, WIDTH)

    if haste:
        haste_timer += dt
        if haste_timer >= HASTE_DURATION:
            haste = False
            haste_timer = 0.0

    if player_hurt_flash > 0:
        player_hurt_flash -= dt

    #Tree spawn 
    if axe_tool and tree_timer >= TREE_INTERVAL:
        spawn_tree()
        tree_timer = 0.0

    #Level-Up Screen — every line is wrapped/centered to the screen width so
    #a long achievement name or reward description can never run off-screen
    if level_up_pending:
        screen.fill((50, 50, 50))
        wrap_w = WIDTH - 40
        y = HEIGHT // 2 - 60
        y += draw_wrapped_centered(screen, font, level_up_message, TEXT_GOLD, WIDTH // 2, y, wrap_w) + 14
        y += draw_wrapped_centered(screen, font, "Choose your reward:", TEXT_CREAM, WIDTH // 2, y, wrap_w) + 14
        y += draw_wrapped_centered(screen, font, f"1: {reward_options[0]}", (196, 214, 255), WIDTH // 2, y, wrap_w) + 6
        draw_wrapped_centered(screen, font, f"2: {reward_options[1]}", (196, 214, 255), WIDTH // 2, y, wrap_w)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    apply_reward(reward_options[0])
                    level_up_pending = False
                    show_level_popup(level)
                elif event.key == pygame.K_2:
                    apply_reward(reward_options[1])
                    level_up_pending = False
                    show_level_popup(level)




        #skips the rest of the current loop iteration and moves to the next one (we havnt learnt continue yet)
        #If level-up screen is active then skip the rest of the game logic for this frame
        continue

    #Events 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Movement (frozen while a conversation is open)
            if event.key in (pygame.K_LEFT, pygame.K_a) and not dialogue_open and not market_open and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open:
                player_facing = "left"
                player_is_walking = move_player(-1, 0)
                player_walk_timer = 0.0
            if event.key in (pygame.K_RIGHT, pygame.K_d) and not dialogue_open and not market_open and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open:
                player_facing = "right"
                player_is_walking = move_player(1, 0)
                player_walk_timer = 0.0
            if event.key in (pygame.K_UP, pygame.K_w) and not dialogue_open and not market_open and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open:
                player_facing = "up"
                player_is_walking = move_player(0, -1)
                player_walk_timer = 0.0
            if event.key in (pygame.K_DOWN, pygame.K_s) and not dialogue_open and not market_open and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open:
                player_facing = "down"
                player_is_walking = move_player(0, 1)
                player_walk_timer = 0.0

            # Seed selection
            seed_list = list(SEEDS.keys())
            for idx, key in enumerate(SEED_KEYS):
                if event.key == key and idx < len(seed_list):
                    selected_seed = seed_list[idx]

            # Inventory toggle only if not level-up
            if event.key == pygame.K_q and not level_up_pending:
                inventory_open = not inventory_open

            # World map: M opens it (outdoors, nothing else open), Esc or M closes it
            if event.key == pygame.K_m and location == "farm":
                if map_open:
                    map_open = False
                elif not inventory_open and not level_up_pending and not dialogue_open and not market_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open:
                    map_open = True
            elif event.key == pygame.K_ESCAPE and map_open:
                map_open = False

            # Crop journal: X opens the compendium of every crop the player has
            # or hasn't yet discovered. Same modal exclusivity as the map.
            if event.key == pygame.K_x:
                if journal_open:
                    journal_open = False
                elif not inventory_open and not level_up_pending and not dialogue_open and not market_open and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open:
                    journal_open = True
            elif event.key == pygame.K_ESCAPE and journal_open:
                journal_open = False

            # Switch tool
            if event.key == pygame.K_z and len(unlocked_tools) > 1:
                idx = unlocked_tools.index(equipped_tool)
                idx = (idx + 1) % len(unlocked_tools)
                equipped_tool = unlocked_tools[idx]

            # Talking to the NPC: E closes an open conversation, or opens
            # one if the player is facing the NPC. just_closed_dialogue
            # keeps this same E press from also triggering another action
            # (e.g. harvesting) underneath the dismissed conversation.
            just_closed_dialogue = False
            if event.key == pygame.K_e:
                if dialogue_open:
                    dialogue_open = False
                    just_closed_dialogue = True
                elif not inventory_open and not level_up_pending and not market_open and not map_open and location == "farm":
                    fdx, fdy = FACING_DELTA[player_facing]
                    facing_pos = (player_x + fdx, player_y + fdy)
                    for npc in npcs:
                        if facing_pos == (round(npc["x"]), round(npc["y"])):
                            dialogue_open = True
                            dialogue_text = next_npc_tip(npc)
                            break
                    else:
                        for villager in villagers:
                            if facing_pos == (round(villager["x"]), round(villager["y"])):
                                dialogue_open = True
                                dialogue_text = f"{villager['name']}: {villager['greeting']}"
                                break

            # Marketplace: E opens a stall when facing it, or (while open)
            # confirms the selected trade / the trailing "Leave" option.
            # Up/Down navigate. just_closed_market mirrors just_closed_dialogue.
            just_closed_market = False
            if event.key == pygame.K_e:
                if market_open:
                    if market_selection == len(active_outpost["trades"]):
                        market_open = False
                        just_closed_market = True
                    else:
                        trade = active_outpost["trades"][market_selection]
                        if trade["type"] == "buy":
                            if emeralds >= trade["price"]:
                                emeralds -= trade["price"]
                                discover_seed(trade["item"], count=trade["qty"])
                                market_message = f"Bought {trade['qty']} {SEEDS[trade['item']]['name']}"
                            else:
                                market_message = "Not enough emeralds!"
                        elif trade["type"] == "sell":
                            if seed_inventory.get(trade["item"], 0) >= trade["qty"]:
                                seed_inventory[trade["item"]] -= trade["qty"]
                                emeralds += trade["price"]
                                market_message = f"Sold {trade['qty']} {SEEDS[trade['item']]['name']}"
                            else:
                                market_message = "Not enough to sell!"
                        elif trade["type"] == "sell_good":
                            if goods_inventory.get(trade["item"], 0) >= trade["qty"]:
                                goods_inventory[trade["item"]] -= trade["qty"]
                                emeralds += trade["price"]
                                market_message = f"Sold {trade['qty']} {GOODS_INFO[trade['item']]['name']}"
                            else:
                                market_message = "Not enough to sell!"
                        elif trade["type"] == "buy_tool":
                            if emeralds >= trade["price"]:
                                emeralds -= trade["price"]
                                apply_reward(f"Unlock {trade['tool_name'].capitalize()}")
                                market_message = f"Bought the {trade['tool_name'].capitalize()}!"
                            else:
                                market_message = "Not enough emeralds!"
                        elif trade["type"] == "buy_pick_upgrade":
                            if emeralds >= trade["price"]:
                                emeralds -= trade["price"]
                                pick_tool["level"] += 1
                                market_message = f"Pick sharpened — now Lvl {pick_tool['level']}!"
                            else:
                                market_message = "Not enough emeralds!"
                        market_message_timer = 2.5
                elif not inventory_open and not level_up_pending and not dialogue_open and not map_open and location == "farm":
                    fdx, fdy = FACING_DELTA[player_facing]
                    fx, fy = player_x + fdx, player_y + fdy
                    if 0 <= fx < WORLD_W and 0 <= fy < WORLD_H:
                        # Blacksmith and fisherman shacks share the market UI —
                        # they just plug in a different `trades` list. Same
                        # active_outpost pointer, different flavor of stock.
                        if farm[fy][fx]["market_id"] is not None:
                            active_outpost = outposts[farm[fy][fx]["market_id"]]
                            market_open = True
                            market_selection = 0
                        elif farm[fy][fx]["smithy_id"] is not None:
                            active_outpost = smithies[farm[fy][fx]["smithy_id"]]
                            active_outpost.setdefault("kind", "smithy")
                            market_open = True
                            market_selection = 0
                        elif farm[fy][fx]["shack_id"] is not None:
                            active_outpost = shacks[farm[fy][fx]["shack_id"]]
                            active_outpost.setdefault("kind", "shack")
                            market_open = True
                            market_selection = 0

            if market_open and event.key == pygame.K_ESCAPE:
                market_open = False
                just_closed_market = True

            if market_open:
                num_options = len(active_outpost["trades"]) + 1
                if event.key in (pygame.K_UP, pygame.K_w):
                    market_selection = (market_selection - 1) % num_options
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    market_selection = (market_selection + 1) % num_options

            # Build menu: B opens/closes it (outdoors, nothing else open).
            # Up/Down pick a building type, E attempts to place it at the
            # tile(s) currently faced.
            just_placed_building = False
            if event.key == pygame.K_b and location == "farm":
                if build_menu_open:
                    build_menu_open = False
                elif not inventory_open and not level_up_pending and not dialogue_open and not market_open and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open:
                    build_menu_open = True
                    build_menu_selection = 0
            elif event.key == pygame.K_ESCAPE and build_menu_open:
                build_menu_open = False

            if build_menu_open:
                if event.key in (pygame.K_UP, pygame.K_w):
                    build_menu_selection = (build_menu_selection - 1) % len(BUILD_MENU_ORDER)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    build_menu_selection = (build_menu_selection + 1) % len(BUILD_MENU_ORDER)
                elif event.key == pygame.K_e:
                    placed = attempt_place_building(BUILD_MENU_ORDER[build_menu_selection])
                    if placed:
                        build_menu_open = False
                        just_placed_building = True
                        recompute_farm_tier()

            # Farm Status screen: K opens/closes it (outdoors, nothing else open)
            if event.key == pygame.K_k and location == "farm":
                if farm_status_open:
                    farm_status_open = False
                elif not inventory_open and not level_up_pending and not dialogue_open and not market_open and not map_open and not journal_open and not build_menu_open and not building_panel_open:
                    farm_status_open = True
            elif event.key == pygame.K_ESCAPE and farm_status_open:
                farm_status_open = False

            # Interacting with an existing player building (facing it, press
            # E) opens its status/production/repair panel. just_placed_building
            # stops the same E press that JUST placed a new building from also
            # being read as "open the building I'm now facing" underneath it.
            # just_opened_building_panel guards the symmetric case: without it,
            # this same E press would also fall through to the "navigate/
            # confirm" block below (now that building_panel_open just flipped
            # True) and instantly confirm whatever option defaults to selected
            # — the same double-action bug the ruin/portal entry had.
            just_opened_building_panel = False
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not just_placed_building and location == "farm":
                if event.key == pygame.K_e:
                    fdx, fdy = FACING_DELTA[player_facing]
                    fx, fy = player_x + fdx, player_y + fdy
                    if 0 <= fx < WORLD_W and 0 <= fy < WORLD_H and farm[fy][fx]["building_id"] is not None:
                        active_building = farm_buildings[farm[fy][fx]["building_id"]]
                        building_panel_open = True
                        building_panel_selection = 0
                        just_opened_building_panel = True

            # Building panel: navigate/confirm/leave
            if building_panel_open and active_building is not None and not just_opened_building_panel:
                options = get_building_panel_options(active_building)
                if event.key in (pygame.K_UP, pygame.K_w):
                    building_panel_selection = (building_panel_selection - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    building_panel_selection = (building_panel_selection + 1) % len(options)
                elif event.key == pygame.K_ESCAPE:
                    building_panel_open = False
                elif event.key == pygame.K_e:
                    chosen = options[building_panel_selection]
                    if chosen["kind"] == "leave":
                        building_panel_open = False
                    elif chosen["kind"] == "recipe" and chosen["affordable"]:
                        consume_recipe_inputs(chosen["recipe"]["input"])
                        proc_time = chosen["recipe"]["time"]
                        proc_qty = chosen["recipe"]["qty"]
                        if active_building["type"] == "mill" and any_active_building("windmill"):
                            proc_time *= 0.6  # Windmill speeds up every Mill's production
                        # Poor building condition -> Lower quality products -> Lower profit
                        if active_building["condition"] < CONDITION_POOR:
                            proc_qty = max(1, proc_qty // 2)
                        elif active_building["condition"] < CONDITION_WORN:
                            proc_time *= 1.3
                        active_building["processing"] = {
                            "recipe_name": chosen["recipe"]["name"], "time_left": proc_time,
                            "output": chosen["recipe"]["output"], "qty": proc_qty,
                        }
                        market_message, market_message_timer = f"Started: {chosen['recipe']['name']}", 2.0
                    elif chosen["kind"] == "collect":
                        out_key, qty = active_building["processing"]["output"], active_building["processing"]["qty"]
                        goods_inventory[out_key] = goods_inventory.get(out_key, 0) + qty
                        active_building["processing"] = None
                        market_message, market_message_timer = f"Collected {qty} {GOODS_INFO[out_key]['name']}", 2.0
                    elif chosen["kind"] == "collect_stock":
                        goods_inventory["honey"] = goods_inventory.get("honey", 0) + active_building["stock"]
                        market_message, market_message_timer = f"Collected {active_building['stock']} Honey", 2.0
                        active_building["stock"] = 0
                    elif chosen["kind"] == "repair":
                        cost = chosen["repair_cost"]
                        if all((emeralds if k == "emeralds" else resources.get(k, 0)) >= v for k, v in cost.items()):
                            for k, v in cost.items():
                                if k == "emeralds":
                                    emeralds -= v
                                else:
                                    resources[k] -= v
                            active_building["condition"] = 100.0
                            market_message, market_message_timer = "Repaired!", 1.6
                        else:
                            market_message, market_message_timer = "Not enough resources to repair!", 1.8

            # Sleeping in the house bed
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and location == "house":
                if event.key == pygame.K_e and (interior_player_x, interior_player_y) == INTERIOR_BED:
                    season_before = season_for_day(day)
                    day += 1
                    day_timer = 0.0
                    for row in farm:
                        for t in row:
                            if t["state"] in ("planted", "sprout", "growing", "grown"): t["timer"] += 2.0
                    for s in seed_inventory: seed_inventory[s] += 5
                    season_after = season_for_day(day)
                    if season_after != season_before:
                        day_popup_queue.append({"text": f"A new season begins: {season_after}", "timer": 0.0})
                    else:
                        day_popup_queue.append({"text": f"Day {day}", "timer": 0.0})

            # Entering the house (must be standing on the doorway and press E)
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and location == "farm":
                if event.key == pygame.K_e and (player_x, player_y) in DOOR_TILES:
                    location = "house"
                    interior_player_x, interior_player_y = INTERIOR_DOOR[0], INTERIOR_DOOR[1] - 1

            # Renting/returning a horse at a stable (facing it and press E)
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and location == "farm":
                if event.key == pygame.K_e:
                    fdx, fdy = FACING_DELTA[player_facing]
                    fx, fy = player_x + fdx, player_y + fdy
                    if 0 <= fx < WORLD_W and 0 <= fy < WORLD_H and farm[fy][fx]["stable_id"] is not None:
                        if mounted:
                            mounted = False
                            market_message = "Returned the horse."
                        elif emeralds >= HORSE_RENTAL_COST:
                            emeralds -= HORSE_RENTAL_COST
                            mounted = True
                            market_message = "Enjoy the ride!"
                        else:
                            market_message = "Not enough emeralds to rent a horse!"
                        market_message_timer = 2.5

            # Paying a kingdom's gate toll (facing it, press E) — a one-time
            # payment; once paid the gate stays open for the rest of the game.
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and location == "farm":
                if event.key == pygame.K_e:
                    fdx, fdy = FACING_DELTA[player_facing]
                    fx, fy = player_x + fdx, player_y + fdy
                    if 0 <= fx < WORLD_W and 0 <= fy < WORLD_H and farm[fy][fx]["kingdom_id"] is not None:
                        kingdom = kingdoms[farm[fy][fx]["kingdom_id"]]
                        if not kingdom["paid"]:
                            if emeralds >= kingdom["toll"]:
                                emeralds -= kingdom["toll"]
                                kingdom["paid"] = True
                                market_message = f"Welcome to {kingdom['name']}!"
                            else:
                                market_message = f"Need {kingdom['toll']}g for the {kingdom['name']} toll!"
                            market_message_timer = 2.5

            # Chopping a tree (must be equipped with the axe and facing it) —
            # drops Wood, the base material for most construction.
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and location == "farm":
                if event.key == pygame.K_e and equipped_tool == axe_tool:
                    fdx, fdy = FACING_DELTA[player_facing]
                    fx, fy = player_x + fdx, player_y + fdy
                    if 0 <= fx < WORLD_W and 0 <= fy < WORLD_H and farm[fy][fx]["state"] == "tree":
                        farm[fy][fx]["state"] = "grass"
                        farm[fy][fx]["tree_variant"] = None
                        swinging, swing_timer = True, 0.0
                        wood_gain = random.randint(4, 8)
                        resources["wood"] += wood_gain
                        market_message, market_message_timer = f"+{wood_gain} Wood", 1.6

            # Mining a boulder (must be equipped with the Pick and facing it) —
            # drops Stone, with a smaller chance of Iron.
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and location == "farm":
                if event.key == pygame.K_e and equipped_tool == pick_tool:
                    fdx, fdy = FACING_DELTA[player_facing]
                    fx, fy = player_x + fdx, player_y + fdy
                    if 0 <= fx < WORLD_W and 0 <= fy < WORLD_H and farm[fy][fx]["state"] == "rock":
                        farm[fy][fx]["state"] = "grass"
                        swinging, swing_timer = True, 0.0
                        stone_gain = random.randint(3, 6) * pick_tool["level"]
                        resources["stone"] += stone_gain
                        toast = f"+{stone_gain} Stone"
                        if random.random() < 0.25:
                            iron_gain = random.randint(1, 2)
                            resources["iron"] += iron_gain
                            toast += f", +{iron_gain} Iron"
                        market_message, market_message_timer = toast, 1.6

            # Entering a ruin (facing it, outdoors, press E) — descends into
            # the underworld, remembering exactly where to reappear on return.
            # just_entered_ruin stops this same E press from also being read
            # as "standing on the portal, return to the surface" below, since
            # the arrival tile IS the portal tile.
            just_entered_ruin = False
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and location == "farm":
                if event.key == pygame.K_e:
                    fdx, fdy = FACING_DELTA[player_facing]
                    fx, fy = player_x + fdx, player_y + fdy
                    if 0 <= fx < WORLD_W and 0 <= fy < WORLD_H and farm[fy][fx]["ruin_id"] is not None:
                        ruin = ruins[farm[fy][fx]["ruin_id"]]
                        surface_return_x, surface_return_y = player_x, player_y
                        current_ruin_id = farm[fy][fx]["ruin_id"]
                        mounted = False
                        location = "underworld"
                        player_x, player_y = ruin["underworld_x"], ruin["underworld_y"]
                        player_visual_x, player_visual_y = float(player_x), float(player_y)
                        just_entered_ruin = True
                        has_visited_underworld = True  # the farm can now be raided

            # Returning to the surface (standing on the portal tile, or
            # facing it, press E)
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and not just_entered_ruin and location == "underworld":
                if event.key == pygame.K_e:
                    fdx, fdy = FACING_DELTA[player_facing]
                    fx, fy = player_x + fdx, player_y + fdy
                    on_portal = underworld[player_y][player_x]["state"] == "portal"
                    facing_portal = (0 <= fx < UNDERWORLD_W and 0 <= fy < UNDERWORLD_H
                                     and underworld[fy][fx]["state"] == "portal")
                    if on_portal or facing_portal:
                        location = "farm"
                        player_x, player_y = surface_return_x, surface_return_y
                        player_visual_x, player_visual_y = float(player_x), float(player_y)
                        current_ruin_id = None

            # Striking a demon (within sword reach, press E, sword equipped) —
            # the swing plays even on a miss, for responsive feedback; a flat
            # hit lands on the nearest demon in range (a reach-radius check
            # rather than an exact facing-tile match, which is fragile against
            # a moving target — round-half-to-even can put a demon's rounded
            # position a full tile off from where it visually stands). On
            # death it drops Hellsteel and counts toward purifying this
            # ruin's patch of desert back on the surface.
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and not just_entered_ruin and location == "underworld":
                if event.key == pygame.K_e and underworld[player_y][player_x]["state"] != "portal" and equipped_tool == sword_tool:
                    swinging, swing_timer = True, 0.0
                    target_demon = None
                    best_dist = SWORD_REACH
                    for demon in demons:
                        d = math.hypot(demon["x"] - player_x, demon["y"] - player_y)
                        if d <= best_dist:
                            best_dist = d
                            target_demon = demon
                    if target_demon is not None:
                        demon = target_demon
                        demon["hp"] -= 1
                        if demon["hp"] <= 0:
                            demons.remove(demon)
                            hellsteel += 1
                            if current_ruin_id is not None:
                                ruin = ruins[current_ruin_id]
                                ruin["kills"] += 1
                                if not ruin["purified"] and ruin["kills"] >= PURIFY_KILLS_NEEDED:
                                    ruin["purified"] = True
                                    purify_around_ruin(ruin)
                                    achievement_queue.append({
                                        "text": "The curse recedes — the desert begins to bloom!",
                                        "timer": 0.0,
                                    })

            # Striking a farm raider (same sword-reach mechanic as underworld
            # demons) — surface raids drop Hellsteel too, since it's the same
            # demon, just wandered up through a ruin rather than met down below.
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and location == "farm":
                if event.key == pygame.K_e and equipped_tool == sword_tool:
                    swinging, swing_timer = True, 0.0
                    target_demon = None
                    best_dist = SWORD_REACH
                    for demon in farm_demons:
                        d = math.hypot(demon["x"] - player_x, demon["y"] - player_y)
                        if d <= best_dist:
                            best_dist = d
                            target_demon = demon
                    if target_demon is not None:
                        target_demon["hp"] -= 1
                        if target_demon["hp"] <= 0:
                            farm_demons.remove(target_demon)
                            hellsteel += 1

            # Tile actions only if inventory closed and outdoors
            if not inventory_open and not level_up_pending and not dialogue_open and not just_closed_dialogue and not market_open and not just_closed_market and not map_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open and location == "farm":
                tile = farm[player_y][player_x]

                # Plant
                if event.key == pygame.K_SPACE and selected_seed in seed_inventory:
                    swinging, swing_timer = True, 0.0
                    seed = SEEDS[selected_seed]
                    positions_to_plant = [(player_x, player_y)]

                    if haste:
                        directions = [(1,0),(0,1)]

                        for dx,dy in directions:
                            nx,ny = player_x+dx,player_y+dy

                            if 0<=nx<WORLD_W and 0<=ny<WORLD_H:
                                t = farm[ny][nx]

                                if t["state"]=="grass" and (nx,ny) not in FARM_BLOCKED_TILES:
                                    positions_to_plant.append((nx,ny))

                                    if len(positions_to_plant)>=3: break



                    for px,py in positions_to_plant:
                        t = farm[py][px]
                        if t["state"]=="grass" and seed_inventory[selected_seed]>0:
                            t["state"]="planted"
                            t["timer"]=0.0
                            t["seed"]=selected_seed
                            t["soil_variant"] = random.randrange(len(SOIL_IMAGES))
                            t["stage_anim"] = 0.0
                            seed_inventory[selected_seed]-=1


                # Harvest
                if event.key == pygame.K_e:
                    swinging, swing_timer = True, 0.0
                    if tile["state"]=="withered":
                        # dead crop: can't be collected, just clear the plot
                        tile["state"]="grass"
                        tile["timer"]=0.0
                        tile["seed"]=None
                        tile["soil_variant"]=None

                    elif tile["state"]=="grown":
                        harvested_seed = tile["seed"]
                        harvest_amount = 1
                        xp_gain = SEEDS[harvested_seed]["xp"]

                        if equipped_tool==pick_tool and pick_tool["level"]>=2:
                            harvest_amount=2
                            xp_gain*=2
                        seed_inventory[harvested_seed]+=harvest_amount
                        xp+=xp_gain
                        harvested+=1
                        farming_skill_xp += xp_gain


                        #tomato haste ability
                        if harvested_seed=="tomato":
                            haste=True
                            haste_timer=0.0

                        #Orchard Plot: apple/grape planted on its footprint
                        #auto-replant on harvest instead of needing a fresh seed
                        orchard_replant = (player_x, player_y) in orchard_tiles and harvested_seed in ("apple", "grape")

                        #Hoe ability
                        if equipped_tool==hoe_tool and seed_inventory.get(harvested_seed,0)>0:
                            tile["state"]="planted"
                            tile["timer"]=0.0
                            tile["seed"]=harvested_seed
                            tile["soil_variant"]=random.randrange(len(SOIL_IMAGES))
                            tile["stage_anim"]=0.0
                            seed_inventory[harvested_seed]-=1
                        elif orchard_replant:
                            tile["state"]="planted"
                            tile["timer"]=0.0
                            tile["seed"]=harvested_seed
                            tile["soil_variant"]=random.randrange(len(SOIL_IMAGES))
                            tile["stage_anim"]=0.0
                        else:
                            tile["state"]="grass"
                            tile["timer"]=0.0
                            tile["seed"]=None
                            tile["soil_variant"]=None

                        #Farming skill: a slower, parallel XP track fed by the
                        #same harvests, unlocking passive farm-wide bonuses
                        #(see farming_skill_growth_mult / _bypasses_winter /
                        #_build_discount) instead of one-off rewards.
                        while farming_skill_xp >= farming_skill_xp_needed(farming_skill_level):
                            farming_skill_xp -= farming_skill_xp_needed(farming_skill_level)
                            farming_skill_level += 1
                            achievement_queue.append({"text": f"Farming Skill Level {farming_skill_level}!", "timer": 0.0})

                        #levil up logic via xp
                        if xp>=xp_needed:
                            level+=1
                            xp=0
                            xp_needed = 10 + level**2 * 8  # quadratic curve: each level meaningfully harder than the last
                            if level in LEVELS:
                                lvl_data=LEVELS[level]
                                unlock_achievement(lvl_data.get("achievement",""))
                                reward_options=[]
                                if level==4:
                                    reward_options=["Unlock Hoe","Skip"] if not hoe_tool else ["Upgrade Pickaxe","Upgrade Hoe"]
                                else:
                                    rewards=lvl_data.get("reward",[])
                                    if len(rewards)==2: reward_options=rewards
                                    elif len(rewards)==1: reward_options=[rewards[0],"Skip"]
                                level_up_pending=True
                                level_up_message=f"Level {level} reached!"


        #zoom
        elif event.type==pygame.MOUSEWHEEL:
            zoom = max(0.5, min(2.0, zoom + 0.1*event.y))

        #Hotbar: pick up a slot on mouse-down
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not level_up_pending:
                drag_slot = hotbar_slot_at(event.pos)

        #Hotbar: drop on mouse-up — same slot (or a miss) selects it,
        #a different slot swaps the two
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drag_slot is not None:
                target = hotbar_slot_at(event.pos)
                if target is not None and target != drag_slot:
                    hotbar_slots[drag_slot], hotbar_slots[target] = hotbar_slots[target], hotbar_slots[drag_slot]
                else:
                    slot = hotbar_slots[drag_slot]
                    if slot["kind"] == "seed":
                        selected_seed = slot["key"]
                    else:
                        equipped_tool = slot["tool"]
                drag_slot = None

    #Continuous movement: keep stepping at a steady interval while a
    #direction key is held, instead of requiring a fresh press per tile.
    if not dialogue_open and not market_open and not map_open and not level_up_pending and not inventory_open and not journal_open and not build_menu_open and not building_panel_open and not farm_status_open:
        keys_held = pygame.key.get_pressed()
        if keys_held[pygame.K_LEFT] or keys_held[pygame.K_a]:
            held_dx, held_dy, held_facing = -1, 0, "left"
        elif keys_held[pygame.K_RIGHT] or keys_held[pygame.K_d]:
            held_dx, held_dy, held_facing = 1, 0, "right"
        elif keys_held[pygame.K_UP] or keys_held[pygame.K_w]:
            held_dx, held_dy, held_facing = 0, -1, "up"
        elif keys_held[pygame.K_DOWN] or keys_held[pygame.K_s]:
            held_dx, held_dy, held_facing = 0, 1, "down"
        else:
            held_dx = None

        if held_dx is not None:
            move_repeat_timer += dt
            if move_repeat_timer >= MOVE_REPEAT_DELAY:
                move_repeat_timer -= MOVE_REPEAT_DELAY
                player_facing = held_facing
                player_is_walking = move_player(held_dx, held_dy)
                player_walk_timer = 0.0
        else:
            move_repeat_timer = 0.0
    else:
        move_repeat_timer = 0.0

    #Farm buildings: construction progress, condition decay, and any
    #in-progress production ticking down — all continuous over real time
    #(scaled by DAY_LENGTH) rather than gated behind sleeping, so a Mill
    #doesn't pause just because you wandered into the underworld.
    for b in farm_buildings:
        if b["stage"] == "building":
            b["progress_days"] += dt / DAY_LENGTH
            info = FARM_BUILDING_TYPES[b["type"]]
            if b["progress_days"] >= info["build_days"]:
                b["stage"] = "active"
                b["condition"] = 100.0
                achievement_queue.append({"text": f"{info['label']} construction complete!", "timer": 0.0})
                recompute_farm_tier()
        elif b["stage"] == "active":
            b["condition"] = max(0.0, b["condition"] - CONDITION_DECAY_PER_DAY * (dt / DAY_LENGTH))
            if b["processing"] is not None and b["processing"]["time_left"] > 0:
                b["processing"]["time_left"] = max(0.0, b["processing"]["time_left"] - dt)
            if b["type"] == "beehive":
                b["_honey_timer"] += dt
                gain_interval = 6.0 if b["flower_bonus"] else 12.0
                if b["_honey_timer"] >= gain_interval:
                    b["_honey_timer"] -= gain_interval
                    b["stock"] += 1

    #Growth update: planted -> sprout -> growing -> grown -> withered.
    #Growth speed is modulated per-tile by growth_rate_at() (farming skill
    #bonus, winter slowdown, nearby Well/Greenhouse) instead of a flat dt.
    for y, row in enumerate(farm):
        for x, tile in enumerate(row):
            state = tile["state"]
            if state == "grass":
                continue

            tile["stage_anim"] += dt

            if state in ("planted", "sprout", "growing", "grown"):
                tile["timer"] += dt * growth_rate_at(x, y)
                seed = SEEDS[tile["seed"]]
                grow_time = seed["grow_time"]
                wither_time = seed.get("wither_time", grow_time * 2)

                if state == "planted" and tile["timer"] >= grow_time * 0.25:
                    tile["state"] = "sprout"
                    tile["stage_anim"] = 0.0
                elif state == "sprout" and tile["timer"] >= grow_time * 0.5:
                    tile["state"] = "growing"
                    tile["stage_anim"] = 0.0
                elif state == "growing" and tile["timer"] >= grow_time:
                    tile["state"] = "grown"
                    tile["stage_anim"] = 0.0
                elif state == "grown" and tile["timer"] >= grow_time + wither_time:
                    tile["state"] = "withered"
                    tile["stage_anim"] = 0.0

    #Player walk animation
    if player_is_walking:
        player_walk_timer += dt
        step = int(player_walk_timer // WALK_FRAME_TIME)
        if step >= 3:
            player_is_walking = False
            player_frame_index = 0
        else:
            player_frame_index = step + 1
    else:
        player_frame_index = 0

    #Tool swing animation
    if swinging:
        swing_timer += dt
        if swing_timer >= SWING_DURATION:
            swinging = False
            swing_timer = 0.0

    # Draw scene
    screen.fill((50,50,50))
    farm_view_rect = pygame.Rect(0, 0, WIDTH, HEIGHT - UI_BAR_HEIGHT)
    screen.set_clip(farm_view_rect)

    if location == "farm":
        #Camera
        cam_x, cam_y = update_camera_view()
        current_ticks = pygame.time.get_ticks()

        # Only iterate the tiles actually on screen (plus a small margin for
        # 2-tile-tall sprites like trees/house that overhang upward) — the
        # world is far too large now to redraw every tile every frame.
        visible_cols = WIDTH // tile_draw_size + 3
        visible_rows = (HEIGHT - UI_BAR_HEIGHT) // tile_draw_size + 3
        cam_x_i, cam_y_i = int(cam_x), int(cam_y)
        x_range = range(max(0, cam_x_i - 1), min(WORLD_W, cam_x_i + visible_cols))
        y_range = range(max(0, cam_y_i - 2), min(WORLD_H, cam_y_i + visible_rows))

        for y in y_range:
            for x in x_range:
                draw_x = (x - cam_x) * tile_draw_size
                draw_y = (y - cam_y) * tile_draw_size
                tile = farm[y][x]

             # --- Ground (grass is always the base layer). Water tiles fall
             # through to the ordinary grass drawing below — the lake/pond
             # itself is one single precomputed smooth shape drawn as its
             # own pass further down, not a per-tile texture, so it reads as
             # a real lake instead of a grid of blended water tiles. ---
                if tile["ground_static"] is not None:
                    ground_scaled = pygame.transform.scale(tile["ground_static"], (tile_draw_size, tile_draw_size))
                    screen.blit(ground_scaled, (draw_x, draw_y))
                else:
                    # Grass is drawn oversized and overlapping its neighbors so
                    # blade tips spill across tile boundaries (no hard squares).
                    ground_img = GROUND_FRAMES[tile["ground_variant"]][grass_frame_for(x, y, current_ticks)]
                    overflow_size = int(tile_draw_size * GRASS_OVERFLOW_SCALE)
                    ground_scaled = pygame.transform.scale(ground_img, (overflow_size, overflow_size))
                    offset = (overflow_size - tile_draw_size) // 2
                    screen.blit(ground_scaled, (draw_x - offset, draw_y - offset))

                if tile["state"] == "grass":
                    if tile["decor"] is not None:
                        decor_scaled = pygame.transform.scale(tile["decor"], (tile_draw_size, tile_draw_size))
                        screen.blit(decor_scaled, (draw_x, draw_y))
                elif tile["soil_variant"] is not None:
                    # --- Tilled soil patch ---
                    soil_img = SOIL_IMAGES[tile["soil_variant"]]
                    soil_scaled = pygame.transform.scale(soil_img, (tile_draw_size, tile_draw_size))
                    screen.blit(soil_scaled, (draw_x, draw_y))

                # --- Tree: sprite is 2 tiles wide x 2 tiles tall (wide canopies
                # need the extra width so they don't clip), centered and
                # bottom-anchored over this tile's 1-tile collision footprint ---
                if tile["tree_variant"] is not None:
                    tree_img = TREE_IMAGES[tile["tree_variant"]]
                    tree_scaled = pygame.transform.scale(tree_img, (tile_draw_size * 2, tile_draw_size * 2))
                    screen.blit(tree_scaled, (draw_x - tile_draw_size // 2, draw_y - tile_draw_size))

                # --- Mineable boulder: flush 1-tile sprite, no overhang ---
                if tile["state"] == "rock":
                    boulder_scaled = pygame.transform.scale(IMG_BOULDER, (tile_draw_size, tile_draw_size))
                    screen.blit(boulder_scaled, (draw_x, draw_y))

                # --- Kingdom wall: flush 1-tile sprite, tiles repeat to form
                # the perimeter (the gate itself is drawn separately, once
                # per kingdom, in the kingdoms pass below) ---
                if tile["state"] == "wall":
                    wall_scaled = pygame.transform.scale(IMG_WALL_STONE, (tile_draw_size, tile_draw_size))
                    screen.blit(wall_scaled, (draw_x, draw_y))

                # --- Crop growth stage, animated ---
                if tile["state"] == "grown":
                    stage_img = CROP_IMAGES.get(tile["seed"])
                else:
                    stage_img = STAGE_IMAGES.get(tile["state"])

                if stage_img is not None:
                    pop = min(1.0, tile["stage_anim"] / STAGE_POP_DURATION)
                    pop_scale = 0.5 + 0.5 * pop
                    size = max(1, int(tile_draw_size * pop_scale))
                    crop_scaled = pygame.transform.scale(stage_img, (size, size))

                    sway = 0
                    if tile["state"] in ("sprout", "growing", "grown"):
                        sway = math.sin(current_ticks * 0.002 + (x * 13 + y * 7)) * (tile_draw_size * 0.045)

                    offset_x = draw_x + (tile_draw_size - size) // 2 + sway
                    offset_y = draw_y + (tile_draw_size - size)
                    screen.blit(crop_scaled, (offset_x, offset_y))

        #Lakes/ponds: one precomputed smooth-shore image per water body,
        #drawn on top of the grass already rendered underneath it, instead
        #of a grid of individually-blended water tiles. Culled to only the
        #ones actually on screen, and each shape caches its own smoothscale
        #result (expensive — real interpolation, not nearest-neighbor) keyed
        #on the target pixel size, since that size only changes when zoom
        #changes, not every single frame — with dozens of lakes on a big
        #map, re-smoothscaling all of them every frame was the single
        #biggest frame-time cost in the game.
        for ws in water_shapes:
            if ws["x"] + ws["w"] < cam_x_i - 1 or ws["x"] > cam_x_i + visible_cols:
                continue
            if ws["y"] + ws["h"] < cam_y_i - 2 or ws["y"] > cam_y_i + visible_rows:
                continue
            ws_dx = (ws["x"] - cam_x) * tile_draw_size
            ws_dy = (ws["y"] - cam_y) * tile_draw_size
            target_size = (int(ws["w"] * tile_draw_size), int(ws["h"] * tile_draw_size))
            if ws.get("_cached_size") != target_size:
                ws["_cached_scaled"] = pygame.transform.smoothscale(ws["surface"], target_size)
                ws["_cached_size"] = target_size
            screen.blit(ws["_cached_scaled"], (ws_dx, ws_dy))

        #Fish: peaceful, swim within their own lake, small bob for a
        #"just below the surface" look.
        for f in fish:
            if f["x"] < cam_x_i - 1 or f["x"] > cam_x_i + visible_cols + 1:
                continue
            if f["y"] < cam_y_i - 1 or f["y"] > cam_y_i + visible_rows + 1:
                continue
            f_draw_x = (f["x"] - cam_x) * tile_draw_size
            f_draw_y = (f["y"] - cam_y) * tile_draw_size
            bob = math.sin(current_ticks * 0.006 + f["x"] * 3) * tile_draw_size * 0.05
            sprite = IMG_FISH if f["facing_right"] else IMG_FISH_FLIPPED
            fish_size = int(tile_draw_size * 0.7)
            fish_scaled = pygame.transform.scale(sprite, (fish_size, fish_size))
            screen.blit(fish_scaled, (f_draw_x + (tile_draw_size - fish_size) // 2,
                                       f_draw_y + (tile_draw_size - fish_size) // 2 - bob))

        # --- House exterior: sprite is 2 tiles tall, anchored so its bottom
        # edge sits on the bottom of its 1-tile solid footprint (the roof
        # and chimney overhang into the tile row above) ---
        house_draw_x = (HOUSE_POS[0] - cam_x) * tile_draw_size
        house_draw_y = (HOUSE_POS[1] - cam_y) * tile_draw_size - tile_draw_size
        house_scaled = pygame.transform.scale(IMG_HOUSE, (tile_draw_size * 2, tile_draw_size * 2))
        screen.blit(house_scaled, (house_draw_x, house_draw_y))

        #Outposts / marketplaces: same bottom-anchored, 2-tiles-tall technique as the house
        for outpost in outposts:
            width_tiles = 2 if outpost["kind"] == "marketplace" else 1
            variant_pool = MARKETPLACE_IMAGES if outpost["kind"] == "marketplace" else OUTPOST_IMAGES
            stall_img = variant_pool[outpost["variant"]]
            stall_draw_x = (outpost["x"] - cam_x) * tile_draw_size
            stall_draw_y = (outpost["y"] - cam_y) * tile_draw_size - tile_draw_size
            stall_scaled = pygame.transform.scale(stall_img, (tile_draw_size * width_tiles, tile_draw_size * 2))
            screen.blit(stall_scaled, (stall_draw_x, stall_draw_y))

        #Stables: same bottom-anchored, 2-tiles-tall, 2-tiles-wide technique
        for stable in stables:
            stable_draw_x = (stable["x"] - cam_x) * tile_draw_size
            stable_draw_y = (stable["y"] - cam_y) * tile_draw_size - tile_draw_size
            stable_scaled = pygame.transform.scale(IMG_STABLE, (tile_draw_size * 2, tile_draw_size * 2))
            screen.blit(stable_scaled, (stable_draw_x, stable_draw_y))

        #Ancient ruins: doorways down into the underworld, same bottom-anchored technique
        for ruin in ruins:
            ruin_draw_x = (ruin["x"] - cam_x) * tile_draw_size
            ruin_draw_y = (ruin["y"] - cam_y) * tile_draw_size - tile_draw_size
            ruin_scaled = pygame.transform.scale(IMG_RUIN, (tile_draw_size * 2, tile_draw_size * 2))
            screen.blit(ruin_scaled, (ruin_draw_x, ruin_draw_y))

        #Wells: a single flush tile, no overhang, so no vertical offset needed
        for well in wells:
            well_draw_x = (well["x"] - cam_x) * tile_draw_size
            well_draw_y = (well["y"] - cam_y) * tile_draw_size
            well_scaled = pygame.transform.scale(IMG_WELL, (tile_draw_size, tile_draw_size))
            screen.blit(well_scaled, (well_draw_x, well_draw_y))

        #Shrines: same bottom-anchored, 2-tiles-tall, 2-tiles-wide technique
        for shrine in shrines:
            shrine_draw_x = (shrine["x"] - cam_x) * tile_draw_size
            shrine_draw_y = (shrine["y"] - cam_y) * tile_draw_size - tile_draw_size
            shrine_scaled = pygame.transform.scale(IMG_SHRINE, (tile_draw_size * 2, tile_draw_size * 2))
            screen.blit(shrine_scaled, (shrine_draw_x, shrine_draw_y))

        #Blacksmiths and fisherman shacks: same 2x2 bottom-anchored pattern
        for smithy in smithies:
            sm_dx = (smithy["x"] - cam_x) * tile_draw_size
            sm_dy = (smithy["y"] - cam_y) * tile_draw_size - tile_draw_size
            sm_scaled = pygame.transform.scale(IMG_BLACKSMITH, (tile_draw_size * 2, tile_draw_size * 2))
            screen.blit(sm_scaled, (sm_dx, sm_dy))
        for shack in shacks:
            sh_dx = (shack["x"] - cam_x) * tile_draw_size
            sh_dy = (shack["y"] - cam_y) * tile_draw_size - tile_draw_size
            sh_scaled = pygame.transform.scale(IMG_FISHERMAN_SHACK, (tile_draw_size * 2, tile_draw_size * 2))
            screen.blit(sh_scaled, (sh_dx, sh_dy))

        #Biome-flavor village centerpieces (pagoda/adobe/snow-cabin): same
        #2x2 bottom-anchored pattern
        for fb in flavor_buildings:
            fb_dx = (fb["x"] - cam_x) * tile_draw_size
            fb_dy = (fb["y"] - cam_y) * tile_draw_size - tile_draw_size
            fb_scaled = pygame.transform.scale(FLAVOR_HOUSE_IMAGES[fb["flavor"]], (tile_draw_size * 2, tile_draw_size * 2))
            screen.blit(fb_scaled, (fb_dx, fb_dy))

        #Kingdom gates: drawn once per kingdom, spanning both of its gate
        #tiles (the wall segments themselves are drawn per-tile above)
        for kingdom in kingdoms:
            gt_dx = (kingdom["gate_x"] - cam_x) * tile_draw_size
            gt_dy = (kingdom["gate_y"] - cam_y) * tile_draw_size - tile_draw_size
            gt_scaled = pygame.transform.scale(IMG_KINGDOM_GATE, (tile_draw_size * 2, tile_draw_size * 2))
            screen.blit(gt_scaled, (gt_dx, gt_dy))

        #Player-constructed farm buildings: bottom-anchored like every other
        #structure. Under construction, the scaffolding overlay + a progress
        #bar stand in for the real sprite; once active, a thin condition bar
        #appears only once it's actually worn (green/yellow/red).
        for b in farm_buildings:
            fw, fh = FARM_BUILDING_TYPES[b["type"]]["footprint"]
            fb_dx = (b["x"] - cam_x) * tile_draw_size
            fb_dy = (b["y"] - cam_y) * tile_draw_size - (tile_draw_size if fh > 1 else 0)
            draw_w, draw_h = tile_draw_size * fw, tile_draw_size * fh
            if b["stage"] == "building":
                site_scaled = pygame.transform.scale(IMG_CONSTRUCTION_SITE, (draw_w, draw_h))
                screen.blit(site_scaled, (fb_dx, fb_dy))
                info = FARM_BUILDING_TYPES[b["type"]]
                pct = min(1.0, b["progress_days"] / info["build_days"])
                bar_rect = pygame.Rect(fb_dx, fb_dy - 8, draw_w, 5)
                draw_bar(screen, bar_rect, pct, (232, 196, 90))
            else:
                bldg_scaled = pygame.transform.scale(FARM_BUILDING_IMAGES[b["type"]], (draw_w, draw_h))
                screen.blit(bldg_scaled, (fb_dx, fb_dy))
                if b["condition"] < CONDITION_WORN:
                    cond_color = (200, 60, 56) if b["condition"] < CONDITION_POOR else (222, 176, 60)
                    bar_rect = pygame.Rect(fb_dx, fb_dy - 8, draw_w, 5)
                    draw_bar(screen, bar_rect, b["condition"] / 100.0, cond_color)

        #NPCs: drawn at their continuous position with the same camera transform
        #as tiles. Idle NPCs get the same subtle 1–2px breathing bob as the
        #player, on individually-phased sine waves so they don't all rise/fall
        #in lockstep like a chorus line.
        for npc in npcs:
            npc_draw_x = (npc["x"] - cam_x) * tile_draw_size
            npc_draw_y = (npc["y"] - cam_y) * tile_draw_size
            npc_sprite = npc["frames"][npc["facing"]][npc["frame_index"]]
            npc_scaled = pygame.transform.scale(npc_sprite, (tile_draw_size, tile_draw_size))
            npc_breath = 0
            if not npc["is_walking"]:
                npc_breath = int(math.sin(current_ticks * 0.0028 + npc["x"] * 1.7) * tile_draw_size * 0.03)
            screen.blit(npc_scaled, (npc_draw_x, npc_draw_y + npc_breath))

        #Villagers: same rendering approach as NPCs, same breathing bob
        for villager in villagers:
            v_draw_x = (villager["x"] - cam_x) * tile_draw_size
            v_draw_y = (villager["y"] - cam_y) * tile_draw_size
            v_sprite = villager["frames"][villager["facing"]][villager["frame_index"]]
            v_scaled = pygame.transform.scale(v_sprite, (tile_draw_size, tile_draw_size))
            v_breath = 0
            if not villager["wandering"]:
                v_breath = int(math.sin(current_ticks * 0.0028 + villager["x"] * 1.7) * tile_draw_size * 0.03)
            screen.blit(v_scaled, (v_draw_x, v_draw_y + v_breath))

        #Peaceful animals: a small hop/bob while moving, flipped to face travel direction
        for animal in animals:
            a_draw_x = (animal["x"] - cam_x) * tile_draw_size
            a_draw_y = (animal["y"] - cam_y) * tile_draw_size
            bob = 0
            if animal["state"] != "idle":
                bob = abs(math.sin(current_ticks * 0.009 + animal["x"] * 3)) * tile_draw_size * 0.08
            sprite_set = ANIMAL_IMAGES if animal["facing_right"] else ANIMAL_IMAGES_FLIPPED
            animal_scaled = pygame.transform.scale(sprite_set[animal["species"]], (tile_draw_size, tile_draw_size))
            screen.blit(animal_scaled, (a_draw_x, a_draw_y - bob))

        #Farm raiders: demons that wandered up through a ruin, same look and
        #behavior as their underworld kin
        for demon in farm_demons:
            fd_draw_x = (demon["x"] - cam_x) * tile_draw_size
            fd_draw_y = (demon["y"] - cam_y) * tile_draw_size
            bob = (abs(math.sin(current_ticks * 0.01 + demon["x"] * 3)) * tile_draw_size * 0.08
                   if demon["state"] != "idle" else math.sin(current_ticks * 0.0022 + demon["x"] * 2.1) * tile_draw_size * 0.04)
            demon_sprite = IMG_DEMON if demon["facing_right"] else IMG_DEMON_FLIPPED
            demon_scaled = pygame.transform.scale(demon_sprite, (tile_draw_size, tile_draw_size))
            screen.blit(demon_scaled, (fd_draw_x, fd_draw_y - bob))
            if demon["hp"] < DEMON_MAX_HP:
                bar_rect = pygame.Rect(fd_draw_x, fd_draw_y - 8, tile_draw_size, 5)
                draw_bar(screen, bar_rect, demon["hp"] / DEMON_MAX_HP, (200, 40, 40))

        draw_size = tile_draw_size
        px = (player_x - cam_x) * tile_draw_size
        py = (player_y - cam_y) * tile_draw_size

        fdx, fdy = FACING_DELTA[player_facing]
        facing_tile = (player_x + fdx, player_y + fdy)
        fx, fy = facing_tile
        facing_in_bounds = 0 <= fx < WORLD_W and 0 <= fy < WORLD_H

        facing_npc_name = None
        for npc in npcs:
            if facing_tile == (round(npc["x"]), round(npc["y"])):
                facing_npc_name = npc["name"]
                break
        if facing_npc_name is None:
            for villager in villagers:
                if facing_tile == (round(villager["x"]), round(villager["y"])):
                    facing_npc_name = villager["name"]
                    break

        facing_farm_demon = any(math.hypot(d["x"] - player_x, d["y"] - player_y) <= SWORD_REACH for d in farm_demons)

        hud_prompt = None
        if (player_x, player_y) in DOOR_TILES:
            hud_prompt = "Press E to enter"
        elif facing_farm_demon and equipped_tool == sword_tool:
            hud_prompt = "Press E to strike"
        elif facing_npc_name is not None:
            hud_prompt = f"Press E to talk to {facing_npc_name}"
        elif facing_in_bounds and farm[fy][fx]["stable_id"] is not None:
            hud_prompt = "Press E to return the horse" if mounted else f"Press E to rent a horse ({HORSE_RENTAL_COST}g)"
        elif facing_in_bounds and equipped_tool == axe_tool and axe_tool is not None and farm[fy][fx]["state"] == "tree":
            hud_prompt = "Press E to chop"
        elif facing_in_bounds and equipped_tool == pick_tool and farm[fy][fx]["state"] == "rock":
            hud_prompt = "Press E to mine"
        elif facing_in_bounds and farm[fy][fx]["market_id"] is not None:
            hud_prompt = "Press E to trade"
        elif facing_in_bounds and farm[fy][fx]["smithy_id"] is not None:
            hud_prompt = "Press E to visit the blacksmith"
        elif facing_in_bounds and farm[fy][fx]["shack_id"] is not None:
            hud_prompt = "Press E to trade with the fisherman"
        elif facing_in_bounds and farm[fy][fx]["ruin_id"] is not None:
            hud_prompt = "Press E to enter the ruins"
        elif facing_in_bounds and farm[fy][fx]["building_id"] is not None:
            fb = farm_buildings[farm[fy][fx]["building_id"]]
            fb_label = FARM_BUILDING_TYPES[fb["type"]]["label"]
            hud_prompt = f"{fb_label}: under construction" if fb["stage"] == "building" else f"Press E to use the {fb_label}"
        elif facing_in_bounds and farm[fy][fx]["kingdom_id"] is not None:
            kingdom = kingdoms[farm[fy][fx]["kingdom_id"]]
            hud_prompt = (f"Welcome to {kingdom['name']}" if kingdom["paid"]
                          else f"Press E to pay {kingdom['toll']}g to enter {kingdom['name']}")

    elif location == "underworld":
        #Camera
        cam_x, cam_y = update_camera_view()
        current_ticks = pygame.time.get_ticks()

        visible_cols = WIDTH // tile_draw_size + 3
        visible_rows = (HEIGHT - UI_BAR_HEIGHT) // tile_draw_size + 3
        cam_x_i, cam_y_i = int(cam_x), int(cam_y)
        x_range = range(max(0, cam_x_i - 1), min(UNDERWORLD_W, cam_x_i + visible_cols))
        y_range = range(max(0, cam_y_i - 2), min(UNDERWORLD_H, cam_y_i + visible_rows))

        for y in y_range:
            for x in x_range:
                draw_x = (x - cam_x) * tile_draw_size
                draw_y = (y - cam_y) * tile_draw_size
                tile = underworld[y][x]

                ground_img = UNDERWORLD_GROUND_IMAGES[tile["ground_variant"]]
                ground_scaled = pygame.transform.scale(ground_img, (tile_draw_size, tile_draw_size))
                screen.blit(ground_scaled, (draw_x, draw_y))

                if tile["state"] == "portal":
                    portal_frame = PORTAL_FRAMES[int(current_ticks * 0.0025) % len(PORTAL_FRAMES)]
                    portal_scaled = pygame.transform.scale(portal_frame, (tile_draw_size, tile_draw_size))
                    screen.blit(portal_scaled, (draw_x, draw_y))
                elif tile["decor"] is not None:
                    decor_scaled = pygame.transform.scale(tile["decor"], (tile_draw_size, tile_draw_size))
                    screen.blit(decor_scaled, (draw_x, draw_y))

                # --- Obstacle: sprite is 1 tile wide x 2 tall, bottom-anchored
                # over this tile's 1-tile collision footprint, like a tree ---
                if tile["state"] == "obstacle":
                    obstacle_img = UNDERWORLD_OBSTACLE_IMAGES[UNDERWORLD_OBSTACLE_INDEX[tile["zone"]]]
                    obstacle_scaled = pygame.transform.scale(obstacle_img, (tile_draw_size, tile_draw_size * 2))
                    screen.blit(obstacle_scaled, (draw_x, draw_y - tile_draw_size))

        #Demons: a small hop/bob while moving, flipped to face travel direction,
        #with a thin HP bar once they've taken damage
        for demon in demons:
            d_draw_x = (demon["x"] - cam_x) * tile_draw_size
            d_draw_y = (demon["y"] - cam_y) * tile_draw_size
            bob = 0
            if demon["state"] != "idle":
                bob = abs(math.sin(current_ticks * 0.01 + demon["x"] * 3)) * tile_draw_size * 0.08
            else:
                # A slower, deeper breathing bob for idle demons — reads
                # as menacing/heaving rather than a peaceful sway.
                bob = math.sin(current_ticks * 0.0022 + demon["x"] * 2.1) * tile_draw_size * 0.04
            demon_sprite = IMG_DEMON if demon["facing_right"] else IMG_DEMON_FLIPPED
            demon_scaled = pygame.transform.scale(demon_sprite, (tile_draw_size, tile_draw_size))
            screen.blit(demon_scaled, (d_draw_x, d_draw_y - bob))
            if demon["hp"] < DEMON_MAX_HP:
                bar_rect = pygame.Rect(d_draw_x, d_draw_y - 8, tile_draw_size, 5)
                draw_bar(screen, bar_rect, demon["hp"] / DEMON_MAX_HP, (200, 40, 40))

        draw_size = tile_draw_size
        px = (player_x - cam_x) * tile_draw_size
        py = (player_y - cam_y) * tile_draw_size

        fdx, fdy = FACING_DELTA[player_facing]
        facing_tile = (player_x + fdx, player_y + fdy)
        fx, fy = facing_tile
        facing_in_bounds = 0 <= fx < UNDERWORLD_W and 0 <= fy < UNDERWORLD_H

        facing_demon = None
        for demon in demons:
            if facing_tile == (round(demon["x"]), round(demon["y"])):
                facing_demon = demon
                break

        on_portal = underworld[player_y][player_x]["state"] == "portal"
        facing_portal = facing_in_bounds and underworld[fy][fx]["state"] == "portal"

        hud_prompt = None
        if on_portal or facing_portal:
            hud_prompt = "Press E to return to the surface"
        elif facing_demon is not None:
            hud_prompt = "Press E to strike" if equipped_tool == sword_tool else "Equip your Sword (Z) to fight"

    else:
        # --- House interior: small fixed room, no camera scrolling ---
        interior_offset_x = (WIDTH - INTERIOR_W * INTERIOR_TILE_SIZE) // 2
        interior_offset_y = (HEIGHT - UI_BAR_HEIGHT - INTERIOR_H * INTERIOR_TILE_SIZE) // 2

        for iy in range(INTERIOR_H):
            for ix in range(INTERIOR_W):
                dx = interior_offset_x + ix * INTERIOR_TILE_SIZE
                dy = interior_offset_y + iy * INTERIOR_TILE_SIZE
                on_border = ix == 0 or iy == 0 or ix == INTERIOR_W - 1 or iy == INTERIOR_H - 1
                tile_img = IMG_WALL if (on_border and (ix, iy) != INTERIOR_DOOR) else IMG_FLOOR
                screen.blit(pygame.transform.scale(tile_img, (INTERIOR_TILE_SIZE, INTERIOR_TILE_SIZE)), (dx, dy))
                if (ix, iy) == INTERIOR_BED:
                    screen.blit(pygame.transform.scale(IMG_BED, (INTERIOR_TILE_SIZE, INTERIOR_TILE_SIZE)), (dx, dy))

        draw_size = INTERIOR_TILE_SIZE
        px = interior_offset_x + interior_player_x * INTERIOR_TILE_SIZE
        py = interior_offset_y + interior_player_y * INTERIOR_TILE_SIZE
        hud_prompt = None

    #Horse (drawn behind the player, only outdoors, while mounted) — gallops
    #in sync with the rider's own walk timer rather than tracking a separate one
    riding = mounted and location == "farm"
    if riding:
        if player_is_walking:
            horse_frame_index = 1 + (int(player_walk_timer // WALK_FRAME_TIME) % 2)
        else:
            horse_frame_index = 0
        horse_frames = HORSE_FRAMES_FLIPPED if player_facing == "left" else HORSE_FRAMES
        horse_sprite = horse_frames[horse_frame_index]
        horse_size = int(draw_size * 1.3)
        horse_scaled = pygame.transform.scale(horse_sprite, (horse_size, horse_size))
        horse_x0 = px + draw_size // 2 - horse_size // 2
        horse_y0 = py + draw_size - horse_size
        screen.blit(horse_scaled, (horse_x0, horse_y0))

        # Seat the rider on the saddle mark (see HORSE_SADDLE in
        # generate_stable_assets.py, ~52% across / 39% down the sprite)
        # rather than standing at normal footing height, and shrink them
        # slightly so they read as sitting atop the horse.
        draw_size = int(draw_size * 0.85)
        saddle_x = horse_x0 + int(horse_size * 0.52)
        saddle_y = horse_y0 + int(horse_size * 0.4)
        px = saddle_x - draw_size // 2
        py = saddle_y - int(draw_size * 0.68)

    #Player (shared by both scenes) — while idle (not walking, not riding),
    #a subtle 1–2px vertical bob on a slow sine wave sells that the character
    #is a living thing breathing, not a static sprite pinned to the ground.
    #While walking, the walk cycle itself carries all the motion — layering
    #the breath bob on top would double it up and look jittery.
    player_sprite = PLAYER_FRAMES[player_facing][player_frame_index]
    player_scaled = pygame.transform.scale(player_sprite, (draw_size, draw_size))
    breath_offset = 0
    if not player_is_walking and not riding:
        breath_offset = int(math.sin(pygame.time.get_ticks() * 0.0028) * draw_size * 0.03)
    screen.blit(player_scaled, (px, py + breath_offset))

    #Held tool/weapon: an idle carried pose that swings through an arc when
    #used (chop/harvest/plant/strike), instead of the tool being invisible.
    if not riding and equipped_tool is not None and equipped_tool["name"] in TOOL_IMAGES:
        idle_angle, swing_arc, ax_frac, ay_frac = TOOL_POSE[player_facing]
        swing_progress = (swing_timer / SWING_DURATION) if swinging else 0.0
        eased = 1 - (1 - swing_progress) ** 2  # fast snap, soft settle
        angle = idle_angle + swing_arc * eased
        tool_size = int(draw_size * 0.62)
        tool_scaled = pygame.transform.scale(TOOL_IMAGES[equipped_tool["name"]], (tool_size, tool_size))
        tool_rotated = pygame.transform.rotate(tool_scaled, angle)
        anchor = (px + int(draw_size * ax_frac), py + int(draw_size * ay_frac))
        tool_rect = tool_rotated.get_rect(center=anchor)
        screen.blit(tool_rotated, tool_rect)

    # Both of these are anchored to the player's on-screen position, which can
    # sit right at the screen edge near a world boundary (camera clamps there
    # instead of centering) — clamp the label's own x so it can't slide off
    # either side, rather than trusting px to always leave enough room.
    tool_label_surf = render_text(font, f"{equipped_tool['name']} Lvl {equipped_tool['level']}", TEXT_CREAM)
    tool_label_x = max(4, min(WIDTH - tool_label_surf.get_width() - 4, px - 5))
    screen.blit(tool_label_surf, (tool_label_x, py - 25))

    if hud_prompt is not None:
        prompt_surf = render_text(ui_font, hud_prompt, TEXT_GOLD)
        prompt_x = max(4, min(WIDTH - prompt_surf.get_width() - 4, px + draw_size // 2 - prompt_surf.get_width() // 2))
        screen.blit(prompt_surf, (prompt_x, py - 46))

    #Season tint: a soft color wash over the whole farm scene standing in
    #for re-skinning every tile per season.
    if location == "farm":
        season_tint_color = SEASON_TINTS[season_for_day(day)]
        season_tint = pygame.Surface((WIDTH, HEIGHT - UI_BAR_HEIGHT), pygame.SRCALPHA)
        season_tint.fill(season_tint_color)
        screen.blit(season_tint, (0, 0))

    #Rain / snow: drawn over the whole farm scene (falling in front of
    #tiles and the player looks natural), skipped underground/indoors.
    if location == "farm" and raining:
        rain_surf = pygame.Surface((WIDTH, HEIGHT - UI_BAR_HEIGHT), pygame.SRCALPHA)
        for drop in rain_drops:
            pygame.draw.line(rain_surf, (180, 200, 235, 130),
                              (drop["x"], drop["y"]), (drop["x"] - drop["length"] * 0.3, drop["y"] + drop["length"]), 2)
        screen.blit(rain_surf, (0, 0))
        dim_overlay = pygame.Surface((WIDTH, HEIGHT - UI_BAR_HEIGHT), pygame.SRCALPHA)
        dim_overlay.fill((30, 34, 46, 45))
        screen.blit(dim_overlay, (0, 0))
    elif location == "farm" and snowing:
        snow_surf = pygame.Surface((WIDTH, HEIGHT - UI_BAR_HEIGHT), pygame.SRCALPHA)
        for flake in snow_flakes:
            pygame.draw.circle(snow_surf, (255, 255, 255, 210),
                                (int(flake["x"]), int(flake["y"])), int(flake["size"]))
        screen.blit(snow_surf, (0, 0))

    #Vignette: fade the edges of the game view (not the UI bar below it)
    screen.blit(VIGNETTE, (0, 0))

    #Damage flash: a brief red tint over the farm view when hurt
    if player_hurt_flash > 0:
        flash_alpha = int(120 * min(1.0, player_hurt_flash / PLAYER_HURT_FLASH_DURATION))
        flash_overlay = pygame.Surface((WIDTH, HEIGHT - UI_BAR_HEIGHT), pygame.SRCALPHA)
        flash_overlay.fill((200, 30, 30, flash_alpha))
        screen.blit(flash_overlay, (0, 0))

    screen.set_clip(None)

    #UI bar background panel
    BAR_TOP = HEIGHT - UI_BAR_HEIGHT
    pygame.draw.rect(screen, (35, 30, 28), (0, BAR_TOP, WIDTH, UI_BAR_HEIGHT))
    ROW1_Y = BAR_TOP + 10

    #Clock + Day + Season
    draw_clock(screen, (34, ROW1_Y + 24), 22, day_timer / DAY_LENGTH)
    screen.blit(render_text(ui_font, f"Day {day}", TEXT_CREAM), (64, ROW1_Y + 6))
    screen.blit(render_text(tool_font, season_for_day(day), TEXT_GOLD), (64, ROW1_Y + 30))

    #Level / XP bar
    screen.blit(render_text(ui_font, f"Lvl {level}  {xp:.1f}/{xp_needed} XP", TEXT_CREAM), (150, ROW1_Y))
    xp_bar_rect = pygame.Rect(150, ROW1_Y + 28, 190, 16)
    draw_bar(screen, xp_bar_rect, xp / xp_needed if xp_needed else 0, TEXT_GOLD)

    #Health bar (the equipped tool is shown held in-hand + in the floating
    #label over the player now, so this HUD slot is freed up for HP instead)
    hp_col_x = 352
    screen.blit(render_text(tool_font, f"HP {player_hp}/{PLAYER_MAX_HP}", TEXT_CREAM), (hp_col_x, ROW1_Y))
    hp_bar_rect = pygame.Rect(hp_col_x, ROW1_Y + 18, 138, 12)
    draw_bar(screen, hp_bar_rect, player_hp / PLAYER_MAX_HP if PLAYER_MAX_HP else 0, (196, 60, 56))

    #Emeralds (currency)
    emerald_icon_small = pygame.transform.scale(IMG_EMERALD, (16, 16))
    screen.blit(emerald_icon_small, (hp_col_x, ROW1_Y + 36))
    screen.blit(render_text(tool_font, str(emeralds), TEXT_GOLD), (hp_col_x + 18, ROW1_Y + 35))

    #Hellsteel (underworld loot currency) — only worth showing once you've found some
    if hellsteel > 0:
        hellsteel_icon_small = pygame.transform.scale(IMG_HELLSTEEL, (16, 16))
        screen.blit(hellsteel_icon_small, (hp_col_x + 68, ROW1_Y + 36))
        screen.blit(render_text(tool_font, str(hellsteel), TEXT_GOLD), (hp_col_x + 86, ROW1_Y + 35))

    #Hotbar: drag-and-drop reorderable seed/tool slots
    for i, slot in enumerate(hotbar_slots):
        slot_rect = hotbar_slot_rect(i)
        slot_x = slot_rect.x + 3

        if slot["kind"] == "seed":
            seed_key = slot["key"]
            highlight = seed_key == selected_seed
            icon_img = CROP_IMAGES.get(seed_key)
            if icon_img is not None:
                screen.blit(pygame.transform.scale(icon_img, (HOTBAR_ICON_SIZE, HOTBAR_ICON_SIZE)), (slot_x, HOTBAR_ROW_Y))
            else:
                pygame.draw.rect(screen, SEEDS[seed_key]["color"], (slot_x, HOTBAR_ROW_Y + 4, HOTBAR_ICON_SIZE, HOTBAR_ICON_SIZE - 8))
            label = f"x{seed_inventory[seed_key]}"
        else:
            tool = slot["tool"]
            highlight = tool is equipped_tool
            pygame.draw.rect(screen, tool["color"], (slot_x, HOTBAR_ROW_Y + 4, HOTBAR_ICON_SIZE, HOTBAR_ICON_SIZE - 8))
            label = f"L{tool['level']}"

        if i != drag_slot:  # dragged slot's icon follows the cursor instead
            count_color = TEXT_GOLD if highlight else TEXT_CREAM
            screen.blit(render_text(ui_font, label, count_color), (slot_x + HOTBAR_ICON_SIZE + 4, HOTBAR_ROW_Y + 3))
        if highlight:
            pygame.draw.rect(screen, TEXT_GOLD, slot_rect, 2)
        elif drag_slot is not None:
            pygame.draw.rect(screen, (110, 96, 80), slot_rect, 1)  # subtle drop-zone outline while dragging

    #Dragged item follows the cursor
    if drag_slot is not None:
        slot = hotbar_slots[drag_slot]
        mx, my = pygame.mouse.get_pos()
        icon_pos = (mx - HOTBAR_ICON_SIZE // 2, my - HOTBAR_ICON_SIZE // 2)
        if slot["kind"] == "seed":
            icon_img = CROP_IMAGES.get(slot["key"])
            if icon_img is not None:
                screen.blit(pygame.transform.scale(icon_img, (HOTBAR_ICON_SIZE, HOTBAR_ICON_SIZE)), icon_pos)
            else:
                pygame.draw.rect(screen, SEEDS[slot["key"]]["color"], (*icon_pos, HOTBAR_ICON_SIZE, HOTBAR_ICON_SIZE - 8))
        else:
            pygame.draw.rect(screen, slot["tool"]["color"], (*icon_pos, HOTBAR_ICON_SIZE, HOTBAR_ICON_SIZE - 8))



    #Inventory
    if inventory_open:
        overlay = pygame.Surface((300,200))
        overlay.set_alpha(220)
        overlay.fill((30,30,30))
        screen.blit(overlay,(WIDTH//2-150,HEIGHT//2-100))
        screen.blit(render_text(font, "Inventory", TEXT_GOLD),(WIDTH//2-50,HEIGHT//2-80))
        y_offset=0
        for seed in SEEDS:
            screen.blit(render_text(font, f"{SEEDS[seed]['name']}: {seed_inventory[seed]}", SEEDS[seed]["color"]),(WIDTH//2-120,HEIGHT//2-50+y_offset))
            y_offset+=30
        screen.blit(render_text(font, f"Equipped Tool: {equipped_tool['name']} Lvl {equipped_tool['level']}", equipped_tool["color"]),(WIDTH//2-120,HEIGHT//2+50))

    #Dialogue box — NPC tips/greetings are full sentences that can easily be
    #wider than the screen as a single line, so wrap them and size the box
    #to however many lines that actually takes instead of a fixed height.
    if dialogue_open:
        box_w = WIDTH - 40
        text_lines = wrap_text(ui_font, dialogue_text, box_w - 32)
        line_h = ui_font.get_height() + 2
        box_h = max(90, 24 + len(text_lines) * line_h + 34)
        box_x, box_y = 20, (HEIGHT - UI_BAR_HEIGHT) - box_h - 16
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((30, 26, 22, 235))
        screen.blit(box, (box_x, box_y))
        pygame.draw.rect(screen, TEXT_GOLD, (box_x, box_y, box_w, box_h), 2)
        ty = box_y + 16
        for line in text_lines:
            screen.blit(render_text(ui_font, line, TEXT_CREAM), (box_x + 16, ty))
            ty += line_h
        screen.blit(render_text(tool_font, "Press E to close", TEXT_GOLD), (box_x + 16, box_y + box_h - 28))

    #Marketplace panel
    if market_open:
        trades = active_outpost["trades"]
        box_w = WIDTH - 40
        box_h = min((HEIGHT - UI_BAR_HEIGHT) - 20, 70 + (len(trades) + 1) * 28)
        box_x, box_y = 20, ((HEIGHT - UI_BAR_HEIGHT) - box_h) // 2
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((30, 26, 22, 235))
        screen.blit(box, (box_x, box_y))
        pygame.draw.rect(screen, TEXT_GOLD, (box_x, box_y, box_w, box_h), 2)

        kind = active_outpost.get("kind", "outpost")
        title = {"marketplace": "Marketplace", "outpost": "Outpost",
                 "smithy": "Blacksmith", "shack": "Fisherman"}.get(kind, "Trade")
        screen.blit(render_text(font, title, TEXT_GOLD), (box_x + 16, box_y + 8))
        emerald_icon = pygame.transform.scale(IMG_EMERALD, (20, 20))
        screen.blit(emerald_icon, (box_x + box_w - 100, box_y + 12))
        screen.blit(render_text(ui_font, str(emeralds), TEXT_CREAM), (box_x + box_w - 74, box_y + 12))

        line_y = box_y + 44
        for i, trade in enumerate(trades):
            if trade["type"] == "buy":
                label = f"Buy {trade['qty']} {SEEDS[trade['item']]['name']} — {trade['price']}g"
            elif trade["type"] == "sell":
                label = f"Sell {trade['qty']} {SEEDS[trade['item']]['name']} — +{trade['price']}g"
            elif trade["type"] == "sell_good":
                label = f"Sell {trade['qty']} {GOODS_INFO[trade['item']]['name']} — +{trade['price']}g"
            elif trade["type"] == "buy_tool":
                label = f"Buy the {trade['tool_name'].capitalize()} — {trade['price']}g"
            elif trade["type"] == "buy_pick_upgrade":
                label = f"Sharpen Pick (+1 lvl) — {trade['price']}g"
            else:
                label = f"{trade['type']} ({trade.get('price', '?')}g)"
            color = TEXT_GOLD if i == market_selection else TEXT_CREAM
            screen.blit(render_text(ui_font, label, color), (box_x + 20, line_y))
            line_y += 28

        leave_color = TEXT_GOLD if market_selection == len(trades) else TEXT_CREAM
        screen.blit(render_text(ui_font, "Leave", leave_color), (box_x + 20, line_y))

    #Marketplace feedback message (e.g. "Bought 5 Corn", "Not enough emeralds!")
    if market_message_timer > 0:
        market_message_timer -= dt
        alpha = 255 if market_message_timer > 0.5 else int(255 * market_message_timer / 0.5)
        draw_wrapped_centered(screen, ui_font, market_message, TEXT_GOLD, WIDTH // 2, 110, WIDTH - 40, alpha=alpha)

    #World map overlay
    if map_open:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 14, 235))
        screen.blit(overlay, (0, 0))

        margin = 20
        scale_factor = min((WIDTH - margin * 2) / WORLD_W, (HEIGHT - margin * 2) / WORLD_H)
        map_w, map_h = int(WORLD_W * scale_factor), int(WORLD_H * scale_factor)
        map_x, map_y = (WIDTH - map_w) // 2, (HEIGHT - map_h) // 2

        scaled_map = pygame.transform.scale(MAP_SURFACE, (map_w, map_h))
        screen.blit(scaled_map, (map_x, map_y))
        pygame.draw.rect(screen, TEXT_GOLD, (map_x, map_y, map_w, map_h), 2)

        def to_map_xy(wx, wy):
            return (map_x + int(wx * scale_factor), map_y + int(wy * scale_factor))

        hx, hy = to_map_xy(HOUSE_POS[0] + 1, HOUSE_POS[1])
        pygame.draw.circle(screen, (140, 90, 60), (hx, hy), 4)

        for outpost in outposts:
            ox, oy = to_map_xy(outpost["x"], outpost["y"])
            color = TEXT_GOLD if outpost["kind"] == "marketplace" else (200, 170, 110)
            radius = 4 if outpost["kind"] == "marketplace" else 3
            pygame.draw.circle(screen, color, (ox, oy), radius)

        for stable in stables:
            sx, sy = to_map_xy(stable["x"], stable["y"])
            pygame.draw.circle(screen, (180, 130, 80), (sx, sy), 3)

        for smithy in smithies:
            smx, smy = to_map_xy(smithy["x"], smithy["y"])
            pygame.draw.circle(screen, (240, 130, 40), (smx, smy), 3)

        for shack in shacks:
            shmx, shmy = to_map_xy(shack["x"], shack["y"])
            pygame.draw.circle(screen, (108, 168, 200), (shmx, shmy), 3)

        for ruin in ruins:
            rmx, rmy = to_map_xy(ruin["x"], ruin["y"])
            color = (110, 220, 190) if ruin["purified"] else (150, 40, 40)
            pygame.draw.circle(screen, color, (rmx, rmy), 4)
            pygame.draw.circle(screen, (10, 10, 14), (rmx, rmy), 4, 1)

        for shrine in shrines:
            shx, shy = to_map_xy(shrine["x"], shrine["y"])
            pygame.draw.circle(screen, (210, 176, 90), (shx, shy), 3)

        for kingdom in kingdoms:
            kx, ky = to_map_xy(kingdom["x"], kingdom["y"])
            color = (230, 200, 90) if kingdom["paid"] else (170, 60, 150)
            pygame.draw.circle(screen, color, (kx, ky), 6)
            pygame.draw.circle(screen, (10, 10, 14), (kx, ky), 6, 1)

        for fb in flavor_buildings:
            fx_m, fy_m = to_map_xy(fb["x"], fb["y"])
            pygame.draw.circle(screen, (240, 170, 200), (fx_m, fy_m), 3)

        for npc in npcs:
            nx, ny = to_map_xy(npc["x"], npc["y"])
            pygame.draw.circle(screen, (110, 150, 220), (nx, ny), 3)

        px_m, py_m = to_map_xy(player_x, player_y)
        pygame.draw.circle(screen, (255, 255, 255), (px_m, py_m), 5)
        pygame.draw.circle(screen, (0, 0, 0), (px_m, py_m), 5, 1)

        title = render_text(font, "World Map", TEXT_GOLD)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, max(4, map_y - 40)))
        hint = render_text(tool_font, "Press M or Esc to close", TEXT_CREAM)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, min(HEIGHT - 24, map_y + map_h + 10)))

    #Crop Journal overlay: a grid showing every crop in the game. Discovered
    #crops render in full color with their name; locked ones are grayed silhouettes
    #with a "?" name and their unlock hint below, so the player has a checklist
    #of what to find/level up to next.
    if journal_open:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 14, 235))
        screen.blit(overlay, (0, 0))

        cols = 3
        cell_w, cell_h = 158, 68
        top_pad = 68
        left_pad = (WIDTH - cols * cell_w) // 2
        j_title = render_text(font, "Crop Journal", TEXT_GOLD)
        screen.blit(j_title, (WIDTH // 2 - j_title.get_width() // 2, 22))
        found_count = len(DISCOVERED_SEEDS & set(SEEDS))
        counter = render_text(tool_font, f"{found_count} / {len(SEEDS)} discovered", TEXT_CREAM)
        screen.blit(counter, (WIDTH // 2 - counter.get_width() // 2, 50))

        for i, (key, info) in enumerate(SEEDS.items()):
            col, row = i % cols, i // cols
            cx = left_pad + col * cell_w
            cy = top_pad + row * cell_h
            discovered = key in DISCOVERED_SEEDS
            # cell background
            bg = (30, 26, 32, 220) if discovered else (24, 22, 26, 220)
            pygame.draw.rect(screen, bg, (cx + 6, cy + 6, cell_w - 12, cell_h - 12), border_radius=4)
            border = TEXT_GOLD if discovered else (72, 68, 76)
            pygame.draw.rect(screen, border, (cx + 6, cy + 6, cell_w - 12, cell_h - 12), 2, border_radius=4)

            icon_img = CROP_IMAGES.get(key)
            if icon_img is not None:
                icon_scaled = pygame.transform.scale(icon_img, (40, 40))
                if not discovered:
                    # gray silhouette: keep the crop's alpha shape but replace
                    # every visible pixel with a dark uniform gray so all you
                    # can read is the outline, not the identity.
                    silhouette = icon_scaled.copy()
                    silhouette.fill((60, 56, 68, 255), special_flags=pygame.BLEND_RGB_MIN)
                    icon_scaled = silhouette
                screen.blit(icon_scaled, (cx + 14, cy + 14))

            # Text column is narrow (icon eats the cell's left third), so
            # everything here uses micro_font and wraps rather than a fixed
            # font that could run past the cell's own right edge.
            text_col_w = cell_w - 66
            name = info["name"] if discovered else "???"
            name_color = TEXT_CREAM if discovered else (140, 136, 148)
            for j, line in enumerate(wrap_text(micro_font, name, text_col_w)[:2]):
                screen.blit(render_text(micro_font, line, name_color), (cx + 60, cy + 12 + j * 14))

            if discovered:
                val_surf = render_text(micro_font, f"{info.get('value', '?')}g", TEXT_GOLD)
                screen.blit(val_surf, (cx + 60, cy + 42))
            else:
                hint = info.get("unlock_hint", "???")
                hint_surf = render_text(micro_font, hint, (140, 136, 148))
                screen.blit(hint_surf, (cx + 60, cy + 42))

        hint = render_text(tool_font, "Press X or Esc to close", TEXT_CREAM)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - UI_BAR_HEIGHT - 24))

    #Build menu: every buildable building type, cost, and affordability
    if build_menu_open:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 14, 235))
        screen.blit(overlay, (0, 0))

        b_title = render_text(font, "Build Menu", TEXT_GOLD)
        screen.blit(b_title, (WIDTH // 2 - b_title.get_width() // 2, 10))
        res_line = f"Wood {resources['wood']}   Stone {resources['stone']}   Iron {resources['iron']}   Emeralds {emeralds}"
        res_surf = render_text(tool_font, res_line, TEXT_CREAM)
        screen.blit(res_surf, (WIDTH // 2 - res_surf.get_width() // 2, 40))

        row_h = 27
        top = 66
        for i, btype in enumerate(BUILD_MENU_ORDER):
            b_info = FARM_BUILDING_TYPES[btype]
            cost_parts = []
            for res, amt in b_info["cost"].items():
                unit = "g" if res == "emeralds" else res[0].upper()
                cost_parts.append(f"{amt}{unit}")
            cost_str = " ".join(cost_parts)
            can_afford = all((emeralds if r == "emeralds" else resources.get(r, 0)) >= a
                              for r, a in b_info["cost"].items())
            if i == build_menu_selection:
                color = TEXT_GOLD
            elif can_afford:
                color = TEXT_CREAM
            else:
                color = (150, 90, 90)
            line = f"{b_info['label']} ({b_info['category']}) — {cost_str} — {b_info['build_days']}d"
            screen.blit(render_text(tool_font, line, color), (30, top + i * row_h))

        hint = render_text(tool_font, "Up/Down select, E to place facing you, Esc/B close", TEXT_CREAM)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - UI_BAR_HEIGHT - 24))

    #Build feedback message (e.g. "Not enough resources!")
    if build_message_timer > 0:
        build_message_timer -= dt
        alpha = 255 if build_message_timer > 0.5 else int(255 * build_message_timer / 0.5)
        draw_wrapped_centered(screen, ui_font, build_message, TEXT_GOLD, WIDTH // 2, 110, WIDTH - 40, alpha=alpha)

    #Building panel: production/repair/status for an existing farm building,
    #same visual language as the marketplace panel
    if building_panel_open and active_building is not None:
        panel_options = get_building_panel_options(active_building)
        box_w = WIDTH - 40

        # Pre-wrap every option's label so the box is sized from the actual
        # rendered line count, not just the option count — an option that
        # wraps to 2 lines (a long recipe/repair-cost string) would otherwise
        # spill past a box sized for 1 line each.
        wrapped_rows = []
        for i, opt in enumerate(panel_options):
            if opt["kind"] == "recipe" and not opt["affordable"]:
                color = (150, 90, 90)
            elif opt["kind"] == "info":
                color = (170, 166, 176)
            elif i == building_panel_selection:
                color = TEXT_GOLD
            else:
                color = TEXT_CREAM
            for line in wrap_text(ui_font, opt["label"], box_w - 40):
                wrapped_rows.append((line, color))

        box_h = min((HEIGHT - UI_BAR_HEIGHT) - 20, 70 + len(wrapped_rows) * 22)
        box_x, box_y = 20, ((HEIGHT - UI_BAR_HEIGHT) - box_h) // 2
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((30, 26, 22, 235))
        screen.blit(box, (box_x, box_y))
        pygame.draw.rect(screen, TEXT_GOLD, (box_x, box_y, box_w, box_h), 2)

        b_info = FARM_BUILDING_TYPES[active_building["type"]]
        screen.blit(render_text(font, b_info["label"], TEXT_GOLD), (box_x + 16, box_y + 8))
        if active_building["stage"] == "active":
            cond_surf = render_text(tool_font, f"Condition {int(active_building['condition'])}%", TEXT_CREAM)
            screen.blit(cond_surf, (box_x + box_w - cond_surf.get_width() - 16, box_y + 14))

        line_y = box_y + 44
        for line, color in wrapped_rows:
            screen.blit(render_text(ui_font, line, color), (box_x + 20, line_y))
            line_y += 22

    #Farm Status screen: tier, farming skill, resources, and every
    #constructed building with its condition — the base-management hub
    if farm_status_open:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 14, 235))
        screen.blit(overlay, (0, 0))

        fs_title = render_text(font, "Farm Status", TEXT_GOLD)
        screen.blit(fs_title, (WIDTH // 2 - fs_title.get_width() // 2, 10))

        tier_surf = render_text(ui_font, FARM_TIERS[farm_tier], TEXT_CREAM)
        screen.blit(tier_surf, (WIDTH // 2 - tier_surf.get_width() // 2, 42))

        y = 70
        skill_needed = farming_skill_xp_needed(farming_skill_level)
        screen.blit(render_text(tool_font, f"Farming Skill Lvl {farming_skill_level}  "
                                            f"({farming_skill_xp:.0f}/{skill_needed:.0f} XP)", TEXT_CREAM), (24, y))
        skill_bar_rect = pygame.Rect(24, y + 18, WIDTH - 48, 10)
        draw_bar(screen, skill_bar_rect, farming_skill_xp / skill_needed if skill_needed else 0, TEXT_GOLD)
        y += 38

        res_surf = render_text(tool_font,
                                f"Wood {resources['wood']}   Stone {resources['stone']}   Iron {resources['iron']}",
                                TEXT_CREAM)
        screen.blit(res_surf, (24, y))
        y += 24

        if farm_buildings:
            screen.blit(render_text(tool_font, "Buildings:", TEXT_GOLD), (24, y))
            y += 20
            for b in farm_buildings:
                label = FARM_BUILDING_TYPES[b["type"]]["label"]
                if b["stage"] == "building":
                    status = "under construction"
                    color = (200, 190, 150)
                else:
                    status = f"condition {int(b['condition'])}%"
                    color = TEXT_CREAM if b["condition"] >= CONDITION_WORN else (
                        (222, 176, 60) if b["condition"] >= CONDITION_POOR else (200, 60, 56))
                line_surf = render_text(micro_font, f"  {label} — {status}", color)
                screen.blit(line_surf, (24, y))
                y += 16
                if y > HEIGHT - UI_BAR_HEIGHT - 40:
                    break
        else:
            screen.blit(render_text(tool_font, "No buildings yet — press B to open the build menu.", (170, 166, 176)),
                        (24, y))

        hint = render_text(tool_font, "Press K or Esc to close", TEXT_CREAM)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - UI_BAR_HEIGHT - 24))

    #Achievement Popups — wrapped/centered so a long achievement name can
    #never spill off either edge of the screen; each popup advances y_offset
    #by however many lines it actually took, so wrapped entries don't overlap
    #the next popup in the queue.
    popup_wrap_w = WIDTH - 40
    y_offset=10
    for popup in achievement_queue[:]:
        popup["timer"]+=dt
        alpha=255
        if popup["timer"]>ACHIEVEMENT_DISPLAY_TIME-0.5: alpha=int(255*(ACHIEVEMENT_DISPLAY_TIME-popup["timer"])/0.5)
        used_h = draw_wrapped_centered(screen, font, popup["text"], TEXT_GOLD, WIDTH // 2, y_offset, popup_wrap_w, alpha=alpha)
        y_offset += used_h + 6

        #remove it if it exceeds achivment display time
        if popup["timer"]>ACHIEVEMENT_DISPLAY_TIME: achievement_queue.remove(popup)

    #Level-Up Popups
    y_offset=50
    for popup in level_popup_queue[:]:
        popup["timer"]+=dt
        used_h = draw_wrapped_centered(screen, font, popup["text"], TEXT_CREAM, WIDTH // 2, y_offset, popup_wrap_w)
        y_offset += used_h + 6
        if popup["timer"]>LEVEL_POPUP_TIME: level_popup_queue.remove(popup)

    #Day Popups
    y_offset=80
    for popup in day_popup_queue[:]:
        popup["timer"]+=dt
        alpha=255
        if popup["timer"]>DAY_POPUP_TIME-0.5: alpha=int(255*(DAY_POPUP_TIME-popup["timer"])/0.5)
        used_h = draw_wrapped_centered(screen, font, popup["text"], TEXT_CREAM, WIDTH // 2, y_offset, popup_wrap_w, alpha=alpha)
        y_offset += used_h
        if popup["timer"]>DAY_POPUP_TIME: day_popup_queue.remove(popup)

    pygame.display.flip()

pygame.quit()



