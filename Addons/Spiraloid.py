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
from bpy.types import Menu
from bl_ui.properties_paint_common import UnifiedPaintPanel

# ------------------------
# global variables

previous_selected_faces = []
wasInEditMode = False
my_shading = 'MATERIAL' 
applyColor = (0.5,0.5,0.5,1.0)
previous_color = (0,0,0,1)
# colorIndex = 0
# isWorkmodeToggled = True
previous_mode =  'OBJECT'

# ------------------------




# class SpiraloidPreferences(AddonPreferences):
#     # this must match the addon name, use '__package__'
#     # when defining this in a submodule of a python package.
#     bl_idname = __name__

#     assets_folder = StringProperty(
#             name="Assets Folder",
#             subtype='DIR_PATH',
#             )

#     def draw(self, context):
#         layout = self.layout
#         layout.label(text="Location for Spiraloid Template Assets")
#         layout.prop(self, "assets_folder")

def in_1_seconds():
    global previous_color
    previous_color = (1,1,1,1)
    print ("Resetting Previous color")

def smart_nuke_vertex_color(self, context):
    if bpy.context.mode == 'EDIT_MESH':
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                assetName = ob.name
                mat =  ob.active_material
                mesh = bpy.context.object.data
                matName = (assetName + "Mat")
                me = ob.data

                bm = bmesh.new()
                bm.from_mesh(mesh)        


                # Assign it to object
                if ob.data.materials:
                    ob.data.materials[0] = mat
                else:
                    ob.data.materials.append(mat)

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)


                #create new vertex color group if none exist
                if not ob.data.vertex_colors:
                    bpy.ops.mesh.vertex_color_add()
                vertexColorName = ob.data.vertex_colors[0].name


                selected_faces = []
                for f in bm.faces:
                    if f.select:
                        selected_faces.append(f)
                if len(selected_faces) == 0: 
                    bpy.ops.mesh.select_all(action='SELECT')

                if previous_color == (0.0,0.0,0.0,1.0):
                    applyColor = (1.0,1.0,1.0,1.0)
                if previous_color == (1.0,1.0,1.0,1.0):
                    applyColor = (0.0,0.0,0.0,1.0)
                previous_color = applyColor
                bpy.app.timers.register(in_1_seconds, first_interval=1)
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                for f in ob.data.polygons:
                    if f.select:
                        for vert_idx, loop_idx in zip(f.vertices, f.loop_indices):
                            if nukeInvert:
                                col = ob.data.vertex_colors[vertexColorName].data[loop_idx].color
                                ob.data.vertex_colors[vertexColorName].data[loop_idx].color = tuple(1-x for x in col)
                            else:
                                ob.data.vertex_colors[vertexColorName].data[loop_idx].color = applyColor

                previous_selected_faces = selected_faces
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)

                mat_output = mat.node_tree.nodes.get('Material Output')
                shader = mat_output.inputs[0].links[0].from_node

                for node in mat.node_tree.nodes:
                    if "BSDF" in node.name: 
                        shader = node

                if shader:
                    base_color_node =  mat.node_tree.nodes.get("Attribute")
                    if base_color_node is not None:
                        mat.node_tree.nodes.remove( base_color_node )
                    colorNode = mat.node_tree.nodes.new('ShaderNodeAttribute')
                    colorNode.attribute_name = vertexColorName
                    mat.node_tree.links.new(shader.inputs[0], colorNode.outputs[0])
    return {'FINISHED'}

