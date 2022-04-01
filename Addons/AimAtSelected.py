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
import mathutils


isAimPivotCursor = False
isTogglePivotCursor = False

isAimUVPivotCursor = False
isToggleUVPivotCursor = False

old_snap_elements = []
old_snap_target = ""
old_use_snap_backface_culling = ""


def main_aim(self, context):
    if context.area.type == 'IMAGE_EDITOR':
        if bpy.context.area.ui_type == 'UV':
            selected_object = bpy.context.selected_objects[0]
            if selected_object:
                global isAimUVPivotCursor
                obj = bpy.context.active_object
                me = obj.data
                bm = bmesh.from_edit_mesh(me)
                selectedFaces = [f for f in bm.faces if f.select]
                selectedEdges = [e for e in bm.edges if e.select]
                selectedVerts = [v for v in bm.verts if v.select]
                uv_center_loc = (0.5, 0.5)
                if (selectedFaces or selectedEdges or selectedVerts):
                    old_uv_cursor_loc =  context.space_data.cursor_location.copy()
                    context.space_data.pivot_point = 'CURSOR'
                    bpy.ops.uv.snap_cursor(target='SELECTED')
                    if context.space_data.cursor_location == old_uv_cursor_loc :
                        # print(":::::::::::::::::::")
                        # print(old_uv_cursor_loc)
                        # print(context.space_data.cursor_location)
                        # print(":::::::::::::::::::")
                        context.space_data.cursor_location = uv_center_loc
                    else :
                        bpy.ops.uv.snap_cursor(target='SELECTED')
                        old_uv_cursor_loc =  context.space_data.cursor_location.copy()
                else :
                    context.space_data.cursor_location = uv_center_loc

    if bpy.context.area.type == 'VIEW_3D':
        global isAimPivotCursor
        
        objects = bpy.context.selected_objects
        if objects:
            context.view_layer.objects.active = objects[0]
            ob = bpy.context.active_object
            if (bpy.context.active_object.mode == 'EDIT'):
                # bm = bmesh.new()
                if ob.type == 'CURVE':
                    selected_knots = []
                    for subcurve in ob.data.splines:
                        for bezpoint in subcurve.bezier_points:
                            if bezpoint.select_control_point:
                                selected_knots.append(bezpoint)
                    old_cursor_loc =  bpy.context.scene.cursor.location.copy()
                    if len(selected_knots) != 0:
                        bpy.ops.view3d.snap_cursor_to_selected()
                        if bpy.context.scene.cursor.location ==  old_cursor_loc :
                            bpy.ops.view3d.snap_cursor_to_center()
                        else :
                            bpy.ops.view3d.view_center_cursor()



                if ob.type == 'MESH':
                    if bpy.context.active_object.data.total_vert_sel != 0:
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
                    else:
                        bpy.ops.view3d.view_center_cursor()
                if ob.type == 'ARMATURE':
                    old_cursor_loc =  bpy.context.scene.cursor.location.copy()
                    if (bpy.context.active_object) :
                        bpy.ops.view3d.snap_cursor_to_selected()
                        if  bpy.context.scene.cursor.location ==  old_cursor_loc :
                            bpy.context.scene.cursor.location = ob.location
                        else :
                            bpy.ops.view3d.view_center_cursor()

            if (bpy.context.active_object.mode == 'POSE'):
                old_cursor_loc =  bpy.context.scene.cursor.location.copy()
                selected_bones = bpy.context.selected_pose_bones
                if selected_bones is not None:
                    bpy.ops.view3d.snap_cursor_to_selected()
                    if bpy.context.scene.cursor.location ==  old_cursor_loc :
                        bpy.context.scene.cursor.location = ob.location
                else:
                    bpy.context.scene.cursor.location = ob.location
                bpy.ops.view3d.view_center_cursor()

                
            if (bpy.context.active_object.mode == 'OBJECT'):
                old_cursor_loc =  bpy.context.scene.cursor.location.copy()
                bpy.ops.view3d.snap_cursor_to_selected()
                if  bpy.context.scene.cursor.location ==  old_cursor_loc :
                    bpy.ops.view3d.snap_cursor_to_center()
                else :
                    bpy.ops.view3d.view_center_cursor()
        else :
            bpy.ops.view3d.view_center_cursor()


