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
SOIL_IMG = load_image("soil.png")
IMG_CARROT = load_image("Carrot.png")
IMG_GROUND1 = load_image("Ground1.png")
IMG_GROUND2 = load_image("Ground2.png")
IMG_GROUND3 = load_image("Ground3.png")
IMG_GROUND4 = load_image("Ground4.png")
IMG_BED = load_image("Bed.png")
GROUND_IMAGES = [IMG_GROUND1, IMG_GROUND2, IMG_GROUND3, IMG_GROUND4]







clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
ui_font = pygame.font.SysFont(None, 28)  # smaller font for in-game UI

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
SEEDS = {
    "corn": {"name": "Corn", "color": (230, 220, 40), "grow_time": 5.0, "xp": 0.5},
    "carrot": {"name": "Carrot", "color": (255, 140, 40), "grow_time": 3.0, "xp": 1.0}
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
            "ground": random.choice(GROUND_IMAGES)
        }
        for x in range(WORLD_W)
    ]
    for y in range(WORLD_H)
]

BED_POS = (0, 0)

#Player
player_x, player_y = 1, 1
harvested = 0
day = 1
xp = 0.0
level = 1
xp_needed = 10

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
zoom = 1.0
tile_draw_size = int(TILE_SIZE * zoom)
view_width, view_height = 10, 10  # Initial view

def start_screen():
    start = True
    selected_option = 0
    options = ["Start Game", "Instructions", "Quit"]
    show_instructions = False
    blink_timer = 0.0
    blink_on = True

    # Mini farm preview
    preview_w, preview_h = 10, 10
    preview_farm = [[{"state": "grass", "timer": 0.0, "seed": None} for x in range(preview_w)] for y in range(preview_h)]
    preview_seeds = ["corn", "carrot"]

    while start:
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

                #movment 
            elif event.type == pygame.KEYDOWN:
                if show_instructions:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                        show_instructions = False
                else:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_SPACE:
                        if selected_option == 0:
                            start = False
                        elif selected_option == 1:
                            show_instructions = True
                        elif selected_option == 2:
                            pygame.quit()
                            exit()

            #choose with scroll wheel 
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    selected_option = (selected_option - 1) % len(options)
                elif event.y < 0:
                    selected_option = (selected_option + 1) % len(options)

        #Update preview farm 
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
        title_font = pygame.font.SysFont(None, 48)
        subtitle_font = pygame.font.SysFont(None, 22)

        title = title_font.render("Arborio", True, (255,255,0))
        subtitle = subtitle_font.render("The Tile Farm Game", True, (255,255,0))

        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 70))


        #Draw menu 
        if show_instructions:
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
                text_surf = font.render(line, True, (255,255,255))
                screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//4 + i*30))
        else:
            for i, option in enumerate(options):
                color = (255,255,255)
                text_surf = font.render(option, True, color)
                x_pos = WIDTH//2 - text_surf.get_width()//2
                y_pos = HEIGHT//2 + i*40
                screen.blit(text_surf, (x_pos, y_pos))

                # Blinking retro highlight
                if i == selected_option and blink_on:
                    highlight_rect = pygame.Rect(x_pos-5, y_pos-5, text_surf.get_width()+10, text_surf.get_height()+10)
                    pygame.draw.rect(screen, (255,255,100), highlight_rect, 2)

        pygame.display.flip()





#Run Main Menu 
start_screen()

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
        SEEDS["pumpkin"] = {"name": "Pumpkin", "color": (255, 100, 0), "grow_time": 60.0, "xp": 10}
        seed_inventory["pumpkin"] = 5
    elif reward == "Unlock Tomato Seeds":
        SEEDS["tomato"] = {"name": "Tomato", "color": (255, 50, 50), "grow_time": 4.0, "xp": 1.2}
        seed_inventory["tomato"] = 5
    elif reward == "Carrot XP Boost":
        SEEDS["carrot"]["xp"] *= 2
    elif reward == "Unlock Cow":
        pass


        #(no sun flower art yet)
    elif reward == "Unlock Sunflower Seeds":
        SEEDS["sunflower"] = {"name": "Sunflower", "color": (255, 255, 0), "grow_time": 5.0, "xp": 2.0}
        seed_inventory["sunflower"] = 5
    elif reward == "Skip":
        pass


