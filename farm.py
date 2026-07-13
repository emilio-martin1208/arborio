import math
import os
import random

import pygame

pygame.init()

# Display must come first
TILE_SIZE = 50
INITIAL_VIEW_TILES = 10
UI_BAR_HEIGHT = 120

WORLD_W, WORLD_H = 50, 50
WIDTH = INITIAL_VIEW_TILES * TILE_SIZE
HEIGHT = INITIAL_VIEW_TILES * TILE_SIZE + UI_BAR_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
CROP_IMAGES = {"corn": IMG_CORN, "tomato": IMG_TOMATO, "pumpkin": IMG_PUMPKIN, "carrot": IMG_CARROT}

IMG_GROUND1 = load_image("Ground1.png")
IMG_GROUND2 = load_image("Ground2.png")
IMG_GROUND3 = load_image("Ground3.png")
IMG_GROUND4 = load_image("Ground4.png")
IMG_BED = load_image("Bed.png")
IMG_HOUSE = load_image("House.png")  # 2 tiles wide x 2 tiles tall; only the bottom row is solid
IMG_FLOOR = load_image("Floor.png")
IMG_WALL = load_image("Wall.png")
GROUND_IMAGES = [IMG_GROUND1, IMG_GROUND2, IMG_GROUND3, IMG_GROUND4]
IMG_DECOR1 = load_image("Decor1.png")
IMG_DECOR2 = load_image("Decor2.png")
DECOR_IMAGES = [IMG_DECOR1, IMG_DECOR2]
DECOR_CHANCE = 0.05  # fraction of grass tiles that get a sparse flower decoration

# Irregular tilled-soil patches (chosen per plot so plots don't look gridded)
SOIL_IMAGES = [load_image("Soil1.png"), load_image("Soil2.png"), load_image("Soil3.png")]

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







clock = pygame.time.Clock()
FONT_NAME = "rockwell"  # falls back to the default system font if unavailable
font = pygame.font.SysFont(FONT_NAME, 26, bold=True)
ui_font = pygame.font.SysFont(FONT_NAME, 19, bold=True)  # smaller font for in-game UI
tool_font = pygame.font.SysFont(FONT_NAME, 16, bold=True)  # compact label for the HUD tool slot

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

#Seeds
# wither_time: how long a ripe/grown crop stays harvestable before it dies
SEEDS = {
    "corn": {"name": "Corn", "color": (230, 220, 40), "grow_time": 5.0, "xp": 0.5, "wither_time": 10.0},
    "carrot": {"name": "Carrot", "color": (255, 140, 40), "grow_time": 3.0, "xp": 1.0, "wither_time": 6.0}
}
selected_seed = "corn"
seed_inventory = {"corn": 5, "carrot": 3}
inventory_open = False

#Tools 
pick_tool = {"name": "Pick", "level": 1, "color": (200, 180, 50)}
hoe_tool = None
axe_tool = None
unlocked_tools = [pick_tool]
equipped_tool = pick_tool

#Farm Grid
farm = [
    [
        {
            "state": "grass",
            "timer": 0.0,
            "seed": None,
            "ground": random.choice(GROUND_IMAGES),
            "decor": random.choice(DECOR_IMAGES) if random.random() < DECOR_CHANCE else None,
            "soil_variant": None,
            "stage_anim": 0.0
        }
        for x in range(WORLD_W)
    ]
    for y in range(WORLD_H)
]

#House: a solid 2-wide x 1-tall building footprint on the farm (the sprite
#itself is drawn 2 tiles tall so the roof/chimney overhang above it), with
#a walkable doorway row beneath it. Stepping onto a door tile enters the interior.
HOUSE_POS = (1, 1)  # kept off the world edge so the roof overhang has room to render
HOUSE_TILES = {(HOUSE_POS[0] + dx, HOUSE_POS[1]) for dx in range(2)}
DOOR_ROW = HOUSE_POS[1] + 1
DOOR_TILES = {(HOUSE_POS[0] + dx, DOOR_ROW) for dx in range(2)}
FARM_BLOCKED_TILES = HOUSE_TILES | DOOR_TILES  # kept clear of trees/crops

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
harvested = 0
day = 1
xp = 0.0
level = 1
xp_needed = 10
day_timer = 0.0
DAY_LENGTH = 45.0  # seconds of real time the HUD clock treats as one in-game day

