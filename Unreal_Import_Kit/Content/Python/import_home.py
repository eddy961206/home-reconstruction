"""Run from Unreal Editor Python console after opening the accompanying project.
Untested in Unreal: the authoring environment has no Unreal installation.
Creates a new map and imports the supplied FBX. Does not modify other projects.
"""
from pathlib import Path
import unreal
root=Path(__file__).resolve().parents[2]
source=root/'SourceAssets'/'Home_Reconstruction.fbx'
if not source.exists():raise RuntimeError('Missing SourceAssets/Home_Reconstruction.fbx')
map_path='/Game/HomeReconstruction/EstimatedHome'
if unreal.EditorAssetLibrary.does_asset_exist(map_path):
    raise RuntimeError('Map already exists; import into a fresh copy rather than overwrite your work.')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level.new_level(map_path)
task=unreal.AssetImportTask();task.filename=str(source);task.destination_path='/Game/HomeReconstruction/Meshes';task.automated=True;task.save=True;task.replace_existing=False
options=unreal.FbxImportUI();options.import_mesh=True;options.import_materials=True;options.import_textures=True;options.import_as_skeletal=False
options.static_mesh_import_data.combine_meshes=False
options.static_mesh_import_data.transform_vertex_to_absolute=True
options.static_mesh_import_data.generate_lightmap_u_vs=True
options.static_mesh_import_data.auto_generate_collision=False
options.static_mesh_import_data.convert_scene=True
options.static_mesh_import_data.convert_scene_unit=True
task.options=options
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
count=0
for path in task.imported_object_paths:
    asset=unreal.load_asset(path)
    if isinstance(asset,unreal.StaticMesh):
        actor=actors.spawn_actor_from_object(asset,unreal.Vector(0,0,0))
        actor.set_actor_label(asset.get_name());count+=1
# FBX material colors transfer; procedural Blender cloth/wood shaders require UE material recreation.
for name,loc,intensity in [('Room_ceiling',(165,170,240),1500),('Kitchen',(380,85,240),700),('Bathroom',(360,-70,225),350)]:
    light=actors.spawn_actor_from_class(unreal.PointLight,unreal.Vector(*loc))
    light.set_actor_label(name);light.point_light_component.set_intensity(intensity)
    light.point_light_component.set_editor_property('attenuation_radius',650.0)
level.save_current_level()
unreal.log('Imported {} meshes. Verify FBX axis/scale and material appearance before use. This is an estimated reconstruction, not a survey.'.format(count))