def smart_nuke_bsdf(self, context, nukeInvert):
    global previous_selected_faces
    global previous_color
    colorIndex = 0
    global applyColor
    global wasInEditMode
    my_areas = bpy.context.workspace.screens[0].areas
    shared_material = True
    colorSwatch = [(0.0,0.0,0.0,1.0), (1.0,1.0,1.0,1.0), (0.5,0.5,0.5,1.0) ]
    selected_objects = bpy.context.selected_objects

    # bpy.context.screen.areas.spaces[0].view_type == areas: EMPTY’, ‘VIEW_3D’, ‘IMAGE_EDITOR’, ‘NODE_EDITOR’, ‘SEQUENCE_EDITOR’, ‘CLIP_EDITOR’, ‘DOPESHEET_EDITOR’, ‘GRAPH_EDITOR’, ‘NLA_EDITOR’, ‘TEXT_EDITOR’, ‘CONSOLE’, ‘INFO’, ‘TOPBAR’, ‘STATUSBAR’, ‘OUTLINER’, ‘PROPERTIES’, ‘FILE_BROWSER’, ‘PREFERENCES’]
    # modes 'OBJECT', 'EDIT', 'POSE', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT', 'PARTICLE_EDIT', 'EDIT_GPENCIL', 'SCULPT_GPENCIL', 'PAINT_GPENCIL', 'WEIGHT_GPENCIL']



    if bpy.context.mode == 'EDIT_MESH':
        maxColorIndex = len(colorSwatch) - 1

        for ob in selected_objects:
            if ob.type == 'MESH':
                assetName = ob.name
                mat =  ob.active_material
                mesh = context.object.data
                matName = (assetName + "Mat")
                me = ob.data

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)

                bm = bmesh.new()
                bm.from_mesh(mesh)        
                
                bpy.ops.object.material_slot_add()
                assetName = ob.name
                matName = (assetName + "Mat")
                mat = bpy.data.materials.new(name=matName)
                new_material_slot_index =  len(ob.data.materials) -1
                ob.data.materials[new_material_slot_index] = mat


                mat.use_nodes = True
                mat_output = mat.node_tree.nodes.get('Material Output')
                shader = mat_output.inputs[0].links[0].from_node
                nodes = mat.node_tree.nodes
                for node in nodes:
                    if node.type != 'OUTPUT_MATERIAL': # skip the material output node as we'll need it later
                        nodes.remove(node) 
                shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
                shader.name = "Principled BSDF"
                shader.label = "Principled BSDF"
                shader.inputs[0].default_value = (0.214041, 0.214041, 0.214041, 1) # base color
                shader.inputs[5].default_value = 1 # specular
                shader.inputs[4].default_value = 0.33 # metallic
                shader.inputs[7].default_value = 0.66 # roughness
                shader.inputs[12].default_value = 0.5  # clearcoat
                shader.inputs[13].default_value = 0.5 # clearcoat roughness

                mat_output = mat.node_tree.nodes.get('Material Output')
                mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

                bpy.ops.object.material_slot_assign()



        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            bpy.context.scene.eevee.use_gtao = True
            bpy.context.scene.eevee.use_bloom = True
            bpy.context.scene.eevee.use_ssr = True
            my_shading =  'MATERIAL'
            
        if bpy.context.scene.render.engine == 'CYCLES':
            my_shading =  'RENDERED'


        for ob in selected_objects:
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob

    if (bpy.context.mode == 'OBJECT'):
            # bpy.ops.wm.call_menu(name=SPIRALOID_MT_PalletColorMenu.bl_idname)

            # bpy.data.palettes["Global_Palette"].name = "Global_Palette"
            selected_objects = bpy.context.selected_objects
            for ob in selected_objects:
                if ob.type == 'MESH' or ob.type == 'CURVE':
                    # if not wasInEditMode:

                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    bpy.ops.object.shade_smooth()

                    #clear out and remake a new material
                    for i in range(len(ob.material_slots)):
                        bpy.ops.object.material_slot_remove({'object': ob})
                        for block in bpy.data.materials:
                            if block.users == 0:
                                bpy.data.materials.remove(block)

                        # # if ob.active_material is not None:
                        # if not len(context.selected_objects) and context.object.type != 'MESH' and context.mode != 'EDIT_MESH':
                        #     for i in range(len(ob.material_slots)):
                        #         bpy.ops.object.material_slot_remove({'object': ob})


                # else:
                    # bpy.ops.object.shade_smooth()
                    # if shared_material :
                    #     ob =  selected_objects[0]
                    assetName = ob.name
                    matName = (assetName + "Mat")
                    mat = bpy.data.materials.new(name=matName)
                    mat.use_nodes = True
                    mat_output = mat.node_tree.nodes.get('Material Output')
                    shader = mat_output.inputs[0].links[0].from_node

                    nodes = mat.node_tree.nodes
                    for node in nodes:
                        if node.type != 'OUTPUT_MATERIAL': # skip the material output node as we'll need it later
                            nodes.remove(node) 

                    shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
                    shader.name = "Principled BSDF"
                    shader.label = "Principled BSDF"
                    shader.inputs[0].default_value = (0.214041, 0.214041, 0.214041, 1) # base color
                    shader.inputs[5].default_value = 1 # specular
                    shader.inputs[4].default_value = 0.33 # metallic
                    shader.inputs[7].default_value = 0.66 # roughness
                    shader.inputs[12].default_value = 0.5  # clearcoat
                    shader.inputs[13].default_value = 0.5 # clearcoat roughness
                    mat_output = mat.node_tree.nodes.get('Material Output')
                    mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])
                    mat.use_backface_culling = True

                    # Assign it to object
                    if ob.data.materials:
                        ob.data.materials[0] = mat
                    else:
                        ob.data.materials.append(mat)

            if not wasInEditMode:
                for ob in selected_objects:
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob


            # if keepcolor:
            #     for ob in selected_objects:
            #         if ob.type == 'MESH':
            #             assetName = ob.name
            #             mat =  ob.active_material
            #             mesh = context.object.data
            #             matName = (assetName + "Mat")
            #             me = ob.data
            #             bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            #             bm = bmesh.new()
            #             bm.from_mesh(mesh)        
                        

            #             # if ob.active_material is not None:
            #             #     mat =  ob.active_material
            #             #     print ("Using existing material" + mat.name)
            #             # else:
            #             #     mat = bpy.data.materials.new(name=matName)
            #             #     mat.use_nodes = True
            #                 # bpy.ops.object.shade_smooth()

            #             #create new vertex color group if none exist
            #             if not ob.data.vertex_colors:
            #                 bpy.ops.mesh.vertex_color_add()
            #             vertexColorName = ob.data.vertex_colors[0].name



            #             # for f in bm.faces:
            #             #     if f.select:
            #             #         print(f.index)
            #             #         selected_faces.append(f)

            #             # bpy.ops.paint.vertex_color_set()
            #             # bpy.ops.paint.vertex_color_set.poll()

            #             # bpy.context.scene.tool_settings.unified_paint_settings.color = appliedColor

            #             # apply color to faces
            #             # i = 0
            #             # for poly in selected_faces:
            #             #     for idx in poly.loop_indices:
            #             #         # rgb = [random.random() for i in range(3)]
            #             #         me.vertex_colors[vertexColorName].data[i].color = applyColor
            #             #         i += 1


            #             selected_faces = []
            #             for f in bm.faces:
            #                 if f.select:
            #                     selected_faces.append(f)


            #             if selected_faces == previous_selected_faces :
            #                 if colorIndex <= maxColorIndex + 1: 
            #                     colorIndex += 1
            #                 else:
            #                     colorIndex = 0
            #             else:
            #                 colorIndex = 0

            #             previous_selected_faces = selected_faces

            #             applyColor = colorSwatch[colorIndex]


            #             bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            #             for f in ob.data.polygons:
            #                 if f.select:
            #                     for vert_idx, loop_idx in zip(f.vertices, f.loop_indices):
            #                         ob.data.vertex_colors[vertexColorName].data[loop_idx].color = applyColor


            #             bpy.ops.object.mode_set(mode='EDIT', toggle=False)


            #             if shader:
            #                 colorNode = mat.node_tree.nodes.new('ShaderNodeAttribute')
            #                 colorNode.attribute_name = vertexColorName            
            #                 mat.node_tree.links.new(shader.inputs[0], colorNode.outputs[0])


            # toggle_workmode(self, context)

                # count = count + 1
            # bpy.context.area.type = original_type


    if bpy.context.mode == 'PAINT_VERTEX':
        for ob in selected_objects:
            print ("----------------------------------------------")
            if ob.type == 'MESH':
                assetName = ob.name
                mat =  ob.active_material
                mesh = context.object.data
                matName = (assetName + "Mat")
                me = ob.data

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)

                bm = bmesh.new()
                bm.from_mesh(mesh)        
                

                if ob.active_material is not None:
                    mat =  ob.active_material
                    print ("Using existing material" + mat.name)
                else:
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    for i in range(len(ob.material_slots)):
                        bpy.ops.object.material_slot_remove({'object': ob})
                        for block in bpy.data.materials:
                            if block.users == 0:
                                bpy.data.materials.remove(block)
                    assetName = ob.name
                    matName = (assetName + "Mat")
                    mat = bpy.data.materials.new(name=matName)
                    mat.use_nodes = True
                    mat_output = mat.node_tree.nodes.get('Material Output')
                    shader = mat_output.inputs[0].links[0].from_node
                    nodes = mat.node_tree.nodes
                    for node in nodes:
                        if node.type != 'OUTPUT_MATERIAL': # skip the material output node as we'll need it later
                            nodes.remove(node) 
                    shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
                    shader.name = "Principled BSDF"
                    shader.label = "Principled BSDF"
                    shader.inputs[0].default_value = (0.214041, 0.214041, 0.214041, 1) # base color
                    shader.inputs[5].default_value = 1 # specular
                    shader.inputs[4].default_value = 0.33 # metallic
                    shader.inputs[7].default_value = 0.66 # roughness
                    shader.inputs[12].default_value = 1  # clearcoat
                    shader.inputs[13].default_value = 0.33 # clearcoat roughness
                    mat_output = mat.node_tree.nodes.get('Material Output')
                    mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])




                    # Assign it to object
                    if ob.data.materials:
                        ob.data.materials[0] = mat
                    else:
                        ob.data.materials.append(mat)

                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)


                #create new vertex color group if none exist
                if not ob.data.vertex_colors:
                    bpy.ops.mesh.vertex_color_add()
                vertexColorName = ob.data.vertex_colors[0].name


                selected_faces = []
                # for f in bm.faces:
                #     if f.select:
                #         selected_faces.append(f)

                # bpy.ops.paint.vertex_color_set()
                # bpy.ops.paint.vertex_color_set.poll()

                # bpy.context.scene.tool_settings.unified_paint_settings.color = appliedColor

                # apply color to faces
                # i = 0
                # for poly in selected_faces:
                #     for idx in poly.loop_indices:
                #         # rgb = [random.random() for i in range(3)]
                #         me.vertex_colors[vertexColorName].data[i].color = applyColor
                #         i += 1


                for f in bm.faces:
                    if f.select:
                        selected_faces.append(f)

                # print("selected_faces is " + str(len(selected_faces)))
                # if len(selected_faces) == len(previous_selected_faces) :
                # isSameSelection = bool(set(selected_faces).intersection(previous_selected_faces))
                # if isSameSelection :
                    # print ("same selection detected!")
                # if colorIndex < maxColorIndex : 
                #     colorIndex += 1
                # else:
                #     colorIndex = 0
                # else:
                #     colorIndex = 0



                if len(selected_faces) == 0: 
                    bpy.ops.mesh.select_all(action='SELECT')

                # applyColor = colorSwatch[colorIndex]

                if previous_color == (0.0,0.0,0.0,1.0):
                    applyColor = (1.0,1.0,1.0,1.0)
                if previous_color == (1.0,1.0,1.0,1.0):
                    applyColor = (0.0,0.0,0.0,1.0)
                previous_color = applyColor
                bpy.app.timers.register(in_1_seconds, first_interval=1)

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                for f in ob.data.polygons:
                    if f.select:
                        for vert_idx, loop_idx in zip(f.vertices, f.loop_indices):
                            if nukeInvert:
                                col = ob.data.vertex_colors[vertexColorName].data[loop_idx].color
                                ob.data.vertex_colors[vertexColorName].data[loop_idx].color = tuple(1-x for x in col)
                            else:
                                ob.data.vertex_colors[vertexColorName].data[loop_idx].color = applyColor


                previous_selected_faces = selected_faces

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)

                mat_output = mat.node_tree.nodes.get('Material Output')
                shader = mat_output.inputs[0].links[0].from_node
                if shader:
                    base_color_node =  mat.node_tree.nodes.get("Attribute")
                    if base_color_node is not None:
                        mat.node_tree.nodes.remove( base_color_node )
                    colorNode = mat.node_tree.nodes.new('ShaderNodeAttribute')
                    colorNode.attribute_name = vertexColorName
                    mat.node_tree.links.new(shader.inputs[0], colorNode.outputs[0])
                    

        bpy.ops.object.mode_set(mode='VERTEX_PAINT', toggle=False)
        
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            bpy.context.scene.eevee.use_gtao = True
            bpy.context.scene.eevee.use_bloom = True
            bpy.context.scene.eevee.use_ssr = True
            my_shading =  'MATERIAL'
            
        if bpy.context.scene.render.engine == 'CYCLES':
            my_shading =  'RENDERED'


        for ob in selected_objects:
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob

    
    if bpy.context.mode == 'PAINT_TEXTURE':
        wasInEditMode = True
        nuke_diffuse_texture(selected_objects, 2048, 2048)
        # my_shading =  'MATERIAL'
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT', toggle=False)





        for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.color_type = 'TEXTURE'
                    space.shading.type = 'SOLID'




    # if shared_material:
    #     bpy.ops.object.material_slot_copy()


def nuke_smoke(self, context):
    selected_objects = bpy.context.selected_objects
    if selected_objects:
        if (bpy.context.mode != 'OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            for ob in selected_objects:
                if ob.type == 'VOLUME':
                    #clear out and remake a new material
                    for i in range(len(ob.material_slots)):
                        bpy.ops.object.material_slot_remove({'object': ob})
                        for block in bpy.data.materials:
                            if block.users == 0:
                                bpy.data.materials.remove(block)

                    assetName = ob.name
                    matName = (assetName + "Mat")
                    mat = bpy.data.materials.new(name=matName)
                    mat.use_nodes = True
                    mat_output = mat.node_tree.nodes.get('Material Output')
                    nodes = mat.node_tree.nodes
                    for node in nodes:
                        if node.type != 'OUTPUT_MATERIAL': # skip the material output node as we'll need it later
                            nodes.remove(node) 

                    scatter = mat.node_tree.nodes.new(type='ShaderNodeVolumeScatter')
                    mix = mat.node_tree.nodes.new(type='ShaderNodeMixShader')
                    volume_info = mat.node_tree.nodes.new(type='ShaderNodeVolumeInfo')
                    math_power_1 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                    math_power_2 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                    math_mult_2 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                    math_mult_3 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                    math_mult_4 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                    ramp = mat.node_tree.nodes.new(type='ColorRamp')
                    shader = mat.node_tree.nodes.new(type='ShaderNodeVolumePrincipled')

                    texture_coord = mat.node_tree.nodes.new(type='ShaderNodeTexCoord')
                    mapping = mat.node_tree.nodes.new(type='ShaderNodeMapping')
                    noise_tex = mat.node_tree.nodes.new(type='ShaderNodeTexNoise')
                    math_add_1 = mat.node_tree.nodes.new(type='ShaderNodeMath')
                    gradient_tex = mat.node_tree.nodes.new(type='ShaderNodeTexGradient')
                    math_mult_1 = mat.node_tree.nodes.new(type='ShaderNodeMath')


                    shader.name = "Principled BSDF"
                    shader.label = "Principled BSDF"
                    shader.inputs[0].default_value = (0.214041, 0.214041, 0.214041, 1) # base color
                    shader.inputs[5].default_value = 1 # specular
                    shader.inputs[4].default_value = 0.33 # metallic
                    shader.inputs[7].default_value = 0.66 # roughness
                    shader.inputs[12].default_value = 0.5  # clearcoat
                    shader.inputs[13].default_value = 0.5 # clearcoat roughness
                    mat_output = mat.node_tree.nodes.get('Material Output')
                    mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])
                    mat.use_backface_culling = True

                    # Assign it to object
                    if ob.data.materials:
                        ob.data.materials[0] = mat
                    else:
                        ob.data.materials.append(mat)



