import warnings; warnings.simplefilter("ignore")
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# 1. UDS: animate time of day so the HeatClock has time to consume
uds = None
for a in eas.get_all_level_actors():
    if a.get_class().get_name().startswith("Ultra_Dynamic_Sky"):
        uds = a
        break
print("UDS:", uds.get_actor_label() if uds else None)
for prop, val in [("Animate Time of Day", True), ("Day Length", 20.0),
                  ("Night Length", 12.0)]:
    try:
        uds.set_editor_property(prop, val)
        print("set", prop, "=", val)
    except Exception as e:
        print("FAILED", prop, ":", e)
try:
    print("Time of Day now:", uds.get_editor_property("Time of Day"))
except Exception as e:
    print("read tod err:", e)

# 2. place the Heat actors
existing = [a.get_actor_label() for a in eas.get_all_level_actors()]
for bp_path, label, pos in [
        ("/Game/Core/Heat/BP_HeatClock", "HeatClock", unreal.Vector(1008, 6048, 700)),
        ("/Game/Core/Heat/BP_HeatTestHarness", "HeatTestHarness", unreal.Vector(1208, 6048, 700))]:
    if any(label in e for e in existing):
        print(label, "already in level")
        continue
    cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
    a = eas.spawn_actor_from_class(cls, pos)
    a.set_folder_path("Core/Heat")
    print("SPAWNED:", a.get_actor_label())

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
