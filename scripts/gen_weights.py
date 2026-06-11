"""Compute landscape paint-layer weights from the island heightmap.

Outputs raw uint8 (0..255) row-major 1009x1009 files for layers Wild, Dirt, Slope.
"""
import numpy as np
from PIL import Image
import os

SRC = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png"
OUT = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps"

v = np.asarray(Image.open(SRC), dtype=np.float64)
h = (v - 32768) / 128.0  # meters

# slope in meters per meter (cell = 1 m at scale 100... actually 1 px = 1 m)
gy, gx = np.gradient(h)
slope = np.sqrt(gx ** 2 + gy ** 2)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


w_slope = smoothstep(0.45, 0.8, slope)                     # cliffs / steep rock
w_dirt = np.maximum(
    smoothstep(2.2, 1.0, h) * smoothstep(-6.0, -2.0, h),   # beach band + shallows
    smoothstep(-4.0, -10.0, h) * 0.8,                      # deeper seabed
)
w_dirt = np.maximum(w_dirt, smoothstep(0.40, 0.65, slope) * 0.3)  # light scree on steeper slopes
w_wild = np.clip(1.0 - w_dirt - w_slope, 0.0, 1.0)

total = w_wild + w_dirt + w_slope
w_wild /= total; w_dirt /= total; w_slope /= total

for name, w in (("Wild", w_wild), ("Dirt", w_dirt), ("Slope", w_slope)):
    path = os.path.join(OUT, f"weight_{name}.raw")
    (w * 255).astype(np.uint8).tofile(path)
    print(name, "->", path, f"avg={w.mean():.2f}")
