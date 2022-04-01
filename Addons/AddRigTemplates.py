bl_info = {
    "name": "Add Spiraloid Rig Templates.",
    "author": "Bay Raitt",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add ",
    "description": "Adds a two vert Wire + Skin, Random Object",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}

import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
import random
import bmesh

previous_random_object_int = 0 

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

    for block in bpy.data.libraries:
        if block.users == 0:
            bpy.data.libraries.remove(block)

    for block in bpy.data.worlds:
        if block.users == 0:
            bpy.data.worlds.remove(block)

    for block in bpy.data.particles:
        if block.users == 0:
            bpy.data.particles.remove(block)

    try:
        bpy.ops.outliner.orphans_purge()
    except:
        pass
    try:
        bpy.ops.outliner.orphans_purge()
    except:
        pass
    try:
        bpy.ops.outliner.orphans_purge()
    except:
        pass

    return {'FINISHED'}

def calc_bounds():
    """Calculates the bounding box for selected vertices. Requires applied scale to work correctly. """
    # for some reason we must change into object mode for the calculations
    mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    mesh = bpy.context.object.data
    verts = [v for v in mesh.vertices]

    # [+x, -x, +y, -y, +z, -z]
    v = verts[0].co
    bounds = [v.x, v.x, v.y, v.y, v.z, v.z]

    for v in verts:
        if bounds[0] < v.co.x:
            bounds[0] = v.co.x
        if bounds[1] > v.co.x:
            bounds[1] = v.co.x
        if bounds[2] < v.co.y:
            bounds[2] = v.co.y
        if bounds[3] > v.co.y:
            bounds[3] = v.co.y
        if bounds[4] < v.co.z:
            bounds[4] = v.co.z
        if bounds[5] > v.co.z:
            bounds[5] = v.co.z

    bpy.ops.object.mode_set(mode=mode)

    return bounds

def safe_divide(a, b):
    if b != 0:
        return a / b
    return 1

def fit_to_object(self, target_bounds):

    new_x = FloatProperty(name="X", min=0, default=1, unit='LENGTH')
    new_y = FloatProperty(name="Y", min=0, default=1, unit='LENGTH')
    new_z = FloatProperty(name="Z", min=0, default=1, unit='LENGTH')

    bounds = calc_bounds()
    self.new_x = bounds[0] - bounds[1]
    self.new_y = bounds[2] - bounds[3]
    self.new_z = bounds[4] - bounds[5]

    bpy.ops.object.mode_set(mode='EDIT')
    x = safe_divide(self.new_x, (float(target_bounds[0][0]) - float(target_bounds[1][0])))
    y = safe_divide(self.new_y, (float(target_bounds[2][0]) - float(target_bounds[3][0])))
    z = safe_divide(self.new_z, (float(target_bounds[4][0]) - float(target_bounds[5][0])))

    bpy.ops.transform.resize(value=(x, y, z))

    return {'FINISHED'}

def add_object(self, context):
    scale_x = self.scale.x
    scale_y = self.scale.y

    verts = [
        Vector((-1 * scale_x, 1 * scale_y, 0)),
        Vector((1 * scale_x, 1 * scale_y, 0)),
        Vector((1 * scale_x, -1 * scale_y, 0)),
        Vector((-1 * scale_x, -1 * scale_y, 0)),
    ]

    edges = []
    faces = [[0, 1, 2, 3]]

    mesh = bpy.data.meshes.new(name="New Object Mesh")
    mesh.from_pydata(verts, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh, operator=self)


def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

def parent_lookup(coll):
    parent_lookup = {}
    for coll in traverse_tree(coll):
        for c in coll.children.keys():
            parent_lookup.setdefault(c, coll.name)
    return parent_lookup

def get_parent_collection(coll):
    coll_name = coll.name
    C = bpy.context
    coll_scene = C.scene.collection
    coll_parents = parent_lookup(coll_scene)
    parent_collection_name = coll_parents.get(coll_name)
    parent_collection = bpy.data.collections.get(parent_collection_name)        
    return parent_collection

def get_mesh_selection_mode(self, context):
    mode = context.tool_settings.mesh_select_mode[:]
    return mode

