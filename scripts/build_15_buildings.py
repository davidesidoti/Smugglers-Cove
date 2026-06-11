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

CUBE = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_Cube")
bb = CUBE.get_bounding_box()
print("SM_Cube bb:", bb.min, bb.max)        # pivot info
ZOFF = -bb.min.z                             # so 'bottom at z' placement works
SP = "/Game/WoodenProps/StaticMeshes/SingleParts/"
props = {n: unreal.EditorAssetLibrary.load_asset(SP + n)
         for n in ["PillarLog1", "Barrel1", "Barrel2", "Box1", "Box3", "Bucket", "Cage"]}
NS_SMALL = unreal.EditorAssetLibrary.load_asset(
    "/Game/Vefects/Free_Fire/Shared/Particles/NS_Fire_Small")
count = 0

def cube(x, y, z_bottom, rot, scale, folder):
    """Place SM_Cube so its CENTER (XY) sits at (x, y) and its bottom at z_bottom.

    SM_Cube's pivot is at the corner (bb 0..100), so subtract the rotated
    half-extent offset to recenter.
    """
    global count
    rotator = unreal.Rotator(*rot)
    local_center = unreal.Vector(50.0 * scale[0], 50.0 * scale[1], 50.0 * scale[2])
    off = rotator.quaternion().rotate_vector(local_center)
    center = unreal.Vector(x, y, z_bottom + 50.0 * scale[2])
    pos = unreal.Vector(center.x - off.x, center.y - off.y, center.z - off.z)
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, pos, rotator)
    a.static_mesh_component.set_static_mesh(CUBE)
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_folder_path(folder)
    count += 1
    return a

def prop(m, x, y, z, yaw, scale, folder):
    global count
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                   unreal.Rotator(0, 0, yaw))
    a.static_mesh_component.set_static_mesh(props[m])
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_folder_path(folder)
    count += 1

def fire(x, y, z, folder):
    global count
    fa = eas.spawn_actor_from_class(unreal.NiagaraActor, unreal.Vector(x, y, z))
    fa.get_components_by_class(unreal.NiagaraComponent)[0].set_asset(NS_SMALL)
    fa.set_folder_path(folder)
    la = eas.spawn_actor_from_class(unreal.PointLight, unreal.Vector(x, y, z + 60))
    lc = la.get_components_by_class(unreal.PointLightComponent)[0]
    lc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    lc.set_editor_property("intensity", 2500.0)
    lc.set_editor_property("light_color", unreal.Color(255, 147, 65, 255))
    lc.set_editor_property("attenuation_radius", 1500.0)
    lc.set_editor_property("cast_shadows", False)
    la.set_folder_path(folder)
    count += 2

def label(x, y, z, yaw, text, folder):
    global count
    a = eas.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(x, y, z),
                                   unreal.Rotator(0, 0, yaw))
    tc = a.get_components_by_class(unreal.TextRenderComponent)[0]
    tc.set_editor_property("text", text)
    tc.set_editor_property("world_size", 70.0)
    tc.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    tc.set_editor_property("text_render_color", unreal.Color(240, 220, 170, 255))
    a.set_folder_path(folder)
    count += 1

WALL_T = 0.16   # wall thickness (cube scale)

