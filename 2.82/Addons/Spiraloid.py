bl_info = {
    'name': 'Spiraloid Toolkit',
    'author': 'Bay Raitt',
    'version': (0, 4),
    'blender': (2, 80, 0),
    "description": "Spiraloid toolkit - requires addons: Bool Tool ",
    'category': 'Import-Export',
    'location': 'Spiraloid > ',
    'wiki_url': ''
    }

import bpy
from bpy_extras.io_utils import ImportHelper
import os.path
import bpy, os
from bpy.props import *
import subprocess

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
    IntProperty,
    CollectionProperty,
)
from bpy.types import (Panel,
                       PropertyGroup,
                       AddonPreferences
                       )

import bmesh




class SpiraloidPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    assets_folder = StringProperty(
            name="Assets Folder",
            subtype='DIR_PATH',
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Location for Spiraloid Template Assets")
        layout.prop(self, "assets_folder")







def nuke_flat_texture(objects, width, height):
    # selected_objects = bpy.context.selected_objects


    # path to the folder
    file_path = bpy.data.filepath
    file_name = bpy.path.display_name_from_filepath(file_path)
    file_ext = '.blend'
    file_dir = file_path.replace(file_name+file_ext, '')
    materials_dir = file_dir+"Materials\\"


    for ob in objects:
        if ob.type == 'MESH':
            if ob.active_material is not None:
                ob.active_material.node_tree.nodes.clear()
                for i in range(len(ob.material_slots)):
                    bpy.ops.object.material_slot_remove({'object': ob})
            bpy.ops.object.shade_smooth()

            assetName = ob.name
            matName = (assetName + "Mat")
            texName_albedo = (assetName + "_albedo")

            mat = bpy.data.materials.new(name=matName)
            mat.use_nodes = True
            mat.node_tree.nodes.clear()
            mat_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

            shader = mat.node_tree.nodes.new(type='ShaderNodeBackground')

            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            texture.image = bpy.data.images.new(texName_albedo, width=width, height=height)
            # texture.image = bpy.ops.image.new('INVOKE_AREA',texName_albedo, width=1024, height=1024, color=[0.5, 0.5, 0.5, 1.0], alpha=True,)
            mat.node_tree.links.new(texture.outputs[0], shader.inputs[0])

            shader.name = "Background"
            shader.label = "Background"

            mat_output = mat.node_tree.nodes.get('Material Output')
            mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

            # Assign it to object
            if ob.data.materials:
                ob.data.materials[0] = mat
            else:
                ob.data.materials.append(mat)                 
            
            if os.path.exists(file_dir):
                if not os.path.exists(materials_dir):
                    os.makedirs(materials_dir)
                else:
                    outImageFileName = texture.image.name+".png"
                    outImageFilePathName = materials_dir+outImageFileName
                    texture.image.file_format = 'PNG'
                    texture.image.filepath = outImageFilePathName
                    texture.image.save()
                    # report({'INFO'},"Baked albedo texture saved to: " + outImageFilePathName )


                    print (outImageFilePathName)
                    # subprocess.Popen('explorer '+ materials_dir)
                    subprocess.call('start '+ outImageFilePathName, shell=True)




    return {'FINISHED'}



def nuke_diffuse_texture(objects, width, height):
    # selected_objects = bpy.context.selected_objects


    # path to the folder
    file_path = bpy.data.filepath
    file_name = bpy.path.display_name_from_filepath(file_path)
    file_ext = '.blend'
    file_dir = file_path.replace(file_name+file_ext, '')
    materials_dir = file_dir+"Materials\\"


    for ob in objects:
        if ob.type == 'MESH':
            if ob.active_material is not None:
                ob.active_material.node_tree.nodes.clear()
                for i in range(len(ob.material_slots)):
                    bpy.ops.object.material_slot_remove({'object': ob})
            bpy.ops.object.shade_smooth()

            assetName = ob.name
            # matName = (assetName + "Mat")
            # matName = file_name
            matName = bytes(file_name, "utf-8").decode("unicode_escape")
            
            texName_albedo = (matName + "_albedo")
            
            mat = bpy.data.materials.new(name=matName)
            mat.use_nodes = True
            mat.node_tree.nodes.clear()
            mat_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

            shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfDiffuse')

            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            texture.image = bpy.data.images.new(texName_albedo, width=width, height=height)
            # texture.image = bpy.ops.image.new('INVOKE_AREA',texName_albedo, width=1024, height=1024, color=[0.5, 0.5, 0.5, 1.0], alpha=True,)
            mat.node_tree.links.new(texture.outputs[0], shader.inputs[0])

            # shader.name = "file_name"
            # shader.label = "file_name"

            mat_output = mat.node_tree.nodes.get('Material Output')
            mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

            # Assign it to object
            if ob.data.materials:
                ob.data.materials[0] = mat
            else:
                ob.data.materials.append(mat)                 
            
            if os.path.exists(file_dir):
                if not os.path.exists(materials_dir):
                    os.makedirs(materials_dir)
                else:
                    outImageFileName = texture.image.name+".png"
                    outImageFilePathName = materials_dir+outImageFileName
                    texture.image.file_format = 'PNG'
                    texture.image.filepath = outImageFilePathName
                    texture.image.save()
                    # report({'INFO'},"Baked albedo texture saved to: " + outImageFilePathName )


                    # subprocess.Popen('explorer '+ materials_dir)
                    # subprocess.call('start '+ outImageFilePathName, shell=True)
                    # print(outImageFilePathName)
                    subprocess.call('start '+ " \"" + "\" " + "\"" +  outImageFilePathName + "\"", shell=True)


    return {'FINISHED'}



def nuke_bsdf_textures(objects, width, height):                
    selected_objects = bpy.context.selected_objects


    # path to the folder
    file_path = bpy.data.filepath
    file_name = bpy.path.display_name_from_filepath(file_path)
    file_ext = '.blend'
    file_dir = file_path.replace(file_name+file_ext, '')
    materials_dir = file_dir+"Materials\\"


    for ob in selected_objects:
        if ob.type == 'MESH':
            if ob.active_material is not None:
                ob.active_material.node_tree.nodes.clear()
                for i in range(len(ob.material_slots)):
                    bpy.ops.object.material_slot_remove({'object': ob})
            bpy.ops.object.shade_smooth()
            bpy.context.object.data.use_auto_smooth = False
            bpy.ops.mesh.customdata_custom_splitnormals_clear()

            assetName = ob.name
            # matName = (assetName + "Mat")
            matName = bytes(file_name, "utf-8").decode("unicode_escape")

            mat = bpy.data.materials.new(name=matName)
            
            mat.use_nodes = True
            texName_albedo = (assetName + "_albedo")
            texName_roughness = (assetName + "_roughness")
            texName_metallic = (assetName + "_metallic")
            texName_emission = (assetName + "_emission")
            texName_normal = (assetName + "_normal") 
            # texName_orm = (assetName + "_orm")

            mat.node_tree.nodes.clear()
            bpy.ops.object.shade_smooth()
            mat_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
            shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            shader.inputs[0].default_value = (1, 1, 1, 1)
            mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            texture.image = bpy.data.images.new(texName_albedo,  width=width, height=height)
            mat.node_tree.links.new(texture.outputs[0], shader.inputs[0])
            if os.path.exists(file_dir):
                if not os.path.exists(materials_dir):
                    os.makedirs(materials_dir)
                else:
                    outImageFileName = texture.image.name+".png"
                    outImageFilePathName = materials_dir+outImageFileName
                    texture.image.file_format = 'PNG'
                    texture.image.filepath = outImageFilePathName
                    texture.image.save()

            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            texture.image = bpy.data.images.new(texName_roughness,  width=width, height=height)
            mat.node_tree.links.new(texture.outputs[0], shader.inputs[7])
            if os.path.exists(file_dir):
                if not os.path.exists(materials_dir):
                    os.makedirs(materials_dir)
                else:
                    outImageFileName = texture.image.name+".png"
                    outImageFilePathName = materials_dir+outImageFileName
                    texture.image.file_format = 'PNG'
                    texture.image.filepath = outImageFilePathName
                    texture.image.save()

            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            texture.image = bpy.data.images.new(texName_metallic,  width=width, height=height)
            mat.node_tree.links.new(texture.outputs[0], shader.inputs[4])
            if os.path.exists(file_dir):
                if not os.path.exists(materials_dir):
                    os.makedirs(materials_dir)
                else:
                    outImageFileName = texture.image.name+".png"
                    outImageFilePathName = materials_dir+outImageFileName
                    texture.image.file_format = 'PNG'
                    texture.image.filepath = outImageFilePathName
                    texture.image.save()

            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            texture.image = bpy.data.images.new(texName_emission,  width=width, height=height)
            mat.node_tree.links.new(texture.outputs[0], shader.inputs[17])
            if os.path.exists(file_dir):
                if not os.path.exists(materials_dir):
                    os.makedirs(materials_dir)
                else:
                    outImageFileName = texture.image.name+".png"
                    outImageFilePathName = materials_dir+outImageFileName
                    texture.image.file_format = 'PNG'
                    texture.image.filepath = outImageFilePathName
                    texture.image.save()

            # texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            # texture.image = bpy.data.images.new(texName_orm,  width=width, height=height)
            # separateRGB =  mat.node_tree.nodes.new(type='ShaderNodeSeparateRGB')
            # mat.node_tree.links.new(texture.outputs[0], separateRGB.inputs[0])
            # mat.node_tree.links.new(separateRGB.outputs[2], shader.inputs[4])
            # mat.node_tree.links.new(separateRGB.outputs[1], shader.inputs[7])

            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            texture.image = bpy.data.images.new(texName_normal, width=width, height=height)
            texture.image.colorspace_settings.name = 'Non-Color'
            bump = mat.node_tree.nodes.new(type='ShaderNodeNormalMap')
            mat.node_tree.links.new(texture.outputs[0], bump.inputs[1])
            mat.node_tree.links.new(bump.outputs[0], shader.inputs[19])
            if os.path.exists(file_dir):
                if not os.path.exists(materials_dir):
                    os.makedirs(materials_dir)
                else:
                    outImageFileName = texture.image.name+".png"
                    outImageFilePathName = materials_dir+outImageFileName
                    texture.image.file_format = 'PNG'
                    texture.image.filepath = outImageFilePathName
                    texture.image.save()

            # Assign it to object
            if ob.data.materials:
                ob.data.materials[0] = mat
            else:
                ob.data.materials.append(mat)





    return {'FINISHED'}

def empty_trash(self, context):

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

    return {'FINISHED'}

class BR_OT_nuke_bsdf(bpy.types.Operator):
    """Nuke Selected Object 50% Gray"""
    bl_idname = "view3d.spiraloid_nuke_bsdf"
    bl_label = "Nuke BSDF"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):                
        selected_objects = bpy.context.selected_objects
        for ob in selected_objects:
            if ob.type == 'MESH':
                if ob.active_material is not None:
                    for i in range(len(ob.material_slots)):
                        bpy.ops.object.material_slot_remove({'object': ob})
                bpy.ops.object.shade_smooth()

                assetName = ob.name
                matName = (assetName + "Mat")



                mat = bpy.data.materials.new(name=matName)
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                for node in nodes:
                    if node.type != 'OUTPUT_MATERIAL': # skip the material output node as we'll need it later
                        nodes.remove(node) 

                shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')

                shader.name = "Principled BSDF"
                shader.label = "Principled BSDF"
                shader.inputs[0].default_value = (0.214041, 0.214041, 0.214041, 1)
                shader.inputs[7].default_value = 0.66
                shader.inputs[7].default_value = 0.66

                mat_output = mat.node_tree.nodes.get('Material Output')
                mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])



                # Assign it to object
                if ob.data.materials:
                    ob.data.materials[0] = mat
                else:
                    ob.data.materials.append(mat)                 
        return {'FINISHED'}

