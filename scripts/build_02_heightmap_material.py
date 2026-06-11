import warnings; warnings.simplefilter("ignore")
import unreal

# 1. Import island heightmap (exact resolution 1009x1009)
imp = unreal.LandscapeService.import_heightmap(
    "Island", r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png")
print("IMPORT:", imp.success, getattr(imp, "resolution", ""), imp.error_message)

# 2. Assign the FoliagePack landscape material (green variant)
mi = unreal.EditorAssetLibrary.load_asset(
    "/Game/FoliagePack_Meshingun/Landscape/Material/MI_Landscape_Green")
print("MI loaded:", mi is not None)
try:
    r = unreal.LandscapeService.set_landscape_material("Island", mi.get_path_name())
    print("SET_MATERIAL via service:", r)
except Exception as e:
    print("service set_material failed:", e)
    # fallback: set the property directly on the actor
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == "Island":
            a.set_editor_property("landscape_material", mi)
            print("SET_MATERIAL via property")
            break

# 3. Save level
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("LEVEL_SAVED")
