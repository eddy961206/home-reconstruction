import bpy,os
r=os.path.dirname(os.path.abspath(__file__));bpy.ops.wm.open_mainfile(filepath=r+'/Home_Reconstruction.blend')
bpy.ops.object.select_all(action='DESELECT')
for o in list(bpy.context.scene.objects):
 if o.type=='CURVE':
  o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o.select_set(False)
bpy.ops.export_scene.gltf(filepath=r+'/Home_Reconstruction.glb',export_format='GLB',export_cameras=True,export_lights=True)
bpy.ops.export_scene.fbx(filepath=r+'/Home_Reconstruction.fbx',object_types={'MESH'},apply_unit_scale=True,axis_forward='-Z',axis_up='Y',bake_anim=False)
