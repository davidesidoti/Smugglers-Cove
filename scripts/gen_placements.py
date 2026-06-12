"""Generate scatter placements from the island heightmap — Smuggler's Cove pack palette.

Mapping (verified): world X = col axis, world Y = row axis, world = (idx-504)*100,
ground Z = h*100. Output: Saved/Heightmaps/placements.json
"""
import json
import math
import numpy as np
from PIL import Image

SRC = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png"
OUT = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\placements.json"

rng = np.random.default_rng(99)
v = np.asarray(Image.open(SRC), dtype=np.float64)
h = (v - 32768) / 128.0
gy, gx = np.gradient(h)
slope = np.sqrt(gx ** 2 + gy ** 2)

SC = "/Game/Smugglers_cove/meshes"
FP = "/Game/FoliagePack_Meshingun/Assets/Foliage/Mesh"

PACK_TREES = [f"{SC}/foliage/SM_island_tree_0{i}" for i in (1, 2, 3)]
INLAND_TREES = [f"{FP}/SM_Oak_Spring_01a", f"{FP}/SM_Maple_Spring_01a",
                f"{FP}/SM_Alder_Spring_01a", f"{FP}/SM_Oak_Fall_01a"]
SHRUBS = [f"{SC}/foliage/SM_island_shrub_0{i}" for i in (1, 2, 3)] + \
         [f"{SC}/foliage/SM_pachira_aquatica_01_{c}" for c in "abcd"]
FERNS = [f"{SC}/foliage/SM_fern_02_fern_02_{c}" for c in "abcd"]
ACCENTS = [f"{SC}/foliage/SM_anthurium_botany_01_{c}" for c in "abc"] + \
          [f"{SC}/foliage/SM_calathea_orbifolia_01_{c}" for c in "abc"]
CLIFFS = [f"{SC}/terrain/SM_coastal_cliff_02_{c}" for c in "abcd"] + \
         [f"{SC}/terrain/SM_coastal_cliff_05_a", f"{SC}/terrain/SM_coastal_cliff_05_b",
          f"{SC}/terrain/SM_coastal_cliff_06_a", f"{SC}/terrain/SM_coastal_cliff_06_b"]
COAST_ROCKS = [f"{SC}/terrain/SM_coast_rocks_0{i}" for i in (1, 2, 3, 4)]
SAND_ROCKS = [f"{SC}/terrain/SM_sand_rocks_small_0{i}" for i in (1, 3, 4)]
HERO_TREE = "/Game/HighPoly_Tree_Model/SM_HP_Tree"

VILLAGE = (1008.0, 6048.0)
V_CLEAR = 7000.0
APRON = (4400.0, 9250.0)
A_CLEAR = 3200.0

def world(r, c):
    return (c - 504) * 100.0, (r - 504) * 100.0

def clear(x, y):
    if (x - VILLAGE[0]) ** 2 + (y - VILLAGE[1]) ** 2 < V_CLEAR ** 2:
        return False
    if (x - APRON[0]) ** 2 + (y - APRON[1]) ** 2 < A_CLEAR ** 2:
        return False
    return True

def fractal(res, octaves=4, base=4):
    out = np.zeros((res, res))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        g = rng.random((n, n))
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((res, res), Image.BICUBIC)
        out += (np.asarray(img) / 255.0 - 0.5) * amp
        tot += amp
        amp *= 0.55
    return out / tot

cluster = fractal(1009)
placements = []
tree_pts = []

