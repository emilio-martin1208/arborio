# Arborio

A tile-based farming RPG built with [pygame](https://www.pygame.org/) — grow crops, raise a farm, trade in a full marketplace economy, explore a huge procedurally-biomed overworld on foot or horseback, and descend through hidden desert ruins into a dangerous underworld to fight demons and slowly purify the land above. All art is hand-generated pixel art (see `scripts/`), and the whole world is procedurally laid out at each new game start.

## Table of contents

- [Running it](#running-it)
- [Controls](#controls)
- [Character select](#character-select)
- [The world & biomes](#the-world--biomes)
- [Farming](#farming)
- [Leveling up](#leveling-up)
- [Tools & combat](#tools--combat)
- [The marketplace economy](#the-marketplace-economy)
- [Villages](#villages)
- [Horses](#horses)
- [Lakes & ponds](#lakes--ponds)
- [Weather & seasons](#weather--seasons)
- [The world map](#the-world-map)
- [The crop journal](#the-crop-journal)
- [The underworld](#the-underworld)
- [NPCs & dialogue](#npcs--dialogue)
- [Project structure](#project-structure)
- [Status & roadmap](#status--roadmap)

## Running it

```bash
pip install pygame
python3 farm.py
```

The game window is resizable and scales the pixel art cleanly to whatever size you drag it to (`pygame.SCALED`), so it's safe to maximize.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys / WASD | Move (tap for one step, hold for continuous movement) |
| Space | Plant the selected seed |
| E | Context-sensitive interact: harvest a crop, chop a tree, swing your sword, talk to an NPC/villager, trade at a stall, rent/return a horse, enter a ruin, return from the underworld, sleep in bed |
| Q | Toggle inventory |
| Z | Switch equipped tool (cycles Pick → Hoe → Axe → Sword as each is unlocked) |
| R T Y U I O P | Quick-select the first 7 crops in your seed list |
| M | Open/close the world map (outdoors only) |
| X | Open/close the crop journal |
| Mouse wheel | Zoom in/out |
| Mouse drag | Reorder/select hotbar slots |
| Esc | Close whichever menu is open (map, journal, market, level-up) |

## Character select

At the title screen you choose one of four farmers to play as, each with their own pixel-art portrait, palette, and a short bio shown on the select screen:

| Character | Bio |
| --- | --- |
| **Hank** | A steady hand who's worked this land his whole life — patient, practical, and up before sunrise. |
| **Jeff** | A restless wanderer who took up farming to slow down, though he still can't sit still for long. |
| **Martha** | Sharp-tongued and sharper-minded, she treats every harvest like a puzzle worth solving. |
| **Marin** | Quiet and observant, with a well-worn atlas in her pack and a soft spot for anything wild and growing. |

Whichever three you *don't* pick become schedule-driven NPCs living in the world — see [NPCs & dialogue](#npcs--dialogue).

## The world & biomes

The overworld is a **200×200 tile** map generated fresh each run with 2D value noise (not simple randomness, so features form real, explorable regions instead of scattered noise). It's split into five biomes, each with its own ground textures, tree species, and animals:

| Biome | Ground | Trees | Notes |
| --- | --- | --- | --- |
| Meadow | Green grass, several color variants | Oak, tall oak, pine, bushy, sapling | Always surrounds your starting farmhouse (safe-radius guarantee) |
| Maple forest | Warm grass tones | Mostly maple, some oak | |
| Sakura grove | Pink-blossom ground accents | Sakura trees | |
| Jungle | Deep green, dense ground cover | Jungle trees, bushy | |
| Desert | Sand | Cactus only | The **only** biome where ancient ruins spawn |

Every ground tile is rendered oversized and overlapping its neighbors with an irregular alpha mask, so tile edges spill into each other — there are no hard grid squares anywhere in the world, water included. Grass tiles gently sway in per-tile-phased wind so gusts visibly roll across a field instead of every blade moving in lockstep.

## Farming

Plant a seed on any empty grass tile with **Space**, then watch it move through real animated growth stages — seedling → sprout → growing → ripe — before it can be harvested with **E**. Ripe crops that sit too long wither and die, so timing matters; different crops have very different wither windows.

18 crops exist in total. You start with Corn and Carrot; everything else is discovered through leveling up, marketplace trades, or the blacksmith/fisherman:

| Crop | Grow time | Wither grace | Value | How to unlock |
| --- | --- | --- | --- | --- |
| Corn | 5s | 10s | 2g | Available from the start |
| Carrot | 3s | 6s | 3g | Available from the start |
| Pumpkin | 60s | 40s | 20g | Reach level 3 |
| Tomato | 4s | 8s | 4g | Reach level 5 |
| Eggplant | 6s | 10s | 5g | Reach level 6 |
| Grape | 9s | 12s | 7g | Reach level 7 |
| Watermelon | 10s | 12s | 8g | Reach level 8 |
| Apple | 12s | 15s | 9g | Reach level 9 |
| Sunflower | 5s | 12s | 4g | Reach level 10 |
| Potato | 4s | 12s | 3g | Buy at a marketplace |
| Cabbage | 5s | 14s | 4g | Buy at a marketplace |
| Lettuce | 3.5s | 7s | 3g | Buy at a marketplace |
| Cucumber | 4.5s | 9s | 4g | Buy at a marketplace |
| Onion | 4s | 11s | 3g | Buy at a marketplace |
| Strawberry | 6s | 8s | 5g | Find at a marketplace |
| Blueberry | 7s | 8s | 6g | Find at a marketplace |
| Wheat | 5s | 20s | 2g | Trade with the fisherman |
| Chili | 5.5s | 9s | 5g | Trade with the blacksmith |

A level-2 Pick doubles both harvest yield and XP from harvesting. A Hoe instantly replants the same plot the moment you harvest it, if you have spare seed.

## Leveling up

XP earned from harvesting drives a level-up screen where you pick one of two rewards. The curve is quadratic (`xp_needed = 10 + level² × 8`), so it gets meaningfully harder as you climb:

| Level | Achievement | Reward |
| --- | --- | --- |
| 1 | Fresh Farmer | — |
| 2 | Level 2 Farmer | Pick → Lvl 2, unlock Hoe |
| 3 | Pumpkin Picker | Unlock Pumpkin |
| 4 | Garden Helper | Pick upgrade |
| 5 | Tomato Tycoon | Unlock Tomato |
| 6 | Woodcutter | Unlock Axe, unlock Eggplant |
| 7 | Vintner | Carrot XP boost, unlock Grape |
| 8 | Melon Master | Unlock Watermelon |
| 9 | Orchardist | Pick → Lvl 3, Hoe → Lvl 2, unlock Apple |
| 10 | Grand Farmer | Unlock Sunflower |

## Tools & combat

You start with a **Pick** (harvesting) and a **Sword** (combat) already equipped; the **Hoe** and **Axe** are unlocked via leveling or the blacksmith. Whatever tool is equipped is drawn *in the player's hand* and swings through a real arc animation whenever you use it — chopping, harvesting, and striking all trigger the same swing, just aimed at different targets.

The Sword is for fighting demons in the underworld (see below): press **E** while facing one to swing at it. Combat is deliberately simple in this pass — a flat hit per swing, a wind-up/recovery timing window, and a shared player HP pool (10 HP) that demons chip away at on contact. If your HP hits 0 you're automatically pulled back to the surface with half HP restored, rather than a hard game-over.

## The marketplace economy

Scattered across the map are two tiers of trading posts, each generated with a randomized set of buy/sell offers:

- **Outposts** — small, single-stall structures, 3 trades each, common (18 spawn per world).
- **Marketplaces** — larger, 2-tile-wide stalls with 5 trades plus tool offers, rarer (5 per world) and always anchor a full village around them.

Trade prices scale off each crop's own base value, with some randomized haggle-room built in. Currency is **Emeralds**, shown in the HUD; you start with 15.

## Villages

Every marketplace is the seed of a real settlement, not just a lone stall:

- A **stable** (rent/return a horse)
- A **blacksmith** — tool upgrades (Axe, Hoe), Chili seeds, and Pick-sharpening upgrades, all for Emeralds
- A **fisherman's shack** — always placed next to water (a small pond is planted nearby if none exists), buys your surplus crops and sells Wheat/Cucumber/Blueberry
- A **well**, and often a **shrine**
- 8–14 wandering villagers with their own idle wander AI and a random greeting when you talk to them (**E**)

## Horses

Every stable has a horse available to rent for 8 Emeralds. While mounted you move twice as fast per step, the horse gallops with a real 3-frame animation synced to your own walk cycle, and you're visually seated on its back (not just standing next to it). Return the horse at any stable, not just the one you rented from.

## Lakes & ponds

Water bodies are stamped onto the map with an organic noise-perturbed fill (never a perfect circle or square), biased away from the bone-dry desert biome. There are 8 large lakes and 12 smaller ponds per world by default, plus any extra small ponds planted next to fisherman shacks that didn't already have water nearby. Water tiles animate with a slow 3-frame ripple and block movement — you can't walk into a lake.

## Weather & seasons

The in-game calendar cycles through **Spring → Summer → Fall → Winter**, 7 days per season, with a subtle color-tint overlay over the whole world so each season reads differently. Weather is periodic and season-aware: it's rain the rest of the year, but snow instead once Winter arrives — full animated raindrops/snowflakes, not just a timer.

## The world map

Press **M** outdoors to pull up a full map of the world (closed with **M** or **Esc**). It shows the biome layout at a glance plus color-coded markers for your house, every outpost/marketplace, stable, blacksmith, fisherman shack, shrine, ancient ruin (red until purified, teal after), NPC, and your own live position.

## The crop journal

Press **X** to open a compendium of all 18 crops. Discovered crops show in full color with their name and sale value; everything you haven't found yet renders as a dark silhouette with a hint on how to unlock it ("Reach level 8", "Trade with the fisherman", "Buy at a marketplace"), so it doubles as a checklist for what to chase next.

## The underworld

Hidden in the desert biome are **ancient ruins** — stone archways with a dark, rune-lit portal — leading down into a dangerous shared underworld.

- **Three zones**, each with distinct art: an **infernal forge** (lava-cracked stone, ember glow), **cursed catacombs** (bone-flecked stone, skull-and-crossbones waymarkers), and a **corrupted temple** (mossy, moss-lit stone). Zones are assigned with the same coarse noise technique as surface biomes, so each forms a real region rather than a scatter of tiles.
- **Demons** wander the underworld and will drift toward you if you get close. Strike them with your Sword (**E**); they hit back for contact damage.
- Defeated demons drop **Hellsteel**, a second currency shown in the HUD alongside Emeralds.
- Every ruin tracks its own kill count. Once enough demons tied to a specific ruin are defeated, a real patch of desert around *that ruin* on the surface purifies into lush meadow — visible on the world map (the ruin's marker turns from red to teal) and in the world itself.
- The tile you arrive on is also the return portal — stand on it (or face it) and press **E** to pop back to exactly the ruin you entered from. Dying does the same automatically.

Combat here is intentionally a first pass — a boss roster, a richer loot table, and more zones are natural next steps (see below).

## NPCs & dialogue

The three playable characters you didn't choose live in the world on individual day-length schedules (home → field → shop → home), each with a small rotating pool of tips relevant to wherever they currently are — talking to the same NPC again cycles to a new line instead of repeating. Ordinary villagers in each settlement wander locally around their home village and have a single random greeting.

## Project structure

```
farm.py                              # the whole game — world-gen, rendering, input, game loop
FarmImg/                             # every sprite/tile, generated (not hand-drawn in an editor)
scripts/
  generate_player_sprite.py          # playable characters + ambient villagers (shared rig)
  generate_ground_tiles.py           # animated grass variants per biome, imperfect tile edges
  generate_landscape_assets.py       # tree species, rocks, bushes, paths
  generate_animal_assets.py          # peaceful wandering animals
  generate_market_assets.py          # outposts, marketplaces, Emerald icon
  generate_stable_assets.py          # stable building + animated horse
  generate_village_buildings.py      # wells, shrines
  generate_water_and_buildings.py    # water tiles, blacksmith, fisherman shack, fish icon, sword
  generate_more_crops.py             # the 14 non-starter crop icons
  generate_biome_decor.py            # per-biome decorative props
  generate_underworld_assets.py      # ruin entrance, portal, 3 underworld zones, demon, Hellsteel
  generate_tool_assets.py            # held-tool sprites (Pick/Hoe/Axe/Sword) for the swing animation
  generate_crop_stages.py            # generic seedling/sprout/growing/withered stage art
  generate_soil_tiles.py             # tilled-soil plot variants
  generate_vignette.py               # screen-edge vignette overlay
```

Every asset is drawn at a higher internal resolution (`SCALE`) with [Pillow](https://pillow.readthedocs.io/) and downsampled with nearest-neighbor filtering, so edges stay crisp instead of blurring like a naive resize would produce. Re-run any script directly to regenerate/tweak its art.

## Status & roadmap

Actively in development. Currently working, all in one continuously-running world:

- Character select, biomes, weather, seasons
- Full crop/tool/leveling loop with 18 crops
- Marketplace economy, villages, blacksmith, fisherman, horses, water
- World map, crop journal
- A first pass at the underworld: ruins, 3 zones, demons, sword combat, Hellsteel, per-ruin purification

Natural next steps: a richer underworld (boss fights, a real loot table, more zones), save/load support, more animal variety, and further combat depth (multiple weapon types, blocking/dodging).
