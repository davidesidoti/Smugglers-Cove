import warnings; warnings.simplefilter("ignore")
import unreal
from array import array

LAYERS = ["Wild", "Dirt", "Slope", "Puddle"]
BASE = "/Game/FoliagePack_Meshingun/Landscape/Layers"

# 1. Register all layers on the landscape
for n in LAYERS:
    r = unreal.LandscapeService.add_layer("Island", f"{BASE}/{n}_LayerInfo")
    print("ADD_LAYER", n, r)

# 2. Write weights from raw uint8 files (row-major 1009x1009)
RES = 1009
for n in ["Wild", "Dirt", "Slope"]:
    raw = array("B")
    with open(rf"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\weight_{n}.raw", "rb") as f:
        raw.fromfile(f, RES * RES)
    weights = [x / 255.0 for x in raw]
    ok = unreal.LandscapeService.set_weights_in_region("Island", n, 0, 0, RES, RES, weights)
    print("SET_WEIGHTS", n, ok)

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("LEVEL_SAVED")
