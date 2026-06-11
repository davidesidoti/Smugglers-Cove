import warnings; warnings.simplefilter("ignore")
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# 1. Ultra Dynamic Sky (contains sun, moon, skylight, fog, clouds)
uds_cls = unreal.EditorAssetLibrary.load_blueprint_class(
    "/Game/UltraDynamicSky/Blueprints/Ultra_Dynamic_Sky")
sky = eas.spawn_actor_from_class(uds_cls, unreal.Vector(0, 0, 20000))
print("CREATED: UDS", sky.get_actor_label() if sky else "FAILED")

# 2. Water zone + ocean (Water plugin)
zone = eas.spawn_actor_from_class(unreal.WaterZone, unreal.Vector(0, 0, 0))
print("CREATED: WaterZone", zone.get_actor_label() if zone else "FAILED")
try:
    zone.set_editor_property("zone_extent", unreal.Vector2D(110000.0, 110000.0))
    print("zone_extent set")
except Exception as e:
    print("zone_extent failed:", e)

ocean = eas.spawn_actor_from_class(unreal.WaterBodyOcean, unreal.Vector(0, 0, 0))
print("CREATED: Ocean", ocean.get_actor_label() if ocean else "FAILED")

# 3. Player start on the village plateau (normalized (0.12, 0.26) -> world)
ps = eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(6048, 13104, 750))
print("CREATED: PlayerStart", ps.get_actor_label() if ps else "FAILED")

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("LEVEL_SAVED")
