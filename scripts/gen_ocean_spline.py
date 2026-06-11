"""Extract the island coastline contour and emit ocean-spline points.

The WaterBodyOcean renders water OUTSIDE its spline polygon. Default is a
20km square that cuts through the bay. We replace it with the +1.5 m land
contour (slightly inland of the Z=0 waterline) so the ocean mesh reaches
every shore, including inside the cove.
"""
import json
import numpy as np
from PIL import Image
from skimage import measure

SRC = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png"
OUT = r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\ocean_spline.json"

LEVEL_M = 1.5          # contour height (m): inland of the waterline
TOL = 6.0              # RDP simplification tolerance (px = m)

v = np.asarray(Image.open(SRC), dtype=np.float64)
h = (v - 32768) / 128.0

contours = measure.find_contours(h, LEVEL_M)
main = max(contours, key=len)          # the island's outer coastline
print(f"contours: {len(contours)}, main length: {len(main)} px-points")


def rdp(points, eps):
    """Ramer-Douglas-Peucker simplification."""
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    line = end - start
    norm = np.linalg.norm(line)
    if norm == 0:
        d = np.linalg.norm(points - start, axis=1)
    else:
        d = np.abs(np.cross(line, start - points)) / norm
    idx = int(np.argmax(d))
    if d[idx] > eps:
        left = rdp(points[: idx + 1], eps)
        right = rdp(points[idx:], eps)
        return np.vstack([left[:-1], right])
    return np.array([start, end])


simplified = rdp(main, TOL)
# drop duplicate closing point if present
if np.allclose(simplified[0], simplified[-1]):
    simplified = simplified[:-1]
print("simplified points:", len(simplified))

# contour points are (row, col) -> world (X=col, Y=row)
pts = [{"x": round((c - 504) * 100.0, 1), "y": round((r - 504) * 100.0, 1)}
       for r, c in simplified]
with open(OUT, "w") as f:
    json.dump(pts, f)
print("saved", OUT)