def stroke_selected(self, context):
    if bpy.context.object:
        starting_mode = bpy.context.object.mode
        if "EDIT" not in starting_mode:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                old_obj = bpy.context.selected_objects[0]
                old_obj_name =old_obj.name
                sel_mode = get_mesh_selection_mode(self, context)
                if not bpy.context.scene.tool_settings.mesh_select_mode[1]:
                    bpy.ops.mesh.region_to_loop()
                bpy.ops.mesh.duplicate()
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                new_obj = bpy.context.selected_objects[1]
                bpy.ops.object.select_all(action='DESELECT')
                new_obj.select_set(state=True)
                bpy.context.view_layer.objects.active = new_obj
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.delete(type='ONLY_FACE')
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                skin_mod = new_obj.modifiers.new(name = 'Skin', type = 'SKIN')
                skin_mod.use_smooth_shade = True
                new_obj.data.use_auto_smooth = True
                # subd_mod = new_obj.modifiers.new(name = 'Subdivision', type = 'SUBSURF')
                dec_mod = new_obj.modifiers.new(name = 'Decimate', type = 'DECIMATE')
                dec_mod.decimate_type = 'DISSOLVE'
                dec_mod.angle_limit = 0.0349066
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.skin_resize(value=(0.25, 0.25, 0.25), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                new_obj_name = old_obj_name + "_stroke"
                existing_stroke_mesh = ""
                try:
                    existing_stroke_mesh = bpy.data.objects[new_obj_name]
                except:
                    pass
                if existing_stroke_mesh:
                    bpy.ops.object.select_all(action='DESELECT')
                    existing_stroke_mesh.select_set(state=True)
                    new_obj.select_set(state=True)
                    bpy.context.view_layer.objects.active = existing_stroke_mesh
                    bpy.ops.object.join()
                    new_obj = bpy.context.selected_objects[0]
                else:
                    new_obj.name = new_obj_name
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                for mod in new_obj.modifiers:
                    mod_name = mod.name
                    if 'Skin' in mod_name:
                        bpy.ops.object.skin_root_mark()
                # bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                # bpy.ops.object.select_all(action='DESELECT')
                # old_obj.select_set(state=True)
                # bpy.context.view_layer.objects.active = old_obj
                # bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                # bpy.context.tool_settings.mesh_select_mode = sel_mode
                
        return {'FINISHED'}


class OBJECT_OT_stroke_selected(Operator, AddObjectHelper):
    """Stroke Selected"""
    bl_idname = "mesh.stroke_selected"
    bl_label = "Stroke Selected"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        stroke_selected(self, context)
        return {'FINISHED'}


class OBJECT_OT_add_random_object(Operator, AddObjectHelper):
    """Create Random Object"""
    bl_idname = "mesh.add_random_object"
    bl_label = "Swap Random Object"
    bl_options = {'REGISTER', 'UNDO'}

    scale: FloatVectorProperty(
        name="scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="scaling",
    )

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        scene_collection = bpy.context.view_layer.layer_collection
        scene_collection_name = scene_collection.name
        active_collection = bpy.context.collection
        active_collection_name = active_collection.name
        s_objects = []
        is_multikill = ""

        old_bounds = ["-1", "-1", "-1", "-1", "1", "1", "1", "1" ]
        if selected_objects:
            if len(selected_objects) == 1:
                is_multikill = False
                s_objects.append(selected_objects[0])
            else:
                is_multikill = True
                for obj in selected_objects:
                    if scene_collection_name is not active_collection_name:
                        active_collection_parent_collection = get_parent_collection(active_collection)
                        if active_collection_parent_collection:
                            active_collection_parent_collection_name = active_collection_parent_collection.name
                        else:
                            active_collection_parent_collection_name = scene_collection_name
                    else:
                        active_collection_parent_collection_name = scene_collection_name

                    col_name = obj.name

                    count = 1 
                    collection_instances = []
                    col =  bpy.data.collections.new(col_name)
                    active_collection.children.link(col)
                    
                    bpy.data.collections[col_name].objects.link(obj)
                    try:
                        bpy.data.collections[active_collection_name].objects.unlink(obj)
                    except:
                        pass

                    
                    if obj.name is not selected_objects[0].name:
                        s_objects.append(obj)

            
            for obj in selected_objects:
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.context.scene.cursor.rotation_euler = obj.rotation_euler
                # old_bound_box_corners_in_world_space = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

                # get longest bounding box edge size
                bb = obj.bound_box
                dx_local = max(bb[i][0] for i in range(8)) - min(bb[i][0] for i in range(8))
                dy_local = max(bb[i][1] for i in range(8)) - min(bb[i][1] for i in range(8))
                dz_local = max(bb[i][2] for i in range(8)) - min(bb[i][2] for i in range(8))
                old_longest_side = max(dx_local*obj.scale[0], dx_local*obj.scale[1], dx_local*obj.scale[2])

                

                bpy.data.objects.remove(bpy.data.objects[obj.name], do_unlink=True)
                empty_trash(self, context)

                if is_multikill:
                    col_i_name = col.name + "_inst"
                    bpy.ops.object.collection_instance_add(collection=col.name, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                    i_col = bpy.context.selected_objects[0]
                    i_col.name = col_i_name
                    collection_instances.append(i_col)
                


            if is_multikill:
                count = 1   
                for icol in collection_instances:
                    if scene_collection_name is active_collection_parent_collection_name:
                        scene = bpy.context.scene
                        try:
                            scene.collection.objects.link(icol)
                        except:
                            pass
                    else:
                        bpy.data.collections[active_collection_parent_collection_name].objects.link(icol)
                    bpy.ops.object.select_all(action='DESELECT')
                    icol.select_set(state=True)
                    # control_object.select_set(state=True)
                    # bpy.context.view_layer.objects.active = control_object
                    bpy.ops.object.parent_set()

            # bpy.ops.object.select_all(action='DESELECT')
            # selected_objects[0].select_set(state=True)
            # bpy.context.view_layer.objects.active = selected_objects[0]

        object_commands = [ "bpy.ops.mesh.primitive_cube_add(", "bpy.ops.mesh.primitive_cube_add(", "bpy.ops.mesh.primitive_cube_add(", "bpy.ops.mesh.primitive_cone_add(", "bpy.ops.mesh.primitive_cross_joint_add(", "bpy.ops.mesh.primitive_cylinder_add(", "bpy.ops.mesh.primitive_diamond_add(", "bpy.ops.mesh.primitive_gear(", "bpy.ops.mesh.primitive_ico_sphere_add(", "bpy.ops.mesh.primitive_monkey_add(",  "bpy.ops.mesh.primitive_round_cube_add(", "bpy.ops.mesh.primitive_star_add(", "bpy.ops.mesh.primitive_steppyramid_add(", "bpy.ops.mesh.primitive_supertoroid_add(", "bpy.ops.mesh.primitive_teapot_add(", "bpy.ops.mesh.primitive_torusknot_add(",  "bpy.ops.mesh.primitive_uv_sphere_add("  ]
        i = len(object_commands) -1
        if i > 0:
            random_int = random.randint(0, i)
            while (random_int == previous_random_object_int):
                random_int = random.randint(0, i)
                if (random_int != previous_random_object_int):
                    break
        else:
            random_int = 0

        print (object_commands[random_int] + "==========================")
        eval(object_commands[random_int] + "rotation=(" + str(bpy.context.scene.cursor.rotation_euler[0]) + " ," + str(bpy.context.scene.cursor.rotation_euler[1]) + " ," + str(bpy.context.scene.cursor.rotation_euler[2]) + "))")

        new_random_object = bpy.context.selected_objects[0]
        # new_random_object.bound_box = old_bounds
        
        if selected_objects:
            # fit to old object
            bb = new_random_object.bound_box
            dx_local = max(bb[i][0] for i in range(8)) - min(bb[i][0] for i in range(8))
            dy_local = max(bb[i][1] for i in range(8)) - min(bb[i][1] for i in range(8))
            dz_local = max(bb[i][2] for i in range(8)) - min(bb[i][2] for i in range(8))
            new_longest_side = max(dx_local*new_random_object.scale[0], dx_local*new_random_object.scale[1], dx_local*new_random_object.scale[2])
            new_scale = old_longest_side / new_longest_side 
        else:
            new_scale = 1

        new_random_object.scale = [ new_scale, new_scale, new_scale]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.normals_make_consistent(inside=False)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        # bpy.ops.object.shade_smooth()
        # new_random_object.data.use_auto_smooth = True
        # new_random_object.data.auto_smooth_angle = 0.785398 #45
        new_random_object.data.auto_smooth_angle = 1.15192 #66

        bpy.ops.object.select_all(action='DESELECT')       
        new_random_object = bpy.context.view_layer.objects.active 
        new_random_object.select_set(state=True)
        bpy.context.view_layer.objects.active = new_random_object

        layer = bpy.context.view_layer
        layer.update()
        
        return {'FINISHED'}

class OBJECT_OT_add_wire_skin(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_wire_skin"
    bl_label = "Add Wire Skin"
    bl_options = {'REGISTER', 'UNDO'}

    scale: FloatVectorProperty(
        name="scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="scaling",
    )

    def execute(self, context):

        #add_object(self, context)
        bpy.ops.mesh.primitive_vert_add()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')            
        ob = bpy.context.view_layer.objects.active 
        ob.select_set(state=True)
        bpy.context.view_layer.objects.active = ob
        skin_mod = ob.modifiers.new(name = 'Skin', type = 'SKIN')                        
        # mirror_mod = ob.modifiers.new(name = 'Mirror', type = 'MIRROR')                
        # mirror_mod.use_bisect_axis[0] = True
        # mirror_mod.use_clip = False
        # mirror_mod.use_mirror_merge = False

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')  
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 1), "orient_type":'LOCAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'LOCAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'INVERSE_SQUARE', "proportional_size":1.21542, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})

        my_areas = bpy.context.workspace.screens[0].areas
        for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'

                    space.shading.type = 'SOLID'
                    space.shading.show_xray = True
                    space.shading.xray_alpha = 1
        bpy.context.space_data.overlay.show_wireframes = False
        layer = bpy.context.view_layer
        layer.update()
        
        return {'FINISHED'}

