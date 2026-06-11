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
    return None

SP = "/Game/WoodenProps/StaticMeshes/SingleParts/"
mesh = {n: unreal.EditorAssetLibrary.load_asset(SP + n) for n in
        ["Platform3", "PillarLog1", "RopeFence1", "Barrel1", "Barrel2", "Box1", "Box2",
         "Bucket", "Cage", "Planks1"]}

def spawn(m, x, y, z, yaw=0.0, scale=(1, 1, 1), folder="Env/Dock"):
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                   unreal.Rotator(0, 0, yaw))
    a.static_mesh_component.set_static_mesh(mesh[m])
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_folder_path(folder)
    return a

# pier axis
sx, sy = 1008.0, 6048.0
ux, uy = 0.822, 0.569
yaw = math.degrees(math.atan2(uy, ux))          # ~34.7
px, py = -uy, ux                                 # left perpendicular

SEG = 310.0
DECK_Z = 45.0                                    # platform actor z -> deck top ~60
START_D = 3850.0
N_SEG = 8
count = 0

# 1. walkway
for i in range(N_SEG):
    d = START_D + (i + 0.5) * SEG
    x, y = sx + ux * d, sy + uy * d
    spawn("Platform3", x, y, DECK_Z + (i % 2) * 1.5, yaw)
    count += 1

# 2. T-head: two side platforms at the end
end_d = START_D + (N_SEG - 0.5) * SEG
ex, ey = sx + ux * end_d, sy + uy * end_d
for s in (1, -1):
    spawn("Platform3", ex + px * 310 * s, ey + py * 310 * s, DECK_Z + 1.0, yaw)
    count += 1

# 3. pillars at joints (pairs), scaled to reach the seabed
for i in range(N_SEG + 1):
    d = START_D + i * SEG
    for s in (1, -1):
        x = sx + ux * d + px * 130 * s
        y = sy + uy * d + py * 130 * s
        g = gz(x, y)
        if g is None:
            continue
        base = g - 60.0                          # embed into ground
        need = (DECK_Z + 20.0) - base            # reach just under deck
        sz = max(need / 333.0, 0.6)
        spawn("PillarLog1", x, y, base, yaw, (1.1, 1.1, sz))
        count += 1

# 4. rope railing on the left side (leave right side clear for boats)
for i in range(2, N_SEG, 2):
    d = START_D + i * SEG
    x = sx + ux * d + px * 140
    y = sy + uy * d + py * 140
    spawn("RopeFence1", x, y, DECK_Z + 18, yaw)
    count += 1

# 5. dressing: barrels/crates at the pier root (on the beach) and deck
root_d = START_D - 250
rx, ry = sx + ux * root_d, sy + uy * root_d
g = gz(rx, ry) or 60
for m, ox, oy, oz, yw in [("Barrel1", 180, 60, 0, 10), ("Barrel2", 250, -40, 0, 70),
                          ("Box1", 60, 180, 0, 30), ("Box2", -60, 240, 0, 55),
                          ("Bucket", 140, 150, 0, 0), ("Cage", -180, 120, 0, 15)]:
    gg = gz(rx + ox, ry + oy) or g
    spawn(m, rx + ox, ry + oy, gg + oz, yw, folder="Env/Dock/Props")
    count += 1
# a couple of crates on the deck end
spawn("Box1", ex + px * 60, ey + py * 60, DECK_Z + 17, 40, folder="Env/Dock/Props")
spawn("Barrel1", ex - px * 80, ey - py * 80, DECK_Z + 17, 0, folder="Env/Dock/Props")
count += 2

print("DOCK actors:", count)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
