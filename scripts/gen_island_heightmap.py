"""Generate the Smuggler's Cove island heightmap.

1009x1009 16-bit grayscale PNG for a UE landscape with scale (100,100,100):
value 32768 = Z 0 (sea level), 128 values per meter.

Layout (world axes, +X = east, +Y = south in image space):
- irregular island ~650 m across, noise-perturbed coastline
- sheltered cove cut into the SE coast (narrow entrance, wider basin)
- flat village plateau (~6 m) on the cove's west shore
- hills rising NW to a ~70 m rocky peak
- seafloor sloping to -14 m at map edge
"""
import numpy as np
from PIL import Image

RES = 1009
M_PER_UNIT = 1.0 / 128.0  # 16-bit value units per meter at Z scale 100
SEED = 1715

rng = np.random.default_rng(SEED)


def fractal_noise(res, octaves=6, base=4, persistence=0.55):
    """Value noise via upsampled random grids."""
    out = np.zeros((res, res), dtype=np.float64)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        n = base * (2 ** o)
        grid = rng.random((n, n))
        img = Image.fromarray((grid * 255).astype(np.uint8)).resize((res, res), Image.BICUBIC)
        out += (np.asarray(img, dtype=np.float64) / 255.0 - 0.5) * amp
        total += amp
        amp *= persistence
    return out / total


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# normalized coords [-1, 1], x = east, y = south
lin = np.linspace(-1.0, 1.0, RES)
X, Y = np.meshgrid(lin, lin)
R = np.sqrt(X ** 2 + Y ** 2)
ANG = np.arctan2(Y, X)

# --- island mask: noise-perturbed radius ---
coast_noise = fractal_noise(RES, octaves=6, base=4, persistence=0.6)
island_radius = 0.66 + coast_noise * 0.34          # ~700 m diameter, ragged coast
island = smoothstep(island_radius, island_radius - 0.20, R)  # 1 inside, 0 at sea

# --- base elevation ---
seafloor = -14.0 + 6.0 * smoothstep(1.0, 0.45, R)  # -14 m at edge, -8 m near shore
detail = fractal_noise(RES, octaves=6, base=6)

# hills: ridge running NW, peak offset toward (-0.25, -0.30)
peak_d = np.sqrt((X + 0.28) ** 2 + (Y + 0.30) ** 2)
hills = 80.0 * smoothstep(0.70, 0.05, peak_d)
hills += 22.0 * smoothstep(0.9, 0.2, np.sqrt((X + 0.05) ** 2 + (Y + 0.55) ** 2))  # N ridge arm
hills *= (0.7 + 0.6 * detail)                       # break up the cone

lowland = 5.0 + 9.0 * detail                        # rolling 1..11 m lowland
land_h = lowland + hills * smoothstep(0.55, 0.15, R + 0.1 * coast_noise)

h = seafloor * (1 - island) + land_h * island

# --- the cove: a sheltered bay bitten out of the SE coast ---
# rotated ellipse straddling the coastline so its mouth opens to the sea
bx, by = 0.28, 0.30                                  # basin center, inside the coast
ANG_BAY = np.radians(-38)
ca, sa = np.cos(ANG_BAY), np.sin(ANG_BAY)
XB = (X - bx) * ca - (Y - by) * sa
YB = (X - bx) * sa + (Y - by) * ca
SEMI_MAJ, SEMI_MIN = 0.34, 0.16
bay_noise = fractal_noise(RES, octaves=4, base=5) * 0.15
d_bay = np.sqrt((XB / SEMI_MAJ) ** 2 + (YB / SEMI_MIN) ** 2) + bay_noise
bay = smoothstep(1.0, 0.55, d_bay)                  # 1 inside the bay
# carve only: lower terrain toward -5.5 m, never raise the ocean floor
bay_floor = np.minimum(h, h * (1 - bay) + (-5.5) * bay)
h = np.where(bay > 0.01, bay_floor, h)

# headlands: two rocky arms at the sides of the bay mouth
ux, uy = ca, -sa                                     # bay major axis (toward the sea, SE)
px_, py_ = -uy, ux                                   # perpendicular
tipx, tipy = bx + ux * SEMI_MAJ * 0.72, by + uy * SEMI_MAJ * 0.72
for s, amp in ((1, 16.0), (-1, 13.0)):
    hx, hy = tipx + s * px_ * (SEMI_MIN + 0.01), tipy + s * py_ * (SEMI_MIN + 0.01)
    d_head = np.sqrt((X - hx) ** 2 + (Y - hy) ** 2)
    head = smoothstep(0.13, 0.02, d_head)
    h = np.maximum(h, head * amp * (0.7 + 0.5 * detail) - 1000.0 * (1 - head))

# sand beach where the bay shore meets pre-existing land only
beach_band = smoothstep(1.30, 1.0, d_bay) * (1 - bay) * island
h = h * (1 - beach_band * 0.75) + 2.2 * (beach_band * 0.75)

# --- village plateau at the cove's inland head, overlooking the water ---
d_village = np.sqrt((X - 0.02) ** 2 + (Y - 0.12) ** 2)
village = smoothstep(0.17, 0.06, d_village) * (1 - bay)
h = h * (1 - village) + 6.0 * village

# soften shoreline: gentle slope between -1.5 m and +2.5 m
shore = smoothstep(2.5, -1.5, h) * smoothstep(-4.0, -1.5, h)
h -= shore * 0.5

# --- encode ---
values = np.clip(32768 + h / M_PER_UNIT, 0, 65535).astype(np.uint16)
img = Image.fromarray(values, mode="I;16")
out = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png"
import os
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print("saved", out)
print(f"height range: {h.min():.1f} .. {h.max():.1f} m")
print(f"land fraction: {(h > 0).mean():.2%}")