#Wind gusts sweeping across the grass
def make_wind_overlay(height):
    band_w, gap, overlay_w = 26, 34, 220
    surf = pygame.Surface((overlay_w, height), pygame.SRCALPHA)
    x = 0
    while x < overlay_w:
        pygame.draw.polygon(surf, (255, 255, 255, 40),
                             [(x, 0), (x + band_w, 0), (x + band_w - 40, height), (x - 40, height)])
        x += band_w + gap
    return surf


WIND_OVERLAY = make_wind_overlay(HEIGHT - UI_BAR_HEIGHT)  # only sweep over the farm view, not the UI bar
WIND_GUST_INTERVAL = 8.0
WIND_GUST_DURATION = 1.6
wind_gust_timer = 0.0
wind_gust_active = False
wind_gust_progress = 0.0
wind_gust_x = 0.0

#Rain
RAIN_INTERVAL = 20.0
RAIN_DURATION = 6.0
rain_timer = 0.0
raining = False
rain_drops = []

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
    4: {"reward": [], "achievement": "Garden Helper"},
    5: {"reward": ["Unlock Tomato Seeds"], "achievement": "Tomato Tycoon"},
    6: {"reward": ["Unlock Axe"], "achievement": "Woodcutter"},
    7: {"reward": ["Carrot XP Boost"], "achievement": "Carrot Master"},
    8: {"reward": ["Unlock Cow"], "achievement": "Livestock Lover"},
    9: {"reward": ["Upgrade Pick Lvl3", "Upgrade Hoe Lvl2"], "achievement": "Ultimate Tool User"},
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

#Zoom / View
zoom = 1.2  # start slightly zoomed in for a closer camera, without excessive upscale blur
tile_draw_size = int(TILE_SIZE * zoom)
view_width, view_height = 10, 10  # Initial view

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

            prompt = render_text(subtitle_font, "Left/Right to choose, Space to confirm, Esc to go back", TEXT_CREAM)
            screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, row_y + portrait_size + 45))

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
    elif reward == "Unlock Axe":
        if not axe_tool:
            axe_tool = {"name": "Axe", "level": 1, "color": (139, 69, 19)}
            unlocked_tools.append(axe_tool)
    elif reward == "Unlock Pumpkin Seeds":
        SEEDS["pumpkin"] = {"name": "Pumpkin", "color": (255, 100, 0), "grow_time": 60.0, "xp": 10, "wither_time": 40.0}
        seed_inventory["pumpkin"] = 5
    elif reward == "Unlock Tomato Seeds":
        SEEDS["tomato"] = {"name": "Tomato", "color": (255, 50, 50), "grow_time": 4.0, "xp": 1.2, "wither_time": 8.0}
        seed_inventory["tomato"] = 5
    elif reward == "Carrot XP Boost":
        SEEDS["carrot"]["xp"] *= 2
    elif reward == "Unlock Cow":
        pass


        #(no sun flower art yet)
    elif reward == "Unlock Sunflower Seeds":
        SEEDS["sunflower"] = {"name": "Sunflower", "color": (255, 255, 0), "grow_time": 5.0, "xp": 2.0, "wither_time": 12.0}
        seed_inventory["sunflower"] = 5
    elif reward == "Skip":
        pass


#tree spawn (not in demo yet)

def spawn_tree():
    empty_tiles = [(x, y) for y in range(WORLD_H) for x in range(WORLD_W)
                   if farm[y][x]["state"] == "grass" and (x, y) not in FARM_BLOCKED_TILES
                   and (x, y) != (player_x, player_y)]
    if empty_tiles:
        x, y = random.choice(empty_tiles)
        farm[y][x]["state"] = "tree"

