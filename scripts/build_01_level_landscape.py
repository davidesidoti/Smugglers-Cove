import warnings; warnings.simplefilter("ignore")
import unreal

# 1. New blank level saved as /Game/Maps/L_Main
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ok = les.new_level("/Game/Maps/L_Main")
print("CREATED_LEVEL:", ok, "/Game/Maps/L_Main")

# 2. Landscape: 16x16 components, 63 quads, 1 section -> 1009x1009, ~1km at scale 100
# Origin at corner: offset by half extent so the island is centered on world origin
half = 1008 * 100 / 2.0  # 50400
res = unreal.LandscapeService.create_landscape(
    location=unreal.Vector(-half, -half, 0),
    rotation=unreal.Rotator(0, 0, 0),
    scale=unreal.Vector(100, 100, 100),
    sections_per_component=1,
    quads_per_section=63,
    component_count_x=16,
    component_count_y=16,
    landscape_label="Island",
)
print("LANDSCAPE:", res.success, res.actor_label, res.error_message)