class BR_OT_nuke_bsdf_vertex_color(bpy.types.Operator):
    """Nuke Selected Object 50% Gray"""
    bl_idname = "view3d.spiraloid_nuke_bsdf_vertex_color"
    bl_label = "Nuke BSDF Vertex Color"
    bl_options = {'REGISTER', 'UNDO'}
   
    def execute(self, context):                
        selected_objects = bpy.context.selected_objects
        for ob in selected_objects:
            assetName = ob.name
            matName = (assetName + "Mat")
            mat = bpy.data.materials.new(name=matName)
            mat.use_nodes = True
            #Check if object is a Mesh
            if ob.type == 'MESH':             
                mat = bpy.data.materials.new(name=matName)
                mat.use_nodes = True
                mat.node_tree.nodes.clear()
                bpy.ops.object.shade_smooth()
                mat_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
                shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
                shader.inputs[0].default_value = (1, 1, 1, 1)
                mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])
                
                colAttr = mat.node_tree.nodes.new('ShaderNodeAttribute')

            #    bpy.data.brushes[0].color = (0.5, 0.5, 0.5)
            #    bpy.ops.paint.vertex_color_set()
            
                context = bpy.context
                mesh = context.object.data
                bm = bmesh.new()
                bm.from_mesh(mesh)

                
                # make a random color table for each vert
                # vert_color = random_color_table[vert.index]
                 
                if not ob.data.vertex_colors:
                    #bpy.ops.mesh.vertex_color_add()
                    color_layer = bm.loops.layers.color.new("Col")
                else :
                    color_layer = bm.loops.layers.color.get(ob.data.vertex_colors[0].name)

                for face in bm.faces:
                    for loop in face.loops:
                        print("Vert:", loop.vert.index)
                        loop[color_layer] = (0.5, 0.5, 0.5, 1.0)
                bm.to_mesh(mesh)

                colAttr.attribute_name = ob.data.vertex_colors[0].name
                mat.node_tree.links.new(shader.inputs['Base Color'], colAttr.outputs['Color'])
                mat_output = mat.node_tree.nodes.get('Material Output')
                mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

                # Assign it to object
                if ob.data.materials:
                    ob.data.materials[0] = mat
                else:
                    ob.data.materials.append(mat)                 
                
        return {'FINISHED'}

class BR_OT_nuke_bsdf_texture(bpy.types.Operator):
    """Nuke Selected Object 50% Gray"""
    bl_idname = "view3d.spiraloid_nuke_bsdf_texture"
    bl_label = "Nuke BSDF Textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        nuke_bsdf_textures(selected_objects, 1024, 1024)
        return {'FINISHED'}   

class BR_OT_nuke_flat(bpy.types.Operator):
    """Nuke Selected Object 50% Gray"""
    bl_idname = "view3d.spiraloid_nuke_flat"
    bl_label = "Nuke Flat"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):                
        selected_objects = bpy.context.selected_objects
        for ob in selected_objects:
            assetName = ob.name
            matName = (assetName + "Mat")
            mat = bpy.data.materials.new(name=matName)
            mat.use_nodes = True
            #Check if object is a Mesh
            if ob.type == 'MESH':             
                mat = bpy.data.materials.new(name=matName)
                mat.use_nodes = True
                mat.node_tree.nodes.clear()
                bpy.ops.object.shade_smooth()
                mat_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
                shader = mat.node_tree.nodes.new(type='ShaderNodeEmission')
                shader.name = "Background"
                shader.label = "Background"
                shader.inputs[0].default_value = (1, 1, 1, 1)
                mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

            #    bpy.data.brushes[0].color = (0.5, 0.5, 0.5)
            #    bpy.ops.paint.vertex_color_set()
                
                # Assign it to object
                if ob.data.materials:
                    ob.data.materials[0] = mat
                else:
                    ob.data.materials.append(mat)                 
                
        return {'FINISHED'}

class BR_OT_nuke_flat_vertex_color(bpy.types.Operator):
    """Nuke Selected Object 50% Gray"""
    bl_idname = "view3d.spiraloid_nuke_flat_vertex_color"
    bl_label = "Nuke Flat Vertex Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):                
        imported_objects = bpy.context.selected_objects
        for ob in imported_objects:
            assetName = ob.name
            matName = (assetName + "Mat")
            mat = bpy.data.materials.new(name=matName)
            mat.use_nodes = True
            shader = mat.node_tree.nodes["Principled BSDF"]
            colAttr = mat.node_tree.nodes.new('ShaderNodeAttribute')
            mat.node_tree.links.new(shader.inputs['Base Color'], colAttr.outputs['Color'])  

            #Check if object is a Mesh
            if ob.type == 'MESH':
                bpy.context.object.active_material.node_tree.nodes.clear()
                mat_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

                bpy.ops.object.shade_smooth() 
                
                matName = (ob.name + "Mat")
                mat = bpy.data.materials.new(name=matName)
                mat.use_nodes = True
                shader = mat.node_tree.nodes.new(type='ShaderNodeEmission')
                shader.name = "Background"
                shader.label = "Background"
                shader.inputs[0].default_value = (1, 1, 1, 1)
                mat_output = mat.node_tree.nodes.get('Material Output')
                mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])
 
            #    bpy.data.brushes[0].color = (0.5, 0.5, 0.5)
            #    bpy.ops.paint.vertex_color_set()
                
                context = bpy.context
                mesh = context.object.data
                bm = bmesh.new()
                bm.from_mesh(mesh)

                
                # make a random color table for each vert
                # vert_color = random_color_table[vert.index]
                 
                if not ob.data.vertex_colors:
                    #bpy.ops.mesh.vertex_color_add()
                    color_layer = bm.loops.layers.color.new("Col")
                else :
                    color_layer = bm.loops.layers.color.get(ob.data.vertex_colors[0].name)

                for face in bm.faces:
                    for loop in face.loops:
                        print("Vert:", loop.vert.index)
                        loop[color_layer] = (1, 1, 1, 1.0)
                bm.to_mesh(mesh)

                colAttr.attribute_name = ob.data.vertex_colors[0].name
                mat.node_tree.links.new(shader.inputs['Base Color'], colAttr.outputs['Color'])
                mat_output = mat.node_tree.nodes.get('Material Output')
                mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

                # Assign it to object
                if ob.data.materials:
                    ob.data.materials[0] = mat
                else:
                    ob.data.materials.append(mat)                 
                
        return {'FINISHED'}

class BR_OT_nuke_flat_texture(bpy.types.Operator):
    """Nuke Selected Object 50% Gray"""
    bl_idname = "view3d.spiraloid_nuke_flat_texture"
    bl_label = "Nuke Flat Texture"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        nuke_flat_texture(selected_objects, 1024, 1024)
        return {'FINISHED'}           

class BR_OT_nuke_diffuse_texture(bpy.types.Operator):
    """Nuke Selected Object with a Diffuse material and create a new texture"""
    bl_idname = "view3d.spiraloid_nuke_diffuse_texture"
    bl_label = "Nuke Diffuse Texture"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        nuke_diffuse_texture(selected_objects, 1024, 1024)
        return {'FINISHED'}           


