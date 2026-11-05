"""Draws the map pictures in assets/map/ from Dutch open data, as prepared for RSopen: the land-use map
of Statistics Netherlands (CBS Bestand Bodemgebruik 2022), dwellings from the BAG and the protected
nature network (NNN).

    python tools/make_maps.py <folder with the BaseData of an RSopen project>

Only needed to change the pictures; the results are committed, so a build does not need the data or
these packages. The class numbers were read off the map at known places (Schiphol, Vondelpark,
Amsterdamse Bos), so a colour here is a drawing decision and not a statement about a class.
"""
import os
import sys

import numpy as np
import rasterio
from PIL import Image, ImageDraw
from rasterio.windows import from_bounds
from scipy import ndimage

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "map")

WATER = [0] + list(range(28, 41))
GROUPS = {
    "residential": [5], "centre": [6, 7, 8], "business": [3, 9], "road": [2], "rail": [1], "works": list(range(10, 16)),
    "green": list(range(16, 21)), "farmland": list(range(21, 25)), "nature": [25, 26, 27], "water": WATER,
}
ON_BLUE = {"residential": "#FAF7F5", "centre": "#F6C9A4", "business": "#CC4100", "road": "#BFE0F2", "rail": "#BFE0F2", "works": "#EE9F6C",
           "green": "#35B597", "farmland": "#148AC4", "nature": "#00866E"}
LAND_USE = {"residential": "#E8743B", "centre": "#CC4100", "business": "#6B4E8E", "road": "#8A97A0", "rail": "#8A97A0", "works": "#E9B98F",
            "green": "#8FD3A8", "farmland": "#EDF2DC", "nature": "#3FA877", "water": "#7FC4E8"}
GROUND = "#EEF4F8"


def rgb(colour):
    return tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))


class Data:
    def __init__(self, folder):
        self.folder = folder

    def read(self, name, left, bottom, width, height):
        with rasterio.open(os.path.join(self.folder, name)) as source:
            window = from_bounds(left, bottom, left + width, bottom + height, source.transform)
            return source.read(1, window=window, boundless=True, fill_value=0)

    def land_use(self, left, bottom, width, height):
        return self.read("Grondgebruik/BBG/BBG2022_100m_Modus_Nederland.tif", left, bottom, width, height)


def most_common_per_cell(grid, step):
    rows, cols = grid.shape[0] // step, grid.shape[1] // step
    out = np.zeros((rows, cols), dtype=grid.dtype)
    for r in range(rows):
        for c in range(cols):
            block = grid[r * step:(r + 1) * step, c * step:(c + 1) * step].ravel()
            out[r, c] = np.bincount(block).argmax()
    return out


def cells_to_image(colours, pixels, gap, ground=None):
    # colours: rows x cols x 4. A small gap between the cells keeps the look of a raster.
    rows, cols = colours.shape[:2]
    image = np.zeros((rows * pixels, cols * pixels, 4), dtype=np.uint8)
    if ground:
        image[..., :3] = rgb(ground)
        image[..., 3] = 255
    for r in range(rows):
        for c in range(cols):
            if colours[r, c, 3]:
                image[r * pixels:(r + 1) * pixels - gap, c * pixels:(c + 1) * pixels - gap] = colours[r, c]
    return Image.fromarray(image, "RGBA")


def paint(grid, palette):
    colours = np.zeros(grid.shape + (4,), dtype=np.uint8)
    for group, codes in GROUPS.items():
        if group in palette:
            colours[np.isin(grid, codes)] = rgb(palette[group]) + (255,)
    return colours


def save(picture, name):
    path = os.path.join(OUT, name + ".png")
    picture.convert("RGBA").quantize(colors=64, method=Image.Quantize.FASTOCTREE).save(path, optimize=True)
    print(name, picture.size, round(os.path.getsize(path) / 1000), "kB")


def hero(data):
    # the North Sea coast to Amsterdam, with room on the sea for the text
    grid = most_common_per_cell(data.land_use(62000, 474000, 64000, 26000), 4)
    save(cells_to_image(paint(grid, ON_BLUE), 8, 1), "hero")


