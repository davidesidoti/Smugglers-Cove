import warnings; warnings.simplefilter("ignore")
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
WARM = unreal.Color(r=255, g=147, b=65, a=255)   # keyword args: unreal.Color is BGRA positionally!
fixed = 0
for a in eas.get_all_level_actors():
    if a.get_class().get_name() != "PointLight":
        continue
    folder = str(a.get_folder_path())
    if not (folder.startswith("Env/Fires") or folder.startswith("Env/Buildings")):
        continue
    lc = a.get_components_by_class(unreal.PointLightComponent)[0]
    old_i = lc.get_editor_property("intensity")
    is_firepit = old_i > 4000
    lc.set_editor_property("light_color", WARM)
    lc.set_editor_property("intensity", 1500.0 if is_firepit else 800.0)
    lc.set_editor_property("attenuation_radius", 1800.0 if is_firepit else 1100.0)
    lc.set_editor_property("source_radius", 18.0)
    fixed += 1
print("lights fixed:", fixed)

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