class BR_OT_empty_trash(bpy.types.Operator):
    """Purge all data blocks with 0 users"""
    bl_idname = "wm.spiraloid_empty_trash"
    bl_label = "Empty Trash"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        empty_trash(self, context)
        return {'FINISHED'}           




class BR_OT_spiraloid_workshop(bpy.types.Operator):
    """Visit the spiraloid workshop for updates and goodies!"""
    bl_idname = "view3d.spiraloid_workshop"
    bl_label = "Visit Workshop..."
    def execute(self, context):                

        return {'FINISHED'}

def scene_mychosenobject_poll(self, object):
    return object.type == 'MESH'

class BakeCollectionSettings(bpy.types.PropertyGroup):
    bakeTargetObject : bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=scene_mychosenobject_poll,
        name="Target Mesh",         
        description="If no target mesh specified, a new automesh will be created from all meshes in collection"
    )
    

    bakeSize : bpy.props.EnumProperty(
        name="Size", 
        description="Width in pixels for baked texture size", 
        items={
            ("size_128", "128","128 pixels", 1),
            ("size_512", "512","512 pixels", 2),
            ("size_1024","1024", "1024 pixels", 3),
            ("size_2048", "2048","2048 pixels", 4),
            ("size_4096", "4096","4096 pixels", 5),
            ("size_8192", "8192","8192 pixels", 6),
            },
        default="size_1024"
    )
    bake_distance : bpy.props.FloatProperty(name="Bake Distance Scale",  description="raycast is largest dimension * this value ", min=0, max=3, default=0.02 )
    bake_to_unlit : bpy.props.BoolProperty(name="Bake Lightmap", description="Bake Collection to new mesh with lightmap texture and unlit shader", default=False)
    bake_albedo : bpy.props.BoolProperty(name="Bake Albedo", description="Bake Collection to mesh with Albedo Texture", default=True)
    bake_normal : bpy.props.BoolProperty(name="Bake Normal", description="Bake Collection to mesh with Normal Texture", default=False)
    bake_metallic : bpy.props.BoolProperty(name="Bake Metallic", description="Bake Collection to mesh with Metallic Texture", default=False)
    bake_roughness : bpy.props.BoolProperty(name="Bake Roughness", description="Bake Collection to mesh with Roughness Texture", default=False)
    bake_emission : bpy.props.BoolProperty(name="Bake Emission", description="Bake Collection to mesh with Emission Texture", default=False)
    bake_opacity : bpy.props.BoolProperty(name="Bake Opacity", description="Bake Collection to mesh with Opacity Texture", default=False)
    bake_w_decimate : bpy.props.BoolProperty(name="Decimate", description="Bake and Emission Textures", default=True)
    bake_w_decimate_ratio : bpy.props.FloatProperty(name="Decimate Ratio",  description="Amount to decimate target mesh", min=0, max=1, default=0.75 )
    bake_background : bpy.props.BoolProperty(name="Bake Background", description="Bake all but collection to spheremap", default=True)