class OBJECT_OT_add_wire_skin_mirrored(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_wire_skin_mirrored"
    bl_label = "Add Wire Skin Mirrored"
    bl_options = {'REGISTER', 'UNDO'}

    scale: FloatVectorProperty(
        name="scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="scaling",
    )

    def execute(self, context):

        #add_object(self, context)
        bpy.ops.mesh.primitive_vert_add()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')            
        ob = bpy.context.view_layer.objects.active 
        ob.select_set(state=True)
        bpy.context.view_layer.objects.active = ob
        skin_mod = ob.modifiers.new(name = 'Skin', type = 'SKIN')                        
        mirror_mod = ob.modifiers.new(name = 'Mirror', type = 'MIRROR')                
        mirror_mod.use_bisect_axis[0] = True
        mirror_mod.use_clip = False
        mirror_mod.use_mirror_merge = True
        bpy.context.object.modifiers["Mirror"].use_mirror_merge = True

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')  
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 1), "orient_type":'LOCAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'LOCAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'INVERSE_SQUARE', "proportional_size":1.21542, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})

        my_areas = bpy.context.workspace.screens[0].areas
        for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'

                    space.shading.type = 'SOLID'
                    space.shading.show_xray = True
                    space.shading.xray_alpha = 1
        bpy.context.space_data.overlay.show_wireframes = False
        layer = bpy.context.view_layer
        layer.update()
        
        return {'FINISHED'}

