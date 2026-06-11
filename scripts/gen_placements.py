"""Generate scatter placements (trees, rocks) from the island heightmap.

Mapping (verified by line traces): world X = col axis, world Y = row axis,
world = (idx - 504) * 100, ground Z = h * 100.
Output: Saved/Heightmaps/placements.json
"""
import json
import numpy as np
from PIL import Image

SRC = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png"
OUT = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\placements.json"

rng = np.random.default_rng(77)
v = np.asarray(Image.open(SRC), dtype=np.float64)
h = (v - 32768) / 128.0
gy, gx = np.gradient(h)          # gy = d/drow (Y), gx = d/dcol (X)
slope = np.sqrt(gx ** 2 + gy ** 2)

TREES = [
    ("/Game/FoliagePack_Meshingun/Assets/Foliage/Mesh/SM_Oak_Spring_01a", 4),
    ("/Game/FoliagePack_Meshingun/Assets/Foliage/Mesh/SM_Maple_Spring_01a", 3),
    ("/Game/FoliagePack_Meshingun/Assets/Foliage/Mesh/SM_Alder_Spring_01a", 3),
    ("/Game/FoliagePack_Meshingun/Assets/Foliage/Mesh/SM_Alder_Spring_01b", 2),
    ("/Game/FoliagePack_Meshingun/Assets/Foliage/Mesh/SM_Oak_Fall_01a", 1),
]
CLIFF_ROCKS = [f"/Game/RP_Vol_01/Mesh/SM_RP_Vol_01_{i:02d}" for i in range(1, 13)]
SMALL_ROCKS = [f"/Game/Rock_Collection_04/Meshes/Rock_0{i}/StaticMeshes/SM_Rock_0{i}" for i in range(1, 8)]

VILLAGE = (1008.0, 6048.0)       # keep-clear center (world XY)
V_CLEAR = 7000.0

def world(r, c):
    return (c - 504) * 100.0, (r - 504) * 100.0

def sample(r, c):
    return h[int(r), int(c)], slope[int(r), int(c)]

placements = []

# clustering noise for trees
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

# --- trees ---
tree_names = [t[0] for t in TREES for _ in range(t[1])]
count, tries = 0, 0
while count < 170 and tries < 30000:
    tries += 1
    r, c = rng.integers(60, 949), rng.integers(60, 949)
    hh, ss = sample(r, c)
    x, y = world(r, c)
    if not (4.0 < hh < 45.0) or ss > 0.35:
        continue
    if cluster[r, c] < 0.02:                       # clustered woods
        continue
    if (x - VILLAGE[0]) ** 2 + (y - VILLAGE[1]) ** 2 < V_CLEAR ** 2:
        continue
    placements.append({
        "mesh": str(rng.choice(tree_names)), "x": round(x + rng.uniform(-40, 40), 1),
        "y": round(y + rng.uniform(-40, 40), 1), "z": round(hh * 100 - 15, 1),
        "yaw": round(rng.uniform(0, 360), 1), "scale": round(rng.uniform(0.85, 1.35), 2),
        "folder": "Env/Trees",
    })
    count += 1
print("trees:", count)

# --- cliff rocks on steep coastal slopes ---
count, tries = 0, 0
while count < 34 and tries < 40000:
    tries += 1
    r, c = rng.integers(40, 969), rng.integers(40, 969)
    hh, ss = sample(r, c)
    x, y = world(r, c)
    if not (-1.5 < hh < 30.0) or ss < 0.45:
        continue
    if (x - VILLAGE[0]) ** 2 + (y - VILLAGE[1]) ** 2 < (V_CLEAR * 0.7) ** 2:
        continue
    placements.append({
        "mesh": str(rng.choice(CLIFF_ROCKS)), "x": round(x, 1), "y": round(y, 1),
        "z": round(hh * 100 - rng.uniform(60, 160), 1),
        "yaw": round(rng.uniform(0, 360), 1), "scale": round(rng.uniform(1.2, 2.6), 2),
        "folder": "Env/Cliffs",
    })
    count += 1
print("cliff rocks:", count)

# --- the two mouth islets: crown them with big rocks ---
# islet centers (design): tip +/- perp, from gen script; world coords
import math
bx, by = 0.28, 0.30
ang = math.radians(-38)
ca, sa = math.cos(ang), math.sin(ang)
ux, uy = ca, -sa
px_, py_ = -uy, ux
tipx, tipy = bx + ux * 0.34 * 0.72, by + uy * 0.34 * 0.72
for s in (1, -1):
    ix, iy = tipx + s * px_ * 0.17, tipy + s * py_ * 0.17
    wx, wy = ix * 50400, iy * 50400
    for k in range(3):
        placements.append({
            "mesh": str(rng.choice(CLIFF_ROCKS)), "x": round(wx + rng.uniform(-900, 900), 1),
            "y": round(wy + rng.uniform(-900, 900), 1), "z": round(rng.uniform(-350, -150), 1),
            "yaw": round(rng.uniform(0, 360), 1), "scale": round(rng.uniform(1.6, 3.0), 2),
            "folder": "Env/Islets",
        })
print("islet rocks: 6")

# --- small rocks on beaches and meadows ---
count, tries = 0, 0
while count < 50 and tries < 30000:
    tries += 1
    r, c = rng.integers(60, 949), rng.integers(60, 949)
    hh, ss = sample(r, c)
    x, y = world(r, c)
    if not (0.3 < hh < 25.0) or ss > 0.4:
        continue
    placements.append({
        "mesh": str(rng.choice(SMALL_ROCKS)), "x": round(x, 1), "y": round(y, 1),
        "z": round(hh * 100 - 20, 1),
        "yaw": round(rng.uniform(0, 360), 1), "scale": round(rng.uniform(0.5, 1.4), 2),
        "folder": "Env/Rocks",
    })
    count += 1
print("small rocks:", count)

with open(OUT, "w") as f:
    json.dump(placements, f)
print("total:", len(placements), "->", OUT)