class BR_OT_bake_collection(bpy.types.Operator):
    """Merge all meshes in active collection, unwrap and bake lighting and textures"""
    bl_idname = "view3d.spiraloid_bake_collection"
    bl_label = "Bake Collection..."
    bl_options = {'REGISTER', 'UNDO'}
    config: bpy.props.PointerProperty(type=BakeCollectionSettings)



    def draw(self, context):
        # bpy.types.Scene.bake_collection_settings = bpy.props.CollectionProperty(type=BakeCollectionSettings)
     
        # scene = bpy.data.scene[0]

        layout = self.layout
        scene = context.scene
        bake_collection_settings = scene.bake_collection_settings
        layout.prop(bake_collection_settings, "bakeTargetObject" )
        layout.prop(bake_collection_settings, "bakeSize")
        layout.prop(bake_collection_settings, "bake_distance")
        layout.prop(bake_collection_settings, "bake_to_unlit")
        layout.prop(bake_collection_settings, "bake_background")
        layout.prop(bake_collection_settings, "bake_albedo")
        layout.prop(bake_collection_settings, "bake_normal")
        layout.prop(bake_collection_settings, "bake_metallic")
        layout.prop(bake_collection_settings, "bake_roughness")
        layout.prop(bake_collection_settings, "bake_emission")
        layout.prop(bake_collection_settings, "bake_opacity")
        layout.prop(bake_collection_settings, "bake_w_decimate")
        layout.prop(bake_collection_settings, "bake_w_decimate_ratio")

        # self.draw(self.layout, context)

    
        # width = bpy.props.IntProperty(name="Width", description="Width in pixels for baked texture size", min=32, max=8196, default=1024)
        # height = bpy.props.IntProperty(name="Height", description="Height in pixels for baked texture size", min=32, max=8196, default=1024)
        # bake_to_unlit = bpy.props.BoolProperty(name="Bake Lightmap", description="Bake Collection to new mesh with lightmap texture and unlit shader", default=False)
        # # bake_to_pbr = BoolProperty(name="Bake BSDF Textures", description="Bake Collection to mesh with Albedo, Normal, Roughness, Metallic, Emission Textures", default=False)
        # bake_albedo = bpy.props.BoolProperty(name="Bake Albedo", description="Bake Collection to mesh with Albedo Texture", default=True)
        # bake_normal = bpy.props.BoolProperty(name="Bake Normal", description="Bake Collection to mesh with Normal Texture", default=False)
        # bake_metallic = bpy.props.BoolProperty(name="Bake Metallic", description="Bake Collection to mesh with Metallic Texture", default=False)
        # bake_roughness = bpy.props.BoolProperty(name="Bake Roughness", description="Bake Collection to mesh with Roughness Texture", default=False)
        # bake_emission = bpy.props.BoolProperty(name="Bake Emission", description="Bake Collection to mesh with Emission Texture", default=False)
        # bake_opacity = bpy.props.BoolProperty(name="Bake Opacity", description="Bake Collection to mesh with Opacity Texture", default=False)

        # Scene.decimate = bpy.props.BoolProperty(name="Decimate", description="Bake and Emission Textures", default=True)
        # if decimate:
        #     ratio = bpy.props.FloatProperty(name="Ratio", description="Amount to decimate target mesh", min=0, max=1, default=0.75)

    def execute(self, context):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')


        # path to the folder
        file_path = bpy.data.filepath
        file_name = bpy.path.display_name_from_filepath(file_path)
        file_ext = '.blend'
        file_dir = file_path.replace(file_name+file_ext, '')
        # materials_dir = file_dir+"\Materials\"
        materials_dir = file_dir+"\\Materials\\"
        if not os.path.exists(materials_dir):
            os.makedirs(materials_dir)
        
        settings = context.scene.bake_collection_settings

        bakemesh = settings.bakeTargetObject

        if settings.bakeSize == "size_128":
            width = 128
            height = 128
        if  settings.bakeSize == "size_512":
            width = 512
            height = 512
        if  settings.bakeSize == "size_1024":
            width = 1024
            height = 1024
        if  settings.bakeSize == "size_2048":
            width = 2048
            height = 2048
        if  settings.bakeSize == "size_4096":
            width = 4096
            height = 4096
        if  settings.bakeSize == "size_8192":
            width = 8192
            height = 8192

        print (settings.bakeSize)
        print (width)
        print (height)

        bake_to_unlit = settings.bake_to_unlit
        bake_albedo = settings.bake_albedo
        bake_normal = settings.bake_normal
        bake_metallic = settings.bake_metallic
        bake_roughness = settings.bake_roughness
        bake_emission = settings.bake_emission
        bake_opacity = settings.bake_opacity
        decimate = settings.bake_w_decimate
        ratio = settings.bake_w_decimate_ratio
        bake_distance = settings.bake_distance
        bake_background = settings.bake_background


        if bake_background :
            active_camera = bpy.context.scene.camera
            if active_camera is not None :
                bpy.ops.object.select_all(action='DESELECT')
                active_camera.select_set(state=True)
                bpy.context.view_layer.objects.active = active_camera
            else :
                cam = bpy.data.cameras.new("MirrorBallCamera")
                active_camera = bpy.data.objects.new("MirrorBallCamera",cam)
                bpy.context.scene.collection.objects.link(active_camera)
                bpy.ops.object.select_all(action='DESELECT')
                active_camera.select_set(state=True)
                bpy.context.view_layer.objects.active = active_camera

            bpy.context.scene.camera=active_camera
            bpy.context.object.data.type = 'PANO'
            bpy.context.object.data.cycles.panorama_type = 'MIRRORBALL'
            bpy.context.object.rotation_euler[0] = 1.5708
            bpy.context.object.rotation_euler[2] = 3.14159

            active_camera.location[2] = 1.61
            bpy.data.scenes[0].render.resolution_x = 512
            bpy.data.scenes[0].render.resolution_y = 512
            bpy.data.scenes[0].render.resolution_percentage = 100
            bpy.ops.render.render( animation=False, write_still=False )


            # newimage=B.Image.New(origimage.name+'_copy',width,height,32)
            # for x in range(0,width):
            #     for y in range(0,height):
            #         newp=origimage.getPixelF(x,y)
            #         newimage.setPixelF(x,y,newp)






        if bake_to_unlit :
            layer_collection = bpy.context.view_layer.layer_collection
            current_collection_name = bpy.context.view_layer.active_layer_collection.collection.name
            current_collection = bpy.data.collections.get(current_collection_name)
            scene_collection = bpy.context.view_layer.layer_collection
            if current_collection is None :
                if context.view_layer.objects.active is not None :
                    collections =  context.view_layer.objects.active.users_collection
                    if len(collections) > 0:
                        bpy.context.view_layer.active_layer_collection = collections()
                        current_collection_name = bpy.context.view_layer.active_layer_collection.collection.name
                        current_collection = bpy.data.collections.get(current_collection_name)
                    else:
                        current_collection = scene_collection
                        self.report({'ERROR'}, 'You must select a collection!')
                        return {'FINISHED'} 

            bake_collection_name = ("Lightmap Bake " + current_collection.name )
            bake_mesh_name = ("Lightmap BakeMesh  " + current_collection.name )
            # bake_to_unlit = True
            # decimate = True
            obj = bpy.context.object
            # print ("::::::::::::::::::::::::::::::::::::::::::::::")

            # for area in bpy.context.screen.areas:
            #     if area.type == 'VIEW_3D':
            #         if bpy.context.selected_objects:
            #             bpy.ops.object.mode_set(mode='OBJECT', toggle=False)   
            bpy.ops.object.select_all(action='DESELECT')
            # cleanup previous bake collection 
            if bpy.data.collections.get(bake_collection_name) : 

                # bpy.context.view_layer.layer_collection.children[bake_collection_name].exclude = False
                # bake_collection = bpy.data.collections.get(bake_collection_name)
                # bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[bake_collection_name]
                # bpy.ops.outliner.collection_delete(hierarchy=True)
                # bpy.context.scene.collection_delete(hierarchy=True)
                cc = bpy.context.view_layer.layer_collection.children[bake_collection_name].collection
                for o in cc.objects:
                    bpy.data.objects.remove(o)
                bpy.context.scene.collection.children.unlink(cc)
                for c in bpy.data.collections:
                    if not c.users:
                        bpy.data.collections.remove(c)


                for image in bpy.data.images:
                    if bake_mesh_name in image.name:
                        bpy.data.images.remove(image)
                        self.report({'WARNING'}, 'Deleted previous bake images!')

                for mat in bpy.data.materials:
                    if bake_mesh_name in mat.name:
                        bpy.data.materials.remove(mat)

                for tex in bpy.data.textures:
                    if bake_mesh_name in tex.name:
                        bpy.data.textures.remove(tex)

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

                    self.report({'WARNING'}, 'Deleted all previous bake data from scene!')


            # # verify all objects have UV's, if not create some.
            # bpy.ops.object.select_all(action='DESELECT')
            # for ob in current_collection.objects :
            #     if ob.type == 'MESH' : 
            #         print (ob.name)
            #         ob.select_set(state=True)
            #         bpy.context.view_layer.objects.active = ob
            #         if not len( ob.data.uv_layers ):
            #             bpy.ops.uv.smart_project()
            #             bpy.ops.uv.smart_project(angle_limit=66)
            #             bpy.ops.uv.smart_project(island_margin=0.05, user_area_weight=0)

            if bakemesh is None:
                # select all objects and the bake mesh to prepare for bake
                bpy.ops.object.select_all(action='DESELECT')
                for ob in current_collection.objects :
                    if ob.type == 'MESH' : 
                        print (ob.name)
                        ob.select_set(state=True)
                        bpy.context.view_layer.objects.active = ob
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                # this duplicates meshes and puts them in the new collection but it doesn't deal w instances well. perhaps duplicate collection might be a better way to go here...
                # we need to make all instances real before joining    
                # bpy.ops.object.select_all(action='SELECT')
                # bpy.ops.object.duplicates_make_real()
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((-4.37114e-08, -1, 0), (1, -4.37114e-08, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'INVERSE_SQUARE', "proportional_size":0.101089, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})

                bpy.ops.object.booltool_auto_union()

                bakemesh = bpy.context.object


                if decimate:
                    bpy.ops.object.modifier_add(type='DECIMATE')
                    bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
                    bpy.context.object.modifiers["Decimate"].angle_limit = 0.0523599
                    bpy.context.object.modifiers["Decimate"].delimit = {'UV'}
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

                    bpy.ops.object.modifier_add(type='TRIANGULATE')
                    bpy.context.object.modifiers["Triangulate"].keep_custom_normals = True
                    bpy.context.object.modifiers["Triangulate"].quad_method = 'FIXED'
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")

                    bpy.ops.object.modifier_add(type='DECIMATE')
                    print (ratio)
                    bpy.context.object.modifiers["Decimate"].ratio = ratio
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

                # area = bpy.context.area
                # old_type = area.type
                # area.type = 'VIEW_3D'
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_all(action='SELECT')
                # if bakemesh.data.uv_layers:
                    # area.type = 'IMAGE_EDITOR'
                bpy.ops.uv.seams_from_islands()

                bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.05)
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                
                # if old_type != "":
                    # area.type = old_type
                # area.type = 'INFO'

            bakemesh.name = bake_mesh_name

            bpy.ops.object.select_all(action='DESELECT')
            bakemesh.select_set(state=True)
            bpy.context.view_layer.objects.active = bakemesh
            selected_objects = bpy.context.selected_objects
            # nuke_flat_texture(selected_objects, self.width, self.height)


            for ob in selected_objects:
                if ob.type == 'MESH':
                    if ob.active_material is not None:
                        ob.active_material.node_tree.nodes.clear()
                        for i in range(len(ob.material_slots)):
                            bpy.ops.object.material_slot_remove({'object': ob})
                    bpy.ops.object.shade_smooth()

                    assetName = ob.name
                    matName = (assetName + "Mat")
                    texName_lightmap = (assetName + "_lightmap")
                    mat = bpy.data.materials.new(name=matName)
                    mat.use_nodes = True
                    mat.node_tree.nodes.clear()
                    mat_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
                    shader = mat.node_tree.nodes.new(type='ShaderNodeBackground')
                    texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                    texture.image = bpy.data.images.new(texName_lightmap, width=width, height=height)

                    mat.node_tree.links.new(texture.outputs[0], shader.inputs[0])

                    shader.name = "Background"
                    shader.label = "Background"

                    mat_output = mat.node_tree.nodes.get('Material Output')
                    mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])



                    # Assign it to object
                    if ob.data.materials:
                        ob.data.materials[0] = mat
                    else:
                        ob.data.materials.append(mat)  





            bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name= bake_collection_name)
            # bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[current_collection_name]
            # bpy.context.view_layer.active_layer_collection.exclude = False

            bpy.ops.object.select_all(action='DESELECT')
            for ob in current_collection.objects :
                if ob.type == 'MESH' : 
                    ob.select_set(state=True)

            bakemesh.select_set(state=True)
            bpy.context.view_layer.objects.active = bakemesh

            #bake the textures
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.render.tile_x =  width
            bpy.context.scene.render.tile_y =  height
            bpy.context.scene.cycles.max_bounces = 4
            bpy.context.scene.cycles.diffuse_bounces = 4
            bpy.context.scene.cycles.glossy_bounces = 4
            bpy.context.scene.cycles.transparent_max_bounces = 4
            bpy.context.scene.cycles.transmission_bounces = 4
            bpy.context.scene.cycles.volume_bounces = 0

            bpy.context.scene.cycles.bake_type = 'COMBINED'
            bpy.context.scene.render.bake.use_selected_to_active = True
            bpy.context.scene.render.bake.use_cage = True
            ray_length = bakemesh.dimensions[1] * bake_distance
            bpy.context.scene.render.bake.cage_extrusion = ray_length
            bpy.context.scene.render.bake.use_pass_direct = True
            bpy.context.scene.render.bake.use_pass_indirect = True

            matnodes = bpy.context.active_object.material_slots[0].material.node_tree.nodes
            imgnodes = [n for n in matnodes if n.type == 'TEX_IMAGE']

            for n in imgnodes:
                if n.image.name == bake_mesh_name + "_lightmap":
                    n.select = True
                    matnodes.active = n
                    if os.path.exists(file_dir):
                        if os.path.exists(materials_dir):
                            outBakeFileName = n.image.name+".png"
                            outRenderFileName = materials_dir+outBakeFileName
                            n.image.file_format = 'PNG'
                            n.image.filepath = outRenderFileName
                            bpy.ops.object.bake(type='COMBINED', filepath=outRenderFileName, save_mode='EXTERNAL')
                            n.image.save()
                            self.report({'INFO'},"Baked lightmap texture saved to: " + outRenderFileName )
                    else:
                        bpy.ops.object.bake(type='COMBINED')
                        n.image.pack()




            # bpy.ops.object.bake('INVOKE_DEFAULT', type='COMBINED')
            # bpy.ops.object.bake("INVOKE_SCREEN", type='COMBINED')
            
            # bpy.context.view_layer.layer_collection.children[bake_collection_name].exclude = False
            # bpy.context.view_layer.layer_collection.children[current_collection_name].exclude = True


            bpy.context.view_layer.layer_collection.children[bake_collection_name].exclude = True
            bpy.context.view_layer.layer_collection.children[current_collection_name].exclude = False
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[current_collection_name]


        if bake_albedo or bake_normal or bake_roughness or bake_metallic or bake_emission or bake_opacity :

        # if not self.bake_to_lightmap:
            layer_collection = bpy.context.view_layer.layer_collection
            current_collection_name = bpy.context.view_layer.active_layer_collection.collection.name
            current_collection = bpy.data.collections.get(current_collection_name)
            scene_collection = bpy.context.view_layer.layer_collection
            if current_collection is None :
                current_collection = scene_collection
                self.report({'ERROR'}, 'You must select a collection!')
                return {'FINISHED'} 

            bake_collection_name = ("BSDF Bake " + current_collection.name )
            bake_mesh_name = ("BakeMesh " + current_collection.name )
            # bake_to_unlit = True
            # decimate = True
            obj = bpy.context.object
            # print ("::::::::::::::::::::::::::::::::::::::::::::::")

            # for area in bpy.context.screen.areas:
            #     if area.type == 'VIEW_3D':
            #         if bpy.context.selected_objects:
            #             bpy.ops.object.mode_set(mode='OBJECT', toggle=False)   
            bpy.ops.object.select_all(action='DESELECT')
            # cleanup previous bake collection 
            if bpy.data.collections.get(bake_collection_name) : 

                # bpy.context.view_layer.layer_collection.children[bake_collection_name].exclude = False
                # bake_collection = bpy.data.collections.get(bake_collection_name)
                # bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[bake_collection_name]
                # bpy.ops.outliner.collection_delete(hierarchy=True)
                # bpy.context.scene.collection_delete(hierarchy=True)
                cc = bpy.context.view_layer.layer_collection.children[bake_collection_name].collection
                for o in cc.objects:
                    bpy.data.objects.remove(o)
                bpy.context.scene.collection.children.unlink(cc)
                for c in bpy.data.collections:
                    if not c.users:
                        bpy.data.collections.remove(c)


                for image in bpy.data.images:
                    if bake_mesh_name in image.name:
                        bpy.data.images.remove(image)
                        self.report({'WARNING'}, 'Deleted previous bake images!')

                for mat in bpy.data.materials:
                    if bake_mesh_name in mat.name:
                        bpy.data.materials.remove(mat)

                for tex in bpy.data.textures:
                    if bake_mesh_name in tex.name:
                        bpy.data.textures.remove(tex)

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

                    self.report({'WARNING'}, 'Deleted all previous bake data from scene!')

            if bakemesh is None:

                # verify all objects have UV's, if not create some.
                bpy.ops.object.select_all(action='DESELECT')
                for ob in current_collection.objects :
                    if ob.type == 'MESH' : 
                        bpy.ops.object.select_all(action='DESELECT')
                        print (ob.name)
                        ob.select_set(state=True)
                        bpy.context.view_layer.objects.active = ob
                        if not len( ob.data.uv_layers ):
                            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                            bpy.ops.mesh.select_all(action='SELECT')
                            # bpy.ops.uv.smart_project()
                            # bpy.ops.uv.smart_project(angle_limit=66)
                            bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.01, user_area_weight=0.75)
                            bpy.ops.uv.average_islands_scale()

                            # select all faces
                            # bpy.ops.mesh.select_all(action='SELECT')
                            bpy.ops.uv.pack_islands(margin=0.017)

                            # bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.1)
                            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                            # bpy.ops.uv.seams_from_islands()


                # select all objects and the bake mesh to prepare for bake
                bpy.ops.object.select_all(action='DESELECT')
                for ob in current_collection.objects :
                    if ob.type == 'MESH' : 
                        print (ob.name)
                        ob.select_set(state=True)
                        bpy.context.view_layer.objects.active = ob
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)



                # this duplicates meshes and puts them in the new collection but it doesn't deal w instances well. perhaps duplicate collection might be a better way to go here...
                # we need to make all instances real before joining    
                # bpy.ops.object.select_all(action='SELECT')
                # bpy.ops.object.duplicates_make_real()
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((-4.37114e-08, -1, 0), (1, -4.37114e-08, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'INVERSE_SQUARE', "proportional_size":0.101089, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})


                bpy.ops.object.booltool_auto_union()

                bakemesh = bpy.context.object

                if decimate:
                    bpy.ops.object.modifier_add(type='DECIMATE')
                    bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
                    bpy.context.object.modifiers["Decimate"].angle_limit = 0.0523599
                    bpy.context.object.modifiers["Decimate"].delimit = {'UV'}
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

                    bpy.ops.object.modifier_add(type='TRIANGULATE')
                    bpy.context.object.modifiers["Triangulate"].keep_custom_normals = True
                    bpy.context.object.modifiers["Triangulate"].quad_method = 'FIXED'
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")

                    bpy.ops.object.modifier_add(type='DECIMATE')
                    bpy.context.object.modifiers["Decimate"].ratio = ratio
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

                # area = bpy.context.area
                # old_type = area.type
                # area.type = 'VIEW_3D'
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_all(action='SELECT')
                # if bakemesh.data.uv_layers:
                    # area.type = 'IMAGE_EDITOR'
                bpy.ops.uv.seams_from_islands()

                # bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001)
                bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                
                # if old_type != "":
                    # area.type = old_type
                # area.type = 'INFO'
            bakemesh.name = bake_mesh_name

            bpy.ops.object.select_all(action='DESELECT')
            bakemesh.select_set(state=True)
            bpy.context.view_layer.objects.active = bakemesh
            selected_objects = bpy.context.selected_objects
            # nuke_bsdf_textures(selected_objects, self.width, self.height)

            for ob in selected_objects:
                    if ob.type == 'MESH':
                        if ob.active_material is not None:
                            ob.active_material.node_tree.nodes.clear()
                            for i in range(len(ob.material_slots)):
                                bpy.ops.object.material_slot_remove({'object': ob})
                        bpy.ops.object.shade_smooth()
                        bpy.context.object.data.use_auto_smooth = False
                        bpy.ops.mesh.customdata_custom_splitnormals_clear()

                        assetName = ob.name
                        matName = (assetName + "Mat")
                        mat = bpy.data.materials.new(name=matName)
                        
                        mat.use_nodes = True
                        texName_albedo = (assetName + "_albedo")
                        texName_roughness = (assetName + "_roughness")
                        texName_metal = (assetName + "_metallic")
                        texName_emission = (assetName + "_emission")
                        texName_normal = (assetName + "_normal") 
                        # texName_orm = (assetName + "_orm")

                        mat.node_tree.nodes.clear()
                        bpy.ops.object.shade_smooth()
                        mat_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
                        shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
                        shader.inputs[0].default_value = (1, 1, 1, 1)
                        mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

                        if bake_albedo:
                            bpy.context.scene.render.bake.use_pass_direct = False
                            bpy.context.scene.render.bake.use_pass_indirect = False
                            bpy.context.scene.render.bake.use_pass_color = True
                            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                            texture.image = bpy.data.images.new(texName_albedo,  width=width, height=height)
                            mat.node_tree.links.new(texture.outputs[0], shader.inputs[0])

                        # if bake_opacity:

                        if bake_roughness:
                            bpy.context.scene.render.bake.use_pass_direct = False
                            bpy.context.scene.render.bake.use_pass_indirect = False
                            bpy.context.scene.render.bake.use_pass_color = False
                            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                            texture.image = bpy.data.images.new(texName_roughness,  width=width, height=height)
                            mat.node_tree.links.new(texture.outputs[0], shader.inputs[7])

                        if bake_metallic:
                            bpy.context.scene.render.bake.use_pass_direct = False
                            bpy.context.scene.render.bake.use_pass_indirect = False
                            bpy.context.scene.render.bake.use_pass_color = True
                            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                            texture.image = bpy.data.images.new(texName_metal,  width=width, height=height)
                            mat.node_tree.links.new(texture.outputs[0], shader.inputs[4])

                        if bake_emission:
                            bpy.context.scene.render.bake.use_pass_direct = False
                            bpy.context.scene.render.bake.use_pass_indirect = False
                            bpy.context.scene.render.bake.use_pass_color = True
                            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                            texture.image = bpy.data.images.new(texName_emission,  width=width, height=height)
                            mat.node_tree.links.new(texture.outputs[0], shader.inputs[17])

                        if bake_normal:
                            bpy.context.scene.render.bake.use_pass_direct = False
                            bpy.context.scene.render.bake.use_pass_indirect = False
                            bpy.context.scene.render.bake.use_pass_color = False
                            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                            texture.image = bpy.data.images.new(texName_normal, width=width, height=height)
                            texture.image.colorspace_settings.name = 'Non-Color'
                            bump = mat.node_tree.nodes.new(type='ShaderNodeNormalMap')
                            mat.node_tree.links.new(texture.outputs[0], bump.inputs[1])
                            mat.node_tree.links.new(bump.outputs[0], shader.inputs[19])

                        # Assign it to object
                        if ob.data.materials:
                            ob.data.materials[0] = mat
                        else:
                            ob.data.materials.append(mat)             






            bpy.context.scene.render.tile_x =  width
            bpy.context.scene.render.tile_y =  height
            bpy.context.scene.cycles.max_bounces = 4
            bpy.context.scene.cycles.diffuse_bounces = 4
            bpy.context.scene.cycles.glossy_bounces = 4
            bpy.context.scene.cycles.transparent_max_bounces = 4
            bpy.context.scene.cycles.transmission_bounces = 4
            bpy.context.scene.cycles.volume_bounces = 0




            bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name= bake_collection_name)

            # bake_collection = bpy.data.collections.get(bake_collection_name)
            # bpy.context.view_layer.active_layer_collection = bake_collection
            # bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[current_collection_name]

            # bpy.context.view_layer.active_layer_collection.exclude = False

            bpy.ops.object.select_all(action='DESELECT')
            for ob in current_collection.objects :
                if ob.type == 'MESH' : 
                    ob.select_set(state=True)

            bakemesh.select_set(state=True)
            bpy.context.view_layer.objects.active = bakemesh

            #bake the textures
            bpy.context.scene.render.engine = 'CYCLES'
            matnodes = bpy.context.active_object.material_slots[0].material.node_tree.nodes
            imgnodes = [n for n in matnodes if n.type == 'TEX_IMAGE']

            for n in imgnodes:
                if n.image.name == bake_mesh_name + "_albedo":
                    n.select = True
                    matnodes.active = n
                    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
                    bpy.context.scene.render.image_settings.color_depth = '8'
                    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
                    bpy.context.scene.render.image_settings.file_format = 'PNG'
                    bpy.context.scene.render.bake.use_pass_indirect = False
                    bpy.context.scene.render.bake.use_pass_direct = False
                    bpy.context.scene.render.bake.use_pass_color = True
                    bpy.context.scene.render.bake.use_selected_to_active = True
                    bpy.context.scene.render.bake.use_cage = True
                    ray_length = bakemesh.dimensions[1] * bake_distance
                    bpy.context.scene.render.bake.cage_extrusion = ray_length
                    if os.path.exists(file_dir):
                        if os.path.exists(materials_dir):
                            outBakeFileName = n.image.name+".png"
                            outRenderFileName = materials_dir+outBakeFileName
                            n.image.file_format = 'PNG'
                            n.image.filepath = outRenderFileName
                            bpy.ops.object.bake(type='DIFFUSE', filepath=outRenderFileName, save_mode='EXTERNAL')
                            n.image.save()
                            self.report({'INFO'},"Baked albedo texture saved to: " + outRenderFileName )
                    else:
                        bpy.ops.object.bake(type='DIFFUSE')
                        n.image.pack()

            for n in imgnodes:
                if n.image.name == bake_mesh_name + "_normal":
                    n.select = True
                    matnodes.active = n
                    bpy.context.scene.cycles.bake_type = 'NORMAL'
                    bpy.context.scene.render.image_settings.color_depth = '16'
                    bpy.context.scene.render.image_settings.color_mode = 'RGB'
                    bpy.context.scene.render.image_settings.file_format = 'PNG'
                    bpy.context.scene.render.bake.use_selected_to_active = True
                    bpy.context.scene.render.bake.use_cage = True
                    ray_length = bakemesh.dimensions[1] * bake_distance
                    bpy.context.scene.render.bake.cage_extrusion = ray_length
                    if os.path.exists(file_dir):
                        if os.path.exists(materials_dir):
                            outBakeFileName = n.image.name+".png"
                            outRenderFileName = materials_dir+outBakeFileName
                            n.image.file_format = 'PNG'
                            n.image.filepath = outRenderFileName
                            bpy.ops.object.bake(type='NORMAL', filepath=outRenderFileName, save_mode='EXTERNAL')
                            n.image.save()
                            self.report({'INFO'},"Baked normal texture saved to: " + outRenderFileName )
                    else:
                        bpy.ops.object.bake(type='NORMAL')
                        n.image.pack()

            for n in imgnodes:
                if n.image.name == bake_mesh_name + "_metal":
                    n.select = True
                    matnodes.active = n
                    bpy.context.scene.cycles.bake_type = 'GLOSSY'
                    bpy.context.scene.render.image_settings.color_depth = '8'
                    bpy.context.scene.render.image_settings.color_mode = 'BW'
                    bpy.context.scene.render.image_settings.file_format = 'PNG'
                    bpy.context.scene.render.bake.use_pass_indirect = False
                    bpy.context.scene.render.bake.use_pass_direct = False
                    bpy.context.scene.render.bake.use_pass_color = True
                    bpy.context.scene.render.bake.use_selected_to_active = True
                    bpy.context.scene.render.bake.use_cage = True
                    ray_length = bakemesh.dimensions[1] * bake_distance
                    bpy.context.scene.render.bake.cage_extrusion = ray_length
                    if os.path.exists(file_dir):
                        if os.path.exists(materials_dir):
                            outBakeFileName = n.image.name+".png"
                            outRenderFileName = materials_dir+outBakeFileName
                            n.image.file_format = 'PNG'
                            n.image.filepath = outRenderFileName
                            bpy.ops.object.bake(type='GLOSSY', filepath=outRenderFileName, save_mode='EXTERNAL')
                            n.image.save()
                            self.report({'INFO'},"Baked metal texture saved to: " + outRenderFileName )
                    else:
                        bpy.ops.object.bake(type='GLOSSY')
                        n.image.pack()

                    bpy.ops.object.bake(type='GLOSSY')

            for n in imgnodes:
                if n.image.name == bake_mesh_name + "_roughness":
                    n.select = True
                    matnodes.active = n
                    bpy.context.scene.cycles.bake_type = 'ROUGHNESS'
                    bpy.context.scene.render.image_settings.color_depth = '8'
                    bpy.context.scene.render.image_settings.color_mode = 'BW'
                    bpy.context.scene.render.image_settings.file_format = 'PNG'
                    bpy.context.scene.render.bake.use_selected_to_active = True
                    bpy.context.scene.render.bake.use_cage = True
                    ray_length = bakemesh.dimensions[1] * bake_distance
                    bpy.context.scene.render.bake.cage_extrusion = ray_length
                    if os.path.exists(file_dir):
                        if os.path.exists(materials_dir):
                            outBakeFileName = n.image.name+".png"
                            outRenderFileName = materials_dir+outBakeFileName
                            n.image.file_format = 'PNG'
                            n.image.filepath = outRenderFileName
                            bpy.ops.object.bake(type='ROUGHNESS', filepath=outRenderFileName, save_mode='EXTERNAL')
                            n.image.save()
                            self.report({'INFO'},"Baked roughness texture saved to: " + outRenderFileName )
                    else:
                        bpy.ops.object.bake(type='ROUGHNESS')
                        n.image.pack()

            for n in imgnodes:
                if n.image.name == bake_mesh_name + "_emission":
                    n.select = True
                    matnodes.active = n
                    bpy.context.scene.cycles.bake_type = 'EMIT'
                    bpy.context.scene.render.image_settings.color_depth = '8'
                    bpy.context.scene.render.image_settings.color_mode = 'BW'
                    bpy.context.scene.render.image_settings.file_format = 'PNG'
                    bpy.context.scene.render.bake.use_selected_to_active = True
                    bpy.context.scene.render.bake.use_cage = True
                    ray_length = bakemesh.dimensions[1] * bake_distance
                    bpy.context.scene.render.bake.cage_extrusion = ray_length
                    if os.path.exists(file_dir):
                        if os.path.exists(materials_dir):
                            outBakeFileName = n.image.name+".png"
                            outRenderFileName = materials_dir+outBakeFileName
                            n.image.file_format = 'PNG'
                            n.image.filepath = outRenderFileName
                            bpy.ops.object.bake(type='EMIT', filepath=outRenderFileName, save_mode='EXTERNAL')
                            n.image.save()
                            self.report({'INFO'},"Baked emission texture saved to: " + outRenderFileName )
                    else:
                        bpy.ops.object.bake(type='EMIT')
                        n.image.pack()

            # bpy.context.scene.cycles.bake_type = 'NORMAL'
            # bpy.context.scene.cycles.bake_type = 'AO'
            # bpy.context.scene.cycles.bake_type = 'ROUGHNESS'
            # bpy.context.scene.cycles.bake_type = 'GLOSSY'
            # if self.bake_emmision :
            #     bpy.context.scene.cycles.bake_type = 'EMIT'
            

            # for image in bpy.data.images:
            #     if (bake_mesh_name + "_albedo") in image.name:
            #         image.pack()

            bpy.context.view_layer.layer_collection.children[bake_collection_name].exclude = False
            bpy.context.view_layer.layer_collection.children[current_collection_name].exclude = True


        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


       