#Camera based on level 
def update_camera_view():
    global view_width, view_height
    # 10 + (level-1)*2, max WORLD size
    view_width = min(10 + (level-1)*2, WORLD_W)
    view_height = min(10 + (level-1)*2, WORLD_H)
    cam_x = max(0, min(player_x - view_width//2, WORLD_W - view_width))
    cam_y = max(0, min(player_y - view_height//2, WORLD_H - view_height))
    return cam_x, cam_y

#Movement: handles farm/house bounds, house walls, and door enter/exit
def try_move(dx, dy):
    global player_x, player_y, interior_player_x, interior_player_y, location

    if location == "farm":
        nx = max(0, min(WORLD_W - 1, player_x + dx))
        ny = max(0, min(WORLD_H - 1, player_y + dy))
        if (nx, ny) in HOUSE_TILES:
            return False  # solid house wall

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
        return moved

#Main Game Loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    # (rain gui not added in demo)
    rain_timer += dt
    tree_timer += dt
    day_timer = (day_timer + dt) % DAY_LENGTH
    tile_draw_size = int(TILE_SIZE * zoom)

    #Wind gust timing
    if wind_gust_active:
        wind_gust_progress += dt / WIND_GUST_DURATION
        if wind_gust_progress >= 1.0:
            wind_gust_active = False
        else:
            wind_gust_x = -220 + wind_gust_progress * (WIDTH + 440)
    else:
        wind_gust_timer += dt
        if wind_gust_timer >= WIND_GUST_INTERVAL:
            wind_gust_timer = 0.0
            wind_gust_active = True
            wind_gust_progress = 0.0

    if haste:
        haste_timer += dt
        if haste_timer >= HASTE_DURATION:
            haste = False
            haste_timer = 0.0

    #Tree spawn 
    if axe_tool and tree_timer >= TREE_INTERVAL:
        spawn_tree()
        tree_timer = 0.0

    #Level-Up Screen 
    if level_up_pending:
        screen.fill((50, 50, 50))
        title = render_text(font, level_up_message, TEXT_GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))

        prompt = render_text(font, "Choose your reward:", TEXT_CREAM)
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 20))

        option_1 = render_text(font, f"1: {reward_options[0]}", (196, 214, 255))
        option_2 = render_text(font, f"2: {reward_options[1]}", (196, 214, 255))
        screen.blit(option_1, (WIDTH//2 - option_1.get_width()//2, HEIGHT//2 + 20))
        screen.blit(option_2, (WIDTH//2 - option_2.get_width()//2, HEIGHT//2 + 50))

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
            # Movement
            if event.key in (pygame.K_LEFT, pygame.K_a):
                player_facing = "left"
                player_is_walking = try_move(-1, 0)
                player_walk_timer = 0.0
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                player_facing = "right"
                player_is_walking = try_move(1, 0)
                player_walk_timer = 0.0
            if event.key in (pygame.K_UP, pygame.K_w):
                player_facing = "up"
                player_is_walking = try_move(0, -1)
                player_walk_timer = 0.0
            if event.key in (pygame.K_DOWN, pygame.K_s):
                player_facing = "down"
                player_is_walking = try_move(0, 1)
                player_walk_timer = 0.0

            # Seed selection
            seed_list = list(SEEDS.keys())
            for idx, key in enumerate(SEED_KEYS):
                if event.key == key and idx < len(seed_list):
                    selected_seed = seed_list[idx]

            # Inventory toggle only if not level-up
            if event.key == pygame.K_q and not level_up_pending:
                inventory_open = not inventory_open

            # Switch tool
            if event.key == pygame.K_z and len(unlocked_tools) > 1:
                idx = unlocked_tools.index(equipped_tool)
                idx = (idx + 1) % len(unlocked_tools)
                equipped_tool = unlocked_tools[idx]

            # Sleeping in the house bed
            if not inventory_open and not level_up_pending and location == "house":
                if event.key == pygame.K_e and (interior_player_x, interior_player_y) == INTERIOR_BED:
                    day += 1
                    day_timer = 0.0
                    for row in farm:
                        for t in row:
                            if t["state"] in ("planted", "sprout", "growing", "grown"): t["timer"] += 2.0
                    for s in seed_inventory: seed_inventory[s] += 5
                    day_popup_queue.append({"text": f"Day {day}", "timer": 0.0})

            # Entering the house (must be standing on the doorway and press E)
            if not inventory_open and not level_up_pending and location == "farm":
                if event.key == pygame.K_e and (player_x, player_y) in DOOR_TILES:
                    location = "house"
                    interior_player_x, interior_player_y = INTERIOR_DOOR[0], INTERIOR_DOOR[1] - 1

            # Tile actions only if inventory closed and outdoors
            if not inventory_open and not level_up_pending and location == "farm":
                tile = farm[player_y][player_x]

                # Plant
                if event.key == pygame.K_SPACE and selected_seed in seed_inventory:
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


                        #tomato haste ability 
                        if harvested_seed=="tomato":
                            haste=True
                            haste_timer=0.0


                        #Hoe ability
                        if equipped_tool==hoe_tool and seed_inventory.get(harvested_seed,0)>0:
                            tile["state"]="planted"
                            tile["timer"]=0.0
                            tile["seed"]=harvested_seed
                            tile["soil_variant"]=random.randrange(len(SOIL_IMAGES))
                            tile["stage_anim"]=0.0
                            seed_inventory[harvested_seed]-=1
                        else:
                            tile["state"]="grass"
                            tile["timer"]=0.0
                            tile["seed"]=None
                            tile["soil_variant"]=None


                        #levil up logic via xp 
                        if xp>=xp_needed:
                            level+=1
                            xp=0
                            xp_needed+=10
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

    #Growth update: planted -> sprout -> growing -> grown -> withered
    for row in farm:
        for tile in row:
            state = tile["state"]
            if state == "grass":
                continue

            tile["stage_anim"] += dt

            if state in ("planted", "sprout", "growing", "grown"):
                tile["timer"] += dt
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

    # Draw scene
    screen.fill((50,50,50))
    farm_view_rect = pygame.Rect(0, 0, WIDTH, HEIGHT - UI_BAR_HEIGHT)
    screen.set_clip(farm_view_rect)

    if location == "farm":
        #Camera
        cam_x, cam_y = update_camera_view()

        for y in range(WORLD_H):
            for x in range(WORLD_W):
                draw_x = (x - cam_x) * tile_draw_size
                draw_y = (y - cam_y) * tile_draw_size
                tile = farm[y][x]

             # --- Ground (grass is always the base layer) ---
                ground_scaled = pygame.transform.scale(tile["ground"], (tile_draw_size, tile_draw_size))
                screen.blit(ground_scaled, (draw_x, draw_y))

                if tile["state"] == "grass":
                    if tile["decor"] is not None:
                        decor_scaled = pygame.transform.scale(tile["decor"], (tile_draw_size, tile_draw_size))
                        screen.blit(decor_scaled, (draw_x, draw_y))
                elif tile["soil_variant"] is not None:
                    # --- Tilled soil patch ---
                    soil_img = SOIL_IMAGES[tile["soil_variant"]]
                    soil_scaled = pygame.transform.scale(soil_img, (tile_draw_size, tile_draw_size))
                    screen.blit(soil_scaled, (draw_x, draw_y))

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
                        sway = math.sin(pygame.time.get_ticks() * 0.002 + (x * 13 + y * 7)) * (tile_draw_size * 0.045)

                    offset_x = draw_x + (tile_draw_size - size) // 2 + sway
                    offset_y = draw_y + (tile_draw_size - size)
                    screen.blit(crop_scaled, (offset_x, offset_y))

        # --- House exterior: sprite is 2 tiles tall, anchored so its bottom
        # edge sits on the bottom of its 1-tile solid footprint (the roof
        # and chimney overhang into the tile row above) ---
        house_draw_x = (HOUSE_POS[0] - cam_x) * tile_draw_size
        house_draw_y = (HOUSE_POS[1] - cam_y) * tile_draw_size - tile_draw_size
        house_scaled = pygame.transform.scale(IMG_HOUSE, (tile_draw_size * 2, tile_draw_size * 2))
        screen.blit(house_scaled, (house_draw_x, house_draw_y))

        #Wind gust sweeping across the field
        if wind_gust_active:
            screen.blit(WIND_OVERLAY, (int(wind_gust_x), 0))

        draw_size = tile_draw_size
        px = (player_x - cam_x) * tile_draw_size
        py = (player_y - cam_y) * tile_draw_size
        show_enter_prompt = (player_x, player_y) in DOOR_TILES

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
        show_enter_prompt = False

    #Player (shared by both scenes)
    player_sprite = PLAYER_FRAMES[player_facing][player_frame_index]
    player_scaled = pygame.transform.scale(player_sprite, (draw_size, draw_size))
    screen.blit(player_scaled, (px, py))
    pygame.draw.rect(screen,equipped_tool["color"],(px+5,py-10,20,5))
    screen.blit(render_text(font, f"{equipped_tool['name']} Lvl {equipped_tool['level']}", TEXT_CREAM),(px-5,py-25))

    if show_enter_prompt:
        prompt_surf = render_text(ui_font, "Press E to enter", TEXT_GOLD)
        screen.blit(prompt_surf, (px + draw_size // 2 - prompt_surf.get_width() // 2, py - 46))

    #Vignette: fade the edges of the game view (not the UI bar below it)
    screen.blit(VIGNETTE, (0, 0))
    screen.set_clip(None)

    #UI bar background panel
    BAR_TOP = HEIGHT - UI_BAR_HEIGHT
    pygame.draw.rect(screen, (35, 30, 28), (0, BAR_TOP, WIDTH, UI_BAR_HEIGHT))
    ROW1_Y = BAR_TOP + 10

    #Clock + Day
    draw_clock(screen, (34, ROW1_Y + 24), 22, day_timer / DAY_LENGTH)
    screen.blit(render_text(ui_font, f"Day {day}", TEXT_CREAM), (64, ROW1_Y + 14))

    #Level / XP bar
    screen.blit(render_text(ui_font, f"Lvl {level}  {xp:.1f}/{xp_needed} XP", TEXT_CREAM), (150, ROW1_Y))
    xp_bar_rect = pygame.Rect(150, ROW1_Y + 28, 190, 16)
    draw_bar(screen, xp_bar_rect, xp / xp_needed if xp_needed else 0, TEXT_GOLD)

    #Equipped tool
    tool_icon_rect = pygame.Rect(356, ROW1_Y + 14, 20, 20)
    pygame.draw.rect(screen, equipped_tool["color"], tool_icon_rect)
    pygame.draw.rect(screen, TEXT_CREAM, tool_icon_rect, 2)
    screen.blit(render_text(tool_font, f"{equipped_tool['name']} L{equipped_tool['level']}", TEXT_CREAM),
                (tool_icon_rect.right + 6, ROW1_Y + 15))

    #Inventory strip
    ROW2_Y = ROW1_Y + 52
    icon_size = 28
    slot_w = 78
    for i, seed_key in enumerate(seed_inventory):
        slot_x = 12 + i * slot_w
        highlight = seed_key == selected_seed
        icon_img = CROP_IMAGES.get(seed_key)
        if icon_img is not None:
            screen.blit(pygame.transform.scale(icon_img, (icon_size, icon_size)), (slot_x, ROW2_Y))
        else:
            pygame.draw.rect(screen, SEEDS[seed_key]["color"], (slot_x, ROW2_Y + 4, icon_size, icon_size - 8))

        count_color = TEXT_GOLD if highlight else TEXT_CREAM
        screen.blit(render_text(ui_font, f"x{seed_inventory[seed_key]}", count_color),
                    (slot_x + icon_size + 4, ROW2_Y + 3))
        if highlight:
            pygame.draw.rect(screen, TEXT_GOLD, (slot_x - 3, ROW2_Y - 3, icon_size + 6, icon_size + 6), 2)



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

    #Achievement Popups
    y_offset=10
    for popup in achievement_queue[:]:
        popup["timer"]+=dt
        alpha=255
        if popup["timer"]>ACHIEVEMENT_DISPLAY_TIME-0.5: alpha=int(255*(ACHIEVEMENT_DISPLAY_TIME-popup["timer"])/0.5)
        text_surf=render_text(font, popup["text"], TEXT_GOLD)
        text_surf.set_alpha(alpha)
        screen.blit(text_surf,(WIDTH//2-text_surf.get_width()//2,y_offset))
        y_offset+=30

        #remove it if it exceeds achivment display time 
        if popup["timer"]>ACHIEVEMENT_DISPLAY_TIME: achievement_queue.remove(popup)

    #Level-Up Popups
    y_offset=50
    for popup in level_popup_queue[:]:
        popup["timer"]+=dt
        text_surf=render_text(font, popup["text"], TEXT_CREAM)
        screen.blit(text_surf,(WIDTH//2-text_surf.get_width()//2,y_offset))
        y_offset+=30
        if popup["timer"]>LEVEL_POPUP_TIME: level_popup_queue.remove(popup)

    #Day Popups
    y_offset=80
    for popup in day_popup_queue[:]:
        popup["timer"]+=dt
        alpha=255
        if popup["timer"]>DAY_POPUP_TIME-0.5: alpha=int(255*(DAY_POPUP_TIME-popup["timer"])/0.5)
        text_surf=render_text(font, popup["text"], TEXT_CREAM)
        text_surf.set_alpha(alpha)
        screen.blit(text_surf,(WIDTH//2-text_surf.get_width()//2,y_offset))
        if popup["timer"]>DAY_POPUP_TIME: day_popup_queue.remove(popup)

    pygame.display.flip()

pygame.quit()



