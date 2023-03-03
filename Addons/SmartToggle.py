bl_info = {
        'name': 'SmartToggler',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'View',
        'location': 'View > Smart Toggle',
        'wiki_url': ''}

import bpy
previous_mode = None


def main_toggle(self, context):
    global previous_mode
    if context.area.type == 'IMAGE_EDITOR':
        if bpy.context.area.ui_type == 'UV':
            bpy.context.area.ui_type = 'VIEW'
        if bpy.context.area.ui_type == 'VIEW':
            bpy.context.area.ui_type = 'UV'

    if bpy.context.area.type == 'VIEW_3D':
        if bpy.context.active_object: 
            if (bpy.context.active_object.mode == 'EDIT'):

                # else:
                    # bpy.ops.object.mode_set(mode='OBJECT')

                if bpy.context.active_object.type == 'ARMATURE':
                    bpy.ops.object.mode_set(mode='POSE')
                    previous_mode = 'POSE'

                if bpy.context.active_object.type == 'MESH' or bpy.context.active_object.type == 'CURVE':
                    if previous_mode == 'SCULPT':
                        bpy.ops.object.mode_set(mode='SCULPT')

                    if previous_mode == 'WEIGHT_PAINT':
                        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                        previous_mode = 'WEIGHT_PAINT'


                if previous_mode == 'EDIT' or previous_mode == None:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    previous_mode = 'OBJECT'
                    

                if previous_mode == 'POSE' or previous_mode == 'WEIGHT_PAINT':
                    active_object = bpy.context.active_object
                    aa = []
                    if active_object.type == "MESH" or active_object.type == "CURVE":
                        for mod in active_object.modifiers:
                            if mod.type == "ARMATURE":
                                active_armature = mod.object 
                                if active_armature:
                                    aa.append(active_armature)
                        if aa:
                            bpy.ops.object.mode_set(mode='OBJECT')
                            bpy.ops.object.select_all(action='DESELECT')
                            for a in aa:
                                a.select_set(state=True)
                                bpy.context.view_layer.objects.active = a
                            bpy.ops.object.mode_set(mode='POSE')
                            previous_mode = None

                return {'FINISHED'}

            if (bpy.context.active_object.mode == 'SCULPT'):
                previous_mode = 'SCULPT'
                bpy.ops.object.mode_set(mode='EDIT')
                print (previous_mode)
                return {'FINISHED'}

            if (bpy.context.active_object.mode == 'OBJECT'):
                if bpy.context.active_object.type == 'ARMATURE':
                    bpy.ops.object.mode_set(mode='EDIT')
                    previous_mode = 'EDIT'

                if bpy.context.active_object.type == 'MESH' or bpy.context.active_object.type == 'CURVE':
                    bpy.ops.object.mode_set(mode='EDIT')
                    previous_mode = 'EDIT'


                return {'FINISHED'}
                    
            if (bpy.context.active_object.mode == 'POSE'):
                arm = bpy.context.active_object
                selected_bones = bpy.context.selected_pose_bones
                if selected_bones:
                    ch = []
                    for laob in bpy.data.objects:
                        if laob.visible_get():
                            if laob.type == "MESH" or laob.type == "CURVE":
                                for mod in laob.modifiers:
                                    if mod.type == "ARMATURE":
                                        if mod.object == arm:
                                            ch.append(laob)
                    if not ch:
                        bpy.ops.object.mode_set(mode='EDIT')
                    else:
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.select_all(action='DESELECT')
                        for mesh in ch:
                            mesh.select_set(state=True)
                            bpy.context.view_layer.objects.active = mesh
                        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                        bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[selected_bones[0].name]
                        bpy.context.object.data.use_paint_mask_vertex = False
                        previous_mode = 'POSE'
                        
                        return {'FINISHED'}
                else:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    arm.select_set(state=True)
                    bpy.context.view_layer.objects.active = arm
                    return {'FINISHED'}

            if (bpy.context.active_object.mode == 'WEIGHT_PAINT'):
                selected_objects = bpy.context.selected_objects
                ar = []
                for obj in selected_objects:
                    for mod in obj.modifiers:
                        if mod.type == "ARMATURE":
                            if mod.object:
                                ar.append(mod.object)
                if not ar:
                    bpy.ops.object.mode_set(mode='OBJECT')
                else:
                    if previous_mode == 'POSE':
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                        bpy.context.object.data.use_paint_mask_vertex = True
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.vertex_group_select()
                        previous_mode = 'WEIGHT_PAINT'
                    else:
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.select_all(action='DESELECT')
                        for arm in ar:
                            arm.select_set(state=True)
                            bpy.context.view_layer.objects.active = arm
                        bpy.ops.object.mode_set(mode='POSE')
                        # previous_mode = None
                    return {'FINISHED'}


                
class BR_OT_smart_toggle(bpy.types.Operator):
    """Smart Toggle between modes"""
    bl_idname = "wm.smart_toggle"
    bl_label = "Smart Toggle"

    def execute(self, context):
        main_toggle(self, context)
        return {'FINISHED'}

def menu_draw_view3d(self, context):
    self.layout.operator(BR_OT_smart_toggle.bl_idname)

def menu_draw_uv(self, context):
    self.layout.operator(BR_OT_smart_toggle.bl_idname)


def register():
    bpy.utils.register_class(BR_OT_smart_toggle)

    bpy.types.VIEW3D_MT_view.append(menu_draw_view3d)  
    bpy.types.IMAGE_MT_view.append(menu_draw_uv)  



def unregister():
    bpy.utils.unregister_class(BR_OT_smart_toggle)
    bpy.types.VIEW3D_MT_view.remove(menu_draw_view3d)  
    bpy.types.VIEW3D_MT_view.remove(menu_draw_uv)  

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_view.remove(menu_draw_view3d)
        bpy.types.VIEW3D_MT_view.remove(menu_draw_uv)

if __name__ == "__main__":
    register()
