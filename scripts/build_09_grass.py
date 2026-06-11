import warnings; warnings.simplefilter("ignore")
import unreal

# 1. LandscapeGrassType asset with two varieties (lush + dried accents)
LGT_PATH = "/Game/SmugglersCove/Env/LGT_CoveGrass"
if not unreal.EditorAssetLibrary.does_asset_exist(LGT_PATH):
    at = unreal.AssetToolsHelpers.get_asset_tools()
    lgt = at.create_asset("LGT_CoveGrass", "/Game/SmugglersCove/Env",
                          unreal.LandscapeGrassType, unreal.LandscapeGrassTypeFactory())
    print("CREATED:", LGT_PATH)
else:
    lgt = unreal.EditorAssetLibrary.load_asset(LGT_PATH)
    print("LOADED existing:", LGT_PATH)

lgt.set_editor_property("enable_density_scaling", True)
varieties = unreal.Array(unreal.GrassVariety)

def make_variety(mesh_path, density, smin, smax):
    v = unreal.GrassVariety()
    v.set_editor_property("grass_mesh", unreal.load_asset(mesh_path))
    v.set_editor_property("grass_density", unreal.PerPlatformFloat(default=density))
    v.set_editor_property("grass_density_quality", unreal.PerQualityLevelFloat(default=density))
    v.set_editor_property("start_cull_distance", unreal.PerPlatformInt(default=8000))
    v.set_editor_property("start_cull_distance_quality", unreal.PerQualityLevelInt(default=8000))
    v.set_editor_property("end_cull_distance", unreal.PerPlatformInt(default=12000))
    v.set_editor_property("end_cull_distance_quality", unreal.PerQualityLevelInt(default=12000))
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

varieties.append(make_variety(
    "/Game/FoliagePack_Meshingun/Assets/Foliage/Mesh/GoundCover/SM_Grass_01a", 220.0, 0.8, 1.4))
varieties.append(make_variety(
    "/Game/FoliagePack_Meshingun/Assets/Foliage/Mesh/GoundCover/SM_DriedGrass_01a", 30.0, 0.7, 1.1))
lgt.set_editor_property("grass_varieties", varieties)
unreal.EditorAssetLibrary.save_asset(LGT_PATH)
print("LGT saved, varieties:", len(varieties))

# 2. Wire LandscapeGrassOutput into M_Landscape, driven by the Wild layer
MAT = "/Game/FoliagePack_Meshingun/Landscape/Material/M_Landscape"
mat = unreal.EditorAssetLibrary.load_asset(MAT)
mel = unreal.MaterialEditingLibrary

# NOTE: run once — no idempotence check (MaterialEditingLibrary cannot list expressions)
if True:
    layer_sample = mel.create_material_expression(
        mat, unreal.MaterialExpressionLandscapeLayerSample, -1200, 900)
    layer_sample.set_editor_property("parameter_name", "Wild")
    grass_out = mel.create_material_expression(
        mat, unreal.MaterialExpressionLandscapeGrassOutput, -900, 900)
    gi = unreal.GrassInput()
    gi.set_editor_property("name", "CoveGrass")
    gi.set_editor_property("grass_type", lgt)
    arr = unreal.Array(unreal.GrassInput)
    arr.append(gi)
    grass_out.set_editor_property("grass_types", arr)
    ok = mel.connect_material_expressions(layer_sample, "", grass_out, "CoveGrass")
    print("CONNECT:", ok)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset(MAT)
    print("MATERIAL recompiled + saved")