def scatter(meshes, count, folder, hmin, hmax, smax, zoff, scmin, scmax,
            need_cluster=None, near=None, near_r=0):
    made, tries = 0, 0
    while made < count and tries < 60000:
        tries += 1
        if near:
            bx, by = near[rng.integers(0, len(near))]
            x = bx + rng.uniform(-near_r, near_r)
            y = by + rng.uniform(-near_r, near_r)
            c, r = int(x / 100 + 504), int(y / 100 + 504)
            if not (30 < r < 979 and 30 < c < 979):
                continue
        else:
            r, c = rng.integers(60, 949), rng.integers(60, 949)
            x, y = world(r, c)
        hh, ss = h[r, c], slope[r, c]
        if not (hmin < hh < hmax) or ss > smax or not clear(x, y):
            continue
        if need_cluster is not None and cluster[r, c] < need_cluster:
            continue
        placements.append({
            "mesh": str(rng.choice(meshes)), "x": round(x, 1), "y": round(y, 1),
            "z": round(hh * 100 + zoff, 1), "yaw": round(rng.uniform(0, 360), 1),
            "scale": round(rng.uniform(scmin, scmax), 2), "folder": folder,
        })
        made += 1
        if folder == "Env/Trees":
            tree_pts.append((x, y))
    return made

print("pack trees:", scatter(PACK_TREES, 120, "Env/Trees", 3.0, 35.0, 0.35, -8, 0.9, 1.5, need_cluster=0.0))
print("inland trees:", scatter(INLAND_TREES, 55, "Env/Trees", 12.0, 48.0, 0.35, -15, 0.85, 1.3, need_cluster=0.02))
print("shrubs:", scatter(SHRUBS, 90, "Env/Shrubs", 2.0, 40.0, 0.4, -10, 0.7, 1.3))
print("ferns:", scatter(FERNS, 70, "Env/Shrubs", 2.5, 40.0, 0.45, -6, 0.8, 1.5,
                        near=tree_pts, near_r=700))
print("accents:", scatter(ACCENTS, 30, "Env/Shrubs", 2.0, 12.0, 0.3, -4, 0.9, 1.4,
                          near=[VILLAGE], near_r=5500))
print("cliffs:", scatter(CLIFFS, 16, "Env/Cliffs", -1.0, 18.0, 9.9, -150, 0.22, 0.42,
                         need_cluster=None))
# keep cliffs only on steep coast: filter pass
kept = []
for p in placements:
    if p["folder"] != "Env/Cliffs":
        kept.append(p); continue
    c = int(p["x"] / 100 + 504); r = int(p["y"] / 100 + 504)
    if slope[r, c] > 0.45 and -1.0 < h[r, c] < 18.0:
        kept.append(p)
placements = kept
print("coast rocks:", scatter(COAST_ROCKS, 14, "Env/Rocks", -3.5, 0.5, 9.9, -80, 0.25, 0.5))
print("sand rocks:", scatter(SAND_ROCKS, 45, "Env/Rocks", 0.2, 4.0, 0.5, -15, 0.6, 1.3))

# hero trees: two big ones near the village edge
for (hx, hy) in [(VILLAGE[0] - 4800, VILLAGE[1] + 2600), (VILLAGE[0] + 3400, VILLAGE[1] - 5200)]:
    c, r = int(hx / 100 + 504), int(hy / 100 + 504)
    placements.append({"mesh": HERO_TREE, "x": hx, "y": hy, "z": round(h[r, c] * 100 - 10, 1),
                       "yaw": float(rng.uniform(0, 360)), "scale": 1.0, "folder": "Env/Trees"})

# islet crowns: pack cliffs on the two mouth islets
ca, sa = math.cos(math.radians(-38)), math.sin(math.radians(-38))
bx, by = 0.28 + ca * 0.08, 0.30 + (-sa) * 0.08
ux, uy = ca, -sa
px_, py_ = -uy, ux
tipx, tipy = bx + ux * 0.42 * 0.72, by + uy * 0.42 * 0.72
for s in (1, -1):
    ix, iy = (tipx + s * px_ * 0.23) * 50400, (tipy + s * py_ * 0.23) * 50400
    for k in range(2):
        placements.append({
            "mesh": str(rng.choice(CLIFFS[4:])), "x": round(ix + rng.uniform(-700, 700), 1),
            "y": round(iy + rng.uniform(-700, 700), 1), "z": round(rng.uniform(-450, -250), 1),
            "yaw": round(rng.uniform(0, 360), 1), "scale": round(rng.uniform(0.18, 0.3), 2),
            "folder": "Env/Islets"})

with open(OUT, "w") as f:
    json.dump(placements, f)
print("total:", len(placements), "->", OUT)
