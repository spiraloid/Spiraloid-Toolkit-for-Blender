bl_info = {
        'name': 'ApplyMeshPose',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'Pose',
        'location': 'W > Appy current pose as rest for armature and all parented objects',
        'wiki_url': ''}

import bpy

isBoneInherit = False

def getLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = getLayerCollection(layer, collName)
        if found:
            return found

# layer_collection = bpy.context.view_layer.layer_collection
# layerColl = getLayerCollection(layer_collection, 'My Collection')
# bpy.context.view_layer.active_layer_collection = layerColl



def main(self, context):
    obj = bpy.context.object
    layer_collection = bpy.context.view_layer.layer_collection
    current_collection = bpy.context.view_layer.active_layer_collection

    hasMultires = False
    hasShrinkwrap = False
    multires_max_level = 0

    if obj.type == 'ARMATURE':
        armt = obj.data
        layer = bpy.context.view_layer
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active = obj
        ch = [child for child in obj.children if child.type == 'MESH' and child.find_armature()]
        for ob in ch:
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            layer = bpy.context.view_layer
            layer.update()
            for mod in [m for m in ob.modifiers if m.type == 'SHRINKWRAP']:
                hasShrinkwrap = True
                for _mod in [_m for _m in ob.modifiers if _m.type == 'MULTIRES']:
                    hasMultires = True
                    # mod.sculpt_levels = 0
                    multires_max_level = _mod.render_levels
                    _mod.sculpt_levels = multires_max_level
                    bpy.ops.object.select_all(action='DESELECT')
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'INVERSE_SQUARE', "proportional_size":0.0570624, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
                    duplicated_detail = bpy.context.object

                    if mod.target is not None:
                        old_shrink_mod = mod.target
                        for o in bpy.context.scene.objects:
                            if o.name == (old_shrink_mod.name):
                                o.name = "delete_me"

                    duplicated_detail.name = (ob.name + "_detail")
                    bpy.ops.object.select_all(action='DESELECT')
                    duplicated_detail.select_set(state=True)
                    bpy.context.view_layer.objects.active = duplicated_detail
                    bpy.ops.object.apply_all_modifiers()

                    # organize sculpt meshes 
                    sculpt_collection = getLayerCollection(layer_collection, 'Sculpts')
                    if sculpt_collection is None:
                        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name="Sculpts")
                        # sculpt_collection = bpy.data.collections.new(name="Sculpts")
                        # bpy.context.scene.collection.children.link(sculpt_collection)
                        sculpt_collection = bpy.data.collections.get('Sculpts')
                        sculpt_collection.objects.link(duplicated_detail)

                        sculpt_collection = getLayerCollection(layer_collection, 'Sculpts')
                        bpy.context.view_layer.active_layer_collection = sculpt_collection
                        sculpt_collection.exclude = True


                    else:
                        # make detail mesh active
                        bpy.ops.object.select_all(action='DESELECT')
                        duplicated_detail.select_set(state=True)
                        bpy.context.view_layer.objects.active = duplicated_detail

                        # move active mesh into collection names 'Sculpts'
                        bpy.ops.collection.objects_remove_active()
                        sculpt_collection = bpy.data.collections.get('Sculpts')
                        sculpt_collection.objects.link(duplicated_detail)
                        sculpt_collection.exclude = True


                    if current_collection:
                        bpy.context.view_layer.active_layer_collection = current_collection
                        current_collection.exclude = False

                    print ("===========================")

                    # duplicated_detail.hide_viewport = True
                    # duplicated_detail.hide_render = True

                    bpy.ops.object.select_all(action='DESELECT')
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob

                    bpy.ops.object.multires_base_apply(modifier="Multires")
                    _mod.sculpt_levels = 0
                    _mod.levels = 0
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=_mod.name)                
                    self.report({'WARNING'}, 'Warning: applied Multires')

                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)                
                self.report({'WARNING'}, 'Warning:  applied shrinkwrap ')



            for mod in [m for m in ob.modifiers if m.type == 'ARMATURE']:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            ob.select_set(state=False)

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(state=True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            layer = bpy.context.view_layer
            layer.update()

        # apply pose to armature
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.armature_apply(selected=False)       
        bpy.ops.wm.context_collection_boolean_set(data_path_iter="selected_pose_bones", data_path_item="bone.use_inherit_scale", type='ENABLE')



        # rebuild armature
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        for ob in ch:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            ob.modifiers.new(name = 'Skeleton', type = 'ARMATURE')
            ob.modifiers['Skeleton'].object = obj

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        # reparent meshes
        for ob in ch:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(state=True)
            bpy.context.view_layer.objects.active = obj
            layer = bpy.context.view_layer
            layer.update()

            ob.select_set(state=True)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            layer = bpy.context.view_layer
            layer.update()

            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            layer = bpy.context.view_layer
            layer.update()


            for o in bpy.context.scene.objects:
                if o.name == (ob.name + "_detail"):

                    # add new multires modifier
                    new_multires = ob.modifiers.new(name = 'Multires', type = 'MULTIRES')
                    new_multires.quality = 10
                    new_multires.uv_smooth = 'NONE'
                    new_multires.subdivision_type = 'CATMULL_CLARK'
                    new_multires.show_only_control_edges = True
                    new_multires.use_creases = False
                    level = multires_max_level
                    if level > 0:
                        for i in range(0, level):
                            bpy.ops.object.multires_subdivide(modifier="Multires")
                    new_multires.sculpt_levels = multires_max_level
                    new_multires.levels = multires_max_level
                    layer.update()

                    # add new shrinkwrap modifier
                    bpy.ops.object.modifier_remove(modifier="Shrinkwrap")
                    new_shrink = ob.modifiers.new(name = 'Shrinkwrap', type = 'SHRINKWRAP')
                    new_shrink.target = bpy.data.objects[duplicated_detail.name]
                    new_shrink.show_on_cage = True
                    bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")

                    layer.update()

                    #set the multires back to lowest level.
                    new_multires.sculpt_levels = multires_max_level
                    new_multires.levels = multires_max_level


        #delete old shrinkwrap meshes
        for o in bpy.context.scene.objects:
            if "delete_me" in o.name:
                # sculpt_collection = bpy.data.collections.get('Sculpts')
                sculpt_collection =  getLayerCollection(layer_collection, 'Sculpts')
                bpy.context.view_layer.active_layer_collection = sculpt_collection
                bpy.context.view_layer.active_layer_collection.exclude = False

                bpy.ops.object.select_all(action='DESELECT')
                o.select_set(state=True)
                bpy.context.view_layer.objects.active = o
                bpy.ops.object.delete(use_global=False)
                bpy.context.view_layer.active_layer_collection.exclude = True


        #         tmp = o.users_collection
        #         tmp = getLayerCollection tmp.name)
        #         bpy.context.view_layer.active_layer_collection = tmp
        #         bpy.context.view_layer.active_layer_collection.exclude = False
        #         bpy.ops.object.select_all(action='DESELECT')
        #         o.select_set(state=True)
        #         bpy.context.view_layer.objects.active = o

        #         bpy.ops.object.delete(use_global=False)
        #         bpy.context.view_layer.active_layer_collection.exclude = True

        #         bpy.context.view_layer.active_layer_collection = current_collection


        # restore initial selection
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        isBoneInherit = False
        bone_inherit(self, context)


def bone_inherit(self, context):
    global isBoneInherit
    obj = bpy.context.object
    prevBoneSelect = bpy.context.selected_pose_bones

    print (prevBoneSelect)
    if obj is not None :
        if obj.type == 'ARMATURE':
            armt = obj.data
            boneNames = armt.bones.keys()
            myBones = armt.bones
            bpy.ops.pose.select_all(action='DESELECT')

            for poseBone in obj.pose.bones:
                poseBone.bone.select = True



            # for b, bone in enumerate(myBones):
            #     b.select = True
            if not isBoneInherit:
                bpy.ops.wm.context_collection_boolean_set(data_path_iter="selected_pose_bones", data_path_item="bone.use_inherit_scale", type='ENABLE')
                bpy.ops.wm.context_collection_boolean_set(data_path_iter="selected_pose_bones", data_path_item="bone.use_inherit_rotation", type='ENABLE')
                self.report({'INFO'}, 'Bones will inherit rotation and scale')

            else :
                bpy.ops.wm.context_collection_boolean_set(data_path_iter="selected_pose_bones", data_path_item="bone.use_inherit_scale", type='DISABLE')
                bpy.ops.wm.context_collection_boolean_set(data_path_iter="selected_pose_bones", data_path_item="bone.use_inherit_rotation", type='DISABLE')
                self.report({'INFO'}, 'Bones will NOT inherit rotation or scale')

            if prevBoneSelect is not None:
                bpy.ops.pose.select_all(action='DESELECT')
                for b in prevBoneSelect:
                    b.bone.select = True


    isBoneInherit = not isBoneInherit



class BR_OT_toggle_bone_inherit(bpy.types.Operator):
    """Set current pose and shape as rest bind shape"""
    bl_idname = "view3d.toggle_bone_inherit"
    bl_label = "Inherit Toggle All"

    def execute(self, context):
        bone_inherit(self, context)
        return {'FINISHED'}


class BR_OT_apply_mesh_pose(bpy.types.Operator):
    """Set current pose and shape as rest bind shape"""
    bl_idname = "view3d.apply_mesh_pose"
    bl_label = "Apply Pose as Rest Pose with Mesh"

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}




def menu_draw_apply(self, context):
    self.layout.operator(BR_OT_apply_mesh_pose.bl_idname)

def menu_draw_bone_settings(self, context):
    self.layout.operator(BR_OT_toggle_bone_inherit.bl_idname)

def register():
    bpy.utils.register_class(BR_OT_apply_mesh_pose)
    bpy.utils.register_class(BR_OT_toggle_bone_inherit)
    bpy.types.VIEW3D_MT_pose_apply.prepend(menu_draw_apply)
    bpy.types.VIEW3D_MT_bone_options_toggle.append(menu_draw_bone_settings)

def unregister():
    bpy.utils.unregister_class(BR_OT_apply_mesh_pose)
    bpy.utils.unregister_class(BR_OT_toggle_bone_inherit)
    bpy.types.VIEW3D_MT_pose_apply.remove(menu_draw_apply)
    bpy.types.VIEW3D_MT_bone_options_toggle.remove(menu_draw_bone_settings)


    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_pose_appy.remove(menu_draw)

if __name__ == "__main__":
    register()
