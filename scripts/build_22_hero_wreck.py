import warnings; warnings.simplefilter("ignore")
import unreal, math

ar = unreal.AssetRegistryHelpers.get_asset_registry()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
count = 0

def spawn(path, x, y, z, rot, scale, folder):
    global count
    m = unreal.EditorAssetLibrary.load_asset(path)
    if m is None:
        print("MISSING:", path); return None
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                   unreal.Rotator(*rot))
    a.static_mesh_component.set_static_mesh(m)
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_folder_path(folder)
    count += 1
    return a

# 1. find the HP tree's real path
hp = [str(a.package_name) for a in ar.get_assets_by_path("/Game/HighPoly_Tree_Model", True)
      if str(a.asset_name) == "SM_HP_Tree"]
print("HP tree:", hp)
if hp:
    import random
    rnd = random.Random(4)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
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
        return 300.0
    for hx, hy in [(-3800, 8600), (4400, 800)]:
        spawn(hp[0], hx, hy, gz(hx, hy) - 10, (0, 0, rnd.uniform(0, 360)), (1, 1, 1), "Env/Trees")

# 2. wreck: pack small boat half-sunk near the east mouth islet
ca, sa = math.cos(math.radians(-38)), math.sin(math.radians(-38))
bx, by = 0.28 + ca * 0.08, 0.30 + (-sa) * 0.08
ux, uy = ca, -sa
tipx, tipy = bx + ux * 0.42 * 0.72, by + uy * 0.42 * 0.72
ix, iy = (tipx - (-uy) * 0.23) * 50400, (tipy - ux * 0.23) * 50400   # east islet
wx, wy = ix + 1400, iy + 500
spawn("/Game/Smugglers_cove/meshes/ships/SM_boat_dutch_small_02",
      wx, wy, -130, (-24, 9, 155), (1, 1, 1), "Env/Wreck")
print("wreck at", round(wx), round(wy))

print("count:", count)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