def toggle_mods():
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        if obj:
            #obj["is_modwires_on"] = not obj["is_modwires_on"]
            for mod in obj.modifiers:
                    mod.show_viewport = not mod.show_viewport
    
    if not bpy.context.selected_objects:
        for vobj in bpy.context.view_layer.objects:
            for mod in vobj.modifiers:
                mod.show_viewport = not mod.show_viewport

    # for vobj in bpy.context.view_layer.objects:
    #     for mod in vobj.modifiers:
    #         mod.show_viewport = not mod.show_viewport
                

# def toggle_workmode(self, context):
#     global isWorkmodeToggled
#     global currentSubdLevel
#     global previous_mode
#     global previous_selection
#     global isWireframe
#     my_areas = bpy.context.workspace.screens[0].areas
#     my_shading = 'WIREFRAME'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
#     bpy.context.space_data.overlay.show_overlays = True
#     bpy.context.space_data.overlay.show_floor = True
#     bpy.context.space_data.overlay.show_axis_x = True
#     bpy.context.space_data.overlay.show_axis_y = True
#     bpy.context.space_data.overlay.show_outline_selected = True
#     bpy.context.space_data.overlay.show_cursor = True
#     bpy.context.space_data.overlay.show_extras = True
#     bpy.context.space_data.overlay.show_relationship_lines = True
#     bpy.context.space_data.overlay.show_bones = True
#     bpy.context.space_data.overlay.show_motion_paths = True
#     bpy.context.space_data.overlay.show_object_origins = True
#     bpy.context.space_data.overlay.show_annotation = True
#     bpy.context.space_data.overlay.show_text = True
#     bpy.context.space_data.overlay.show_stats = True


#     for obj in bpy.context.scene.objects:
#         # if obj.visible_get and obj.type == 'MESH':
#         if obj.visible_get :
            
#             # for mod in [m for m in obj.modifiers if m.type == 'MULTIRES']:
#             #     mod_max_level = mod.render_levels
#             #     if isWorkmodeToggled:
#             #         currentSubdLevel = mod.levels
#             #         mod.levels = mod_max_level
#             #         mod.sculpt_levels = mod_max_level
#             #     if not isWorkmodeToggled:
#             #         mod.levels = currentSubdLevel
#             #         mod.sculpt_levels = currentSubdLevel
#             #         if currentSubdLevel != 0:
#             #             bpy.context.space_data.overlay.show_wireframes = False


#             # for mod in [m for m in obj.modifiers if m.type == 'SUBSURF']:
#             #     mod_max_level = mod.render_levels
#             #     if isWorkmodeToggled:
#             #         currentSubdLevel = mod.levels
#             #         mod.levels = mod_max_level
#             #     if not isWorkmodeToggled:
#             #         mod.levels = currentSubdLevel
#             #         if currentSubdLevel != 0:
#             #             bpy.context.space_data.overlay.show_wireframes = False
#             is_toon_shaded = obj.get("is_toon_shaded")
#             if is_toon_shaded:
#                 for mod in obj.modifiers:
#                     if 'InkThickness' in mod.name:
#                         obj.modifiers["InkThickness"].show_viewport = True
#                     if 'WhiteOutline' in mod.name:
#                         obj.modifiers["WhiteOutline"].show_viewport = True
#                     if 'BlackOutline' in mod.name:
#                         obj.modifiers["BlackOutline"].show_viewport = True

#             if isWorkmodeToggled:
#                 previous_selection = bpy.context.selected_objects

#                 bpy.context.space_data.overlay.show_overlays = True
#                 bpy.context.space_data.overlay.show_floor = False
#                 bpy.context.space_data.overlay.show_axis_x = False
#                 bpy.context.space_data.overlay.show_axis_y = False
#                 bpy.context.space_data.overlay.show_cursor = False
#                 bpy.context.space_data.overlay.show_relationship_lines = False
#                 bpy.context.space_data.overlay.show_bones = False
#                 bpy.context.space_data.overlay.show_motion_paths = False
#                 bpy.context.space_data.overlay.show_object_origins = False
#                 bpy.context.space_data.overlay.show_annotation = False
#                 bpy.context.space_data.overlay.show_text = False
#                 bpy.context.space_data.overlay.show_text = False
#                 bpy.context.space_data.overlay.show_outline_selected = False
#                 bpy.context.space_data.overlay.show_extras = False
#                 bpy.context.space_data.show_gizmo = False
#                 bpy.context.space_data.overlay.show_stats = False


#                 selected_objects = bpy.context.selected_objects
#                 if not selected_objects:
#                     bpy.context.space_data.overlay.show_outline_selected = True


#                 bpy.context.space_data.overlay.wireframe_threshold = 1
#                 if bpy.context.space_data.overlay.show_wireframes:
#                     isWireframe = True
#                     bpy.context.space_data.overlay.show_outline_selected = True
#                     bpy.context.space_data.overlay.show_extras = True
#                     # bpy.context.space_data.overlay.show_cursor = True
#                 else:
#                     isWireframe = False
#                     # bpy.context.space_data.overlay.show_outline_selected = False
#                     # bpy.context.space_data.overlay.show_extras = False

#                 # bpy.context.space_data.overlay.show_wireframes = False

#                 if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
#                     # bpy.context.scene.eevee.use_bloom = True
#                     # bpy.context.scene.eevee.use_ssr = True
#                     my_shading =  'MATERIAL'

#                     lights = [o for o in bpy.context.scene.objects if o.type == 'LIGHT']
#                     if (lights):
#                         bpy.context.space_data.shading.use_scene_lights = True
#                         bpy.context.space_data.shading.use_scene_world = True
#                     else:
#                         bpy.context.space_data.shading.use_scene_lights = False
#                         bpy.context.space_data.shading.use_scene_world = False

#                     if bpy.context.scene.world:
#                         bpy.context.space_data.shading.use_scene_world = True
#                     else:
#                         bpy.context.space_data.shading.use_scene_world = False





#                 if bpy.context.scene.render.engine == 'CYCLES':
#                     my_shading =  'RENDERED'


#                     lights = [o for o in bpy.context.scene.objects if o.type == 'LIGHT']
#                     # if (lights):
#                     #     bpy.context.space_data.shading.use_scene_lights_render = True
#                     # else:
#                     #     bpy.context.space_data.shading.use_scene_lights = False
#                     #     bpy.context.space_data.shading.studiolight_intensity = 1


#                     if bpy.context.scene.world is None:
#                         if (lights):
#                             bpy.context.space_data.shading.use_scene_world_render = False
#                             bpy.context.space_data.shading.studiolight_intensity = 0.01
#                         else:
#                             bpy.context.space_data.shading.use_scene_world_render = False
#                             bpy.context.space_data.shading.studiolight_intensity = 1
#                     else:
#                         bpy.context.space_data.shading.use_scene_world_render = True
#                         if (lights):
#                             bpy.context.space_data.shading.use_scene_lights_render = True



#                 if bpy.context.mode == 'OBJECT':
#                     previous_mode =  'OBJECT'
#                 if bpy.context.mode == 'EDIT_MESH':
#                     previous_mode =  'EDIT'
#                     bpy.context.space_data.overlay.show_overlays = False
#                 if bpy.context.mode == 'POSE':
#                     previous_mode =  'POSE'
#                     bpy.context.space_data.overlay.show_bones = True
#                 if bpy.context.mode == 'SCULPT':
#                     previous_mode =  'SCULPT'
#                 if bpy.context.mode == 'PAINT_VERTEX':
#                     previous_mode =  'VERTEX_PAINT'
#                 if bpy.context.mode == 'WEIGHT_PAINT':
#                     previous_mode =  'WEIGHT_PAINT'
#                 if bpy.context.mode == 'TEXTURE_PAINT':
#                     previous_mode =  'TEXTURE_PAINT'


#                 # bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


                
#             if not isWorkmodeToggled:    
#                 bpy.context.space_data.overlay.show_overlays = True
#                 bpy.context.space_data.overlay.show_cursor = True
#                 bpy.context.space_data.overlay.show_floor = True
#                 bpy.context.space_data.overlay.show_axis_x = True
#                 bpy.context.space_data.overlay.show_axis_y = True
#                 bpy.context.space_data.overlay.show_extras = True
#                 bpy.context.space_data.overlay.show_relationship_lines = True
#                 bpy.context.space_data.overlay.show_bones = True
#                 bpy.context.space_data.overlay.show_motion_paths = True
#                 bpy.context.space_data.overlay.show_object_origins = True
#                 bpy.context.space_data.overlay.show_annotation = True
#                 bpy.context.space_data.overlay.show_text = True
#                 bpy.context.space_data.overlay.show_stats = True
#                 bpy.context.space_data.overlay.wireframe_threshold = 1
#                 bpy.context.space_data.show_gizmo = True


