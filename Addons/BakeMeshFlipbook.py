bl_info = {
        'name': 'BakeMeshFlipbook',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'Animation',
        'location': 'Object > Animation > Bake Mesh Flipbook',
        'wiki_url': ''}


import bpy
from math import *
from mathutils import *
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    CollectionProperty,
)
from bpy.types import (Panel,
                       PropertyGroup,
                       AddonPreferences
                       )



def empty_trash(self, context):
    for block in bpy.data.collections:
        if not block.users:
            bpy.data.collections.remove(block)

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

    for block in bpy.data.actions:
        if block.users == 0:
            bpy.data.actions.remove(block)

    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)

    for block in bpy.data.curves:
        if block.users == 0:
            bpy.data.curves.remove(block)

    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)

    for block in bpy.data.grease_pencils:
        if block.users == 0:
            bpy.data.grease_pencils.remove(block)

    for block in bpy.data.texts:
        if block.users == 0:
            bpy.data.texts.remove(block)

    for block in bpy.data.fonts:
        if block.users == 0:
            bpy.data.fonts.remove(block)

    return {'FINISHED'}

def scene_mychosenobject_poll(self, object):
    return object.type == 'MESH'

class BakeFlipbookPanelSettings(bpy.types.PropertyGroup):
    start_frame : bpy.props.IntProperty(name="Start Frame",  description="frame to start Flipbook", default=1 )
    end_frame : bpy.props.IntProperty(name="End Frame",  description="frame to end Flipbook", default=40 )
    frame_step : bpy.props.IntProperty(name="Frame Step",  description="Flipbook frame step", min=1, default=2 )
    decimate : bpy.props.BoolProperty(name="Decimate Frames",  description="decimate frames", default=True )
    boolean : bpy.props.BoolProperty(name="Boolean Frames",  description="boolean frames", default=False )
    apply_decimate : bpy.props.BoolProperty(name="Apply Decimation",  description="apply decimation to frames", default=True )
    decimate_ratio : FloatProperty(
        name="Decimate Ratio",
        description="Choose percentage to reduce mesh by",
        min=0.0 , max=1.0,
        default=0.33,
    )
    boolObject : bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=scene_mychosenobject_poll,
        name="Bool Mesh",         
        description="Choose a mesh to be subtracted from each frame."
    )
    boolStrategy : bpy.props.EnumProperty(
        name="Boolean Type", 
        description="Boolean parameters", 
        items={
            ("Difference","Difference", "Difference", 1),
            ("UNION", "UNION","UNION", 2),
            ("Intersect", "Intersect","Intersect", 3),
            },
        default="Difference"
    )

