bl_info = {
    "name": "Add Rig Templates Wire",
    "author": "Bay Raitt",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Wire Skin",
    "description": "Adds a new wire skinned objects with a mirror modifier",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


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
#        mirror_mod = ob.modifiers.new(name = 'Mirror', type = 'MIRROR')                
#        mirror_mod.use_bisect_axis[0] = True
#        mirror_mod.use_clip = False
#        mirror_mod.use_mirror_merge = False

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
        mirror_mod = ob.modifiers.new(name = 'Mirror', type = 'MIRROR')                
        mirror_mod.use_bisect_axis[0] = True
        mirror_mod.use_clip = True
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



# Registration

def add_object_button(self, context):
    
    self.layout.operator(
        OBJECT_OT_add_wire_skin.bl_idname,
        text="Wire + Skin",
        icon='MOD_SKIN')
    self.layout.operator(
        OBJECT_OT_add_wire_skin_mirrored.bl_idname,
        text="Wire + Skin + Mirror",
        icon='MOD_SKIN')

# This allows you to right click on a button and link to the manual
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/dev/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "editors/3dview/object"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_wire_skin)
    bpy.utils.register_class(OBJECT_OT_add_wire_skin_mirrored)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_wire_skin)
    bpy.utils.unregister_class(OBJECT_OT_add_wire_skin_mirrored)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()
