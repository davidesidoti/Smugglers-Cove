import warnings; warnings.simplefilter("ignore")
import unreal

SRC = "/Game/FoliagePack_Meshingun/Assets/Foliage/Mesh/GoundCover/SM_Grass_01a"
DST_DIR = "/Game/SmugglersCove/Env"
DST = DST_DIR + "/SM_CoveGrass"
GREEN_MI = "/Game/FoliagePack_Meshingun/Assets/Foliage/Material/GroundCover/MI_GreenGrass_Fo_01a"

# 1. Duplicate the grass mesh and give it the green material
if not unreal.EditorAssetLibrary.does_asset_exist(DST):
    ok = unreal.EditorAssetLibrary.duplicate_asset(SRC, DST)
    print("DUPLICATED:", bool(ok))
sm = unreal.EditorAssetLibrary.load_asset(DST)
mi = unreal.EditorAssetLibrary.load_asset(GREEN_MI)
sm.set_material(0, mi)
unreal.EditorAssetLibrary.save_asset(DST)
print("green material set on", DST)

# 2. Repoint the lush variety in the grass type
lgt = unreal.EditorAssetLibrary.load_asset("/Game/SmugglersCove/Env/LGT_CoveGrass")
varieties = lgt.get_editor_property("grass_varieties")
new_vars = unreal.Array(unreal.GrassVariety)
for v in varieties:
    mesh = v.get_editor_property("grass_mesh")
    if mesh and mesh.get_name() == "SM_Grass_01a":
        v.set_editor_property("grass_mesh", sm)
        print("variety repointed to SM_CoveGrass")
    new_vars.append(v)
lgt.set_editor_property("grass_varieties", new_vars)
unreal.EditorAssetLibrary.save_asset("/Game/SmugglersCove/Env/LGT_CoveGrass")
print("LGT saved")

# 3. Flush grass cache so it rebuilds with the new mesh
unreal.SystemLibrary.execute_console_command(
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),
    "grass.FlushCache")
print("grass cache flushed")