def build_house(cx, cy, face_yaw, W, D, H, name, folder, open_front=False, door_w=150):
    """Local frame: +X = facing direction. W along local Y, D along local X."""
    rad = math.radians(face_yaw)
    c, s = math.cos(rad), math.sin(rad)
    g = gz(cx, cy)
    def at(lx, ly):
        return cx + lx * c - ly * s, cy + lx * s + ly * c
    # floor slab
    x, y = at(0, 0)
    cube(x, y, g - 12, (0, 0, face_yaw), (D / 100 + 0.3, W / 100 + 0.3, 0.18), folder)
    fz = g + 6  # floor top
    # back wall
    x, y = at(-D / 2, 0)
    cube(x, y, fz, (0, 0, face_yaw), (WALL_T, W / 100, H / 100), folder)
    # side walls
    for sy in (1, -1):
        x, y = at(0, sy * W / 2)
        cube(x, y, fz, (0, 0, face_yaw), (D / 100, WALL_T, H / 100), folder)
    # front: door gap or open posts
    if open_front:
        for sy in (1, -1):
            x, y = at(D / 2, sy * (W / 2 - 30))
            prop("PillarLog1", x, y, fz - 10, face_yaw, (1.2, 1.2, H / 333 * 1.05), folder)
    else:
        seg = (W - door_w) / 2
        for sy in (1, -1):
            x, y = at(D / 2, sy * (door_w / 2 + seg / 2))
            cube(x, y, fz, (0, 0, face_yaw), (WALL_T, seg / 100, H / 100), folder)
        # lintel over the door
        x, y = at(D / 2, 0)
        cube(x, y, fz + 230, (0, 0, face_yaw), (WALL_T, door_w / 100 + 0.02, (H - 230) / 100), folder)
    # gable roof: ridge along local Y, panels slope down toward +/-X
    A = 26.0
    slope_len = (D / 2) / math.cos(math.radians(A)) + 60
    ridge_h = fz + H + math.tan(math.radians(A)) * D / 4
    for sx, pitch in ((1, A), (-1, -A)):
        x, y = at(sx * D / 4, 0)
        cube(x, y, ridge_h - 10, (0, pitch * -sx, face_yaw),
             (slope_len / 100, W / 100 + 0.35, 0.10), folder)
    # sign over the door + torch beside it
    x, y = at(D / 2 + 35, 0)
    label(x, y, fz + H + 60, face_yaw, name, folder)
    x, y = at(D / 2 + 90, W / 2 + 60)
    fire(x, y, fz + 230, folder)
    return fz

# --- Taverna: big, angle 65 deg from plaza
rad = math.radians(65)
tx, ty = 1008 + math.cos(rad) * 2300, 6048 + math.sin(rad) * 2300
fz = build_house(tx, ty, 65 + 180, 1100, 800, 320, "TAVERNA", "Env/Buildings/Taverna")
# barrels outside
for ox, oy, m in ((-620, 380, "Barrel1"), (-680, 250, "Barrel2"), (-560, 300, "Box1")):
    prop(m, tx + ox * 0.5, ty + oy * 0.5, gz(tx + ox * 0.5, ty + oy * 0.5), 30, (1, 1, 1),
         "Env/Buildings/Taverna")

# --- Fabbro (forge): open front, angle 245 deg
rad = math.radians(245)
fx, fy = 1008 + math.cos(rad) * 2200, 6048 + math.sin(rad) * 2200
fz = build_house(fx, fy, 245 + 180, 700, 600, 280, "FABBRO", "Env/Buildings/Fabbro",
                 open_front=True)
# forge brazier inside
rad2 = math.radians(245 + 180)
bx, by = fx - math.cos(rad2) * 150, fy - math.sin(rad2) * 150
prop("Bucket", bx, by, fz, 0, (1.7, 1.7, 1.3), "Env/Buildings/Fabbro")
fire(bx, by, fz + 80, "Env/Buildings/Fabbro")

# --- Magazzino (warehouse): big door, angle 350 deg (toward the dock path)
rad = math.radians(350)
wx, wy = 1008 + math.cos(rad) * 2500, 6048 + math.sin(rad) * 2500
fz = build_house(wx, wy, 350 + 180, 900, 1200, 380, "MAGAZZINO", "Env/Buildings/Magazzino",
                 door_w=260)
# crates inside and outside
import random
rnd = random.Random(3)
for i in range(5):
    ox, oy = rnd.uniform(-250, 250), rnd.uniform(-250, 250)
    prop(rnd.choice(["Box1", "Box3", "Cage", "Barrel2"]), wx + ox, wy + oy, fz,
         rnd.uniform(0, 360), (1, 1, 1), "Env/Buildings/Magazzino")

print("BUILDING actors:", count)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