class BR_OT_bake_mesh_flipbook(bpy.types.Operator):
    """Bake selected object as a mesh per frame with animated visibility like a flipbook"""
    bl_idname = "BR_OT_bake_mesh_flipbook"
    bl_label = "Bake Mesh Flipbook..."
    bl_options = {'REGISTER', 'UNDO'}
    config = bpy.props.PointerProperty(type=BakeFlipbookPanelSettings)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bake_flipbook_panel_settings = scene.bake_flipbook_panel_settings

        strategy_row = layout.row(align=True)

        layout.prop(bake_flipbook_panel_settings, "start_frame")
        layout.prop(bake_flipbook_panel_settings, "end_frame")
        layout.separator()
        layout.prop(bake_flipbook_panel_settings, "frame_step")
        layout.prop(bake_flipbook_panel_settings, "decimate")
        d_row = layout.row(align=True)
        if bake_flipbook_panel_settings.decimate == True:
            layout.prop(bake_flipbook_panel_settings, "apply_decimate")
            layout.prop(bake_flipbook_panel_settings, "decimate_ratio")
            d_row.enabled = True
        else :
            d_row.enabled = False

        layout.prop(bake_flipbook_panel_settings, "boolean")
        b_row = layout.row(align=True)
        if bake_flipbook_panel_settings.boolean == True:
            layout.prop(bake_flipbook_panel_settings, "boolObject" )
            layout.prop(bake_flipbook_panel_settings, "boolStrategy" )
            b_row.enabled = True
        else :
            b_row.enabled = False

    def execute(self, context):          
        settings = context.scene.bake_flipbook_panel_settings
        flipbook_collection_name = "Flipbook"
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # cleanup previous bake collection 
        if bpy.data.collections.get(flipbook_collection_name) : 
            old_bake_collection = bpy.data.collections.get(flipbook_collection_name)
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[flipbook_collection_name]
            bpy.data.collections.remove(old_bake_collection)
            empty_trash(self, context)
            self.report({'INFO'}, 'Deleted Previous Flipbook collection!')

        flipbook_collection = bpy.data.collections.new(flipbook_collection_name)
        bpy.context.scene.collection.children.link(flipbook_collection)

        frame_start = settings.start_frame
        end_frame = settings.end_frame
        frame_step = settings.frame_step
        durationf = (end_frame - frame_start) / frame_step
        duration = int(durationf)

        selected_objects = bpy.context.selected_objects
        for ob in selected_objects:
            source_collection = ob.users_collection[0]            
            source_collection_name = source_collection.name         
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob

            bpy.context.scene.frame_set(frame_start)
            for i in range(duration):
                i = i * frame_step
                bpy.context.scene.frame_set((frame_start + i) + frame_step)

                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = ob
                ob.select_set(state=True)
                # bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'INVERSE_SQUARE', "proportional_size":0.101089, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})


                dupe = bpy.context.selected_objects
                dupe[0].name = ("frame_" + str(i))
                for mod in [m for m in dupe[0].modifiers]:
                    # bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)  #pre 2.90 syntax
                    bpy.ops.object.modifier_apply(modifier=mod.name)

                bpy.ops.object.particle_system_remove()

                if settings.decimate:
                        mod = bpy.data.objects[dupe[0].name].modifiers.new(name='Decimate',type='DECIMATE')
                        mod.decimate_type = 'DISSOLVE'
                        mod.angle_limit = 0.0872665

                        mod2 = bpy.data.objects[dupe[0].name].modifiers.new(name='Decimate',type='DECIMATE')
                        mod2.use_collapse_triangulate = True
                        mod2.ratio = settings.decimate_ratio
                        
                        if settings.apply_decimate:
                            bpy.ops.object.select_all(action='DESELECT')
                            dupe[0].select_set(state=True)
                            bpy.context.view_layer.objects.active =  dupe[0]
                            for mod in [m for m in  dupe[0].modifiers if m.type == 'DECIMATE']:
                                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name) #pre 2.90 syntax
                                bpy.ops.object.modifier_apply(modifier=mod.name)

                if settings.boolean and settings.boolObject is not "Null":
                    mod = bpy.data.objects[dupe[0].name].modifiers.new(name='Boolean',type='BOOLEAN')
                    mod.object = bpy.data.objects[settings.boolObject.name]
                    bpy.ops.object.select_all(action='DESELECT')
                    dupe[0].select_set(state=True)
                    bpy.context.view_layer.objects.active =  dupe[0]
                    for mod in [m for m in  dupe[0].modifiers if m.type == 'BOOLEAN']:
                        bpy.context.object.modifiers["Boolean"].operation = settings.boolStrategy
                        # bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                        bpy.ops.object.modifier_apply(modifier=mod.name)

                if settings.decimate:
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    bpy.ops.mesh.select_face_by_sides(number=6, type='GREATER', extend=False)
                    bpy.ops.mesh.delete(type='FACE')
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


                if not settings.shapekey:
                    cur_scalex = dupe[0].scale.x
                    cur_scaley = dupe[0].scale.y
                    cur_scalez = dupe[0].scale.z

                    dupe[0].scale.x = 0.001
                    dupe[0].scale.y = 0.001
                    dupe[0].scale.z = 0.001  
                    # dupe[0].hide_viewport = True
                    # dupe[0].keyframe_insert(data_path="hide_viewport", frame= frame_start + i - frame_step )
                    dupe[0].keyframe_insert(data_path="scale", frame =  (frame_start + i) - frame_step )

                    dupe[0].scale.x = cur_scalex
                    dupe[0].scale.y = cur_scaley
                    dupe[0].scale.z = cur_scalez  
                    # dupe[0].hide_viewport = False                
                    # dupe[0].keyframe_insert(data_path="hide_viewport", frame= frame_start + i)
                    dupe[0].keyframe_insert(data_path="scale", frame= frame_start + i)
                    # context.scene.frame_set(frame_start + i + frame_step - .001, subframe=0.001)
                    # dupe[0].keyframe_insert(data_path="scale", frame= (frame_start + i) + frame_step - .001)

                    dupe[0].scale.x = 0.001
                    dupe[0].scale.y = 0.001
                    dupe[0].scale.z = 0.001                 
                    # dupe[0].hide_viewport = True
                    # dupe[0].keyframe_insert(data_path="hide_viewport", frame= frame_start + i + frame_step)
                    dupe[0].keyframe_insert(data_path="scale", frame= (frame_start + i) + frame_step)
                    



                    bpy.data.collections[source_collection_name].objects.unlink(dupe[0])
                    bpy.data.collections[flipbook_collection_name].objects.link(dupe[0])

                    fcurves = dupe[0].animation_data.action.fcurves
                    for fcurve in fcurves:
                        for kf in fcurve.keyframe_points:
                            kf.interpolation = 'CONSTANT'
                else:
                    if i != 0:
                        bpy.ops.object.select_all(action='DESELECT')
                        dupe[0].select_set(state=True)
                        bpy.context.view_layer.objects.active =  dupe[0]
                        bpy.ops.object.join_shapes()
                        bpy.data.shape_keys["Key"].key_blocks["frame_10"].value = 1
                        bpy.ops.action.delete()






