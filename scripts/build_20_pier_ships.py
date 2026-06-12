import warnings; warnings.simplefilter("ignore")
import unreal, math

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = ues.get_editor_world()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ignore = [a for a in eas.get_all_level_actors() if "Water" in a.get_class().get_name()]

def gz(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x, y, 30000), unreal.Vector(x, y, -30000),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ignore,
        unreal.DrawDebugTrace.NONE, True, unreal.LinearColor.RED, unreal.LinearColor.GREEN, 0.0)
    if hit:
        for v in hit.to_tuple():
            if isinstance(v, unreal.Vector):
                return v.z
    return None

M = "/Game/Smugglers_cove/meshes"
mesh = {}
for n, p in [("pier1", f"{M}/structures/SM_wooden_pier_section_01"),
             ("pier2", f"{M}/structures/SM_wooden_pier_section_02"),
             ("pier3", f"{M}/structures/SM_wooden_pier_section_03"),
             ("pier4", f"{M}/structures/SM_wooden_pier_section_04"),
             ("poles", f"{M}/structures/SM_wooden_pier_poles"),
             ("lantern", f"{M}/props/SM_wooden_lantern_01"),
             ("boat", f"{M}/ships/SM_boat_dutch_small_01"),
             ("pinnace", f"{M}/ships/SM_ship_pinnace"),
             ("pinnace_sails", f"{M}/ships/SM_ship_pinnace_sails"),
             ("crate", f"{M}/props/SM_wooden_crate_01"),
             ("barrels", f"{M}/props/SM_wooden_barrels_01_a")]:
    mesh[n] = unreal.EditorAssetLibrary.load_asset(p)
print("meshes loaded:", all(mesh.values()))
count = 0

def spawn(m, x, y, z, rot=(0, 0, 0), scale=(1, 1, 1), folder="Env/Pier"):
    global count
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                   unreal.Rotator(*rot))
    a.static_mesh_component.set_static_mesh(mesh[m])
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_folder_path(folder)
    count += 1
    return a

def lantern_light(x, y, z, folder="Env/Pier"):
    global count
    la = eas.spawn_actor_from_class(unreal.PointLight, unreal.Vector(x, y, z + 45))
    lc = la.get_components_by_class(unreal.PointLightComponent)[0]
    lc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    lc.set_editor_property("intensity", 180.0)
    lc.set_editor_property("light_color", unreal.Color(r=255, g=160, b=70, a=255))
    lc.set_editor_property("attenuation_radius", 900.0)
    lc.set_editor_property("cast_shadows", False)
    la.set_folder_path(folder)
    count += 1

# --- pier axis: root on the apron sand, head over deep water ---
sx, sy = 5040.0, 9576.0          # axis origin
ux, uy = 0.837, 0.548            # toward bay centre
yaw = math.degrees(math.atan2(uy, ux))
start_d = -600.0                 # dry sand (shoreline at d ~ -420)
print("root ground z:", gz(sx + ux * start_d, sy + uy * start_d))

SEG = 250.0
N = 12
kinds = ["pier1", "pier2", "pier3", "pier4"]
for i in range(N):
    dd = start_d + (i + 0.5) * SEG
    x, y = sx + ux * dd, sy + uy * dd
    spawn(kinds[i % 4], x, y, 0.0, (0, 0, yaw))
    # lantern every 3rd section on the left edge
    if i % 3 == 2:
        px_, py_ = -uy, ux
        lx, ly = x + px_ * 150, y + py_ * 150
        spawn("lantern", lx, ly, 115.0, (0, 0, yaw))
        lantern_light(lx, ly, 130.0)

# T-head: two sections across at the end
end_d = start_d + N * SEG
exx, eyy = sx + ux * (end_d + 120), sy + uy * (end_d + 120)
for s in (1, -1):
    px_, py_ = -uy, ux
    spawn(kinds[1], exx + px_ * 170 * s, eyy + py_ * 170 * s, 0.0, (0, 0, yaw + 90))
# cargo on the head
spawn("crate", exx, eyy, 105.0, (0, 0, yaw + 30), folder="Env/Pier/Props")
spawn("barrels", exx + px_ * 90, eyy + py_ * 90, 105.0, (0, 0, yaw), folder="Env/Pier/Props")

# --- ships ---
# small dutch boat moored on the right side of the pier head
bx = exx + uy * 420
by = eyy - ux * 420
spawn("boat", bx, by, 10.0, (0, 0, yaw - 95), folder="Env/Ships")
# pinnace anchored mid-basin (deep water)
pxw, pyw = 0.30 * 50400, 0.31 * 50400
print("pinnace ground z:", gz(pxw, pyw))
spawn("pinnace", pxw, pyw, 0.0, (0, 0, -55), folder="Env/Ships")
spawn("pinnace_sails", pxw, pyw, 0.0, (0, 0, -55), folder="Env/Ships")

print("PIER+SHIPS actors:", count)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("SAVED")
