import warnings; warnings.simplefilter("ignore")
import unreal

# 1. verify the template content arrived
ok = unreal.EditorAssetLibrary.does_asset_exist(
    "/Game/FPMovement/Player/Blueprints/BP_PlayerMode")
print("BP_PlayerMode exists:", ok)
info = unreal.BlueprintService.get_blueprint_info("/Game/FPMovement/Player/Blueprints/BP_PlayerMode")
print("mode info:", str(info)[:400])

# default pawn configured on the GameMode CDO
gm_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/FPMovement/Player/Blueprints/BP_PlayerMode")
cdo = unreal.get_default_object(gm_cls)
pawn = cdo.get_editor_property("default_pawn_class")
hud = cdo.get_editor_property("hud_class")
print("default pawn:", pawn.get_name() if pawn else None)
print("hud:", hud.get_name() if hud else None)

# 2. set L_Main's world-settings GameMode override
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ws = world.get_world_settings()
ws.set_editor_property("default_game_mode", gm_cls)
print("L_Main game mode override ->", gm_cls.get_name())

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
