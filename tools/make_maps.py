"""Draws the map pictures in assets/map/ from the land-use map of Statistics Netherlands (CBS
Bestand Bodemgebruik 2022, 100 metre grid, most common class per cell, as prepared for RSopen).

    python tools/make_maps.py <path to BBG2022_100m_Modus_Nederland.tif>

Only needed to change the pictures; the results are committed, so a build does not need the data.
The class numbers were read off the map at known places (Schiphol, Vondelpark, Amsterdamse Bos),
so a colour here is a drawing decision and not a statement about a class.
"""
import collections
import os
import sys

from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "map")
TOP_Y = 625000  # RD coordinate of the top of the raster; its left edge is RD x 0
SOURCE_CELL = 100

WATER = {0} | set(range(28, 41))
GROUPS = {
    "residential": {5}, "centre": {6, 7, 8}, "business": {3, 9}, "infrastructure": {1, 2}, "works": set(range(10, 16)),
    "green": set(range(16, 21)), "farmland": set(range(21, 25)), "nature": {25, 26, 27},
}
ON_BLUE = {"residential": "#FAF7F5", "centre": "#F6C9A4", "business": "#CC4100", "infrastructure": "#BFE0F2", "works": "#EE9F6C",
           "green": "#35B597", "farmland": "#148AC4", "nature": "#00866E"}
ON_LIGHT = {"residential": "#0077B3", "centre": "#005A87", "business": "#CC4100", "infrastructure": "#8CC7E6", "works": "#EE9F6C",
            "green": "#A5D9C4", "farmland": "#D3E7F2", "nature": "#74C2A2"}

# picture name, left and bottom RD coordinate, map metres per cell, columns, rows
HERO = ("hero", 62000, 474000, 400, 160, 65)
CROPS = [
    ("land-use-modelling", 76000, 438000, 800, 66, 12),   # the Randstad
    ("spatial-planning", 134000, 470000, 300, 66, 12),    # Almere and Het Gooi
    ("climate-adaptation", 96000, 412000, 800, 66, 12),   # the rivers
    ("location-value", 112000, 481000, 200, 66, 12),      # Amsterdam
    ("accessibility", 128000, 451000, 300, 66, 12),       # Utrecht
    ("geodesign", 66000, 433000, 300, 66, 12),            # the port of Rotterdam
]


def group_of(code):
    for name, codes in GROUPS.items():
        if code in codes:
            return name
    return None


def draw(raster, name, left, bottom, metres, cols, rows, palette, pixels, gap):
    step = metres // SOURCE_CELL
    top_row = (TOP_Y - bottom) // SOURCE_CELL - rows * step
    picture = Image.new("RGBA", (cols * pixels, rows * pixels), (0, 0, 0, 0))
    pen = ImageDraw.Draw(picture)
    for row in range(rows):
        for col in range(cols):
            x = left // SOURCE_CELL + col * step
            y = top_row + row * step
            block = raster.crop((x, y, x + step, y + step)).tobytes()
            code = collections.Counter(block).most_common(1)[0][0]
            group = None if code in WATER else group_of(code)
            if group:
                pen.rectangle((col * pixels, row * pixels, (col + 1) * pixels - 1 - gap, (row + 1) * pixels - 1 - gap), fill=palette[group])
    path = os.path.join(OUT, name + ".png")
    picture.quantize(colors=16, method=Image.Quantize.FASTOCTREE).save(path, optimize=True)
    print(name, picture.size, round(os.path.getsize(path) / 1000), "kB")


def main():
    Image.MAX_IMAGE_PIXELS = None
    raster = Image.open(sys.argv[1])
    raster.load()
    os.makedirs(OUT, exist_ok=True)
    draw(raster, *HERO, ON_BLUE, 8, 1)
    for crop in CROPS:
        draw(raster, *crop, ON_LIGHT, 6, 1)


if __name__ == "__main__":
    main()