#                 if isWireframe:
#                     bpy.context.space_data.overlay.show_wireframes = True
#                 else:
#                     bpy.context.space_data.overlay.show_wireframes = False
#                 bpy.context.space_data.shading.color_type = 'RANDOM'

#                 if previous_mode == 'EDIT' or previous_mode == 'OBJECT' or previous_mode == 'POSE':
#                     my_shading = 'SOLID'
#                     # for ob in bpy.context.scene.objects:
#                     #     if ob.type == 'MESH':
#                     #         if ob.data.vertex_colors:
#                     #             bpy.context.space_data.shading.color_type = 'VERTEX'
#                     #         else:
#                     #             bpy.context.space_data.shading.color_type = 'RANDOM'

#                 is_toon_shaded = obj.get("is_toon_shaded")
#                 if is_toon_shaded:
#                     for mod in obj.modifiers:
#                         if 'InkThickness' in mod.name:
#                             obj.modifiers["InkThickness"].show_viewport = False
#                         if 'WhiteOutline' in mod.name:
#                             obj.modifiers["WhiteOutline"].show_viewport = False
#                         if 'BlackOutline' in mod.name:
#                             obj.modifiers["BlackOutline"].show_viewport = False
                        

#                 if previous_mode == 'EDIT':
#                     if not len(bpy.context.selected_objects):
#                         bpy.ops.object.editmode_toggle()
#                     # else:
#                     #     for ob in previous_selection :
#                     #         # if ob.type == 'MESH' : 
#                     #         ob.select_set(state=True)
#                     #         bpy.context.view_layer.objects.active = ob
#                     #     bpy.ops.object.editmode_toggle()



#                 if previous_mode == 'VERTEX_PAINT':
#                     my_shading = 'SOLID'
#                     bpy.context.space_data.shading.light = 'FLAT'


#                 if previous_mode == 'SCULPT':
#                     my_shading =  'SOLID'
#                     bpy.context.space_data.shading.color_type = 'MATERIAL'
#                     bpy.context.space_data.overlay.show_floor = False
#                     bpy.context.space_data.overlay.show_axis_x = False
#                     bpy.context.space_data.overlay.show_axis_y = False
#                     bpy.context.space_data.overlay.show_cursor = False
#                     bpy.context.space_data.overlay.show_relationship_lines = False
#                     bpy.context.space_data.overlay.show_bones = False
#                     bpy.context.space_data.overlay.show_motion_paths = False
#                     bpy.context.space_data.overlay.show_object_origins = False
#                     bpy.context.space_data.overlay.show_annotation = False
#                     bpy.context.space_data.overlay.show_text = False
#                     bpy.context.space_data.overlay.show_text = False
#                     bpy.context.space_data.overlay.show_outline_selected = False
#                     bpy.context.space_data.overlay.show_extras = False
#                     bpy.context.space_data.overlay.show_overlays = True
#                     bpy.context.space_data.show_gizmo = False
        

#                 # bpy.ops.object.mode_set(mode=previous_mode, toggle=False)


#             scene = bpy.context.scene
#             # for area in my_areas:
#             #     for space in area.spaces:
#             #         if space.type == 'VIEW_3D':
#             #             space.shading.type = my_shading

#             # set viewport display
#             for area in  bpy.context.screen.areas:  # iterate through areas in current screen
#                 if area.type == 'VIEW_3D':
#                     for space in area.spaces:  # iterate through spaces in current VIEW_3D area
#                         if space.type == 'VIEW_3D':  # check if space is a 3D view
#                             # space.shading.type = 'MATERIAL'  # set the viewport shading to material
#                             space.shading.type = my_shading
#                             if scene.world is not None:
#                                 space.shading.use_scene_world = True
#                                 space.shading.use_scene_lights = True


                            

#             for image in bpy.data.images:
#                 image.reload()

#     isWorkmodeToggled = not isWorkmodeToggled
#     return {'FINISHED'}

# class SPIRALOID_MT__toggle_workmode(bpy.types.Operator):
#     """Toggle Workmode"""
#     bl_idname = "wm.spiraloid_toggle_workmode"
#     bl_label = "Toggle Workmode"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(cls, context):
#         return True #context.space_data.type == 'VIEW_3D'

#     def execute(self, context):
#         toggle_workmode(self, context)
#         return {'FINISHED'}



class SPIRALOID_MT_PalletColorMenu(bpy.types.Menu):
    bl_idname = 'SPIRALOID_MT_PalletColorMenu'
    bl_label = 'Pick Flood Color'

    def draw(self, context):
        for i in range(5):
            row = self.layout.row()
            row.prop(context.scene.colors[i], "color", text=str(i))

# def nuke_bsdf_vertex_color(self, context):
#     global previous_selected_faces
#     global colorIndex
#     global applyColor
#     colorSwatch = [(0.5,0.5,0.5,1.0), (0.25,0.25,0.25,1.0), (0.0,0.0,0.0,1.0), (1.0,1.0,1.0,1.0), (0.75,0.75,0.75,1.0) ]
#     maxColorIndex = len(colorSwatch)

#     # bpy.ops.wm.call_menu(name=SPIRALOID_MT_PalletColorMenu.bl_idname)

#     nuke_bsdf(self, context)

#     # context = bpy.context
#     selected_objects = bpy.context.selected_objects
#     for ob in selected_objects:
#         if ob.type == 'MESH':
#             assetName = ob.name
#             mat =  ob.active_material
#             mesh = context.object.data
#             matName = (assetName + "Mat")
#             me = ob.data

#             bm = bmesh.new()
#             bm.from_mesh(mesh)        
            

#             # if ob.active_material is not None:
#             #     mat =  ob.active_material
#             #     print ("Using existing material" + mat.name)
#             # else:
#             #     mat = bpy.data.materials.new(name=matName)
#             #     mat.use_nodes = True
#                 # bpy.ops.object.shade_smooth()

#             #create new vertex color group if none exist
#             if not ob.data.vertex_colors:
#                 bpy.ops.mesh.vertex_color_add()
#             vertexColorName = ob.data.vertex_colors[0].name



#             # for f in bm.faces:
#             #     if f.select:
#             #         print(f.index)
#             #         selected_faces.append(f)

#             # bpy.ops.paint.vertex_color_set()
#             # bpy.ops.paint.vertex_color_set.poll()

#             # bpy.context.scene.tool_settings.unified_paint_settings.color = appliedColor

#             # apply color to faces
#             # i = 0
#             # for poly in selected_faces:
#             #     for idx in poly.loop_indices:
#             #         # rgb = [random.random() for i in range(3)]
#             #         me.vertex_colors[vertexColorName].data[i].color = applyColor
#             #         i += 1

#             if len(context.selected_objects) and context.object.type == 'MESH' and context.mode == 'EDIT_MESH':
#                 selected_faces = []
#                 for f in ob.data.polygons:
#                     if f.select:
#                         selected_faces.append(f)

#                 if selected_faces == previous_selected_faces :
#                     if colorIndex <= maxColorIndex + 1: 
#                         colorIndex = colorIndex + 1
#                     else:
#                         colorIndex = 0
#                     applyColor = colorSwatch[colorIndex]
#                 else:
#                     applyColor = colorSwatch[0]

#                 bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
#                 for f in ob.data.polygons:
#                     if f.select:
#                         for vert_idx, loop_idx in zip(f.vertices, f.loop_indices):
#                             ob.data.vertex_colors[vertexColorName].data[loop_idx].color = applyColor
#                 bpy.ops.object.mode_set(mode='EDIT', toggle=False)

#                 previous_selected_faces = selected_faces

#             bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

#             mat_output = mat.node_tree.nodes.get('Material Output')
#             shaderNode = mat_output.inputs[0].links[0].from_node
#             if shaderNode:
#                 colorNode = mat.node_tree.nodes.new('ShaderNodeAttribute')
#                 colorNode.attribute_name = vertexColorName            
#                 mat.node_tree.links.new(shaderNode.inputs[0], colorNode.outputs[0])


#         #    bpy.data.brushes[0].color = (0.5, 0.5, 0.5)
#         #    bpy.ops.paint.vertex_color_set()
        


            
#             # # make a random color table for each vert
#             # # vert_color = random_color_table[vert.index]
                
#             # if not ob.data.vertex_colors:
#             #     #bpy.ops.mesh.vertex_color_add()
#             #     color_layer = bm.loops.layers.color.new("Col")
#             # else :
#             #     color_layer = bm.loops.layers.color.get(ob.data.vertex_colors[0].name)

#             # if len(selected_faces) == 0:
#             #     for face in bm.faces:
#             #         for loop in face.loops:
#             #             print("Vert:", loop.vert.index)
#             #             loop[color_layer] = (0.5, 0.5, 0.5, 1.0)
#             #     bm.to_mesh(mesh)
#             # else:
#             #     for face in selected_faces:
#             #         for loop in face.loops:
#             #             print("Vert:", loop.vert.index)
#             #             loop[color_layer] = appliedColor




#             # colAttr.attribute_name = ob.data.vertex_colors[0].name
#             # mat.node_tree.links.new(shader.inputs['Base Color'], colAttr.outputs['Color'])
#             # mat_output = mat.node_tree.nodes.get('Material Output')
#             # mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

#             # # Assign it to object
#             # if ob.data.materials:
#             #     ob.data.materials[0] = mat
#             # else:
#             #     ob.data.materials.append(mat)                 
            
