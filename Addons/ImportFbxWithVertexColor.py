bl_info = {
        'name': 'ImportFbxWithVertexColor',
        'author': 'Bay Raitt',
        'version': (0, 4),
        'blender': (2, 80, 0),
        "description": "Imports an .fbx file with vertex color and sets up the material and creates an optional decimation",
        'category': 'Import-Export',
        'location': 'File > Import/Export',
        'wiki_url': ''}

import bpy
from bpy_extras.io_utils import ImportHelper
import os.path
import bpy, os
from bpy.props import *


import os
import warnings
import re
from itertools import count, repeat
from collections import namedtuple
from math import pi

import bpy
from bpy.types import Operator
from mathutils import Vector

from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    CollectionProperty,
)

def highlightObjects(selection_list):
    for i in selection_list:
        bpy.data.objects[i.name].select_set(state=True)



    
class BR_OT_import_fbx_with_vertex_color(bpy.types.Operator, ImportHelper):
    """Import Multiple .FBX Files at Once"""
    bl_idname = "import_scene.fbx_w_color"    
    bl_label = 'FBX (.fbx) w vertex color'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "FBX Files w Vertex Color"

    # ImportHelper mixin class uses this
    filename_ext = ".obj"

    filter_glob : StringProperty(
            default="*.obj",
            options={'HIDDEN'},
            )

    # Selected files
    files : CollectionProperty(type=bpy.types.PropertyGroup)

    # List of operator properties, the attributes will be assigned
    image_search_setting : BoolProperty(
            name="Image Search",
            description="Search subdirs for any associated images "
                        "(Warning, may be slow)",
            default=True,
            )

    decimate_setting : BoolProperty(
            name="Decimate Mesh",
            description="Decimate each layer"
                        "(Warning, may be slow)",
            default=True,
            )
            
    apply_setting : BoolProperty(
            name="Apply Decimation",
            description="Apply all decimation modifiers"
                        "(Warning, may be slow)",
            default=True,
            )
            
    material_setting : BoolProperty(
            name="Single Material",
            description="Use single material for all objects",
            default=True,
            )
            
    parent_setting : BoolProperty(
            name="Group",
            description="Parent all subobjects underneath an empty",
            default=True,
            )

    decimate_ratio : FloatProperty(
            name="Ratio",
            description="Choose percentage to reduce mesh by",
            min=0.0 , max=1.0,
            default=0.25,
            )

    axis_forward_setting : EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='-Y',
            )

    axis_up_setting : EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Z',
            )

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)

        box : layout.box()
        row : box.row()
                
        row.prop(self, "decimate_setting")
        row.prop(self, "decimate_ratio")
        layout.prop(self, "apply_setting")
        layout.prop(self, "material_setting")
        layout.prop(self, "parent_setting")              
               
        layout.prop(self, "axis_forward_setting")
        layout.prop(self, "axis_up_setting")

#        layout.prop(self, "image_search_setting")

    def execute(self, context):

        # get the folder
        folder = (os.path.dirname(self.filepath))


        # iterate through the selected files
        for i in self.files:

            newObjects = ""

            # generate full path to file
            path_to_file = (os.path.join(folder, i.name))

            # call obj operator and assign ui values                  
            bpy.ops.import_scene.fbx(filepath = path_to_file,
                                use_manual_orientation=True, 
                                axis_forward = self.axis_forward_setting,
                                axis_up = self.axis_up_setting
                                )
#                                use_image_search = self.image_search_setting
#                                use_manual_orientation=False, 
#                                global_scale=1, 
#                                bake_space_transform=False, 
#                                use_custom_normals=True, 
#                                use_image_search=True, 
#                                use_alpha_decals=False, 
#                                decal_offset=0, 
#                                use_anim=True, 
#                                anim_offset=1, 
#                                use_custom_props=True, 
#                                use_custom_props_enum_as_string=True, 
#                                ignore_leaf_bones=False, 
#                                force_connect_children=False, 
#                                automatic_bone_orientation=False, 
#                                primary_bone_axis='Y', secondary_bone_axis='X', 
#                                use_prepost_rot=True 
#                                
            imported_objects = bpy.context.selected_objects
            print('Imported name: ', imported_objects)
            
            if self.material_setting:
                assetName = i.name.replace(".fbx", '')
                matName = (assetName + "Mat")
                mat = bpy.data.materials.new(name=matName)
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes["Principled BSDF"]
                colAttr = mat.node_tree.nodes.new('ShaderNodeAttribute')
                mat.node_tree.links.new(bsdf.inputs['Base Color'], colAttr.outputs['Color'])  

            
            for ob in imported_objects:
                
                #Check if object is a Mesh
                if ob.type == 'MESH':             
                    if ob.data.vertex_colors:
                        if not self.material_setting:                        
                            matName = (ob.name + "Mat")
                            mat = bpy.data.materials.new(name=matName)
                            mat.use_nodes = True
                            bsdf = mat.node_tree.nodes["Principled BSDF"]
                            colAttr = mat.node_tree.nodes.new('ShaderNodeAttribute')
                            colAttr.attribute_name = ob.data.vertex_colors[0].name
                            mat.node_tree.links.new(bsdf.inputs['Base Color'], colAttr.outputs['Color'])

                            # Assign it to object
                            if ob.data.materials:
                                ob.data.materials[0] = mat
                            else:
                                ob.data.materials.append(mat)
                        else:
                            mat.use_nodes = True
                            colAttr.attribute_name = ob.data.vertex_colors[0].name

                            # Assign it to object
                            if ob.data.materials:
                                ob.data.materials[0] = mat
                            else:
                                ob.data.materials.append(mat)

                if self.decimate_setting:
                        mod = bpy.data.objects[ob.name].modifiers.new(name='Decimate',type='DECIMATE')
                        mod.decimate_type = 'DISSOLVE'
                        mod.angle_limit = 0.0872665

                        mod2 = bpy.data.objects[ob.name].modifiers.new(name='Decimate',type='DECIMATE')
                        mod2.use_collapse_triangulate = True
                        mod2.ratio = self.decimate_ratio
                        
                        if self.apply_setting:
                            bpy.ops.object.select_all(action='DESELECT')
                            ob.select_set(state=True)
                            bpy.context.view_layer.objects.active = ob
                            for mod in [m for m in ob.modifiers if m.type == 'DECIMATE']:
                                bpy.ops.object.modifier_apply(modifier=mod.name)

                                
            if self.parent_setting:
                assetName = i.name.replace(".fbx", '')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.empty_add(type='CIRCLE', align='WORLD', radius=(1), location=(0, 0, 0), rotation=(1.5708, 0, 0))
                obj = bpy.context.view_layer.objects.active
                obj.name = assetName
                layer = bpy.context.view_layer
                layer.update()
                for ob in imported_objects:
                            bpy.ops.object.select_all(action='DESELECT')
                            obj.select_set(state=True)
                            bpy.context.view_layer.objects.active = obj                                            
                            ob.select_set(state=True)
                            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

            layer = bpy.context.view_layer
            layer.update()

                    

                        