class BR_OT_add_cavity(bpy.types.Operator):
    """insert cavity nodes"""
    bl_idname = "view3d.spiraloid_add_cavity"
    bl_label = "Insert Cavity"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)                
        selected_objects = bpy.context.selected_objects
        if selected_objects is not None :
            aob = bpy.context.view_layer.objects.active
            for ob in selected_objects:
                if ob.type == 'MESH':
                    if ob.active_material is not None:
                        mat =  ob.active_material
                        mat.use_nodes = True

                        bevel = mat.node_tree.nodes.new(type='ShaderNodeBevel')
                        tcoord = mat.node_tree.nodes.new(type='ShaderNodeTexCoord')
                        crossp = mat.node_tree.nodes.new(type='ShaderNodeVectorMath')
                        mult = mat.node_tree.nodes.new(type='ShaderNodeMath')
                        gamma = mat.node_tree.nodes.new(type='ShaderNodeGamma')
                        ramp = mat.node_tree.nodes.new(type='ShaderNodeValToRGB')
                        mix = mat.node_tree.nodes.new(type='ShaderNodeMixShader')
                        shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfGlossy')
                        mat_output = mat.node_tree.nodes.get('Material Output')
                        existing_node_output = mat_output.inputs[0].links[0].from_node

                        matnodes = bpy.context.active_object.material_slots[0].material.node_tree.nodes
                        imgnodes = [n for n in matnodes if n.type == 'ShaderNodeBsdfPrincipled']
                        for n in imgnodes:
                            existing_shader_color_input = n.inputs[0].links[0].from_node
                            mat.node_tree.links.new(shader.inputs[0], existing_shader_color_input.outputs[0])

                        crossp.operation = 'CROSS_PRODUCT'
                        mult.operation = 'MULTIPLY'
                        mult.inputs[1].default_value = 2
                        bevel.samples = 8
                        bevel.inputs[0].default_value = 0.4
                        gamma.inputs[1].default_value = 0.3
                        ramp.color_ramp.elements[0].position = 0.00
                        ramp.color_ramp.elements[1].position = 0.33
                        ramp.color_ramp.interpolation = 'EASE'
                        shader.inputs[0].default_value = (0, 0, 0, 1)
                        shader.inputs[1].default_value = 1
                        shader.inputs[1].default_value = 1

                        mat.node_tree.links.new(bevel.outputs[0], crossp.inputs[0])
                        mat.node_tree.links.new(tcoord.outputs[1], crossp.inputs[1])
                        mat.node_tree.links.new(crossp.outputs[1], mult.inputs[0])
                        mat.node_tree.links.new(mult.outputs[0], gamma.inputs[0])
                        mat.node_tree.links.new(gamma.outputs[0], ramp.inputs[0])
                        mat.node_tree.links.new(ramp.outputs[0], mix.inputs[0])


                        mat.node_tree.links.new(shader.outputs[0], mix.inputs[1])
                        mat.node_tree.links.new(existing_node_output.outputs[0], mix.inputs[2])
                        mat.node_tree.links.new(mix.outputs[0], mat_output.inputs[0])




                        # Assign it to object
                        # if ob.data.materials:
                        #     ob.data.materials[0] = mat
                        # else:
                        #     ob.data.materials.append(mat)
                    else:
                        self.report({'ERROR'}, 'You must have a material assigned first!')
            for ob in selected_objects:
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = aob
        return {'FINISHED'}

        

