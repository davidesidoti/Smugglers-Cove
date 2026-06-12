import warnings; warnings.simplefilter("ignore")
import unreal

# 1. discover plugin classes
wp = [n for n in dir(unreal) if "waterphys" in n.lower()]
print("WaterPhysics classes:", wp)

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ocean = next(a for a in eas.get_all_level_actors()
             if a.get_class().get_name() == "WaterBodyOcean")

# 2. spawn the bridge actor that adds water physics to the UE water body
cls = None
for cand in ["WaterPhysics_WaterBody", "WaterPhysics_GenericWaterBody", "WaterPhysicsActor"]:
    cls = getattr(unreal, cand, None)
    if cls:
        print("using class:", cand)
        break
if cls is None:
    print("NO bridge actor class found - inspect:", wp)
else:
    existing = [a for a in eas.get_all_level_actors() if a.get_class().get_name().startswith("WaterPhysics")]
    if existing:
        actor = existing[0]
        print("bridge already in level:", actor.get_actor_label())
    else:
        actor = eas.spawn_actor_from_class(cls, unreal.Vector(0, 0, 0))
        print("SPAWNED:", actor.get_actor_label())
    # point it at the ocean
    for prop in ["water_bodies", "WaterBodies"]:
        try:
            arr = actor.get_editor_property(prop)
            arr.append(ocean)
            actor.set_editor_property(prop, arr)
            print("water_bodies set:", len(arr))
            break
        except Exception as e:
            print("prop", prop, "->", e)

# 3. make the moored small boat a physics body
boat = None
for a in eas.get_all_level_actors():
    if str(a.get_folder_path()) == "Env/Ships" and a.get_class().get_name() == "StaticMeshActor":
        sm = a.static_mesh_component.get_editor_property("static_mesh")
        if sm and sm.get_name() == "SM_boat_dutch_small_01":
            boat = a
            break
print("boat:", boat.get_actor_label() if boat else None)
if boat:
    comp = boat.static_mesh_component
    comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    comp.set_simulate_physics(True)
    comp.set_linear_damping(0.4)
    comp.set_angular_damping(0.8)
    boat.set_actor_location(unreal.Vector(boat.get_actor_location().x,
                                          boat.get_actor_location().y, 40.0), False, False)
    print("boat physics enabled, mass:", comp.get_mass())

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
