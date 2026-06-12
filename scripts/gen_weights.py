"""Compute landscape paint-layer weights from the island heightmap.

Targets the Smuggler's Cove pack terrain material (5 layers):
grass / sand / coast / cliff / ocean.
Outputs raw uint8 (0..255) row-major 1009x1009 files per layer.
"""
import numpy as np
from PIL import Image
import os

SRC = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png"
OUT = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps"

v = np.asarray(Image.open(SRC), dtype=np.float64)
h = (v - 32768) / 128.0  # meters

gy, gx = np.gradient(h)
slope = np.sqrt(gx ** 2 + gy ** 2)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# --- base bands by height ---
w_ocean = smoothstep(-1.5, -5.0, h)                       # underwater floor
w_coast = smoothstep(-3.5, -1.0, h) * smoothstep(1.2, -0.2, h)  # wet rocky shoreline band
w_sand = smoothstep(0.0, 0.9, h) * smoothstep(3.2, 1.6, h)      # dry beach band
w_grass = smoothstep(2.2, 3.5, h)                          # vegetated land
w_cliff = smoothstep(0.45, 0.8, slope) * smoothstep(-1.0, 0.5, h)  # steep rock above water

# --- sand paths + market plaza (stamped over grass) ---
def seg_dist(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    t = np.clip(((px - ax) * abx + (py - ay) * aby) / (abx ** 2 + aby ** 2), 0, 1)
    return np.sqrt((px - (ax + t * abx)) ** 2 + (py - (ay + t * aby)) ** 2)

cols, rows = np.meshgrid(np.arange(h.shape[1], dtype=np.float64),
                         np.arange(h.shape[0], dtype=np.float64))
VIL = (514, 564)                     # village hub (world 1000, 6000)
PATHS = [
    [VIL, (565, 614)],               # village -> dock apron
    [VIL, (494, 474), (474, 384)],   # village -> north meadow
    [VIL, (424, 544), (354, 504)],   # village -> west slope
]
d_path = np.full(h.shape, 1e9)
for wp in PATHS:
    for (ax, ay), (bx, by) in zip(wp[:-1], wp[1:]):
        d_path = np.minimum(d_path, seg_dist(cols, rows, ax, ay, bx, by))
path_mask = smoothstep(5.0, 2.5, d_path) * smoothstep(0.5, 2.5, h)
d_plaza = np.sqrt((cols - VIL[0]) ** 2 + (rows - VIL[1]) ** 2)
path_mask = np.maximum(path_mask, smoothstep(16.0, 11.0, d_plaza))
w_sand = np.maximum(w_sand, path_mask)
w_grass = w_grass * (1 - path_mask)

# --- normalize ---
total = w_ocean + w_coast + w_sand + w_grass + w_cliff + 1e-6
for name, w in (("grass", w_grass), ("sand", w_sand), ("coast", w_coast),
                ("cliff", w_cliff), ("ocean", w_ocean)):
    wn = w / total
    path = os.path.join(OUT, f"weight_{name}.raw")
    (wn * 255).astype(np.uint8).tofile(path)
    print(name, f"avg={wn.mean():.2f}", "->", path)
