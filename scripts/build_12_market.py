import warnings; warnings.simplefilter("ignore")
import unreal, math

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = ues.get_editor_world()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ignore = [a for a in eas.get_all_level_actors() if "Water" in a.get_class().get_name()]

def gz(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x, y, 30000), unreal.Vector(x, y, -30000),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ignore,
        unreal.DrawDebugTrace.NONE, True, unreal.LinearColor.RED, unreal.LinearColor.GREEN, 0.0)
    if hit:
        for v in hit.to_tuple():
            if isinstance(v, unreal.Vector):
                return v.z
    return 600.0

SP = "/Game/WoodenProps/StaticMeshes/SingleParts/"
NAMES = ["PillarLog1", "PillarLog2", "Planks1", "Planks2", "Barrel1", "Barrel2", "Barrel3",
         "Box1", "Box2", "Box3", "Box4", "Bucket", "Cage", "Fence2_1", "Stairs1"]
mesh = {n: unreal.EditorAssetLibrary.load_asset(SP + n) for n in NAMES}
count = 0

def spawn(m, x, y, z, rot=(0, 0, 0), scale=(1, 1, 1), folder="Env/Market"):
    global count
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                   unreal.Rotator(*rot))
    a.static_mesh_component.set_static_mesh(mesh[m])
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_folder_path(folder)
    count += 1
    return a

CX, CY = 1008.0, 6048.0

def build_stall(cx, cy, face_yaw, variant=0):
    """Open market stall: 4 posts, slanted plank roof, plank counter on barrels."""
    g = gz(cx, cy)
    rad = math.radians(face_yaw)
    fx, fy = math.cos(rad), math.sin(rad)      # facing (toward plaza center)
    px, py = -fy, fx                            # stall width axis
    W, D = 170.0, 130.0                         # half width / half depth
    # posts (rear taller via scale, front shorter -> roof slope)
    for sw in (1, -1):
        for sd, szz in ((1, 0.75), (-1, 0.92)):  # front 2.5m, rear 3.1m
            x = cx + px * W * sw + fx * D * sd
            y = cy + py * W * sw + fy * D * sd
            spawn("PillarLog1", x, y, gz(x, y) - 20, (0, 0, face_yaw), (1, 1, szz))
    # slanted roof: two Planks sheets side by side, pitched down toward the front
    for sw in (1, -1):
        spawn("Planks1" if variant % 2 == 0 else "Planks2",
              cx + px * (W - 15) * sw * 0.95, cy + py * (W - 15) * sw * 0.95,
              g + 268, (0, -9, face_yaw), (1.15, 1.0, 1.0))
    # counter: plank sheet over two barrels at the front
    bx, by = cx + fx * (D - 30), cy + fy * (D - 30)
    for sw in (1, -1):
        spawn("Barrel1", bx + px * 100 * sw, by + py * 100 * sw, gz(bx, by) - 3, (0, 0, face_yaw))
    spawn("Planks1", bx, by, g + 126, (0, 0, face_yaw), (1.0, 0.55, 0.8))
    # goods
    spawn("Box1", cx - fx * 60, cy - fy * 60, g + 1, (0, 0, face_yaw + 25))
    spawn("Bucket", bx + px * 40, by + py * 40, g + 128, (0, 0, face_yaw + 60))

# 4 stalls around the plaza, facing the centre
for i, ang in enumerate((20, 110, 200, 290)):
    rad = math.radians(ang)
    sxp = CX + math.cos(rad) * 950
    syp = CY + math.sin(rad) * 950
    build_stall(sxp, syp, ang + 180, i)

# plaza dressing: crate/barrel clusters between stalls
import random
rnd = random.Random(7)
for ang in (65, 155, 245, 335):
    rad = math.radians(ang)
    x = CX + math.cos(rad) * 1050
    y = CY + math.sin(rad) * 1050
    g = gz(x, y)
    for j, m in enumerate(rnd.sample(["Barrel2", "Barrel3", "Box2", "Box3", "Box4", "Cage"], 3)):
        ox, oy = rnd.uniform(-120, 120), rnd.uniform(-120, 120)
        spawn(m, x + ox, y + oy, gz(x + ox, y + oy) + 1, (0, 0, rnd.uniform(0, 360)),
              folder="Env/Market/Props")

# a well... no well mesh; use a big bucket on a cage pedestal at centre
g = gz(CX, CY)
spawn("Cage", CX, CY, g + 1, (0, 0, 15))
spawn("Bucket", CX, CY, g + 24, (0, 0, 40), (1.6, 1.6, 1.6))

print("MARKET actors:", count)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