def land_use_modelling(data):
    # the Randstad in all its classes: what a land-use model works with
    grid = most_common_per_cell(data.land_use(72000, 438000, 96000, 40000), 10)
    save(cells_to_image(paint(grid, LAND_USE), 8, 1, GROUND), "land-use-modelling")


def spatial_planning(data):
    # the Green Heart: what is built, and which nature is protected
    left, bottom, width, height = 96000, 442000, 72000, 30000
    land = most_common_per_cell(data.land_use(left, bottom, width, height), 7)
    nature = data.read("Grondgebruik/Natuur/Ring_rel_100m_NNN20230829_Nederland.tif", left, bottom, width, height)
    rows, cols = land.shape
    colours = np.zeros((rows, cols, 4), dtype=np.uint8)
    colours[...] = rgb("#E7EEF2") + (255,)
    step_n = nature.shape[0] // rows
    for r in range(rows):
        for c in range(cols):
            if (nature[r * step_n:(r + 1) * step_n, c * step_n:(c + 1) * step_n] == NATURE_CODE).mean() > 0.4:
                colours[r, c] = rgb("#008053") + (255,)
    colours[np.isin(land, GROUPS["water"])] = rgb("#A9D6EE") + (255,)
    colours[np.isin(land, GROUPS["residential"] + GROUPS["centre"] + GROUPS["business"])] = rgb("#0077B3") + (255,)
    save(cells_to_image(colours, 10, 1, GROUND), "spatial-planning")


def climate_adaptation(data):
    # the delta: the water that everything in this theme comes back to
    grid = most_common_per_cell(data.land_use(36000, 398000, 112000, 46000), 10)
    colours = np.zeros(grid.shape + (4,), dtype=np.uint8)
    colours[...] = rgb("#F2EFED") + (255,)
    colours[np.isin(grid, GROUPS["water"])] = rgb("#0077B3") + (255,)
    colours[np.isin(grid, GROUPS["residential"] + GROUPS["centre"] + GROUPS["business"])] = rgb("#CC4100") + (255,)
    colours[np.isin(grid, GROUPS["nature"])] = rgb("#7CC4A6") + (255,)
    save(cells_to_image(colours, 7, 1, GROUND), "climate-adaptation")


def location_value(data):
    # how far each built-up place in Amsterdam is from open space, a factor in what a house is worth
    left, bottom, width, height = 106000, 479000, 33600, 14000
    grid = data.land_use(left - 5000, bottom - 5000, width + 10000, height + 10000)
    built = np.isin(grid, GROUPS["residential"] + GROUPS["centre"] + GROUPS["business"])
    open_land = np.isin(grid, GROUPS["farmland"] + GROUPS["nature"] + GROUPS["green"])
    labels, count = ndimage.label(open_land)
    sizes = ndimage.sum_labels(open_land, labels, range(1, count + 1))
    large = np.isin(labels, np.flatnonzero(sizes >= 25) + 1)  # at least 25 hectares
    distance = ndimage.distance_transform_edt(~large) * 100
    margin = 50
    built, distance, grid = built[margin:-margin, margin:-margin], distance[margin:-margin, margin:-margin], grid[margin:-margin, margin:-margin]
    step = 3
    rows, cols = built.shape[0] // step, built.shape[1] // step
    ramp = [rgb(c) for c in ("#A9D6EE", "#5FB2DE", "#0077B3", "#005A87", "#7A4A7E", "#CC4100")]
    colours = np.zeros((rows, cols, 4), dtype=np.uint8)
    colours[...] = rgb("#F3F5EC") + (255,)
    for r in range(rows):
        for c in range(cols):
            block_b = built[r * step:(r + 1) * step, c * step:(c + 1) * step]
            block_g = grid[r * step:(r + 1) * step, c * step:(c + 1) * step]
            if np.isin(block_g, GROUPS["water"]).mean() > 0.5:
                colours[r, c] = rgb("#E2EAEE") + (255,)
            elif block_b.mean() >= 0.5:
                d = distance[r * step:(r + 1) * step, c * step:(c + 1) * step][block_b].mean()
                colours[r, c] = ramp[min(int(d / 280), len(ramp) - 1)] + (255,)
    save(cells_to_image(colours, 7, 1, GROUND), "location-value")