class BR_OT_add_ao(bpy.types.Operator):
    """insert ambient occlusion node"""
    bl_idname = "view3d.spiraloid_add_ao"
    bl_label = "Insert AO"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)                
        selected_objects = bpy.context.selected_objects
        if selected_objects is not None :
            aob = bpy.context.view_layer.objects.active
            for ob in selected_objects:
                if ob.type == 'MESH':
                    if ob.active_material is not None:
                        mat =  ob.active_material
                        mat.use_nodes = True

                        ao = mat.node_tree.nodes.new(type='ShaderNodeAmbientOcclusion')
                        black = mat.node_tree.nodes.new(type='ShaderNodeEmission')
                        mix = mat.node_tree.nodes.new(type='ShaderNodeMixShader')
                        ramp = mat.node_tree.nodes.new(type='ShaderNodeValToRGB')

                        ramp.color_ramp.elements[0].position = 0.33
                        ramp.color_ramp.elements[1].position = 0.66
                        ramp.color_ramp.interpolation = 'B_SPLINE'



                        ramp.color_ramp.elements[0].color = (0.214041, 0.214041, 0.214041, 1)

                        black.inputs[0].default_value = (0, 0, 0, 1)


                        mat_output = mat.node_tree.nodes.get('Material Output')
                        existing_shader = mat_output.inputs[0].links[0].from_node


                        mat.node_tree.links.new(ao.outputs[0], ramp.inputs[0])
                        mat.node_tree.links.new(ramp.outputs[0], mix.inputs[0])
                        mat.node_tree.links.new(black.outputs[0], mix.inputs[1])
                        mat.node_tree.links.new(existing_shader.outputs[0], mix.inputs[2])
                        mat.node_tree.links.new(mix.outputs[0], mat_output.inputs[0])

                        matnodes = bpy.context.active_object.material_slots[0].material.node_tree.nodes
                        imgnodes = [n for n in matnodes if n.type == 'NORMAL_MAP']
                        for n in imgnodes:
                            mat.node_tree.links.new(n.outputs[0], ao.inputs[2])


                        # Assign it to object
                        # if ob.data.materials:
                        #     ob.data.materials[0] = mat
                        # else:
                        #     ob.data.materials.append(mat)
                    else:
                        self.report({'ERROR'}, 'You must have a material assigned first!')
            for ob in selected_objects:
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = aob
        return {'FINISHED'}

        
