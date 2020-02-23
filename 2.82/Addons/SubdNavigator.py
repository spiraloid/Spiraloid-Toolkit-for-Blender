bl_info = {
        'name': 'Subd Navigator',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'View',
        'location': 'View > SubD More/Less/Toggle',
        'wiki_url': ''}

import bpy

isToggleSubd = True
currentSubdLevel = 0

def main_decrease(context):
    for obj in bpy.context.scene.objects:
        if obj.visible_get and obj.type == 'MESH':
            for mod in [m for m in obj.modifiers if m.type == 'MULTIRES']:
                mod_next_level = mod.levels - 1
                if mod_next_level >= 0:
                    mod.levels = mod_next_level
                    mod.sculpt_levels = mod_next_level
            for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:
                mod_next_level = mod.levels - 1
                if mod_next_level >= 0:
                    mod.levels = mod_next_level
                    bpy.context.space_data.overlay.show_wireframes = False
                else :
                    bpy.context.space_data.overlay.show_wireframes = True

    return {'FINISHED'}

def main_increase(context):
    for obj in bpy.context.scene.objects:
        for mod in [m for m in obj.modifiers if m.type == 'MULTIRES']:
            mod_max_level = mod.render_levels
            mod_next_level = mod.levels + 1
            if mod_next_level <= mod_max_level:
                mod.levels = mod_next_level
                mod.sculpt_levels = mod_next_level
        for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:
            mod_max_level = mod.render_levels
            mod_next_level = mod.levels + 1
            if mod_next_level <= mod_max_level:
                mod.levels = mod_next_level
    bpy.context.space_data.overlay.show_wireframes = False
    return {'FINISHED'}



def main_subdivide(context):
    s = bpy.context.object
    if bpy.context.mode == 'OBJECT' or bpy.context.mode == 'POSE':
        for obj in bpy.context.scene.objects:
            if obj.visible_get and  obj.type == 'MESH':
                s_modifier_count = len([m for m in obj.modifiers if m.type == 'SUBSURF'])
                m_modifier_count = len([m for m in obj.modifiers if m.type == 'MULTIRES']) 
                modifier_count = m_modifier_count + s_modifier_count
                if modifier_count == 0:
                        obj.modifiers.new(name = 'Subdivision', type = 'SUBSURF')
                        bpy.ops.object.select_all(action='DESELECT')
                        obj.select_set(state=True)
                        bpy.context.view_layer.objects.active = obj
                        bpy.ops.object.shade_smooth()
                        obj.data.use_auto_smooth = True
                        obj.data.auto_smooth_angle = 1.0472

    if bpy.context.mode == 'SCULPT':
        obj = s
        s_modifier_count = len([m for m in obj.modifiers if m.type == 'SUBSURF'])
        m_modifier_count = len([m for m in obj.modifiers if m.type == 'MULTIRES']) 
        modifier_count = m_modifier_count + s_modifier_count
        if modifier_count == 0:
            mod = obj.modifiers.new(name = 'Multires', type = 'MULTIRES')
            mod.quality = 6
            mod.uv_smooth = 'NONE'
            mod.subdivision_type = 'CATMULL_CLARK'
            mod.show_only_control_edges = True
            mod.use_creases = False
            level = 4
            if level > 0:
                for i in range(0, level):
                    bpy.ops.object.multires_subdivide(modifier="Multires")
            bpy.ops.object.shade_smooth()
            bpy.ops.object.mode_set(mode='SCULPT', toggle=False)
            main_toggle(context)
            main_toggle(context)

    for obj in bpy.context.scene.objects:
        for mod in [m for m in obj.modifiers if m.type == 'MULTIRES']:
            mod_max_level = mod.render_levels
            mod_next_level = mod.levels + 1
            if mod_next_level <= mod_max_level:
                mod.levels = mod_next_level
                mod.sculpt_levels = mod_next_level
        for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:
            mod_max_level = mod.render_levels
            mod_next_level = mod.levels + 1
            if mod_next_level <= mod_max_level:
                mod.levels = mod_next_level


    if bpy.context.mode == 'OBJECT' or bpy.context.mode == 'POSE':
        if s is not None :
            bpy.ops.object.select_all(action='DESELECT')
            s.select_set(state=True)
            bpy.context.view_layer.objects.active = s
    return {'FINISHED'}

