import warnings; warnings.simplefilter("ignore")
import unreal, json
from array import array

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# 1. clear old scatter + dock + boat + fires (market/buildings/heat stay)
DOOMED = ("Env/Trees", "Env/Cliffs", "Env/Rocks", "Env/Islets",
          "Env/Dock", "Env/Boat", "Env/Wreck", "Env/Fires")
n = 0
for a in eas.get_all_level_actors():
    f = str(a.get_folder_path())
    if any(f == d or f.startswith(d + "/") for d in DOOMED):
        eas.destroy_actor(a); n += 1
print("DELETED scatter/dock/fires:", n)

# 2. re-import enlarged heightmap
imp = unreal.LandscapeService.import_heightmap(
    "Island", r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png")
print("REIMPORT:", imp.success, imp.error_message)

# 3. pack terrain material + layers
MAT = "/Game/Smugglers_cove/materials/terrain/terrain_material/M_terrain_master"
r = unreal.LandscapeService.set_landscape_material("Island", MAT)
print("SET_MATERIAL:", r)

BASE = "/Game/Smugglers_cove/materials/terrain/terrain_material"
layer_names = {}
for n_ in ["grass", "sand", "coast", "cliff", "ocean"]:
    info_path = f"{BASE}/{n_}_LayerInfo"
    info = unreal.EditorAssetLibrary.load_asset(info_path)
    lname = str(info.get_editor_property("layer_name"))
    layer_names[n_] = lname
    ok = unreal.LandscapeService.add_layer("Island", info_path)
    print("ADD_LAYER", n_, "->", lname, ok)

# 4. weights
RES = 1009
for n_, lname in layer_names.items():
    raw = array("B")
    with open(rf"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\weight_{n_}.raw", "rb") as f:
        raw.fromfile(f, RES * RES)
    ok = unreal.LandscapeService.set_weights_in_region("Island", lname, 0, 0, RES, RES,
                                                       [x / 255.0 for x in raw])
    print("WEIGHTS", lname, ok)

# 5. ocean spline for the new coastline
with open(r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\ocean_spline.json") as f:
    pts = json.load(f)
ocean = next(a for a in eas.get_all_level_actors()
             if a.get_class().get_name() == "WaterBodyOcean")
spline = ocean.get_components_by_class(unreal.SplineComponent)[0]
ocean.modify(); spline.modify()
spline.set_spline_points([unreal.Vector(p["x"], p["y"], 0.0) for p in pts],
                         unreal.SplineCoordinateSpace.WORLD, True)
spline.set_closed_loop(True, True)
print("OCEAN SPLINE points:", spline.get_number_of_spline_points())

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
