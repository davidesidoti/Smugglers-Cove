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
mesh = {n: unreal.EditorAssetLibrary.load_asset(SP + n) for n in ["PillarLog1", "Bucket"]}
ROCK = unreal.EditorAssetLibrary.load_asset(
    "/Game/Rock_Collection_04/Meshes/Rock_03/StaticMeshes/SM_Rock_03")
NS_SMALL = unreal.EditorAssetLibrary.load_asset(
    "/Game/Vefects/Free_Fire/Shared/Particles/NS_Fire_Small")
NS_MED = unreal.EditorAssetLibrary.load_asset(
    "/Game/Vefects/Free_Fire/Shared/Particles/NS_Fire_Medium")
print("assets:", all([NS_SMALL, NS_MED, ROCK] + list(mesh.values())))
count = 0

def sm_spawn(m, x, y, z, yaw=0.0, scale=(1, 1, 1), folder="Env/Fires"):
    global count
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                   unreal.Rotator(0, 0, yaw))
    comp = a.static_mesh_component
    comp.set_static_mesh(m if not isinstance(m, str) else mesh[m])
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_folder_path(folder)
    count += 1
    return a

def fire(x, y, z, ns, light_intensity, radius, folder="Env/Fires"):
    global count
    fa = eas.spawn_actor_from_class(unreal.NiagaraActor, unreal.Vector(x, y, z))
    nc = fa.get_components_by_class(unreal.NiagaraComponent)[0]
    nc.set_asset(ns)
    fa.set_folder_path(folder)
    la = eas.spawn_actor_from_class(unreal.PointLight, unreal.Vector(x, y, z + 60))
    lc = la.get_components_by_class(unreal.PointLightComponent)[0]
    lc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    lc.set_editor_property("intensity", light_intensity)
    lc.set_editor_property("light_color", unreal.Color(r=255, g=147, b=65, a=255))  # BGRA positional trap!
    lc.set_editor_property("attenuation_radius", radius)
    lc.set_editor_property("source_radius", 12.0)
    lc.set_editor_property("cast_shadows", False)
    la.set_folder_path(folder)
    count += 2

CX, CY = 1008.0, 6048.0

# 1. torch poles near each market stall
for ang in (38, 128, 218, 308):
    rad = math.radians(ang)
    x = CX + math.cos(rad) * 1250
    y = CY + math.sin(rad) * 1250
    g = gz(x, y)
    sm_spawn("PillarLog1", x, y, g - 15, ang, (0.55, 0.55, 0.85))
    fire(x, y, g + 268, NS_SMALL, 250.0, 1100.0)

# 2. fire pit on the apron beach by the pier root
fx, fy = 3900, 8500
g = gz(fx, fy)
import random
rnd = random.Random(5)
for i in range(7):
    a = math.radians(i * 51.4)
    sm_spawn(ROCK, fx + math.cos(a) * 95, fy + math.sin(a) * 95, g - 18,
             rnd.uniform(0, 360), (0.22, 0.22, 0.18))
fire(fx, fy, g + 6, NS_MED, 600.0, 1800.0)

print("FIRE actors:", count)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