class BR_OT_add_curvature(bpy.types.Operator):
    """insert curvature nodes"""
    bl_idname = "view3d.spiraloid_add_curvature"
    bl_label = "Insert Curvature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)                
        selected_objects = bpy.context.selected_objects
        if selected_objects is not None :
            aob = bpy.context.view_layer.objects.active
            for ob in selected_objects:
                bpy.ops.object.select_all(action='DESELECT')
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
                if ob.type == 'MESH':
                    if ob.active_material is not None:
                        mat =  ob.active_material
                        mat.use_nodes = True
                        nodes = mat.node_tree.nodes

                        geometry = mat.node_tree.nodes.new(type='ShaderNodeNewGeometry')
                        ramp = mat.node_tree.nodes.new(type='ShaderNodeValToRGB')
                        contrast = mat.node_tree.nodes.new(type='ShaderNodeBrightContrast')
                        multR1 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                        multG1 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                        multB1 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                        multR2 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                        multG2 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                        multB2 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                        separateRGB = mat.node_tree.nodes.new(type='ShaderNodeSeparateRGB')
                        combineRGB = mat.node_tree.nodes.new(type='ShaderNodeCombineRGB')


                        multR1.operation = 'MULTIPLY'
                        multG1.operation = 'MULTIPLY'
                        multB1.operation = 'MULTIPLY'
                        multR2.operation = 'MULTIPLY'
                        multG2.operation = 'MULTIPLY'
                        multB2.operation = 'MULTIPLY'
                        ramp.color_ramp.elements[0].position = 0.40
                        ramp.color_ramp.elements[1].position = 0.55
                        ramp.color_ramp.interpolation = 'EASE'

                        contrast.inputs[1].default_value = 2
                        contrast.inputs[2].default_value = 3



                        matnodes = bpy.context.active_object.material_slots[0].material.node_tree.nodes
                        shadernodes = [n for n in matnodes if "BSDF" in n.name]
                        for n in shadernodes:
                            if not n.inputs[0].links:
                                rgb = nodes.new("ShaderNodeRGB")
                                rgb.outputs[0].default_value = n.inputs[0].default_value
                                mat.node_tree.links.new(rgb.outputs[0], separateRGB.inputs[0])
                            else :
                                alphasocket = n.inputs[0]
                                node_in = n.inputs
                                for nn in n.inputs[0].links:
                                    mat.node_tree.links.new(nn.from_node.outputs[0],  separateRGB.inputs[0])
                            mat.node_tree.links.new(combineRGB.outputs[0],  n.inputs[0])

                        mat.node_tree.links.new(geometry.outputs[7], ramp.inputs[0])
                        mat.node_tree.links.new(ramp.outputs[0], contrast.inputs[0])
                        mat.node_tree.links.new(contrast.outputs[0], multR1.inputs[0])
                        mat.node_tree.links.new(contrast.outputs[0], multG1.inputs[0])
                        mat.node_tree.links.new(contrast.outputs[0], multB1.inputs[0])
                        mat.node_tree.links.new(separateRGB.outputs[0], multR1.inputs[1])
                        mat.node_tree.links.new(separateRGB.outputs[1], multG1.inputs[1])
                        mat.node_tree.links.new(separateRGB.outputs[2], multB1.inputs[1])
                        mat.node_tree.links.new(separateRGB.outputs[0], multR2.inputs[1])
                        mat.node_tree.links.new(separateRGB.outputs[1], multG2.inputs[1])
                        mat.node_tree.links.new(separateRGB.outputs[2], multB2.inputs[1])                        
                        mat.node_tree.links.new(multR1.outputs[0],multR2.inputs[0])
                        mat.node_tree.links.new(multG1.outputs[0],multG2.inputs[0])
                        mat.node_tree.links.new(multB1.outputs[0],multB2.inputs[0])
                        mat.node_tree.links.new(multR2.outputs[0],combineRGB.inputs[0])
                        mat.node_tree.links.new(multG2.outputs[0],combineRGB.inputs[1])
                        mat.node_tree.links.new(multB2.outputs[0],combineRGB.inputs[2])

                                    

                        # Assign it to object
                        # if ob.data.materials:
                        #     ob.data.materials[0] = mat
                        # else:
                        #     ob.data.materials.append(mat)
                    else:
                        self.report({'ERROR'}, 'You must have a material assigned first!')
            for ob in selected_objects:
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = aob
        return {'FINISHED'}


class BR_OT_bake_vertex_color(bpy.types.Operator):
    """convert vertex color to texture"""
    bl_idname = "view3d.spiraloid_vertex_color_to_texture"
    bl_label = "Vertex Color to Texture"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):                
        return {'FINISHED'}

class BR_OT_bake_texture_to_vertex_color(bpy.types.Operator):
    """convert texture to vertex color"""
    bl_idname = "view3d.spiraloid_texture_to_vertex_color"
    bl_label = "Texture To Vertex Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):                

        return {'FINISHED'}