def main_toggle(context):
    global isToggleSubd
    global currentSubdLevel
    my_areas = bpy.context.workspace.screens[0].areas
    my_shading = 'WIREFRAME'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
    bpy.context.space_data.overlay.show_overlays = True
    bpy.context.space_data.overlay.show_floor = True
    bpy.context.space_data.overlay.show_axis_x = True
    bpy.context.space_data.overlay.show_axis_y = True
    bpy.context.space_data.overlay.show_outline_selected = True
    bpy.context.space_data.overlay.show_cursor = True
    bpy.context.space_data.overlay.show_extras = True
    bpy.context.space_data.overlay.show_relationship_lines = True
    bpy.context.space_data.overlay.show_bones = True
    bpy.context.space_data.overlay.show_motion_paths = True
    bpy.context.space_data.overlay.show_object_origins = True
    bpy.context.space_data.overlay.show_annotation = True
    bpy.context.space_data.overlay.show_text = True
    bpy.context.space_data.overlay.show_text = True


    for obj in bpy.context.scene.objects:
        if obj.visible_get and  obj.type == 'MESH':
            for mod in [m for m in obj.modifiers if m.type == 'MULTIRES']:
                mod_max_level = mod.render_levels
                if isToggleSubd:
                    currentSubdLevel = mod.levels
                    mod.levels = mod_max_level
                    mod.sculpt_levels = mod_max_level
                if not isToggleSubd:
                    mod.levels = currentSubdLevel
                    mod.sculpt_levels = currentSubdLevel
                    if currentSubdLevel != 0:
                        bpy.context.space_data.overlay.show_wireframes = False


            for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:
                mod_max_level = mod.render_levels
                if isToggleSubd:
                    currentSubdLevel = mod.levels
                    mod.levels = mod_max_level
                if not isToggleSubd:
                    mod.levels = currentSubdLevel
                    if currentSubdLevel != 0:
                        bpy.context.space_data.overlay.show_wireframes = False

            if isToggleSubd:
                bpy.context.space_data.overlay.show_overlays = True
                bpy.context.space_data.overlay.show_floor = False
                bpy.context.space_data.overlay.show_axis_x = False
                bpy.context.space_data.overlay.show_axis_y = False
                bpy.context.space_data.overlay.show_outline_selected = False
                bpy.context.space_data.overlay.show_cursor = False
                bpy.context.space_data.overlay.show_extras = False
                bpy.context.space_data.overlay.show_relationship_lines = False
                bpy.context.space_data.overlay.show_bones = False
                bpy.context.space_data.overlay.show_motion_paths = False
                bpy.context.space_data.overlay.show_object_origins = False
                bpy.context.space_data.overlay.show_annotation = False
                bpy.context.space_data.overlay.show_text = False
                bpy.context.space_data.overlay.show_text = False

                if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
                    bpy.context.scene.eevee.use_gtao = True
                    bpy.context.scene.eevee.use_bloom = True
                    bpy.context.scene.eevee.use_ssr = True
                    bpy.context.space_data.overlay.show_overlays = False
                    my_shading =  'MATERIAL'

                if bpy.context.scene.render.engine == 'CYCLES':
                    my_shading =  'RENDERED'

                
            if not isToggleSubd:    
                bpy.context.space_data.overlay.show_overlays = True
                bpy.context.space_data.overlay.show_floor = True
                bpy.context.space_data.overlay.show_axis_x = True
                bpy.context.space_data.overlay.show_axis_y = True
                bpy.context.space_data.overlay.show_outline_selected = True
                bpy.context.space_data.overlay.show_cursor = True
                bpy.context.space_data.overlay.show_extras = True
                bpy.context.space_data.overlay.show_relationship_lines = True
                bpy.context.space_data.overlay.show_bones = True
                bpy.context.space_data.overlay.show_motion_paths = True
                bpy.context.space_data.overlay.show_object_origins = True
                bpy.context.space_data.overlay.show_annotation = True
                bpy.context.space_data.overlay.show_text = True
                bpy.context.space_data.overlay.show_text = True
                bpy.context.space_data.shading.color_type = 'RANDOM'

                my_shading = 'SOLID'

            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading



            for image in bpy.data.images:
                image.reload()

    isToggleSubd = not isToggleSubd
    return {'FINISHED'}

class BR_OT_subdivide_visible(bpy.types.Operator):
    """increase sudvision levels for visible objects"""
    bl_idname = "view3d.subdivide_visible"
    bl_label = "Subdivide Visible"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_subdivide(context)
        return {'FINISHED'}
                
class BR_OT_subd_decrease(bpy.types.Operator):
    """decrease sudvision levels for visible objects"""
    bl_idname = "view3d.subd_decrease"
    bl_label = "SubD Less"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_decrease(context)
        return {'FINISHED'}


class BR_OT_subd_increase(bpy.types.Operator):
    """increase sudvision levels for visible objects"""
    bl_idname = "view3d.subd_increase"
    bl_label = "SubD More"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_increase(context)
        return {'FINISHED'}

class BR_OT_subd_toggle(bpy.types.Operator):
    """Toggle All To Lowest/Highest Sudvision"""
    bl_idname = "view3d.subd_toggle"
    bl_label = "Toggle Workmode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True #context.space_data.type == 'VIEW_3D'

    def execute(self, context):
        main_toggle(context)
        return {'FINISHED'}


def menu_draw(self, context):
    layout = self.layout
    layout.separator()
    self.layout.operator(BR_OT_subdivide_visible.bl_idname)
    self.layout.operator(BR_OT_subd_increase.bl_idname)
    self.layout.operator(BR_OT_subd_decrease.bl_idname)
    self.layout.operator(BR_OT_subd_toggle.bl_idname)


def register():
    bpy.utils.register_class(BR_OT_subdivide_visible)
    bpy.utils.register_class(BR_OT_subd_increase)
    bpy.utils.register_class(BR_OT_subd_decrease)
    bpy.utils.register_class(BR_OT_subd_toggle)
    bpy.types.VIEW3D_MT_view.append(menu_draw)  

def unregister():
    bpy.utils.unregister_class(BR_OT_subdivide_visible)
    bpy.utils.unregister_class(BR_OT_subd_increase)
    bpy.utils.unregister_class(BR_OT_subd_decrease)
    bpy.utils.unregister_class(BR_OT_subd_toggle)
    bpy.types.VIEW3D_MT_view.remove(menu_draw)  

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_view.remove(menu_draw)

if __name__ == "__main__":
    register()
