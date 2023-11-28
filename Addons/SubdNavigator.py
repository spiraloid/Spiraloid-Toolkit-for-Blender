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
isWireframe = False
currentSubdLevel = 0
previous_mode = 'EDIT'
previous_selection = ""


def operator_exists(idname):
    names = idname.split(".")
    print(names)
    a = bpy.ops
    for prop in names:
        a = getattr(a, prop)
    try:
        name = a.__repr__()
    except Exception as e:
        print(e)
        return False
    return True


def automap(mesh_objects):
    # UV map target_object if no UV's present
    for mesh_object in mesh_objects:
        if mesh_object.type == 'MESH':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.select_all(action='DESELECT')
            mesh_object.select_set(state=True)
            bpy.context.view_layer.objects.active = mesh_object
            if not len( mesh_object.data.uv_layers ):
                bpy.ops.mesh.uv_texture_add()
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.cube_project(cube_size=10, scale_to_bounds=True)

    #select all meshes and pack into one UV set together
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.select_all(action='DESELECT')
    for mesh_object in mesh_objects:
        mesh_object.select_set(state=True)
        bpy.context.view_layer.objects.active = mesh_object

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.ui_type = 'UV'
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                        bpy.context.scene.tool_settings.use_uv_select_sync = True
                        bpy.ops.uv.select_all(action='SELECT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        if operator_exists("uvpackmaster2"):
                            bpy.context.scene.uvp2_props.pack_to_others = False
                            bpy.context.scene.uvp2_props.margin = 0.01
                            bpy.context.scene.uvp2_props.rot_step = 5
                            bpy.ops.uvpackmaster2.uv_measure_area()
                            bpy.ops.uv.average_islands_scale()
                            bpy.ops.uv.pack_islands(override , margin=0.005)
                            bpy.ops.uvpackmaster2.uv_pack()
                        else:
                            bpy.ops.uv.average_islands_scale(override)
                            bpy.ops.uv.pack_islands(override , margin=0.005)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    return {'FINISHED'} 


def main_decrease(context):
    is_max_subd = False

    # set any LOD properties on any objects
    control_object = ""
    lod_val = ""
    has_lod_controller = ""
    lod_property_string = "LOD"
    objects = bpy.context.scene.objects
    for cobj in objects:
        has_lod_controller = cobj.get(lod_property_string)
        if has_lod_controller is not None:
            control_object = cobj
            lod_val = control_object[lod_property_string]
    if control_object :
        lod_next_level =  lod_val -1
        if lod_next_level >= 0:
            control_object["LOD"] = lod_next_level
        control_object.hide_render = control_object.hide_render


    for obj in bpy.context.scene.objects:
        if obj.visible_get and obj.type == 'MESH':
            for mod in [m for m in obj.modifiers if m.type == 'MULTIRES']:
                mod_next_level = mod.levels - 1
                if mod_next_level >= 0:
                    mod.levels = mod_next_level
                    mod.sculpt_levels = mod_next_level

                if mod_next_level != mod.render_levels:
                    for mod in [m for m in obj.modifiers if m.type == 'DECIMATE' or m.type == 'TRIANGULATE']:
                        mod.show_viewport = False


            for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:
                showing_decimators = False

                mod_next_level = mod.levels - 1

                    # bpy.context.space_data.overlay.show_wireframes = False
                if mod.levels == mod.render_levels:
                    for dmod in [m for m in obj.modifiers if m.type == 'DECIMATE' or m.type == 'TRIANGULATE']:
                        if dmod.show_viewport == True:
                            showing_decimators = True
                            
                if showing_decimators:
                    for dmod in [m for m in obj.modifiers if m.type == 'DECIMATE' or m.type == 'TRIANGULATE']:
                        dmod.show_viewport = False
                        mod_next_level = mod.render_levels
                else:
                    mod_next_level = mod_next_level

                if mod_next_level >= 0:
                    mod.levels = mod_next_level
                        

                if mod_next_level == 0:
                    # bpy.context.space_data.overlay.show_wireframes = True
                    for dmod in [m for m in obj.modifiers if m.type == 'DECIMATE'  or m.type == 'TRIANGULATE']:
                        dmod.show_viewport = False

    return {'FINISHED'}

def main_increase(context):
    is_decimated = False
    is_max_subd = False

    # set any LOD properties on any objects
    control_object = ""
    lod_val = ""
    has_lod_controller = ""
    lod_property_string = "LOD"
    objects = bpy.context.scene.objects
    for cobj in objects:
        has_lod_controller = cobj.get(lod_property_string)
        if has_lod_controller is not None:
            control_object = cobj
            lod_val = control_object[lod_property_string]
    if control_object :
        lod_next_level =  lod_val + 1
        if lod_next_level <= 2:
            control_object["LOD"] = lod_next_level
        control_object.hide_render = control_object.hide_render


    for obj in bpy.context.scene.objects:
        s_modifier_count = len([m for m in obj.modifiers if m.type == 'SUBSURF'])
        d_modifier_count = len([m for m in obj.modifiers if m.type == 'DECIMATE'])
        m_modifier_count = len([m for m in obj.modifiers if m.type == 'MULTIRES']) 
        modifier_count = m_modifier_count + s_modifier_count + d_modifier_count

        if modifier_count != 0:
            for mod in [m for m in obj.modifiers if m.type == 'MULTIRES']:
                mod_max_level = mod.render_levels
                mod_next_level = mod.levels + 1
                if mod_next_level <= mod_max_level:
                    mod.levels = mod_next_level
                    mod.sculpt_levels = mod_next_level

                if mod_next_level == mod_max_level:
                    for mod in [m for m in obj.modifiers if m.type == 'DECIMATE' or m.type == 'TRIANGULATE']:
                        mod.show_viewport = not mod.show_viewport

            for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:
                mod_max_level = mod.render_levels
                mod_next_level = mod.levels + 1
                if mod_next_level <= mod_max_level:
                    mod.levels = mod_next_level
                else :
                    is_max_subd = True
                # if mod_next_level == mod_max_level:

            if is_max_subd:
                
                for mod in [m for m in obj.modifiers if m.type == 'DECIMATE' or m.type == 'TRIANGULATE']:
                    is_decimated = True
                    if not mod.show_viewport :
                        mod.show_viewport = not mod.show_viewport
                    



                if is_decimated:
                    for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:              
                            # optimized_mod_next_level = mod.levels - 1
                            optimized_mod_next_level = mod.levels
                            mod.levels = optimized_mod_next_level

    # bpy.context.space_data.overlay.show_wireframes = False
    return {'FINISHED'}




def main_subdivide(self, context):
    s = bpy.context.object
    # selected_objects = bpy.context.scene.objects
    selected_objects = bpy.context.selected_objects
    if bpy.context.mode == 'OBJECT' or bpy.context.mode == 'POSE':
        for obj in selected_objects:
            if obj.visible_get and  obj.type == 'MESH':

                for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:
                    obj.modifiers.remove(mod)

                for mod in [m for m in obj.modifiers if m.type == 'DECIMATE' or m.type == 'TRIANGULATE']:
                    obj.modifiers.remove(mod)


                d_modifier_count = len([m for m in obj.modifiers if m.type == 'DECIMATE'])
                s_modifier_count = len([m for m in obj.modifiers if m.type == 'SUBSURF'])
                m_modifier_count = len([m for m in obj.modifiers if m.type == 'MULTIRES']) 
                modifier_count = m_modifier_count + s_modifier_count + d_modifier_count


                if modifier_count == 0:
                    mod = obj.modifiers.new(name = 'Subdivision', type = 'SUBSURF')
                    mod.levels = 2
                    mod.render_levels = 2

                    # mod = obj.modifiers.new(name = 'Multires', type = 'MULTIRES')
                    # bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')
                    # bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')

                    mod.uv_smooth = 'NONE'
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(state=True)
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.shade_smooth()
                    obj.data.use_auto_smooth = True
                    obj.data.auto_smooth_angle = 1.0472

                    mod = obj.modifiers.new(name = 'Decimate', type = 'DECIMATE')
                    mod.decimate_type = 'DISSOLVE'
                    mod.angle_limit = 0.00349066
                    mod.delimit = {'SEAM'}
                    mod.use_dissolve_boundaries = False

                    mod = obj.modifiers.new(name = 'Decimate', type = 'DECIMATE')
                    mod.decimate_type = 'COLLAPSE'
                    mod.use_collapse_triangulate = False
                    mod.ratio = 0.33
                
                    mod = obj.modifiers.new(name = 'Triangulate', type = 'TRIANGULATE')
                    mod.quad_method = 'BEAUTY'
                    mod.ngon_method = 'CLIP'


                for mod in [m for m in obj.modifiers if m.type == 'DECIMATE' or m.type == 'TRIANGULATE']:
                    mod.show_viewport = not mod.show_viewport


    if bpy.context.mode == 'SCULPT':
        obj = s
        s_modifier_count = len([m for m in obj.modifiers if m.type == 'SUBSURF'])
        m_modifier_count = len([m for m in obj.modifiers if m.type == 'MULTIRES']) 
        modifier_count = m_modifier_count + s_modifier_count
        if modifier_count == 0:
            mod = obj.modifiers.new(name = 'Multires', type = 'MULTIRES')
            mod.quality = 6
            mod.uv_smooth = 'NONE'
            # mod.show_only_control_edges = True
            mod.use_creases = False
            level = 5
            if level > 0:
                for i in range(0, level):
                    bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.shade_smooth()
            bpy.ops.object.mode_set(mode='SCULPT', toggle=False)
            # toggle_workmode(self,context)
            # toggle_workmode(self,context)
            mod.sculpt_levels = 5

    for obj in bpy.context.scene.objects:
        for mod in [m for m in obj.modifiers if m.type == 'MULTIRES']:
            mod_max_level = mod.render_levels
            mod_next_level = mod.levels + 1
            if mod_next_level <= mod_max_level:
                mod.levels = mod_next_level
                mod.sculpt_levels = mod_max_level
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




class BR_OT_subdivide_selected(bpy.types.Operator):
    """increase sudvision levels for selected objects and add decimation modifiers"""
    bl_idname = "view3d.subdivide_selected"
    bl_label = "Subdivide Selected"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_subdivide(self,context)
        return {'FINISHED'}
                
class BR_OT_subd_decrease(bpy.types.Operator):
    """decrease sudvision levels for visible objects with smart decimator toggle"""
    bl_idname = "view3d.subd_decrease"
    bl_label = "SubD Less"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_decrease(context)
        return {'FINISHED'}


class BR_OT_subd_increase(bpy.types.Operator):
    """increase sudvision levels for visible objects with smart decimator toggle"""
    bl_idname = "view3d.subd_increase"
    bl_label = "SubD More"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_increase(context)
        return {'FINISHED'}

class BR_OT_automesh(bpy.types.Operator):
    """create a low res voxel object and add shirinkwrap a multires subdivision to it"""
    bl_idname = "view3d.subd_automesh"
    bl_label = "Automesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        desired_polycount = 1500
        previous_mode = ""
        s = bpy.context.object
        selected_objects = bpy.context.selected_objects
        if selected_objects:
            split_target_polycount = desired_polycount / len(selected_objects)

            if (bpy.context.mode != 'OBJECT'):
                previous_mode = bpy.context.mode
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            for obj in selected_objects:
                if obj.visible_get and obj.type == 'MESH':
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(state=True)
                    bpy.context.view_layer.objects.active = obj

                    
                    bpy.ops.object.duplicate_move()
                    for v in bpy.context.window.screen.areas:
                        if v.type=='VIEW_3D':                
                            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                            bpy.ops.mesh.select_all(action='SELECT')
                            bpy.ops.mesh.separate(type='LOOSE')
                            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                            # automap(bpy.context.selected_objects)
                            bpy.ops.object.modifier_apply(modifier="Auto Boolean")
                            bpy.ops.object.booltool_auto_union()


                    automesh = bpy.context.selected_objects[0]
                    obj_name = obj.name
                    automesh.name = obj_name + "_automesh"
                    bpy.ops.object.select_all(action='DESELECT')
                    automesh.select_set(state=True)
                    bpy.context.view_layer.objects.active = automesh

                    shapekeys = []
                    if automesh.data.shape_keys:
                        shapekeys = [o for o in automesh.data.shape_keys.key_blocks]
                    if shapekeys:
                        for key in shapekeys:
                            bpy.ops.object.shape_key_add(from_mix=True)
                        for key in automesh.data.shape_keys.key_blocks:
                            automesh.shape_key_remove(key)        
                    bpy.ops.object.convert(target='MESH')

                    # mod = automesh.modifiers.new(name = 'Remesh', type = 'REMESH')
                    # mod.voxel_size = 0.15
                    # mod.adaptivity = 0.015
                    # mod.use_smooth_shade = True
                    # bpy.ops.object.modifier_apply(modifier=mod.name)

                    if operator_exists("qremesher"):
                        print("---------------------")
                        bpy.ops.qremesher.reset_scene_prefs()
                        bpy.context.scene.qremesher.target_count = 1000
                        bpy.context.scene.qremesher.adaptive_size = 50
                        bpy.context.scene.qremesher.adapt_quad_count = True
                        bpy.context.scene.qremesher.use_materials = True
                        bpy.context.scene.qremesher.autodetect_hard_edges = True
                        bpy.ops.qremesher.remesh()
                    else:
                        for v in bpy.context.window.screen.areas:
                            if v.type=='VIEW_3D':                
                                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                                bpy.ops.mesh.select_all(action='SELECT')

                                depsgraph2 = bpy.context.evaluated_depsgraph_get()
                                ob_eval2 = automesh.evaluated_get(depsgraph2)
                                planar_decim_polycount = len(ob_eval2.data.polygons)
                                ratio = split_target_polycount / planar_decim_polycount 

                                bpy.ops.mesh.decimate(ratio=ratio)
                                bpy.ops.mesh.remove_doubles(threshold=0.5)
                                bpy.ops.mesh.tris_convert_to_quads(face_threshold=3.14159, shape_threshold=3.13985, seam=False, sharp=False)
                                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                    mod = automesh.modifiers.new(name = 'Multires', type = 'MULTIRES')
                    mod.quality = 6
                    mod.uv_smooth = 'NONE'
                    mod.use_creases = False
                    level = 5
                    if level > 0:
                        for i in range(0, level):
                            shrink_mod = automesh.modifiers.new(name = 'Shrinkwrap', type = 'SHRINKWRAP')
                            shrink_mod.wrap_method = 'PROJECT'
                            shrink_mod.use_negative_direction = True
                            shrink_mod.use_positive_direction = True
                            shrink_mod.project_limit = .5
                            shrink_mod.target = bpy.data.objects[obj_name]
                            bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')
                            bpy.ops.object.modifier_apply(modifier=shrink_mod.name)
                    mod.sculpt_levels = 5



                    # raise KeyboardInterrupt()


                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(state=True)
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.delete()

                    bpy.ops.object.select_all(action='DESELECT')
                    automesh.select_set(state=True)
                    bpy.context.view_layer.objects.active = automesh
                    automesh.name = obj_name


            if previous_mode:
                bpy.ops.object.mode_set(mode= previous_mode, toggle=False)


        return {'FINISHED'}


def menu_draw(self, context):
    layout = self.layout
    layout.separator()
    self.layout.operator(BR_OT_automesh.bl_idname)
    self.layout.operator(BR_OT_subdivide_selected.bl_idname)
    self.layout.operator(BR_OT_subd_increase.bl_idname)
    self.layout.operator(BR_OT_subd_decrease.bl_idname)
    # self.layout.operator(BR_OT_subd_toggle.bl_idname)


def register():
    bpy.utils.register_class(BR_OT_automesh)
    bpy.utils.register_class(BR_OT_subdivide_selected)
    bpy.utils.register_class(BR_OT_subd_increase)
    bpy.utils.register_class(BR_OT_subd_decrease)
    # bpy.utils.register_class(BR_OT_subd_toggle)
    bpy.types.VIEW3D_MT_view.append(menu_draw)  

def unregister():
    bpy.utils.unregister_class(BR_OT_automesh)
    bpy.utils.unregister_class(BR_OT_subdivide_selected)
    bpy.utils.unregister_class(BR_OT_subd_increase)
    bpy.utils.unregister_class(BR_OT_subd_decrease)
    # bpy.utils.unregister_class(BR_OT_subd_toggle)
    bpy.types.VIEW3D_MT_view.remove(menu_draw)  

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_view.remove(menu_draw)

if __name__ == "__main__":
    register()
