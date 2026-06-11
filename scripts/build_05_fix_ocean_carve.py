import warnings; warnings.simplefilter("ignore")
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()

# 1. Stop the ocean from sculpting the landscape
for a in actors:
    if a.get_class().get_name() == "WaterBodyOcean":
        comp = a.get_editor_property("water_body_component")
        try:
            comp.set_editor_property("affects_landscape", False)
            print("affects_landscape=False on", a.get_actor_label())
        except Exception as e:
            print("set affects_landscape failed:", e)

# 2. Delete the water brush manager left on the landscape
for a in actors:
    if "WaterBrushManager" in a.get_actor_label() or "BrushManager" in a.get_class().get_name():
        print("DELETING:", a.get_actor_label(), a.get_class().get_name())
        eas.destroy_actor(a)

# 3. Restore the island heightmap
imp = unreal.LandscapeService.import_heightmap(
    "Island", r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png")
print("REIMPORT:", imp.success, imp.error_message)

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("LEVEL_SAVED")