def accessibility(data):
    # roads and railways around Utrecht, drawn at 25 metres: a network rather than cells
    left, bottom, width, height = 122000, 447000, 30000, 12500
    grid = data.read("Grondgebruik/BBG/BBG2022_25m_Modus_Nederland.tif", left, bottom, width, height)
    road = ndimage.binary_dilation(np.isin(grid, GROUPS["road"]))
    rail = ndimage.binary_dilation(np.isin(grid, GROUPS["rail"]), iterations=1)
    built = np.isin(grid, GROUPS["residential"] + GROUPS["centre"] + GROUPS["business"])
    image = np.zeros(grid.shape + (3,), dtype=np.uint8)
    image[...] = rgb("#F4F7F9")
    image[built] = rgb("#D5E6F0")
    image[np.isin(grid, GROUPS["water"])] = rgb("#BDE0F2")
    image[road] = rgb("#0077B3")
    image[rail] = rgb("#CC4100")
    save(Image.fromarray(image, "RGB"), "accessibility")


def geodesign(data):
    # dwellings per hectare in Amsterdam as height: the city as a model you can look at
    left, bottom, width, height = 117000, 483000, 9000, 7500
    dwellings = None
    for name in ("eengezins_SocialeHuur", "eengezins_VrijeSector", "meergezins_SocialeHuur", "meergezins_VrijeSector"):
        part = np.nan_to_num(data.read(f"StandBasisjaar/Wonen/{name}_Nederland.tif", left, bottom, width, height).astype(float))
        dwellings = part if dwellings is None else dwellings + part
    land = data.land_use(left, bottom, width, height)
    step = 4
    rows, cols = dwellings.shape[0] // step, dwellings.shape[1] // step
    totals = dwellings[:rows * step, :cols * step].reshape(rows, step, cols, step).sum(axis=(1, 3))
    water = np.isin(land[:rows, :cols], GROUPS["water"])
    a, b, c = 3.4, 1.7, 0.15
    canvas = (768, 320)
    picture = Image.new("RGB", canvas, rgb("#EEF4F8"))
    pen = ImageDraw.Draw(picture)
    ox, oy = canvas[0] / 2 - (cols - rows) * a / 2, canvas[1] / 2 - (cols + rows) * b / 2 + 34
    ramp = [rgb(x) for x in ("#BFDFF0", "#6FB7DF", "#0077B3", "#005A87", "#CC4100")]
    limits = (25, 60, 110, 200)

    def to_screen(x, y, h):
        return (ox + (x - y) * a, oy + (x + y) * b - h * c)

    for total in range(rows + cols):
        for y in range(rows):
            x = total - y
            if not 0 <= x < cols:
                continue
            h = min(totals[y, x], 420)
            base = rgb("#BDE0F2") if water[y, x] and h == 0 else rgb("#E4EDF2")
            top = ramp[sum(h > limit for limit in limits)] if h else base
            corners = [to_screen(x, y, h), to_screen(x + 0.92, y, h), to_screen(x + 0.92, y + 0.92, h), to_screen(x, y + 0.92, h)]
            if h:
                shade_l = tuple(int(v * 0.72) for v in top)
                shade_r = tuple(int(v * 0.86) for v in top)
                pen.polygon([corners[3], corners[2], to_screen(x + 0.92, y + 0.92, 0), to_screen(x, y + 0.92, 0)], fill=shade_l)
                pen.polygon([corners[1], corners[2], to_screen(x + 0.92, y + 0.92, 0), to_screen(x + 0.92, y, 0)], fill=shade_r)
            pen.polygon(corners, fill=top)
    save(picture, "geodesign")


def netherlands(data):
    # the whole country, for the research page
    grid = most_common_per_cell(data.land_use(0, 300000, 280000, 325000), 10)
    colours = paint(grid, LAND_USE)
    colours[np.isin(grid, [0])] = (0, 0, 0, 0)
    save(cells_to_image(colours, 2, 0), "netherlands")


NATURE_CODE = 0


def main():
    data = Data(sys.argv[1])
    os.makedirs(OUT, exist_ok=True)
    for draw in (hero, land_use_modelling, spatial_planning, climate_adaptation, location_value, accessibility, geodesign, netherlands):
        draw(data)


if __name__ == "__main__":
    main()
