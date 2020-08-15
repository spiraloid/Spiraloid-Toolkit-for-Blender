bl_info = {
        'name': 'AimAtSelected',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'View',
        'location': 'View > Aim at selected',
        'wiki_url': ''}

import bpy
import bmesh



isAimPivotCursor = False
isTogglePivotCursor = False

def main_aim(context):
    global isAimPivotCursor
    

    if (bpy.context.active_object.mode == 'EDIT'):


        # bm = bmesh.new()
        ob = bpy.context.active_object

        if ob.type == 'MESH':
            bm = bmesh.from_edit_mesh(ob.data)
            returnToEdgeMode = False
            returnToFaceMode = False
            old_cursor_loc =  bpy.context.scene.cursor.location.copy()

            activElem = bm.select_history.active
            if (activElem != None and type(activElem).__name__ == 'BMEdge'):
                returnToEdgeMode = True
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

            if (activElem != None and type(activElem).__name__ == 'BMFace'):
                returnToFaceMode = True
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

            for v in bm.verts:
                if (v.select == True):
                    bpy.ops.view3d.snap_cursor_to_selected()
                    if  bpy.context.scene.cursor.location ==  old_cursor_loc :
                        bpy.ops.view3d.snap_cursor_to_center()
                    else :
                        bpy.ops.view3d.view_center_cursor()
            
            if returnToFaceMode :
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

            if returnToEdgeMode :
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

        if ob.type == 'ARMATURE':
            old_cursor_loc =  bpy.context.scene.cursor.location.copy()
            if (bpy.context.active_object) :
                bpy.ops.view3d.snap_cursor_to_selected()
                if  bpy.context.scene.cursor.location ==  old_cursor_loc :
                    bpy.ops.view3d.snap_cursor_to_center()
                else :
                    bpy.ops.view3d.view_center_cursor()

        
                
    if (bpy.context.active_object.mode == 'OBJECT'):
        old_cursor_loc =  bpy.context.scene.cursor.location.copy()
        if (bpy.context.active_object) :
            bpy.ops.view3d.snap_cursor_to_selected()
            if  bpy.context.scene.cursor.location ==  old_cursor_loc :
                bpy.ops.view3d.snap_cursor_to_center()

            else :
                bpy.ops.view3d.view_center_cursor()








def main_toggle(context):
#    context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
    global isTogglePivotCursor

    
    if isTogglePivotCursor:
        context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        bpy.ops.view3d.snap_cursor_to_selected()
        
    if not isTogglePivotCursor:    
        context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        bpy.ops.view3d.snap_cursor_to_center()

    isTogglePivotCursor = not isTogglePivotCursor

                
class BR_OT_aim_at_selected(bpy.types.Operator):
    """Aim at Selected"""
    bl_idname = "view3d.aim_at_selected"
    bl_label = "Aim Selected"

    def execute(self, context):
        main_aim(context)
        return {'FINISHED'}


class BR_OT_toggle_pivots(bpy.types.Operator):
    """set individual origins"""
    bl_idname = "view3d.toggle_pivots"
    bl_label = "Toggle Local/Global"

    def execute(self, context):
        main_toggle(context)
        return {'FINISHED'}






def menu_draw(self, context):
    self.layout.operator(BR_OT_aim_at_selected.bl_idname)
    self.layout.operator(BR_OT_toggle_pivots.bl_idname)


def register():
    bpy.utils.register_class(BR_OT_aim_at_selected)
    bpy.utils.register_class(BR_OT_toggle_pivots)
    bpy.types.VIEW3D_MT_view.prepend(menu_draw)  

def unregister():
    bpy.utils.unregister_class(BR_OT_aim_at_selected)
    bpy.utils.unregister_class(BR_OT_toggle_pivots)
    bpy.types.VIEW3D_MT_view.remove(menu_draw)  

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_view.remove(menu_draw)

if __name__ == "__main__":
    register()