#     return {'FINISHED'}




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


def quadrant_map(mesh_objects):
    # UV map target_object if no UV's present
    for mesh_object in mesh_objects:
        if mesh_object.type == 'MESH':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.select_all(action='DESELECT')
            mesh_object.select_set(state=True)
            bpy.context.view_layer.objects.active = mesh_object
            bpy.ops.mesh.uv_texture_add()
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='SELECT')

            bpy.ops.mesh.mark_seam(clear=True)

            bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), xstart=mesh_object.dimensions[1], xend=mesh_object.dimensions[1], ystart=mesh_object.dimensions[2], yend=mesh_object.dimensions[2])
            bpy.ops.mesh.mark_seam(clear=False)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 1, 0), xstart=mesh_object.dimensions[1], xend=mesh_object.dimensions[1], ystart=mesh_object.dimensions[2], yend=mesh_object.dimensions[2])
            bpy.ops.mesh.mark_seam(clear=False)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 0, 1), xstart=mesh_object.dimensions[1], xend=mesh_object.dimensions[1], ystart=mesh_object.dimensions[2], yend=mesh_object.dimensions[2])
            bpy.ops.mesh.mark_seam(clear=False)
            bpy.ops.mesh.select_all(action='SELECT')

            # bpy.ops.uv.cube_project(cube_size=10, scale_to_bounds=True)
            bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.015)


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
                        # bpy.ops.uv.minimize_stretch(override, iterations=100)
                        if operator_exists("uvpackmaster2"):
                            bpy.context.scene.uvp2_props.pack_to_others = False
                            bpy.context.scene.uvp2_props.margin = 0.01
                            bpy.context.scene.uvp2_props.rot_step = 5
                            bpy.ops.uvpackmaster2.uv_measure_area()
                            bpy.ops.uv.average_islands_scale()
                            bpy.ops.uv.pack_islands(override , margin=0.015)
                            bpy.ops.uvpackmaster2.uv_pack()
                        else:
                            bpy.ops.uv.average_islands_scale(override)
                            bpy.ops.uv.pack_islands(override , margin=0.015)




            # bpy.ops.mesh.select_all(action='SELECT')
            # C=bpy.context
            # old_area_type = C.area.type
            # C.area.type='IMAGE_EDITOR'
            # bpy.ops.uv.pack_islands(margin=0.017)
            # C.area.type=old_area_type


    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # raise Exception('stopping script')

    return {'FINISHED'} 








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
                # bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02, area_weight=0.75, correct_aspect=True, scale_to_bounds=True)
                # bpy.ops.uv.seams_from_islands()
                # bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
                # bpy.ops.uv.minimize_stretch(iterations=1024)
                # bpy.ops.uv.average_islands_scale()

                bpy.ops.uv.cube_project(cube_size=10, scale_to_bounds=True)

                # area = bpy.context.area
                # old_type = area.type
                # if bakemesh.data.uv_layers:
                    # area.type = 'IMAGE_EDITOR'
                    # if operator_exists("uvpackmaster2"):
                    #     bpy.context.scene.uvp2_props.pack_to_others = False
                    #     bpy.context.scene.uvp2_props.margin = 0.015
                    #     bpy.ops.uvpackmaster2.uv_pack()
                # if old_type != "":
                    # area.type = old_type
            

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
                        # bpy.ops.uv.minimize_stretch(override, iterations=100)
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




            # bpy.ops.mesh.select_all(action='SELECT')
            # C=bpy.context
            # old_area_type = C.area.type
            # C.area.type='IMAGE_EDITOR'
            # bpy.ops.uv.pack_islands(margin=0.017)
            # C.area.type=old_area_type


    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # raise Exception('stopping script')

    return {'FINISHED'} 



def uvmap_mesh(mesh_objects):
    current_mode = bpy.context.mode
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # bpy.ops.object.select_all(action='DESELECT')
    # for ob in mesh_objects:
    #     if ob.type == 'MESH':
    #         ob.select_set(state=True)
    #         bpy.context.view_layer.objects.active = ob
    #         bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    #     bpy.ops.object.mode_set(mode='EDIT', toggle=False)   
    #     bpy.ops.mesh.select_all(action='SELECT')
    #     # bpy.ops.uv.cube_project(cube_size=1.27702, clip_to_bounds=False, scale_to_bounds=True)
    #     bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02, user_area_weight=0.75, use_aspect=True, stretch_to_bounds=True)
    #     bpy.ops.uv.minimize_stretch(iterations=256)
    #     bpy.ops.uv.average_islands_scale()

    #     # if operator_exists('uvpackmaster2'):
    #     #     for area in bpy.context.screen.areas:
    #     #         if area.type == 'IMAGE_EDITOR':
    #     #             override = bpy.context.copy()
    #     #             override['space_data'] = area.spaces.active
    #     #             override['region'] = area.regions[-1]
    #     #             override['area'] = area
    #     #             bpy.context.scene.uvp2_props.pack_to_others = False
    #     #             bpy.context.scene.uvp2_props.margin = 0.01
    #     #             bpy.ops.uvpackmaster2.uv_pack()

    #     # if decimate:
    #     #     bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    #     #     bpy.ops.object.modifier_add(type='DECIMATE')
    #     #     bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
    #     #     bpy.context.object.modifiers["Decimate"].angle_limit = 0.0523599
    #     #     bpy.context.object.modifiers["Decimate"].delimit = {'UV'}
    #     #     bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

    #     #     bpy.ops.object.modifier_add(type='TRIANGULATE')
    #     #     bpy.context.object.modifiers["Triangulate"].keep_custom_normals = True
    #     #     bpy.context.object.modifiers["Triangulate"].quad_method = 'FIXED'
    #     #     bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")

    #     #     bpy.ops.object.modifier_add(type='DECIMATE')
    #     #     bpy.context.object.modifiers["Decimate"].ratio = ratio
    #     #     bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
    #     #     bpy.ops.object.mode_set(mode='EDIT', toggle=False)




    #     bpy.ops.mesh.select_all(action='SELECT')
    #     # bpy.ops.uv.stitch(use_limit=False, snap_islands=True, limit=0, static_island=0, active_object_index=0, midpoint_snap=False, clear_seams=True, mode='EDGE', stored_mode='EDGE')
    #     bpy.ops.mesh.mark_seam(clear=True)
    #     bpy.ops.uv.seams_from_islands()
    #     bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    #     bpy.ops.uv.pack_islands(margin=0.0025)
    #     # bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # for ob in mesh_objects:
    # for i in range(0, mesh_objects):
    for i in range(len(mesh_objects)):
        ob = mesh_objects[i]
        if ob.type == 'MESH':
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            if not len( ob.data.uv_layers ):
                bpy.ops.mesh.uv_texture_add()
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02, area_weight=0.75, correct_aspect=True, scale_to_bounds=True)
                bpy.ops.uv.seams_from_islands()
                bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            for region in area.regions:
                                if region.type == 'WINDOW':
                                    override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                                    bpy.ops.uv.select_all(action='SELECT')
                                    bpy.ops.uv.average_islands_scale(override)
                                    bpy.ops.uv.minimize_stretch(override, iterations=300)
                                    bpy.ops.uv.pack_islands(override , margin=0.05)


            #select all meshes and pack into one UV set together
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.select_all(action='DESELECT')
            for ob in mesh_objects:
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='SELECT')
            # C=bpy.context
            # old_area_type = C.area.type
            # C.area.type='GRAPH_EDITOR'
            # bpy.ops.uv.pack_islands(margin=0.017)
            # C.area.type=old_area_type

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for region in area.regions:
                            if region.type == 'WINDOW':
                                override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                                bpy.ops.uv.select_all(action='SELECT')
                                bpy.ops.uv.average_islands_scale(override)
                                bpy.ops.uv.minimize_stretch(override, iterations=300)
                                bpy.ops.uv.pack_islands(override , margin=0.05)




            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.mode_set(mode=current_mode, toggle=False)

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
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            for i in range(len(ob.material_slots)):
                bpy.ops.object.material_slot_remove({'object': ob})
            if not len(ob.data.uv_layers):
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                selected_objects = bpy.context.selected_objects
                # uvmap_mesh(selected_objects)
                automap(selected_objects)

            bpy.ops.object.shade_smooth()

            assetName = ob.name
            matName = (assetName + "Mat")
            # matName = file_name
            # matName = bytes(file_name, "utf-8").decode("unicode_escape")
            
            texName_albedo = (assetName + "_albedo")
            
            mat = bpy.data.materials.new(name=matName)
            mat.use_nodes = True
            mat.node_tree.nodes.clear()
            mat_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

            shader = mat.node_tree.nodes.new(type='ShaderNodeBsdfDiffuse')

            texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            # texture.image = bpy.data.images.new(texName_albedo, width=width, height=height)
            old_image = bpy.data.images.get(texName_albedo)
            if old_image != None:
                old_image.user_clear()
                bpy.data.images.remove(old_image)
            bpy.ops.image.new(name=texName_albedo, width=width, height=height, color=(0.5, 0.5, 0.5, 1.0), alpha=False, generated_type='BLANK', float=False, use_stereo_3d=False, tiled=False)
            texture.image = bpy.data.images[texName_albedo] 
            new_image = bpy.data.images[texName_albedo]

            C=bpy.context
            old_area_type = C.area.type
            C.area.type='IMAGE_EDITOR'
            C.area.spaces.active.image = new_image
            bpy.ops.image.pack()
            C.area.type=old_area_type



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
                # else:
                #     matnodes = mat.node_tree.nodes
                #     C=bpy.context
                #     old_area_type = C.area.type
                #     C.area.type='NODE_EDITOR'
                #     texture.select = True
                #     matnodes.active = texture
                #     texture.image.pack()
                #     C.area.type=old_area_type



        # set a temporary context to poll correctly
        context = bpy.context.copy()
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        context['area'] = area
                        context['region'] = region
                        break
                break
        bpy.ops.image.view_zoom_ratio(context,ratio=1)
        bpy.ops.image.pack(context)


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