#  utils for batch processing kitbash stamps.       
#                bpy.context.scene.objects.active = bpy.context.selected_objects[0]
#                bpy.ops.object.modifier_add(type='SUBSURF')
#                bpy.context.object.modifiers["Subsurf"].levels = 2
#                bpy.ops.object.modifier_add(type='DECIMATE')
#                bpy.context.object.modifiers["Decimate.001"].ratio = 0.5
#                bpy.ops.object.modifier_add(type='DECIMATE')
#                bpy.context.object.modifiers["Decimate.001"].decimate_type = 'DISSOLVE'
#                bpy.context.object.modifiers["Decimate.001"].delimit = {'SEAM', 'SHARP'}
#                bpy.context.object.modifiers["Decimate.001"].angle_limit = 0.0523599
#                bpy.ops.object.modifier_add(type='TRIANGULATE')
#                bpy.context.object.modifiers["Triangulate"].quad_method = 'BEAUTY'
#                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
#                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate.001")
#                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")
#                bpy.ops.object.mode_set(mode='EDIT')
#                bpy.ops.mesh.select_all(action = 'DESELECT')
#                bpy.ops.mesh.select_all(action='TOGGLE')
#                bpy.ops.mesh.tris_convert_to_quads()
#                bpy.ops.mesh.faces_shade_smooth()
#                bpy.ops.mesh.mark_sharp(clear=True)
#                bpy.ops.mesh.mark_sharp(clear=True, use_verts=True)
#                #if not bpy.context.object.data.uv_layers:
#                bpy.ops.uv.smart_project(island_margin=0.01 , user_area_weight=0.75)
#                bpy.ops.object.mode_set(mode='OBJECT')
#                bpy.context.object.data.use_auto_smooth = True
#                bpy.context.object.data.auto_smooth_angle = 0.575959

            bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}



    
    
    
    
    


    filepath : StringProperty(name="File path", description="File filepath of Fbx", maxlen=4096, default="")
    filter_folder : BoolProperty(name="Filter folders", description="", default=True, options={'HIDDEN'})
    filter_glob : StringProperty(default="*.fbx", options={'HIDDEN'})
    files : CollectionProperty(name='File path', type=bpy.types.OperatorFileListElement)
    filename_ext = '.fbx'
    
    #@classmethod
    #def poll(cls, context):
    #   return context.active_object is not None and context.active_object.type == 'MESH'

    # ImportHelper mixin class uses this
    filename_ext = ".fbx"

    filter_glob : StringProperty(
            default="*.fbx",
            options={'HIDDEN'},
            )

    # Selected files
    files : CollectionProperty(type=bpy.types.PropertyGroup)



def menu_import_draw(self, context):
    self.layout.operator(BR_OT_import_fbx_with_vertex_color.bl_idname)

    
def menu_export_draw(self, context):
    self.layout.operator(BR_OT_export_shapekey_as_obj.bl_idname)


classes = (
    BR_OT_import_fbx_with_vertex_color,
)



def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_import_draw)
    bpy.types.TOPBAR_MT_file_export.append(menu_export_draw)


                

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
            
    bpy.types.TOPBAR_MT_file_import.remove(menu_import_draw)
    bpy.types.TOPBAR_MT_file_export.remove(menu_export_draw)

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_view.remove(menu_import_draw)
        bpy.types.VIEW3D_MT_view.remove(menu_export_draw)
if __name__ == "__main__":
    try:
        # by running unregister here we can run this script
        # in blenders text editor
        # the first time we run this script inside blender
        # we get an error that removing the changes fails
        unregister()
    except:
        pass
    register()
