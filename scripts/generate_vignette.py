"""Generates FarmImg/Vignette.png: a soft dark fade toward the edges of
the farm viewport (500x500, matching farm.py's WIDTH x (HEIGHT-UI_BAR_HEIGHT)).
Blitted once per frame over the game world so the view reads like it's
framed, with the center left fully clear. Re-run to retune the falloff.
"""
import os

from PIL import Image

VIEWPORT_W = 500
VIEWPORT_H = 500
RAMP_START = 175   # gradient values (0=center, 255=corner) below this stay fully transparent
MAX_ALPHA = 80     # darkest alpha reached at the far corners

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "FarmImg")


def make_vignette():
    # radial_gradient is 0 at the center, 255 at the corners
    grad = Image.radial_gradient("L").resize((VIEWPORT_W, VIEWPORT_H))
    span = 255 - RAMP_START

    def alpha_fn(v):
        dark = max(0, v - RAMP_START)
        return int(min(MAX_ALPHA, dark / span * MAX_ALPHA))

    alpha = grad.point(alpha_fn)
    black = Image.new("RGB", (VIEWPORT_W, VIEWPORT_H), (0, 0, 0))
    vignette = Image.merge("RGBA", (*black.split(), alpha))
    return vignette


def main():
    vignette = make_vignette()
    path = os.path.join(OUT_DIR, "Vignette.png")
    vignette.save(path)
    print(f"wrote {path} ({vignette.size[0]}x{vignette.size[1]})")


if __name__ == "__main__":
    main()