# Menu UI
def add_object_button(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(
        OBJECT_OT_add_wire_skin.bl_idname,
        text="Wire + Skin",
        icon='MOD_SKIN')
    layout.operator(
        OBJECT_OT_add_wire_skin_mirrored.bl_idname,
        text="Wire + Skin + Mirror",
        icon='MOD_SKIN')
    layout.separator()

def add_random_object(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(
        OBJECT_OT_add_random_object.bl_idname,
        text="Cube Killer",
        icon='LIGHTPROBE_CUBEMAP')
    layout.separator()

def add_to_face_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(
        OBJECT_OT_stroke_selected.bl_idname,
        text="Stroke Selected")
    layout.separator()



# New Add Item Menu
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/dev/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "editors/3dview/object"),
    )
    return url_manual_prefix, url_manual_mapping

# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_add_wire_skin)
    bpy.utils.register_class(OBJECT_OT_add_wire_skin_mirrored)
    bpy.utils.register_class(OBJECT_OT_add_random_object)
    bpy.utils.register_class(OBJECT_OT_stroke_selected)
    
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
    bpy.types.VIEW3D_MT_add.prepend(add_random_object)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(add_to_face_menu)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_wire_skin)
    bpy.utils.unregister_class(OBJECT_OT_add_wire_skin_mirrored)
    bpy.utils.unregister_class(OBJECT_OT_add_random_object)
    bpy.utils.unregister_class(OBJECT_OT_stroke_selected)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)
    bpy.types.VIEW3D_MT_add.remove(add_random_object)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(add_to_face_menu)

if __name__ == "__main__":
    register()
