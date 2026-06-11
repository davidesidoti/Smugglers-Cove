import warnings; warnings.simplefilter("ignore")
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# 1. Clear previous scatter (everything in Env/ folders)
doomed = [a for a in eas.get_all_level_actors()
          if str(a.get_folder_path()).startswith("Env")]
for a in doomed:
    eas.destroy_actor(a)
print("DELETED scatter:", len(doomed))

# 2. Re-import updated heightmap
imp = unreal.LandscapeService.import_heightmap(
    "Island", r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\island_1009.png")
print("REIMPORT:", imp.success, imp.error_message)

# 3. Repaint weights
from array import array
RES = 1009
for n in ["Wild", "Dirt", "Slope"]:
    raw = array("B")
    with open(rf"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\weight_{n}.raw", "rb") as f:
        raw.fromfile(f, RES * RES)
    ok = unreal.LandscapeService.set_weights_in_region(
        "Island", n, 0, 0, RES, RES, [x / 255.0 for x in raw])
    print("WEIGHTS", n, ok)
print("DONE")