def group_make(self, new_group_name):
    self.node_tree = bpy.data.node_groups.new(new_group_name, 'ShaderNodeGroup')
    self.group_name = self.node_tree.name

    nodes = self.node_tree.nodes
    inputnode.location = (-300, 0)
    outputnode.location = (300, 0)
    return self.node_tree

def add_ao(self, context, objects):
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)                
    selected_objects = objects 
    if selected_objects is not None :
        # ob = bpy.context.view_layer.objects.active
        for ob in selected_objects:
            if ob.type == 'MESH':
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = ob
                if ob.active_material is not None:
                    mat =  ob.active_material
                    mat.use_nodes = True
                    ao_group_name = 'AO group'

                    gnodes = [n for n in mat.node_tree.nodes if n.name == ao_group_name]
                    print(gnodes)
                    for g in gnodes:
                        g.select = True
                        matnodes.active = g
                        bpy.ops.node.delete_reconnect()


                    mat_output = mat.node_tree.nodes.get('Material Output')
                    shader_node = mat_output.inputs[0].links[0].from_node


                    group = bpy.data.node_groups.new(type="ShaderNodeTree", name= ao_group_name)

                    #Creating Group Input
                    group.inputs.new("NodeSocketShader", "Input1")
                    group.inputs.new("NodeSocketInterfaceFloat", "AO Intensity")
                    input_node = group.nodes.new("NodeGroupInput")
                    input_node.location = (0, 0)



                    #Creating Group Output
                    group.outputs.new("NodeSocketShader", "Output1")
                    output_node = group.nodes.new("NodeGroupOutput")
                    output_node.location = (500, 0)


                    # Creating Principled bsdf Node
                    #You can create any node here which you think are required to be in the group as these will be created automatically in a group


                    # ao_group = mat.node_tree.nodes.new('ShaderNodeGroup')


                    # # ao_group.name = ao_group_name
                    # ao_group.node_tree = bpy.data.node_groups[mat.node_tree.name] 
                    # # ao_group.node_tree = bpy.data.node_groups['BASE SKP']
                    # D.node_groups['NodeGroup'].nodes['Group Input']
                    
                    # #  relink everything
                    # mat.node_tree.links.new(shader_node.outputs[0], ao_group.inputs[0])
                    # mat.node_tree.links.new(ao_group.outputs[0], mat_output.inputs[0])

                    # # ao_group_input = mat.node_tree.nodes.new('NodeGroupInput')
                    # # ao_group_output = mat.node_tree.nodes.new('NodeGroupOutput')

                    ao = group.nodes.new(type='ShaderNodeAmbientOcclusion')
                    black = group.nodes.new(type='ShaderNodeEmission')
                    mix = group.nodes.new(type='ShaderNodeMixShader')
                    gamma = group.nodes.new(type='ShaderNodeGamma')

                    ao.samples = 4
                    ao.inputs[1].default_value = 0.5

                    black.inputs[0].default_value = (0, 0, 0, 1)


                    mat_output = mat.node_tree.nodes.get('Material Output')
                    existing_shader = mat_output.inputs[0].links[0].from_node


                    group.links.new(ao.outputs[0], gamma.inputs[0])
                    group.links.new(gamma.outputs[0], mix.inputs[0])
                    group.links.new(black.outputs[0], mix.inputs[1])
                    # group.links.new(existing_shader.outputs[0], mix.inputs[2])
                    group.links.new(input_node.outputs[0], mix.inputs[2])
                    group.links.new(mix.outputs[0], mat_output.inputs[0])


                    #creating links between nodes in group
                    group.links.new(input_node.outputs[1], gamma.inputs[1])
                    group.links.new(mix.outputs[0], output_node.inputs[0])

                    # Putting Node Group to the node editor
                    tree = bpy.context.object.active_material.node_tree
                    group_node = tree.nodes.new("ShaderNodeGroup")
                    group_node.node_tree = group
                    group_node.location = (-40,0)

                    #connections bewteen node group to output 
                    links = tree.links    
                    link = links.new(group_node.outputs[0], mat_output.inputs[0])
                    link = links.new(shader_node.outputs[0], group_node.inputs[0])

                    #setup material slider ranges
                    group.inputs[1].name = "AO Intensity"
                    group.inputs[1].default_value = 3
                    group.inputs[1].min_value = 0
                    group.inputs[1].max_value = 50
                # else:
                #     self.report({'ERROR'}, 'You must have a material assigned first!')
                    
        for ob in selected_objects:
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob

        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            bpy.context.scene.eevee.use_gtao = True
            bpy.context.scene.eevee.gtao_distance = 2


    return {'FINISHED'}

def add_gradient(self, context):
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)                
    selected_objects = bpy.context.selected_objects
    if (bpy.context.mode == 'OBJECT'):
            selected_objects = bpy.context.selected_objects
            for ob in selected_objects:
                if ob.type == 'MESH' or ob.type == 'CURVE':
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                    if ob.active_material is not None:
                        mat = ob.active_material
                    else:
                        assetName = ob.name
                        matName = (assetName + "Mat")
                        mat = bpy.data.materials.new(name=matName)
                        mat.use_nodes = True

                    mat_output = mat.node_tree.nodes.get('Material Output')
                    shader = mat_output.inputs[0].links[0].from_node
                    tex_coord = mat.node_tree.nodes.new(type='ShaderNodeTexCoord')
                    mapping = mat.node_tree.nodes.new(type='ShaderNodeMapping')
                    sep_xyz = mat.node_tree.nodes.new(type='ShaderNodeSeparateXYZ')
                    ramp = mat.node_tree.nodes.new(type='ShaderNodeValToRGB')

                    mat.node_tree.links.new(tex_coord.outputs[0], mapping.inputs[0])
                    mat.node_tree.links.new(mapping.outputs[0], sep_xyz.inputs[0])
                    mat.node_tree.links.new(sep_xyz.outputs[2], ramp.inputs[0])
                    mat.node_tree.links.new(ramp.outputs[0], shader.inputs[0])

                    # change shader properties
                    ramp.color_ramp.elements[0].position = 0.1
                    ramp.color_ramp.elements[0].color = (0.1, 0.1, 0.1, 1)
                    ramp.color_ramp.interpolation = 'EASE'

                                    
                                
                    # Assign it to object
                    if ob.data.materials:
                        ob.data.materials[0] = mat
                    else:
                        ob.data.materials.append(mat)

            for ob in selected_objects:
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    # #types = {'VIEW_3D', 'TIMELINE', 'GRAPH_EDITOR', 'DOPESHEET_EDITOR', 'NLA_EDITOR', 'IMAGE_EDITOR', 'SEQUENCE_EDITOR', 'CLIP_EDITOR', 'TEXT_EDITOR', 'NODE_EDITOR', 'LOGIC_EDITOR', 'PROPERTIES', 'OUTLINER', 'USER_PREFERENCES', 'INFO', 'FILE_BROWSER', 'CONSOLE'}
                    area.type='NODE_EDITOR'
                    area.ui_type='ShaderNodeTree'
                    override = bpy.context.copy()
                    override['area'] = area
                    # do the stuff
                    # bpy.ops.node_relax.arrange(override)    
                    bpy.ops.node.nw_del_unused(override)
                    # set the pane back to a 3Dview
                    area.type = 'VIEW_3D'
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

    selected_objects = bpy.context.selected_objects
    for mesh_object in selected_objects:
        try:
            del mesh_object["cycles"]     
        except:
            pass

        try:
            del mesh_object["b_painter_active_material"]     
        except:
            pass

        try:
            del mesh_object["ant_landscape"]     
        except:
            pass

        try:
            del mesh_object["free_ik"]     
        except:
            pass

        try:
            del mesh_object["cycles_visibility"]     
        except:
            pass

        try:
            del mesh_object["ht_props"]     
        except:
            pass

        try:
            del mesh_object["ant_landscape"]     
        except:
            pass

    # outliner.orphans_purge
    return {'FINISHED'}

class SPIRALOID_MT_nuke_bsdf_uv_texture(bpy.types.Operator):
    """Nuke Selected Object 50% Gray"""
    bl_idname = "view3d.spiraloid_nuke_bsdf_uv_texture"
    bl_label = "Nuke BSDF UV Textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        nuke_bsdf_textures(selected_objects, 1024, 1024)
        return {'FINISHED'}   

class SPIRALOID_MT_nuke_bsdf_triplanar_texture(bpy.types.Operator):
    """Nuke Selected Object 50% Gray"""
    bl_idname = "view3d.spiraloid_nuke_bsdf_triplanar_texture"
    bl_label = "Nuke BSDF Triplanar Textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        nuke_bsdf_textures(selected_objects, 1024, 1024)
        return {'FINISHED'}  

class SPIRALOID_MT_nuke_flat(bpy.types.Operator):
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
                shader.inputs[0].default_value = (0, 0, 0, 1)
                mat.node_tree.links.new(shader.outputs[0], mat_output.inputs[0])

            #    bpy.data.brushes[0].color = (0.5, 0.5, 0.5)
            #    bpy.ops.paint.vertex_color_set()
                
                # Assign it to object
                if ob.data.materials:
                    ob.data.materials[0] = mat
                else:
                    ob.data.materials.append(mat)                 
                
                ob.active_material.use_backface_culling = True



        return {'FINISHED'}

