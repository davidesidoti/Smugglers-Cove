"""Pick coastal-cliff placements directly on the steep shore band."""
import json
import numpy as np
from PIL import Image

SRC = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png"
OUT = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\placements.json"

rng = np.random.default_rng(123)
v = np.asarray(Image.open(SRC), dtype=np.float64)
h = (v - 32768) / 128.0
gy, gx = np.gradient(h)
slope = np.sqrt(gx ** 2 + gy ** 2)

SC = "/Game/Smugglers_cove/meshes/terrain"
CLIFFS = [f"{SC}/SM_coastal_cliff_02_{c}" for c in "abcd"] + \
         [f"{SC}/SM_coastal_cliff_05_a", f"{SC}/SM_coastal_cliff_05_b",
          f"{SC}/SM_coastal_cliff_06_a", f"{SC}/SM_coastal_cliff_06_b"]

cand = np.argwhere((h > -0.5) & (h < 8.0) & (slope > 0.40))
print("candidates:", len(cand))
rng.shuffle(cand)

chosen = []
placements = []
for r, c in cand:
    x, y = (c - 504) * 100.0, (r - 504) * 100.0
    if (x - 1008) ** 2 + (y - 6048) ** 2 < 7000 ** 2:        # village clear
        continue
    if (x - 4400) ** 2 + (y - 9250) ** 2 < 4000 ** 2:        # pier apron clear
        continue
    if any((x - cx) ** 2 + (y - cy) ** 2 < 3200 ** 2 for cx, cy in chosen):
        continue
    # slope direction -> face the sea (outward = downhill)
    dx, dy = gx[r, c], gy[r, c]
    yaw = float(np.degrees(np.arctan2(-dy, -dx)))
    placements.append({
        "mesh": str(rng.choice(CLIFFS)), "x": round(x, 1), "y": round(y, 1),
        "z": round(h[r, c] * 100 - 140, 1), "yaw": round(yaw + rng.uniform(-25, 25), 1),
        "scale": round(rng.uniform(0.22, 0.4), 2), "folder": "Env/Cliffs",
    })
    chosen.append((x, y))
    if len(chosen) >= 14:
        break

with open(OUT, "w") as f:
    json.dump(placements, f)
print("cliffs:", len(placements), "->", OUT)
