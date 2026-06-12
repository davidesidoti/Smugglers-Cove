import warnings; warnings.simplefilter("ignore")
import unreal
from array import array

# 1. LGT with the pack's bermuda grass meshes
LGT_PATH = "/Game/SmugglersCove/Env/LGT_Bermuda"
if not unreal.EditorAssetLibrary.does_asset_exist(LGT_PATH):
    at = unreal.AssetToolsHelpers.get_asset_tools()
    lgt = at.create_asset("LGT_Bermuda", "/Game/SmugglersCove/Env",
                          unreal.LandscapeGrassType, unreal.LandscapeGrassTypeFactory())
else:
    lgt = unreal.EditorAssetLibrary.load_asset(LGT_PATH)
lgt.set_editor_property("enable_density_scaling", True)
varieties = unreal.Array(unreal.GrassVariety)

def variety(mesh_path, density, smin, smax):
    v = unreal.GrassVariety()
    v.set_editor_property("grass_mesh", unreal.load_asset(mesh_path))
    v.set_editor_property("grass_density", unreal.PerPlatformFloat(default=density))
    v.set_editor_property("grass_density_quality", unreal.PerQualityLevelFloat(default=density))
    v.set_editor_property("start_cull_distance", unreal.PerPlatformInt(default=9000))
    v.set_editor_property("start_cull_distance_quality", unreal.PerQualityLevelInt(default=9000))
    v.set_editor_property("end_cull_distance", unreal.PerPlatformInt(default=14000))
    v.set_editor_property("end_cull_distance_quality", unreal.PerQualityLevelInt(default=14000))
    v.set_editor_property("scale_x", unreal.FloatInterval(min=smin, max=smax))
    v.set_editor_property("scale_y", unreal.FloatInterval(min=smin, max=smax))
    v.set_editor_property("scale_z", unreal.FloatInterval(min=smin, max=smax))
    v.set_editor_property("allowed_density_range", unreal.FloatInterval(min=0.0, max=1.0))
    v.set_editor_property("scaling", unreal.GrassScaling.UNIFORM)
    v.set_editor_property("random_rotation", True)
    v.set_editor_property("align_to_surface", True)
    v.set_editor_property("use_grid", True)
    v.set_editor_property("placement_jitter", 1.0)
    return v

F = "/Game/Smugglers_cove/meshes/foliage"
varieties.append(variety(f"{F}/SM_grass_bermuda_01_dense", 420.0, 1.1, 1.9))
varieties.append(variety(f"{F}/SM_grass_bermuda_01_medium", 140.0, 1.0, 1.7))
lgt.set_editor_property("grass_varieties", varieties)
unreal.EditorAssetLibrary.save_asset(LGT_PATH)
print("LGT_Bermuda saved")

# 2. wire LandscapeGrassOutput into the pack terrain material (RUN ONCE)
MAT = "/Game/Smugglers_cove/materials/terrain/terrain_material/M_terrain_master"
mat = unreal.EditorAssetLibrary.load_asset(MAT)
mel = unreal.MaterialEditingLibrary
ls = mel.create_material_expression(mat, unreal.MaterialExpressionLandscapeLayerSample, -1400, 1200)
ls.set_editor_property("parameter_name", "grass")
go = mel.create_material_expression(mat, unreal.MaterialExpressionLandscapeGrassOutput, -1100, 1200)
gi = unreal.GrassInput()
gi.set_editor_property("name", "Bermuda")
gi.set_editor_property("grass_type", lgt)
arr = unreal.Array(unreal.GrassInput)
arr.append(gi)
go.set_editor_property("grass_types", arr)
print("CONNECT:", mel.connect_material_expressions(ls, "", go, "Bermuda"))
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset(MAT)
print("MATERIAL recompiled")

# 3. re-register layers + weights (recompile deregisters them)
BASE = "/Game/Smugglers_cove/materials/terrain/terrain_material"
RES = 1009
for n_ in ["grass", "sand", "coast", "cliff", "ocean"]:
    unreal.LandscapeService.add_layer("Island", f"{BASE}/{n_}_LayerInfo")
    raw = array("B")
    with open(rf"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\weight_{n_}.raw", "rb") as f:
        raw.fromfile(f, RES * RES)
    ok = unreal.LandscapeService.set_weights_in_region("Island", n_, 0, 0, RES, RES,
                                                       [x / 255.0 for x in raw])
    print("LAYER+WEIGHTS", n_, ok)

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
unreal.SystemLibrary.execute_console_command(ues.get_editor_world(), "grass.FlushCache")
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