class SPIRALOID_MT_nuke_flat_vertex_color(bpy.types.Operator):
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

class SPIRALOID_MT_nuke_flat_texture(bpy.types.Operator):
    """Nuke Selected Object 50% Gray"""
    bl_idname = "view3d.spiraloid_nuke_flat_texture"
    bl_label = "Nuke Flat Texture"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        nuke_flat_texture(selected_objects, 1024, 1024)
        return {'FINISHED'}           

class SPIRALOID_MT_nuke_diffuse_texture(bpy.types.Operator):
    """Nuke Selected Object with a Diffuse material and create a new texture"""
    bl_idname = "view3d.spiraloid_nuke_diffuse_texture"
    bl_label = "Nuke Diffuse Texture"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        nuke_diffuse_texture(selected_objects, 1024, 1024)
        return {'FINISHED'}           

class SPIRALOID_MT_empty_trash(bpy.types.Operator):
    """Purge all data blocks with 0 users"""
    bl_idname = "wm.spiraloid_empty_trash"
    bl_label = "Empty Trash"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        empty_trash(self, context)
        return {'FINISHED'}           




class SPIRALOID_MT__workshop(bpy.types.Operator):
    """Visit the spiraloid workshop for updates and goodies!"""
    bl_idname = "view3d.spiraloid_workshop"
    bl_label = "Visit Workshop..."
    def execute(self, context):                

        return {'FINISHED'}

def scene_mychosenobject_poll(self, object):
    return object.type == 'MESH'

class SPIRALOID_MT_add_cavity(bpy.types.Operator):
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

        

class SPIRALOID_MT_add_ao(bpy.types.Operator):
    """insert ambient occlusion node"""
    bl_idname = "object.spiraloid_add_ao"
    bl_label = "Insert AO"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        add_ao(self, context, selected_objects)
        return {'FINISHED'}


class SPIRALOID_MT_add_gradient(bpy.types.Operator):
    """insert gradient nodes"""
    bl_idname = "object.spiraloid_add_gradient"
    bl_label = "Insert Gradient"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_gradient(self, context)
        return {'FINISHED'}


class SPIRALOID_MT_add_curvature(bpy.types.Operator):
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


class SPIRALOID_MT_bake_vertex_color(bpy.types.Operator):
    """convert vertex color to texture"""
    bl_idname = "view3d.spiraloid_vertex_color_to_texture"
    bl_label = "Vertex Color to Texture"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):                
        return {'FINISHED'}

class SPIRALOID_MT_bake_texture_to_vertex_color(bpy.types.Operator):
    """convert texture to vertex color"""
    bl_idname = "view3d.spiraloid_texture_to_vertex_color"
    bl_label = "Texture To Vertex Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):                

        return {'FINISHED'}


class SPIRALOID_MT_regenerate_video(bpy.types.Operator):
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

class SPIRALOID_MT_nuke(bpy.types.Operator):
    """create a new material with gray color, ao and curvature material nodes."""
    bl_idname = "wm.spiraloid_nuke"
    bl_label = "Nuke"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        global wasInEditMode
        global my_shading
        global keepcolor
        my_areas = bpy.context.workspace.screens[0].areas
        selected_objects = bpy.context.selected_objects
        wasInEditMode = False

        if selected_objects:
            if len(context.selected_objects) and context.object.type == 'MESH' and context.mode == 'EDIT_MESH':
                wasInEditMode =True

            if context.object.type == 'MESH':
                smart_nuke_bsdf(self, context, False)
            # SPIRALOID_MT_add_curvature.execute(self, context)
            # SPIRALOID_MT_add_cavity.execute(self, context)

            if context.object.type == 'VOLUME':
                nuke_smoke(self, context)

            # copy last material copy to all objects.
            for ob in selected_objects:
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
                bpy.ops.object.material_slot_copy()
        else:
            bpy.ops.object.gpencil_add(align='WORLD', location=(0.688679, -0.108224, 2.18184), scale=(1, 1, 1), type='EMPTY')
            gp_object = bpy.context.selected_objects[0]
            gp_object_name = "GPencil.TEMPLATE"
            gp_object.name = gp_object_name
            bpy.ops.gpencil.layer_add()
            gp_object.data.layers["GP_Layer"].use_lights = False
            bpy.ops.material.new()
            gp_mat_name = (gp_object_name + "Mat")
            mat = bpy.data.materials.new(name=gp_mat_name)
            bpy.data.materials.create_gpencil_data(mat)
            gp_object.data.materials.append(mat)
            bpy.ops.gpencil.paintmode_toggle()
            startFrame = bpy.context.scene.frame_start
            bpy.context.scene.frame_set(startFrame)
            gp_object.keyframe_insert(data_path="location", index=-1, frame=startFrame)
            bpy.context.scene.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'
            bpy.context.scene.tool_settings.gpencil_sculpt.lock_axis = 'VIEW'
            bpy.data.brushes["Ink Pen"].color = (0, 0, 0)


        for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if wasInEditMode :
                        if space.shading.type == 'SOLID':
                            space.shading.color_type = 'VERTEX'
                    else:
                        space.shading.type = my_shading
            
            # bpy.context.scene.tool_settings.use_keyframe_insert_auto =    True


        return {'FINISHED'}

class SPIRALOID_MT_nuke_invert(bpy.types.Operator):
    """create a new material with gray color, ao and curvature material nodes."""
    bl_idname = "wm.spiraloid_nuke_invert"
    bl_label = "Nuke Invert"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        global wasInEditMode
        global my_shading
        global keepcolor
        my_areas = bpy.context.workspace.screens[0].areas
        selected_objects = bpy.context.selected_objects
        wasInEditMode = False

        if len(context.selected_objects) and context.object.type == 'MESH' and context.mode == 'EDIT_MESH':
            wasInEditMode =True

        smart_nuke_bsdf(self, context, True)
        # SPIRALOID_MT_add_curvature.execute(self, context)
        # SPIRALOID_MT_add_cavity.execute(self, context)

        # copy last material copy to all objects.
        for ob in selected_objects:
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.material_slot_copy()

        for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if wasInEditMode :
                        if space.shading.type == 'SOLID':
                            space.shading.color_type = 'VERTEX'
                    else:
                        space.shading.type = my_shading
        return {'FINISHED'}




class SPIRALOID_MT_uvmap(bpy.types.Operator):
    """unwrap selected objects into a shared UV space"""
    bl_idname = "view3d.spiraloid_uvmap"
    bl_label = "Batch Unwrap"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if (bpy.context.mode != 'OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        selected_objects = bpy.context.selected_objects
        selected_objects[0].select_set(state=True)
        bpy.context.view_layer.objects.active = selected_objects[0]
        automap(selected_objects)
        return {'FINISHED'}

class SPIRALOID_MT_uvmap_quadrants(bpy.types.Operator):
    """unwrap selected objects into a shared UV space adding ne geometry edges on the primary axis planes"""
    bl_idname = "view3d.spiraloid_uvmap_quadrants"
    bl_label = "Batch Unwrap Quadrants"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if (bpy.context.mode != 'OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        selected_objects = bpy.context.selected_objects
        selected_objects[0].select_set(state=True)
        bpy.context.view_layer.objects.active = selected_objects[0]
        quadrant_map(selected_objects)
        return {'FINISHED'}

class SPIRALOID_MT_automesh(bpy.types.Operator):
    """generate a quad mesh with multires and UV's that looks like the same mesh"""
    bl_idname = "view3d.spiraloid_automesh"
    bl_label = "Automesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.visible_get and  obj.type == 'MESH':
                print(obj.name)
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(state=True)
                bpy.context.view_layer.objects.active = obj

                bpy.ops.qremesher.remesh()

                remeshed_object = bpy.context.selected_objects

                multires_mod = remeshed_object.modifiers.new(name = 'Multires', type = 'MULTIRES')
                level = 3
                if level > 0:
                    for i in range(0, level):
                        bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')

                shrink_mod = remeshed_object.modifiers.new(name = 'Shrinkwrap', type = 'SHRINKWRAP')
                shrink_mod.target = bpy.data.objects[obj.name]
                shrink_mod.wrap_method = 'PROJECT'
                shrink_mod.offset = 0
                shrink_mod.project_limit = 0.2
                shrink_mod.subsurf_levels = 0
                shrink_mod.use_negative_direction = True
                shrink_mod.use_positive_direction = True
                shrink_mod.cull_face = 'OFF'

                for mod in [m for m in remeshed_object.modifiers]:
                    if 'Shrinkwrap' in mod.name:
                        bpy.ops.object.modifier_apply( modifier=mod.name)

                obj.select_set(state=True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.material_slot_copy()
                bpy.ops.object.select_all(action='DESELECT')
                remeshed_object.select_set(state=True)
                bpy.context.view_layer.objects.active = remeshed_object

        return {'FINISHED'}

last_visible_object_index = 0

class SPIRALOID_MT_cycle_visible_next(bpy.types.Operator):
    """Isolate each visible object one by one"""
    bl_idname = "wm.spiraloid_cycle_visible_next"
    bl_label = "Cycle Next Visible"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global last_visible_object_index
        next_visible_object_index =  last_visible_object_index
        active_collection = ""
        selected_objects = bpy.context.selected_objects

        visible_objects = []
        for obj in bpy.context.view_layer.objects:
            if obj.visible_get: 
                obj_type = obj.type
                if obj_type == 'MESH' or obj_type == 'CURVE' or obj_type == 'Empty':
                    obj_name = obj.name
                    visible_objects.append(obj)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces[0]
                if space.local_view: #check if using local view
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region} #override context
                            bpy.ops.view3d.localview(override, frame_selected=False) #switch to global view
        # if selected_objects:
        #     active_collection = selected_objects[0].users_collection[0]
        # else:
        #     scenee_collections = bpy.context.scene.collection.children
        #     active_collection = scenee_collections[0]
        # collection_objects = active_collection.all_objects
        collection_objects = visible_objects
        num_objects =  len(collection_objects) -1
        if next_visible_object_index < num_objects:
            next_visible_object_index = next_visible_object_index + 1 
            obj = collection_objects[next_visible_object_index]
        else:
            obj = collection_objects[0]
            next_visible_object_index = 0
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active = obj
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region} #override context
                        bpy.ops.view3d.localview(override, frame_selected=False)
        last_visible_object_index = next_visible_object_index
        return {'FINISHED'}


class SPIRALOID_MT_cycle_visible_previous(bpy.types.Operator):
    """Isolate each visible object one by one"""
    bl_idname = "wm.spiraloid_cycle_visible_previous"
    bl_label = "Cycle Previously Visible"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global last_visible_object_index
        next_visible_object_index =  last_visible_object_index
        active_collection = ""
        selected_objects = bpy.context.selected_objects
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces[0]
                if space.local_view: #check if using local view
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region} #override context
                            bpy.ops.view3d.localview(override, frame_selected=False) #switch to global view
        if selected_objects:
            active_collection = selected_objects[0].users_collection[0]
        else:
            scenee_collections = bpy.context.scene.collection.children
            active_collection = scenee_collections[0]
        collection_objects = active_collection.all_objects
        num_objects =  len(collection_objects) -1
        if next_visible_object_index > 0:
            next_visible_object_index = next_visible_object_index - 1 
            obj = collection_objects[next_visible_object_index]
        else:
            obj = collection_objects[num_objects]
            next_visible_object_index = num_objects
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active = obj
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region} #override context
                        bpy.ops.view3d.localview(override, frame_selected=False)
        last_visible_object_index = next_visible_object_index
        return {'FINISHED'}