#         hold = 2
#         fBuff = 0
        
#         currentStart =  bpy.context.scene.frame_current
#         currentF =  bpy.context.scene.frame_current

#         # get objects selected in the viewport
#         viewport_selection = bpy.context.selected_objects

#         # get export objects
#         obj_list = viewport_selection
#         obj_list = [i for i in bpy.context.scene.objects]

#         # deselect all objects
#         bpy.ops.object.select_all(action='DESELECT')

#         for myobj in obj_list:
#             myobj.select_set(state=True)
#             bpy.context.view_layer.objects.active = myobj


#             # Clear all previous animation data
#             myobj.animation_data_clear()
            
#             if len(obj_list) > 0:
#                 for i in range(len(obj_list)):
#                     if (myobj == obj_list[i - 1]):

#                         fBuff = currentStart
                        
#                         # Set frame 
# #                        bpy.context.scene.frame_set(fBuff)

#                         # Set current scale
#                         myobj.scale.x = 1.0
#                         myobj.scale.y = 1.0
#                         myobj.scale.z = 1.0

#                         # Insert new keyframe for scale
#                         myobj.keyframe_insert(data_path="scale", frame = fBuff)

#                         fBuff = currentStart + hold

#                         # Insert new keyframe for scale
#                         myobj.keyframe_insert(data_path="scale", frame = fBuff)
                        
#                         fBuff = currentStart + hold + 1

#                         # Set current scale
#                         myobj.scale.x = 0.001
#                         myobj.scale.y = 0.001
#                         myobj.scale.z = 0.001

#                         # Insert new keyframe for scale
#                         myobj.keyframe_insert(data_path="scale", frame = fBuff)

#                         fBuff = currentStart - 1
                        
#                         # Insert new keyframe for scale
#                         myobj.keyframe_insert(data_path="scale", frame = fBuff)
                        
#                         fcurves = myobj.animation_data.action.fcurves
#                         for fcurve in fcurves:
#                             for kf in fcurve.keyframe_points:
#                                 kf.interpolation = 'CONSTANT'

                        
#                 currentStart =  currentStart + hold + 1              
#             myobj.select_set(state=False)
#             bpy.context.scene.frame_set(currentF)


        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



def menu_draw(self, context):
    self.layout.operator(BR_OT_bake_mesh_flipbook.bl_idname)



def register():
    bpy.utils.register_class(BR_OT_bake_mesh_flipbook)
    bpy.types.VIEW3D_MT_object_animation.append(menu_draw)  

    bpy.utils.register_class(BakeFlipbookPanelSettings)
    bpy.types.Scene.bake_flipbook_panel_settings = bpy.props.CollectionProperty(type=BakeFlipbookPanelSettings)

def unregister():
    bpy.utils.unregister_class(BR_OT_bake_mesh_flipbook)
    bpy.types.VIEW3D_MT_object_animation.remove(menu_draw)  
    bpy.utils.unregister_class(BakeFlipbookPanelSettings)

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_view.remove(menu_draw)

if __name__ == "__main__":
    register()


