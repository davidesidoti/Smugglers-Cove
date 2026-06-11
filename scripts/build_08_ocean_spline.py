import warnings; warnings.simplefilter("ignore")
import unreal, json

with open(r"D:\Github\Smugglers-Cove\SmugglersCove\Saved\Heightmaps\ocean_spline.json") as f:
    pts = json.load(f)

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ocean = next(a for a in eas.get_all_level_actors()
             if a.get_class().get_name() == "WaterBodyOcean")
spline = ocean.get_components_by_class(unreal.SplineComponent)[0]

ocean.modify()
spline.modify()
vecs = [unreal.Vector(p["x"], p["y"], 0.0) for p in pts]
spline.set_spline_points(vecs, unreal.SplineCoordinateSpace.WORLD, True)
spline.set_closed_loop(True, True)
print("points now:", spline.get_number_of_spline_points(), "closed:", spline.is_closed_loop())

# force the water mesh to rebuild
try:
    ocean.rerun_construction_scripts()
    print("rerun_construction_scripts OK")
except Exception as e:
    print("rerun failed:", e)

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
