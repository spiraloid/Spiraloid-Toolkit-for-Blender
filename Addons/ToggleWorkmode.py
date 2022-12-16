bl_info = {
        'name': 'ToggleWorkmode',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'View',
        'location': 'View > Toggle Workmode',
        'wiki_url': ''}

import bpy

previous_mode = 'EDIT'
isWorkmodeToggled = True
isWireframe = False

def toggle_workmode(self, context, rendermode):
    global isWorkmodeToggled
    global currentSubdLevel
    global previous_mode
    global previous_selection
    global isWireframe
    global previous_toolbar_state
    global previous_region_ui_state
    global previous_gpencil_object

    if rendermode:
        isWorkmodeToggled = True        

    if previous_mode != 'PAINT_GPENCIL':
        if bpy.context.mode == 'OBJECT':
            previous_mode =  'OBJECT'
    else:
        previous_mode =  'PAINT_GPENCIL'

    if bpy.context.mode == 'EDIT_MESH':
        previous_mode =  'EDIT'
        bpy.context.space_data.overlay.show_overlays = False
    if bpy.context.mode == 'POSE':
        previous_mode =  'POSE'
        bpy.context.space_data.overlay.show_bones = True
    if bpy.context.mode == 'SCULPT':
        previous_mode =  'SCULPT'
    if bpy.context.mode == 'PAINT_VERTEX':
        previous_mode =  'VERTEX_PAINT'
    if bpy.context.mode == 'WEIGHT_PAINT':
        previous_mode =  'WEIGHT_PAINT'
    if bpy.context.mode == 'TEXTURE_PAINT':
        previous_mode =  'TEXTURE_PAINT'
    if bpy.context.mode == 'PAINT_GPENCIL':
        previous_mode =  'PAINT_GPENCIL'
        previous_gpencil_object = bpy.context.active_object
    my_shading = 'SOLID'


    # my_areas = bpy.context.workspace.screens[0].areas
    # for area in my_areas:
    #     for space in area.spaces:
    #         if space.type == 'VIEW_3D':

    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    my_shading = 'WIREFRAME'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
                    space.overlay.show_overlays = True
                    space.overlay.show_floor = True
                    space.overlay.show_axis_x = True
                    space.overlay.show_axis_y = True
                    space.overlay.show_outline_selected = True
                    space.overlay.show_cursor = True
                    space.overlay.show_extras = True
                    space.overlay.show_relationship_lines = True
                    space.overlay.show_bones = True
                    space.overlay.show_motion_paths = True
                    space.overlay.show_object_origins = True
                    space.overlay.show_annotation = True
                    space.overlay.show_text = True
                    space.overlay.show_stats = True
                    previous_toolbar_state = space.show_region_toolbar
                    previous_region_ui_state = space.show_region_ui
                    space.show_region_header = True


                    if isWorkmodeToggled:
                        previous_selection = bpy.context.selected_objects
                        space.overlay.show_overlays = True
                        space.overlay.show_floor = False
                        space.overlay.show_axis_x = False
                        space.overlay.show_axis_y = False
                        space.overlay.show_cursor = False
                        space.overlay.show_relationship_lines = False
                        space.overlay.show_bones = False
                        space.overlay.show_motion_paths = False
                        space.overlay.show_object_origins = True
                        space.overlay.show_annotation = False
                        space.overlay.show_text = False
                        space.overlay.show_stats = False
                        space.overlay.show_outline_selected = False
                        space.overlay.show_extras = False
                        space.show_gizmo = False
                        space.overlay.show_text = False
                        space.overlay.show_stats = False
                        space.show_region_toolbar = previous_toolbar_state
                        space.show_region_ui = previous_region_ui_state
                        space.show_region_header = True



                        selected_objects = bpy.context.selected_objects
                        if not selected_objects:
                            space.overlay.show_outline_selected = True


                        space.overlay.wireframe_threshold = 1
                        if space.overlay.show_wireframes:
                            isWireframe = True
                            # space.overlay.show_outline_selected = True
                            space.overlay.show_extras = True
                            space.overlay.show_overlays = True
                            space.overlay.show_text = True
                            space.overlay.show_stats = True
                            space.overlay.wireframe_opacity = 0.4


                            # bpy.context.space_data.overlay.show_cursor = True
                        else:
                            isWireframe = False
                            if not bpy.context.selected_objects:
                                space.overlay.show_object_origins = False

                            # bpy.context.space_data.overlay.show_outline_selected = False
                            # bpy.context.space_data.overlay.show_extras = False

                        # bpy.context.space_data.overlay.show_wireframes = False

                        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
                            # bpy.context.scene.eevee.use_bloom = True
                            # bpy.context.scene.eevee.use_ssr = True
                            my_shading =  'MATERIAL'

                            lights = [o for o in bpy.context.scene.objects if o.type == 'LIGHT']
                            if (lights):
                                space.shading.use_scene_lights = True
                                space.shading.use_scene_world = True
                            else:
                                space.shading.use_scene_lights = True
                                space.shading.use_scene_world = False

                            if bpy.context.scene.world:
                                space.shading.use_scene_world = True
                            else:
                                space.shading.use_scene_world = False


                        if bpy.context.scene.render.engine == 'CYCLES':
                            my_shading =  'RENDERED'
                            lights = [o for o in bpy.context.scene.objects if o.type == 'LIGHT']
                            # if (lights):
                            #     bpy.context.space_data.shading.use_scene_lights_render = True
                            # else:
                            #     bpy.context.space_data.shading.use_scene_lights = False
                            #     bpy.context.space_data.shading.studiolight_intensity = 1


                            if bpy.context.scene.world is None:
                                if (lights):
                                    space.shading.use_scene_world_render = False
                                    space.shading.studiolight_intensity = 0.01
                                else:
                                    space.shading.use_scene_world_render = False
                                    space.shading.studiolight_intensity = 1
                            else:
                                space.shading.use_scene_world_render = True
                                if (lights):
                                    space.shading.use_scene_lights_render = True

                        if previous_mode == 'PAINT_GPENCIL':
                            if previous_gpencil_object:
                                selected_object = bpy.context.view_layer.objects.active
                                if selected_object:
                                    if selected_object.type == 'GPENCIL':
                                        bpy.ops.gpencil.paintmode_toggle()
                                        bpy.context.mode == 'PAINT_GPENCIL'


                        if previous_mode == 'SCULPT':
                            bpy.context.scene.tool_settings.sculpt.show_face_sets = False


                    else:
                        space.overlay.show_overlays = True
                        space.overlay.show_cursor = True
                        space.overlay.show_floor = True
                        space.overlay.show_axis_x = True
                        space.overlay.show_axis_y = True
                        space.overlay.show_extras = True
                        space.overlay.show_relationship_lines = False
                        space.overlay.show_bones = True
                        space.overlay.show_motion_paths = True
                        space.overlay.show_object_origins = True
                        space.overlay.show_annotation = True
                        space.overlay.show_text = True
                        space.overlay.show_stats = True
                        space.overlay.wireframe_threshold = 1
                        space.overlay.wireframe_opacity = 0.75


                        space.show_gizmo = True
                        # space.show_region_header = True
                        space.show_region_toolbar = previous_toolbar_state
                        space.show_region_ui = previous_region_ui_state


                        if previous_mode == 'EDIT':
                            if not len(bpy.context.selected_objects):
                                bpy.ops.object.editmode_toggle()
                            # else:
                            #     for ob in previous_selection :
                            #         # if ob.type == 'MESH' : 
                            #         ob.select_set(state=True)
                            #         bpy.context.view_layer.objects.active = ob
                            #     bpy.ops.object.editmode_toggle()

                        if previous_mode == 'PAINT_GPENCIL':
                            if previous_gpencil_object:
                                # bpy.ops.object.select_all(action='DESELECT')

                                try:
                                    previous_gpencil_object.select_set(state=True)
                                    bpy.context.view_layer.objects.active = previous_gpencil_object
                                    bpy.ops.gpencil.paintmode_toggle()
                                except:
                                    pass

                                my_shading = 'MATERIAL'
                                space.overlay.show_overlays = True
                                space.overlay.show_cursor = True
                                space.overlay.show_floor = True
                                space.overlay.show_axis_x = True
                                space.overlay.show_axis_y = True
                                space.overlay.show_extras = True
                                space.overlay.show_relationship_lines = False
                                space.overlay.show_bones = True
                                space.overlay.show_motion_paths = True
                                space.overlay.show_object_origins = True
                                space.overlay.show_annotation = True
                                space.overlay.show_text = True
                                space.overlay.show_stats = True
                                space.overlay.wireframe_threshold = 1
                                space.overlay.show_fade_inactive = False
                                space.show_gizmo = True

                                # space.show_region_header = True
                                space.show_region_toolbar = previous_toolbar_state
                                space.show_region_ui = previous_region_ui_state



                        if previous_mode == 'VERTEX_PAINT':
                            my_shading = 'SOLID'
                            space.shading.light = 'FLAT'


                        if previous_mode == 'SCULPT':
                            my_shading =  'SOLID'
                            space.shading.color_type = 'VERTEX'
                            # space.show_specular_highlight = False
                            space.shading.light = 'MATCAP'
                            space.overlay.show_floor = False
                            space.overlay.show_axis_x = False
                            space.overlay.show_axis_y = False
                            space.overlay.show_cursor = False
                            space.overlay.show_relationship_lines = False
                            space.overlay.show_bones = False
                            space.overlay.show_motion_paths = False
                            space.overlay.show_object_origins = False
                            space.overlay.show_annotation = False
                            space.overlay.show_text = False
                            space.overlay.show_text = False
                            space.overlay.show_outline_selected = False
                            space.overlay.show_extras = False
                            space.overlay.show_overlays = True
                            space.show_gizmo = True
                            space.shading.show_backface_culling = True
                            space.overlay.sculpt_mode_mask_opacity = 0.5
                            space.shading.show_cavity = True
                            space.shading.cavity_ridge_factor = 0.1
                            space.shading.cavity_valley_factor = 1.0
                            space.shading.curvature_ridge_factor = 0.1
                            space.shading.curvature_valley_factor = 0.7


                            if isWireframe:
                                bpy.context.scene.tool_settings.sculpt.show_face_sets = True
                            else:
                                bpy.context.scene.tool_settings.sculpt.show_face_sets = False




                        if previous_mode == 'EDIT' or previous_mode == 'OBJECT' or previous_mode == 'POSE':
                            my_shading = 'SOLID'
                            # for ob in bpy.context.scene.objects:
                            #     if ob.type == 'MESH':
                            #         if ob.data.vertex_colors:
                            #             bpy.context.space_data.shading.color_type = 'VERTEX'
                            #         else:
                            #             bpy.context.space_data.shading.color_type = 'RANDOM'


                        if isWireframe:
                            space.overlay.show_wireframes = True
                            space.overlay.wireframe_opacity = 0.75
                        else:
                            space.overlay.show_wireframes = False
                        # space.shading.color_type = 'RANDOM'
                        # space.shading.show_backface_culling = True
                        space.shading.show_shadows = False


    for obj in bpy.context.scene.objects:
        # if obj.visible_get and obj.type == 'MESH':
        if obj.visible_get :
        # if True :
            
            # for mod in [m for m in obj.modifiers if m.type == 'MULTIRES']:
            #     mod_max_level = mod.render_levels
            #     if isWorkmodeToggled:
            #         currentSubdLevel = mod.levels
            #         mod.levels = mod_max_level
            #         mod.sculpt_levels = mod_max_level
            #     if not isWorkmodeToggled:
            #         mod.levels = currentSubdLevel
            #         mod.sculpt_levels = currentSubdLevel
            #         if currentSubdLevel != 0:
            #             bpy.context.space_data.overlay.show_wireframes = False


            # for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:
            #     mod_max_level = mod.render_levels
            #     if isWorkmodeToggled:
            #         currentSubdLevel = mod.levels
            #         mod.levels = mod_max_level
            #     if not isWorkmodeToggled:
            #         mod.levels = currentSubdLevel
            #         if currentSubdLevel != 0:
            #             bpy.context.space_data.overlay.show_wireframes = False

            scene = bpy.context.scene
            if isWorkmodeToggled:
                is_workmode = obj.get("workmode")
                if is_workmode is not None:
                    obj["workmode"] = True
                is_toon_shaded = obj.get("is_toon_shaded")
                if is_toon_shaded:
                    for mod in obj.modifiers:
                        mod_name = mod.name
                        if 'InkThickness' in mod_name:
                            obj.modifiers["InkThickness"].show_viewport = True
                        if 'WhiteOutline' in mod_name:
                            obj.modifiers["WhiteOutline"].show_viewport = True
                        if 'BlackOutline' in mod_name:
                            obj.modifiers["BlackOutline"].show_viewport = True

            else:
                is_workmode = obj.get("workmode")
                if is_workmode is not None:
                    obj["workmode"] = False
                is_toon_shaded = obj.get("is_toon_shaded")
                if is_toon_shaded:
                    for mod in obj.modifiers:
                        mod_name = mod.name
                        if 'InkThickness' in mod_name:
                            obj.modifiers["InkThickness"].show_viewport = False
                        if 'WhiteOutline' in mod_name:
                            obj.modifiers["WhiteOutline"].show_viewport = False
                        if 'BlackOutline' in mod_name:
                            obj.modifiers["BlackOutline"].show_viewport = False
        # cheesy hack to update drivers
        obj.hide_render = obj.hide_render

                # bpy.ops.object.mode_set(mode=previous_mode, toggle=False)


            # for area in my_areas:
            #     for space in area.spaces:
            #         if space.type == 'VIEW_3D':
            #             space.shading.type = my_shading

    # set viewport display
    
    for area in  bpy.context.screen.areas:  # iterate through areas in current screen
        if area.type == 'VIEW_3D':
            for space in area.spaces:  # iterate through spaces in current VIEW_3D area
                if space.type == 'VIEW_3D':  # check if space is a 3D view
                    # space.shading.type = 'MATERIAL'  # set the viewport shading to material
                    space.shading.type = my_shading
                    try: 
                        if scene.world is not None:
                            space.shading.use_scene_world = True
                            space.shading.use_scene_lights = True
                    except:
                        pass
                                

    for image in bpy.data.images:
        image.reload()

    isWorkmodeToggled = not isWorkmodeToggled
    return {'FINISHED'}


class BR_OT_toggle_workmode(bpy.types.Operator):
    """Toggle Workmode"""
    bl_idname = "wm.spiraloid_toggle_workmode"
    bl_label = "Toggle Workmode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True #context.space_data.type == 'VIEW_3D'

    def execute(self, context):
        toggle_workmode(self, context, False)
        return {'FINISHED'}


def menu_draw_view3d(self, context):
    self.layout.operator(BR_OT_toggle_workmode.bl_idname)

def menu_draw_uv(self, context):
    self.layout.operator(BR_OT_aim_at_selected.bl_idname)
    self.layout.operator(BR_OT_toggle_pivots.bl_idname)

def register():
    bpy.utils.register_class(BR_OT_toggle_workmode)
    bpy.types.VIEW3D_MT_view.prepend(menu_draw_view3d)  


def unregister():
    bpy.types.VIEW3D_MT_view.remove(menu_draw_view3d)  
    bpy.utils.unregister_class(BR_OT_toggle_workmode)


    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_view.remove(menu_draw_view3d)

if __name__ == "__main__":
    register()
