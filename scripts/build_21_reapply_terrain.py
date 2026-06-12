import warnings; warnings.simplefilter("ignore")
import unreal, json
from array import array

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# 1. clear pier + ships (rebuilt after)
n = 0
for a in eas.get_all_level_actors():
    f = str(a.get_folder_path())
    if f.startswith("Env/Pier") or f.startswith("Env/Ships"):
        eas.destroy_actor(a); n += 1
print("DELETED pier/ships:", n)

# 2. re-import heightmap (apron moved to the real shoreline)
imp = unreal.LandscapeService.import_heightmap(
    "Island", r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png")
print("REIMPORT:", imp.success, imp.error_message)

# 3. weights
RES = 1009
for n_ in ["grass", "sand", "coast", "cliff", "ocean"]:
    raw = array("B")
    with open(rf"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\weight_{n_}.raw", "rb") as f:
        raw.fromfile(f, RES * RES)
    ok = unreal.LandscapeService.set_weights_in_region("Island", n_, 0, 0, RES, RES,
                                                       [x / 255.0 for x in raw])
    print("WEIGHTS", n_, ok)

# 4. ocean spline
with open(r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\ocean_spline.json") as f:
    pts = json.load(f)
ocean = next(a for a in eas.get_all_level_actors()
             if a.get_class().get_name() == "WaterBodyOcean")
spline = ocean.get_components_by_class(unreal.SplineComponent)[0]
ocean.modify(); spline.modify()
spline.set_spline_points([unreal.Vector(p["x"], p["y"], 0.0) for p in pts],
                         unreal.SplineCoordinateSpace.WORLD, True)
spline.set_closed_loop(True, True)
print("SPLINE points:", spline.get_number_of_spline_points())

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
unreal.SystemLibrary.execute_console_command(ues.get_editor_world(), "grass.FlushCache")
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
