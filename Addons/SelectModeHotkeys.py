bl_info = {
    "name": "Select Mode Hotkeys",
    "author": "Your Name",
    "version": (1, 3),
    "blender": (3, 0, 0),
    "location": "View3D > Mesh > Select Mode Hotkeys",
    "description": "Adds operators to set the select mode to vertices, edges, and faces, which can be assigned to hotkeys. Also adds a 'Select' menu to the header of the 3D Viewport in Edit Mode.",
    "category": "Mesh",
}

import bpy
from bpy.types import Menu

class SetSelectModeVerticesOperator(bpy.types.Operator):
    bl_idname = "mesh.set_select_mode_vertices"
    bl_label = "Set Select Mode to Vertices"
    bl_description = "Set the select mode to vertices"
    
    def execute(self, context):
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.context.space_data.overlay.show_faces = False
        return {'FINISHED'}

class SetSelectModeEdgesOperator(bpy.types.Operator):
    bl_idname = "mesh.set_select_mode_edges"
    bl_label = "Set Select Mode to Edges"
    bl_description = "Set the select mode to edges"
    
    def execute(self, context):
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.context.space_data.overlay.show_faces = False
        return {'FINISHED'}

class SetSelectModeFacesOperator(bpy.types.Operator):
    bl_idname = "mesh.set_select_mode_faces"
    bl_label = "Set Select Mode to Faces"
    bl_description = "Set the select mode to faces"
    
    def execute(self, context):
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.context.space_data.overlay.show_faces = True
        return {'FINISHED'}

class SelectMenu(Menu):
    bl_label = "Select"
    bl_idname = "VIEW3D_MT_select_edit_mesh_select_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.set_select_mode_vertices", text="Vertices", icon='VERTEXSEL')
        layout.operator("mesh.set_select_mode_edges", text="Edges", icon='EDGESEL')
        layout.operator("mesh.set_select_mode_faces", text="Faces", icon='FACESEL')

def register():
    bpy.utils.register_class(SetSelectModeVerticesOperator)
    bpy.utils.register_class(SetSelectModeEdgesOperator)
    bpy.utils.register_class(SetSelectModeFacesOperator)
    bpy.utils.register_class(SelectMenu)

    bpy.types.VIEW3D_MT_select_edit_mesh.append(SelectMenu.draw)

def unregister():
    bpy.utils.unregister_class(SetSelectModeVerticesOperator)
    bpy.utils.unregister_class(SetSelectModeEdgesOperator)
    bpy.utils.unregister_class(SetSelectModeFacesOperator)
    bpy.utils.unregister_class(SelectMenu)

    bpy.types.VIEW3D_MT_select_edit_mesh.remove(SelectMenu.draw)

if __name__ == "__main__":
    register()