#tree spawn (not in demo yet)

def spawn_tree():
    empty_tiles = [(x, y) for y in range(WORLD_H) for x in range(WORLD_W)
                   if farm[y][x]["state"] == "grass" and (x, y) != BED_POS
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

#Main Game Loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    # (rain gui not added in demo)
    rain_timer += dt
    tree_timer += dt
    tile_draw_size = int(TILE_SIZE * zoom)

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
        title = font.render(level_up_message, True, (255, 255, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))

        prompt = font.render("Choose your reward:", True, (255, 255, 255))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 20))

        option_1 = font.render(f"1: {reward_options[0]}", True, (200, 200, 255))
        option_2 = font.render(f"2: {reward_options[1]}", True, (200, 200, 255))
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
                player_x = max(0, player_x - 1)
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                player_x = min(WORLD_W - 1, player_x + 1)
            if event.key in (pygame.K_UP, pygame.K_w):
                player_y = max(0, player_y - 1)
            if event.key in (pygame.K_DOWN, pygame.K_s):
                player_y = min(WORLD_H - 1, player_y + 1)

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

            # Tile actions only if inventory closed
            if not inventory_open and not level_up_pending:
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

                                if t["state"]=="grass" and (nx,ny)!=BED_POS:
                                    positions_to_plant.append((nx,ny))

                                    if len(positions_to_plant)>=3: break



                    for px,py in positions_to_plant:
                        t = farm[py][px]
                        if t["state"]=="grass" and seed_inventory[selected_seed]>0:
                            t["state"]="planted"
                            t["timer"]=0.0
                            t["seed"]=selected_seed
                            t["img"] = SOIL_IMG  # ← assign soil image
                            seed_inventory[selected_seed]-=1


                # Harvest / Sleep
                if event.key == pygame.K_e:
                    if (player_x,player_y)==BED_POS:
                        day+=1
                        for row in farm:
                            for t in row:
                                if t["state"] in ("planted","sprout"): t["timer"]+=2.0
                        for s in seed_inventory: seed_inventory[s]+=5
                        day_popup_queue.append({"text":f"Day {day}","timer":0.0})


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
                            seed_inventory[harvested_seed]-=1
                        else:
                            tile["state"]="grass"
                            tile["timer"]=0.0
                            tile["seed"]=None


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

    #Growth update
    for row in farm:
        for tile in row:
            if tile["state"] in ("planted","sprout"):
                tile["timer"]+=dt
                seed=SEEDS[tile["seed"]]
                if tile["timer"]>=seed["grow_time"]*0.5 and tile["state"]=="planted": tile["state"]="sprout"
                if tile["timer"]>=seed["grow_time"]: tile["state"]="grown"

    #Camera
    cam_x, cam_y = update_camera_view()

    # Draw farm
    screen.fill((50,50,50))

    for y in range(WORLD_H):
        for x in range(WORLD_W):
            draw_x = (x - cam_x) * tile_draw_size
            draw_y = (y - cam_y) * tile_draw_size
            rect = pygame.Rect(draw_x, draw_y, tile_draw_size, tile_draw_size)
            tile = farm[y][x]

         # --- Ground / Soil ---
            if tile["state"] in ("planted", "sprout", "grown") and "img" in tile:
                soil_scaled = pygame.transform.scale(tile["img"], (tile_draw_size, tile_draw_size))
                screen.blit(soil_scaled, (draw_x, draw_y))
            else:
                ground_img = tile["ground"]
                ground_scaled = pygame.transform.scale(ground_img, (tile_draw_size, tile_draw_size))
                screen.blit(ground_scaled, (draw_x, draw_y))

            # --- Bed ---
            if (x, y) == BED_POS:
                bed_scaled = pygame.transform.scale(IMG_BED, (tile_draw_size, tile_draw_size))
                screen.blit(bed_scaled, (draw_x, draw_y))


            # --- Crops ---
            if tile["state"] == "grown":
                seed = tile["seed"]

                if seed == "corn":
                    img = IMG_CORN
                elif seed == "tomato":
                    img = IMG_TOMATO
                elif seed == "pumpkin":
                    img = IMG_PUMPKIN
                elif seed == "carrot":
                    img = IMG_CARROT

                else:
                    img = None

                if img:
                    crop_scaled = pygame.transform.scale(img, (tile_draw_size, tile_draw_size))
                    screen.blit(crop_scaled, (draw_x, draw_y))

        # Optional grid border
        pygame.draw.rect(screen, (0,0,0), rect, 1)

    #Player
    px=(player_x-cam_x)*tile_draw_size
    py=(player_y-cam_y)*tile_draw_size
    pygame.draw.rect(screen,COLORS["player"],(px,py,int(tile_draw_size*0.6),int(tile_draw_size*0.6)))
    pygame.draw.rect(screen,equipped_tool["color"],(px+5,py-10,20,5))
    screen.blit(font.render(f"{equipped_tool['name']} Lvl {equipped_tool['level']}",True,(255,255,255)),(px-5,py-25))

    #UI
    ui_y = HEIGHT - 28
    ui_text = f"Day {day} | Harvested: {harvested} | XP: {xp:.1f}/{xp_needed} | Lvl {level} | Seed: {SEEDS[selected_seed]['name']}"
    screen.blit(ui_font.render(ui_text, True, (255,255,255)), (10, ui_y))



    #Inventory
    if inventory_open:
        overlay = pygame.Surface((300,200))
        overlay.set_alpha(220)
        overlay.fill((30,30,30))
        screen.blit(overlay,(WIDTH//2-150,HEIGHT//2-100))
        screen.blit(font.render("Inventory",True,(255,255,255)),(WIDTH//2-50,HEIGHT//2-80))
        y_offset=0
        for seed in SEEDS:
            screen.blit(font.render(f"{SEEDS[seed]['name']}: {seed_inventory[seed]}",True,SEEDS[seed]["color"]),(WIDTH//2-120,HEIGHT//2-50+y_offset))
            y_offset+=30
        screen.blit(font.render(f"Equipped Tool: {equipped_tool['name']} Lvl {equipped_tool['level']}",True,equipped_tool["color"]),(WIDTH//2-120,HEIGHT//2+50))

    #Achievement Popups
    y_offset=10
    for popup in achievement_queue[:]:
        popup["timer"]+=dt
        alpha=255
        if popup["timer"]>ACHIEVEMENT_DISPLAY_TIME-0.5: alpha=int(255*(ACHIEVEMENT_DISPLAY_TIME-popup["timer"])/0.5)
        text_surf=font.render(popup["text"],True,(255,215,0))
        text_surf.set_alpha(alpha)
        screen.blit(text_surf,(WIDTH//2-text_surf.get_width()//2,y_offset))
        y_offset+=30

        #remove it if it exceeds achivment display time 
        if popup["timer"]>ACHIEVEMENT_DISPLAY_TIME: achievement_queue.remove(popup)

    #Level-Up Popups
    y_offset=50
    for popup in level_popup_queue[:]:
        popup["timer"]+=dt
        text_surf=font.render(popup["text"],True,(255,255,255))
        screen.blit(text_surf,(WIDTH//2-text_surf.get_width()//2,y_offset))
        y_offset+=30
        if popup["timer"]>LEVEL_POPUP_TIME: level_popup_queue.remove(popup)

    #Day Popups
    y_offset=80
    for popup in day_popup_queue[:]:
        popup["timer"]+=dt
        alpha=255
        if popup["timer"]>DAY_POPUP_TIME-0.5: alpha=int(255*(DAY_POPUP_TIME-popup["timer"])/0.5)
        text_surf=font.render(popup["text"],True,(255,255,255))
        text_surf.set_alpha(alpha)
        screen.blit(text_surf,(WIDTH//2-text_surf.get_width()//2,y_offset))
        if popup["timer"]>DAY_POPUP_TIME: day_popup_queue.remove(popup)

    pygame.display.flip()

pygame.quit()