class SPIRALOID_MT_toggle_mods(bpy.types.Operator):
    """Toggle the modifiers for selected objects, otherwise toggle all visible"""
    bl_idname = "wm.spiraloid_toggle_mods"
    bl_label = "Toggle Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        toggle_mods()
        return {'FINISHED'}



#------------------------------------------------------
#------------------------------------------------------


# class DialogPanel(bpy.types.Panel):
#     bl_idname = "Choose bake options"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "TOOLS"
#     bl_context = "object"

#     def draw(self, context):

#         layout.operator(SPIRALOID_MT_bake_collection.bl_idname)

def populate_coll(scene):
    bpy.app.handlers.scene_update_pre.remove(populate_coll)
    scene.coll.clear()
    for identifier, name, description in enum_items:
        scene.coll.add().name = name

# def menu_draw_bake(self, context):
#     self.layout.operator("view3d.spiraloid_bake_collection", 
#         text="Bake Collection...")
#     # layout.menu(SpiraloidOutlinerMenu.bl_idname)

#     bpy.ops.object.dialog_operator('INVOKE_DEFAULT')


#------------------------------------------------------

class SPIRALOID_MT_Menu(bpy.types.Menu):
    bl_idname = "SPIRALOID_MT_Menu"
    bl_label = "Spiraloid"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("wm.spiraloid_nuke")
        layout.operator("wm.spiraloid_nuke_invert")
        # layout.operator("view3d.INFO_HT_spiraloid_color_pallet")

        layout.menu(SPIRALOID_MT_SubMenuMaterials.bl_idname )
        layout.menu(SPIRALOID_MT_SubMenuUtilities.bl_idname )

        layout.separator()

        layout.menu(SPIRALOID_MT_SubMenuHelp.bl_idname, icon="QUESTION")
        layout.separator()
        layout.operator("wm.spiraloid_empty_trash")





class SPIRALOID_MT_SubMenuHelp(bpy.types.Menu):
    bl_idname = 'SPIRALOID_MT_SubMenuHelp'
    bl_label = 'Help'

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.spiraloid_workshop")

class SPIRALOID_MT_SubMenuUtilities(bpy.types.Menu):
    bl_idname = 'SPIRALOID_MT_SubMenuUtilities'
    bl_label = 'Utilities'

    def draw(self, context):
        layout = self.layout
        # layout.operator("view3d.spiraloid_bake_collection")
        layout.operator("view3d.spiraloid_automesh")
        layout.operator("view3d.spiraloid_uvmap")
        layout.operator("view3d.spiraloid_uvmap_quadrants")
        layout.separator()
        layout.operator("wm.spiraloid_cycle_visible_next")
        layout.operator("wm.spiraloid_cycle_visible_previous")
        layout.separator()
        layout.operator("view3d.spiraloid_vertex_color_to_texture")
        layout.operator("view3d.spiraloid_texture_to_vertex_color")
        layout.separator()
        layout.operator("view3d.spiraloid_regenerate_scene_strip")

class SPIRALOID_MT_SubMenuMaterials(bpy.types.Menu):
    bl_idname = 'SPIRALOID_MT_SubMenuMaterials'
    bl_label = 'Materials'

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.spiraloid_nuke_flat_texture")
        layout.operator("view3d.spiraloid_nuke_diffuse_texture")
        layout.operator("view3d.spiraloid_nuke_bsdf_uv_texture")
        layout.operator("view3d.spiraloid_nuke_bsdf_triplanar_texture")
        layout.separator()
        layout.operator("view3d.spiraloid_nuke_flat")
        layout.separator() 
        layout.operator("view3d.spiraloid_nuke_flat_vertex_color")
        layout.separator()
        layout.operator("object.spiraloid_add_ao")
        layout.operator("view3d.spiraloid_add_curvature")
        layout.operator("view3d.spiraloid_add_cavity")
        layout.operator("object.spiraloid_add_gradient")



def draw_item(self, context):
    layout = self.layout
    layout.menu(SPIRALOID_MT_Menu.bl_idname)

def draw_toggle_mods_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(SPIRALOID_MT_toggle_mods.bl_idname)

# def add_to_render_menu(self, context):
#     self.layout.operator("wm.spiraloid_toggle_workmode", 
#         text="Toggle Workmode")

#------------------------------------------------------

classes = (
    SPIRALOID_MT_PalletColorMenu,
    SPIRALOID_MT_Menu,
    SPIRALOID_MT_SubMenuHelp,
    SPIRALOID_MT_toggle_mods,
    SPIRALOID_MT_cycle_visible_next,
    SPIRALOID_MT_cycle_visible_previous,
    SPIRALOID_MT_SubMenuUtilities,
    SPIRALOID_MT_SubMenuMaterials,
    SPIRALOID_MT_nuke,
    SPIRALOID_MT_nuke_invert,
    SPIRALOID_MT_nuke_bsdf_uv_texture,
    SPIRALOID_MT_nuke_bsdf_triplanar_texture,
    SPIRALOID_MT_nuke_flat,
    SPIRALOID_MT_uvmap,
    SPIRALOID_MT_uvmap_quadrants,
    SPIRALOID_MT_automesh,
    SPIRALOID_MT_nuke_flat_vertex_color,
    SPIRALOID_MT_nuke_flat_texture,
    SPIRALOID_MT_nuke_diffuse_texture,
    SPIRALOID_MT__workshop,
    SPIRALOID_MT_bake_vertex_color,
    SPIRALOID_MT_add_ao,
    SPIRALOID_MT_add_curvature,
    SPIRALOID_MT_add_cavity,
    SPIRALOID_MT_add_gradient,
    SPIRALOID_MT_bake_texture_to_vertex_color,
    SPIRALOID_MT_regenerate_video,
    SPIRALOID_MT_empty_trash,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.TOPBAR_MT_editor_menus.append(draw_item)
    bpy.types.VIEW3D_MT_view.append(draw_toggle_mods_menu) 

    # bpy.types.TOPBAR_MT_render.append(add_to_render_menu)
    # bpy.types.OUTLINER_MT_collection.append(draw_context_menus)
    # bpy.types.TOPBAR_MT_render.append(menu_draw_bake)
    # bpy.utils.register_class(SpiraloidPreferences)
    # bpy.utils.register_class(SPIRALOID_MT_bake_collection)
    # bpy.utils.register_class(BakeCollectionSettings)
    # bpy.types.Scene.bake_collection_settings = bpy.props.PointerProperty(type=BakeCollectionSettings)
#    bpy.types.SEQUENCER_MT_add.prepend(add_object_button)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_item)
    bpy.types.VIEW3D_MT_view.remove(draw_toggle_mods_menu) 

    # bpy.types.TOPBAR_MT_render.remove(add_to_render_menu)
    # bpy.types.OUTLINER_MT_collection.remove(draw_context_menus)
    # bpy.types.TOPBAR_MT_render.remove(menu_draw_bake)
    # bpy.utils.unregister_class(SpiraloidPreferences)

    # if __name__ != "__main__":
        # bpy.types.TOPBAR_MT_render.remove(menu_draw_bake)
        # bpy.types.SEQUENCER_MT_add.remove(add_object_button)

if __name__ == "__main__":
    register()

    # The menu can also be called from scripts
#bpy.ops.wm.call_menu(name=SpiraloidMenu.bl_idname)

#debug console
#__import__('code').interact(local=dict(globals(), **locals()))
# pauses wherever this line is:
# code.interact