class BR_OT_surface_snap_activate(bpy.types.Operator):
    """Surface Snap Acivate"""
    bl_idname = "wm.surface_snap_activate"
    bl_label = "Surface Snap_Activate"

    def execute(self, context):
        global old_snap_elements
        global old_snap_target
        global old_use_snap_backface_culling

        # get current snap parameters
        old_snap_elements = bpy.context.scene.tool_settings.snap_elements
        old_snap_target = bpy.context.scene.tool_settings.snap_target
        old_use_snap_backface_culling = bpy.context.scene.tool_settings.use_snap_backface_culling

        # set snap parameters
        bpy.context.scene.tool_settings.snap_elements = {'FACE'}
        bpy.context.scene.tool_settings.snap_target = 'MEDIAN'
        bpy.context.scene.tool_settings.use_snap_backface_culling = True

        return {'FINISHED'}

class BR_OT_surface_snap_deactivate(bpy.types.Operator):
    """Surface Snap Dectivate"""
    bl_idname = "wm.surface_snap_deactivate"
    bl_label = "Surface Snap_Deactivate"

    def execute(self, context):
        global old_snap_elements
        global old_snap_target
        global old_use_snap_backface_culling

        # set snap parameters
        bpy.context.scene.tool_settings.snap_elements = old_snap_elements
        bpy.context.scene.tool_settings.snap_target = old_snap_target
        bpy.context.scene.tool_settings.use_snap_backface_culling = old_use_snap_backface_culling

        return {'FINISHED'}




def main_toggle(context):
    if context.area.type == 'IMAGE_EDITOR':
        if bpy.context.area.ui_type == 'UV':
            global isToggleUVPivotCursor
            uv_center_loc = (0.5, 0.5)

            if isToggleUVPivotCursor:
                # context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
                context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
                bpy.ops.uv.snap_cursor(target='SELECTED')
                
            if not isToggleUVPivotCursor:    
                context.space_data.pivot_point = 'CURSOR'
                context.space_data.cursor_location = uv_center_loc

            isToggleUVPivotCursor = not isToggleUVPivotCursor



    if bpy.context.area.type == 'VIEW_3D':
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
    bl_idname = "wm.aim_at_selected"
    bl_label = "Aim Selected"

    def execute(self, context):
        main_aim(self, context)
        return {'FINISHED'}


class BR_OT_toggle_pivots(bpy.types.Operator):
    """set individual origins"""
    bl_idname = "wm.toggle_pivots"
    bl_label = "Toggle Local/Global"

    def execute(self, context):
        main_toggle(context)
        return {'FINISHED'}






def menu_draw_view3d(self, context):
    self.layout.operator(BR_OT_aim_at_selected.bl_idname)
    self.layout.operator(BR_OT_toggle_pivots.bl_idname)

def menu_draw_uv(self, context):
    self.layout.operator(BR_OT_aim_at_selected.bl_idname)
    self.layout.operator(BR_OT_toggle_pivots.bl_idname)


def register():
    bpy.utils.register_class(BR_OT_aim_at_selected)
    bpy.utils.register_class(BR_OT_toggle_pivots)

    bpy.utils.register_class(BR_OT_surface_snap_activate)
    bpy.utils.register_class(BR_OT_surface_snap_deactivate)


    bpy.types.VIEW3D_MT_view.prepend(menu_draw_view3d)  
    bpy.types.IMAGE_MT_view.prepend(menu_draw_uv)  



def unregister():
    bpy.utils.unregister_class(BR_OT_aim_at_selected)
    bpy.utils.unregister_class(BR_OT_toggle_pivots)
    bpy.types.VIEW3D_MT_view.remove(menu_draw_view3d)  
    bpy.types.VIEW3D_MT_view.remove(menu_draw_uv)  

    bpy.utils.unregister_class(BR_OT_surface_snap_activate)
    bpy.utils.unregister_class(BR_OT_surface_snap_deactivate)


    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_view.remove(menu_draw_view3d)
        bpy.types.VIEW3D_MT_view.remove(menu_draw_uv)

if __name__ == "__main__":
    register()
