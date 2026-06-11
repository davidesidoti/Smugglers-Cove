import warnings; warnings.simplefilter("ignore")
import unreal, json, sys

BATCH_START = int(globals().get("BATCH_START", 0))
BATCH_SIZE = int(globals().get("BATCH_SIZE", 90))

with open(r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\placements.json") as f:
    items = json.load(f)

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mesh_cache = {}
spawned = 0
for it in items[BATCH_START:BATCH_START + BATCH_SIZE]:
    m = mesh_cache.get(it["mesh"])
    if m is None:
        m = unreal.EditorAssetLibrary.load_asset(it["mesh"])
        mesh_cache[it["mesh"]] = m
    if m is None:
        print("MISSING MESH:", it["mesh"]); continue
    a = eas.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(it["x"], it["y"], it["z"]),
        unreal.Rotator(0, 0, it["yaw"]))
    if a is None:
        print("SPAWN FAILED at", it["x"], it["y"]); continue
    a.static_mesh_component.set_static_mesh(m)
    s = it["scale"]
    a.set_actor_scale3d(unreal.Vector(s, s, s))
    a.set_folder_path(it["folder"])
    spawned += 1
print(f"SPAWNED {spawned} ({BATCH_START}..{BATCH_START + BATCH_SIZE})")