class BR_OT_regenerate_video(bpy.types.Operator):
    """remake video sequencer scene strip from all scenes"""
    bl_idname = "view3d.spiraloid_regenerate_scene_strip"
    bl_label = "Regenerate Scene Strip"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_scene = bpy.context.scene
        count = 0
        original_type = bpy.context.area.type

        for a in bpy.context.screen.areas:
            if a.type == 'SEQUENCE_EDITOR':
                if a.spaces[0].view_type == 'SEQUENCER':  
                    bpy.context.area.type ="SEQUENCE_EDITOR"
                    for scene in bpy.data.scenes :
                        if scene is not main_scene :
                            bpy.ops.sequencer.scene_strip_add(frame_start=count, channel=1, scene=bpy.data.scenes[count].name)
                            activeStrip = bpy.context.scene.sequence_editor.active_strip            
                            bpy.context.scene.sequence_editor.sequences_all[activeStrip.name].frame_final_duration = 1
                        count = count + 1
                    bpy.context.area.type = original_type
        return {'FINISHED'}


class BR_OT_nuke(bpy.types.Operator):
    """create a new material with gray color, ao and curvature material nodes."""
    bl_idname = "view3d.spiraloid_nuke"
    bl_label = "Nuke"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):                
        BR_OT_nuke_bsdf.execute(self, context)
        BR_OT_add_ao.execute(self, context)
        BR_OT_add_curvature.execute(self, context)
        BR_OT_add_cavity.execute(self, context)
        return {'FINISHED'}


#------------------------------------------------------
#------------------------------------------------------


# class DialogPanel(bpy.types.Panel):
#     bl_idname = "Choose bake options"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "TOOLS"
#     bl_context = "object"

#     def draw(self, context):

#         layout.operator(BR_OT_bake_collection.bl_idname)

def populate_coll(scene):
    bpy.app.handlers.scene_update_pre.remove(populate_coll)
    scene.coll.clear()
    for identifier, name, description in enum_items:
        scene.coll.add().name = name

def menu_draw_bake(self, context):
    self.layout.operator("view3d.spiraloid_bake_collection", 
        text="Bake Collection...")
    # layout.menu(SpiraloidOutlinerMenu.bl_idname)

    bpy.ops.object.dialog_operator('INVOKE_DEFAULT')


#------------------------------------------------------

class SpiraloidMenu(bpy.types.Menu):
    bl_idname = "INFO_HT_spiraloid_menu"
    bl_label = "Spiraloid"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.spiraloid_nuke")
        layout.menu(SpiraloidSubMenuMaterials.bl_idname )
        layout.menu(SpiraloidSubMenuUtilities.bl_idname )
        layout.separator()

        layout.menu(SpiraloidSubMenuHelp.bl_idname, icon="QUESTION")
        layout.separator()

        layout.operator("wm.spiraloid_empty_trash")





class SpiraloidSubMenuHelp(bpy.types.Menu):
    bl_idname = 'view3d.spiraloid_help_submenu'
    bl_label = 'Help'

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.spiraloid_workshop")



class SpiraloidSubMenuUtilities(bpy.types.Menu):
    bl_idname = 'view3d.spiraloid_utilities_submenu'
    bl_label = 'Utilities'

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.spiraloid_bake_collection")
        layout.operator("view3d.spiraloid_vertex_color_to_texture")
        layout.operator("view3d.spiraloid_texture_to_vertex_color")
        layout.separator()

        layout.operator("view3d.spiraloid_regenerate_scene_strip")

class SpiraloidSubMenuMaterials(bpy.types.Menu):
    bl_idname = 'view3d.spiraloid_materials_submenu'
    bl_label = 'Materials'

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.spiraloid_nuke_flat_texture")
        layout.operator("view3d.spiraloid_nuke_diffuse_texture")
        layout.operator("view3d.spiraloid_nuke_bsdf_texture")
        layout.separator()
        layout.operator("view3d.spiraloid_nuke_bsdf")
        layout.operator("view3d.spiraloid_nuke_flat")
        layout.separator() 
        layout.operator("view3d.spiraloid_nuke_bsdf_vertex_color")
        layout.operator("view3d.spiraloid_nuke_flat_vertex_color")
        layout.separator()
        layout.operator("view3d.spiraloid_add_ao")
        layout.operator("view3d.spiraloid_add_curvature")
        layout.operator("view3d.spiraloid_add_cavity")



def draw_item(self, context):
    layout = self.layout
    layout.menu(SpiraloidMenu.bl_idname)


def register():
    bpy.utils.register_class(BakeCollectionSettings)
    bpy.types.Scene.bake_collection_settings = bpy.props.PointerProperty(type=BakeCollectionSettings)

    bpy.utils.register_class(SpiraloidMenu)
    bpy.utils.register_class(SpiraloidSubMenuHelp)    
    bpy.utils.register_class(SpiraloidSubMenuUtilities)    
    bpy.utils.register_class(SpiraloidSubMenuMaterials)    
    # bpy.utils.register_class(SpiraloidOutlinerMenu)    

    bpy.utils.register_class(BR_OT_nuke)
    bpy.utils.register_class(BR_OT_nuke_bsdf)
    bpy.utils.register_class(BR_OT_nuke_bsdf_vertex_color)
    bpy.utils.register_class(BR_OT_nuke_bsdf_texture)
    bpy.utils.register_class(BR_OT_nuke_flat)
    bpy.utils.register_class(BR_OT_nuke_flat_vertex_color)
    bpy.utils.register_class(BR_OT_nuke_flat_texture)
    bpy.utils.register_class(BR_OT_nuke_diffuse_texture)
    
    bpy.utils.register_class(BR_OT_spiraloid_workshop)
    bpy.utils.register_class(BR_OT_bake_vertex_color)
    bpy.utils.register_class(BR_OT_add_ao)
    bpy.utils.register_class(BR_OT_add_curvature) 
    bpy.utils.register_class(BR_OT_add_cavity) 

    bpy.utils.register_class(BR_OT_bake_texture_to_vertex_color)
    bpy.utils.register_class(BR_OT_regenerate_video) 

    bpy.utils.register_class(BR_OT_empty_trash) 

    
    bpy.types.TOPBAR_MT_editor_menus.append(draw_item)
    # bpy.types.OUTLINER_MT_collection.append(draw_context_menus)

    bpy.utils.register_class(BR_OT_bake_collection)
    bpy.types.TOPBAR_MT_render.append(menu_draw_bake)
    
    bpy.utils.register_class(SpiraloidPreferences)

#    bpy.types.SEQUENCER_MT_add.prepend(add_object_button)

def unregister():

    # bpy.utils.unregister_class(BakeCollectionSettings)

    bpy.utils.unregister_class(SpiraloidMenu)
    bpy.utils.unregister_class(SpiraloidSubMenuComic)

    bpy.utils.unregister_class(SpiraloidSubMenuHelp)
    bpy.utils.unregister_class(SpiraloidSubMenuUtilities)
    bpy.utils.unregister_class(SpiraloidSubMenuMaterials)
    # bpy.utils.unregister_class(SpiraloidOutlinerMenu)
    
    bpy.utils.unregister_class(BR_OT_new_3d_comic)      
    bpy.utils.unregister_class(BR_OT_add_comic_scene)      
    bpy.utils.unregister_class(BR_OT_delete_comic_scene)      
    bpy.utils.unregister_class(BR_OT_import_panel_scenes)
    bpy.utils.unregister_class(BR_OT_archive_3d_comic)
    bpy.utils.unregister_class(BR_OT_nuke)
    bpy.utils.unregister_class(BR_OT_nuke_bsdf)
    bpy.utils.unregister_class(BR_OT_nuke_bsdf_vertex_color)
    bpy.utils.unregister_class(BR_OT_nuke_bsdf_texture)
    bpy.utils.unregister_class(BR_OT_nuke_flat)
    bpy.utils.unregister_class(BR_OT_nuke_flat_vertex_color)
    bpy.utils.unregister_class(BR_OT_nuke_flat_texture)
    bpy.utils.unregister_class(BR_OT_nuke_diffuse_texture)
    
    bpy.utils.unregister_class(BR_OT_add_wordballoon) 
    bpy.utils.unregister_class(BR_OT_build_3d_comic) 
    bpy.utils.unregister_class(BR_OT_spiraloid_workshop) 
    bpy.utils.unregister_class(BR_OT_bake_collection) 
    bpy.utils.unregister_class(BR_OT_bake_vertex_color) 
    bpy.utils.unregister_class(BR_OT_add_ao) 
    bpy.utils.unregister_class(BR_OT_add_curvature) 
    bpy.utils.unregister_class(BR_OT_add_cavity) 
    bpy.utils.unregister_class(BR_OT_bake_texture_to_vertex_color) 
    bpy.utils.unregister_class(BR_OT_regenerate_video) 

    bpy.utils.unregister_class(BR_OT_empty_trash) 
    
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_item)
    # bpy.types.OUTLINER_MT_collection.remove(draw_context_menus)
    bpy.types.TOPBAR_MT_render.remove(menu_draw_bake)

    bpy.utils.unregister_class(SpiraloidPreferences)



    if __name__ != "__main__":
        bpy.types.TOPBAR_MT_render.remove(menu_draw_bake)
#    bpy.types.SEQUENCER_MT_add.remove(add_object_button)

if __name__ == "__main__":
    register()

    # The menu can also be called from scripts
#bpy.ops.wm.call_menu(name=SpiraloidMenu.bl_idname)

#debug console
#__import__('code').interact(local=dict(globals(), **locals()))
# pauses wherever this line is:
# code.interact