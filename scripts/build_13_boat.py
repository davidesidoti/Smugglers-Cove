import warnings; warnings.simplefilter("ignore")
import unreal, math

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SP = "/Game/WoodenProps/StaticMeshes/SingleParts/"
NAMES = ["BridgePlank1", "Plank2", "SquareLog", "SingleLog1", "Beam2", "Box1", "Bucket", "Plank5"]
mesh = {n: unreal.EditorAssetLibrary.load_asset(SP + n) for n in NAMES}
count = 0

def spawn(m, x, y, z, rot, scale, folder):
    global count
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                   unreal.Rotator(*rot))
    a.static_mesh_component.set_static_mesh(mesh[m])
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_folder_path(folder)
    count += 1
    return a

def build_skiff(bx, by, bz, byaw, folder, broken=False):
    """Flat-bottomed skiff, local frame: +Y = bow direction (length), +X = starboard."""
    rad = math.radians(byaw)
    c, s = math.cos(rad), math.sin(rad)
    def P(lx, ly, lz, lyaw=0.0, roll=0.0, pitch=0.0, m="Plank2", sc=(1, 1, 1)):
        wx = bx + lx * c - ly * s
        wy = by + lx * s + ly * c
        spawn(m, wx, wy, bz + lz, (roll, pitch, byaw + lyaw), sc, folder)
    # bottom: two long deck planks side by side
    P(-40, 0, -12, 0, 0, 0, "BridgePlank1", (1.0, 1.05, 1.0))
    P(40, 0, -12, 0, 0, 0, "BridgePlank1", (1.0, 1.05, 1.0))
    # side strakes (two per side, flared outward)
    for sx in (1, -1):
        P(85 * sx, 0, 22, 0, 72 * sx, 0, "Plank2", (1.0, 0.85, 1.0))
        P(98 * sx, 0, 55, 0, 80 * sx, 0, "Plank2", (1.0, 0.80, 1.0))
    # bow: converging planks
    for sx in (1, -1):
        P(45 * sx, 295, 35, -22 * sx, 75 * sx, 0, "Plank2", (1.0, 0.30, 1.0))
    # transom
    P(0, -320, 30, 90, 0, 0, "Beam2", (1.0, 0.55, 2.2))
    # gunwales
    for sx in (1, -1):
        P(92 * sx, 0, 70, 0, 0, 0, "SquareLog", (0.5, 0.85, 0.5))
    # bench + cargo
    P(0, -80, 48, 90, 0, 0, "Beam2", (1.0, 0.55, 1.0))
    P(0, -190, 0, 25, 0, 0, "Box1", (0.9, 0.9, 0.9))
    P(30, 150, 0, 0, 0, 0, "Bucket", (1, 1, 1))
    # mast + yard
    if broken:
        P(0, 60, 60, 0, 0, -52, "SingleLog1", (1.4, 1.4, 1.4))   # fallen mast
    else:
        P(0, 60, 0, 0, 0, -90, "SingleLog1", (1.6, 1.3, 1.3))    # upright (pitch -90: +X -> +Z)
        P(0, 60, 380, 90, 0, 0, "SingleLog1", (0.85, 1.0, 1.0))  # yard across

# 1. skiff moored alongside the pier (starboard side, mid-length)
ux, uy = 0.822, 0.569
pier_yaw = math.degrees(math.atan2(uy, ux))
d = 5300.0
bx = 1008 + ux * d + uy * 320
by = 6048 + uy * d - ux * 320
build_skiff(bx, by, 0.0, pier_yaw - 90.0, "Env/Boat")
print("skiff at", round(bx), round(by))

# 2. wreck half-sunk near the east mouth islet
wx, wy = 29900, 16300
rad = math.radians(150)
# tilted hull
import random
rnd = random.Random(11)
# reuse builder but tilt via placing on a lowered Z and rolling each part is complex;
# simpler: build it level but sunken and add roll on the whole frame via per-part roll offset
build_skiff(wx, wy, -95.0, 150.0, "Env/Wreck", broken=True)
# scattered floating planks
for i in range(5):
    ang = rnd.uniform(0, 360)
    r = rnd.uniform(300, 900)
    px = wx + math.cos(math.radians(ang)) * r
    py = wy + math.sin(math.radians(ang)) * r
    spawn("Plank2", px, py, -6, (rnd.uniform(-4, 4), 0, rnd.uniform(0, 360)),
          (1, rnd.uniform(0.4, 0.9), 1), "Env/Wreck")

print("BOAT actors:", count)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
