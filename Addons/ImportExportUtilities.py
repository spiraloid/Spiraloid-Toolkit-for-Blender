bl_info = {
        'name': 'Obj Import-Export Utilities',
        'author': 'Bay Raitt',
        'version': (0, 3),
        'blender': (2, 80, 0),
        "description": "Import Obj Folder as Shape Keys, Export Shape Keys as Obj Folder, Batch Import Obj Folder, Batch Export Selected",
        'category': 'Import-Export',
        'location': 'File > Import/Export',
        'wiki_url': ''}

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import os.path
import bpy, os
from bpy.props import *


import os
import warnings



class BR_OT_load_obj_as_shapekey(bpy.types.Operator):
        bl_idname = 'load.obj_as_shapekey'
        bl_label = '.obj sequence as shape keys'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "Obj sequence as shape key(s)"

        filepath : StringProperty(name="File path", description="File filepath of Obj", maxlen=4096, default="")
        filter_folder : BoolProperty(name="Filter folders", description="", default=True, options={'HIDDEN'})
        filter_glob : StringProperty(default="*.obj", options={'HIDDEN'})
        files : CollectionProperty(name='File path', type=bpy.types.OperatorFileListElement)
        filename_ext = '.obj'
        
        #@classmethod
        #def poll(cls, context):
        #   return context.active_object is not None and context.active_object.type == 'MESH'

        def execute(self, context):
                #get file names, sort, and set target mesh
                spath : os.path.split(self.filepath)
                files = [file.name for file in self.files]
                files.sort()
                target = bpy.context.scene.objects.active
                #add all ojs in sequence as shape  keys
                for f in files:
                        fp : os.path.join(spath[0], f)
                        self.load_obj(fp)
                #now delete objs
                sknames = [sk.name for sk in target.data.shape_keys.key_blocks]
                bpy.ops.object.select_all(action='DESELECT')
                for obj in sknames:
                        if obj != 'Basis':
                                target.data.shape_keys.key_blocks[obj].interpolation = 'KEY_LINEAR'
                                bpy.context.scene.objects.active = bpy.data.objects[obj]
                                bpy.data.objects[obj].select = True
                                bpy.ops.object.delete()
                        bpy.ops.object.select_all(action='DESELECT')
                #reselect target mesh and make active
                bpy.context.scene.objects.active = target
                target.select = True
                return{'FINISHED'}

        def invoke(self, context, event):
                wm : context.window_manager.fileselect_add(self)
                return {'RUNNING_MODAL'}

        def load_obj(self, fp):
                bpy.ops.import_scene.obj(filepath=fp,split_mode='OFF')
                bpy.ops.object.join_shapes()
                return

class   BR_OT_export_shapekey_as_obj(bpy.types.Operator):
        bl_idname   =   "export.shape_keys_as_obj_sequence"
        bl_label =  '.obj sequence from Shape Keys'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "Export Shape Keys as Obj files"
        
        @classmethod
        def poll(cls, context):
            return context.active_object is not None and context.active_object.type == 'MESH'
            
        def execute(self,   context):

                #: Name of function for calling the nif export operator.
                IOpath = "export_scene.folder"

                #: How the nif import operator is labelled in the user interface.
                bl_label = "Export to folder"
                    
                o   =   bpy.context.object # Reference the active   object
            
                #   Reset   all shape   keys to 0   (skipping   the Basis   shape   on index 0
                for skblock in o.data.shape_keys.key_blocks[1:]:
                        skblock.value   =   0

                #write out the home shape
                objFileName =   "zero.obj" # File   name = basis name
                objPath :  join(   IOpath, objFileName )
                bpy.ops.export_scene.obj(   filepath = objPath, use_selection   =   True )

                #   Iterate over shape key blocks   and save each   as an   OBJ file
                for skblock in o.data.shape_keys.key_blocks[1:]:
                        skblock.value   =   1.0  # Set shape key value to   max

                        #   Set OBJ file path   and Export OBJ
                        objFileName =   skblock.name + ".obj"   #   File name   =   shapekey name
                        objPath :  join(   IOpath, objFileName )
                        bpy.ops.export_scene.obj(   filepath = objPath, use_selection   =   True )
                        skblock.value   =   0   #   Reset   shape   key value   to 0
                return{'FINISHED'}

def highlightObjects(selection_list):
    for i in selection_list:
        bpy.data.objects[i.name].select_set(state=True)

class   BR_OT_export_selected_as_obj(bpy.types.Operator, ExportHelper):
        bl_idname   =   "export_scene.selected_to_folder"
        bl_label =  '.obj sequence'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "Export selected meshes as separate obj files"
        bl_options = {'PRESET', 'UNDO'}

        # ExportHelper mixin class uses this
        filename_ext = ".obj"

        filter_glob : StringProperty(
                default="*.obj;*.mtl",
                options={'HIDDEN'},
                )

        # List of operator properties, the attributes will be assigned
        # to the class instance from the operator setting before calling.

        use_selection_setting : BoolProperty(
                name="Use Selection",
                description="Export selected obects only",
                default=True,
                )


        # object group
        use_mesh_modifiers_setting : BoolProperty(
                name="Apply Modifiers",
                description="Apply modifiers (preview resolution)",
                default=True,
                )

        # extra data group
        use_edges_setting : BoolProperty(
                name="Include Edges",
                description="",
                default=True,
                )
        use_smooth_groups_setting : BoolProperty(
                name="Smooth Groups",
                description="Write sharp edges as smooth groups",
                default=False,
                )
        use_smooth_groups_bitflags_setting : BoolProperty(
                name="Bitflag Smooth Groups",
                description="Same as 'Smooth Groups', but generate smooth groups IDs as bitflags "
                            "(produces at most 32 different smooth groups, usually much less)",
                default=False,
                )
        use_normals_setting : BoolProperty(
                name="Write Normals",
                description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
                default=True,
                )
        use_uvs_setting : BoolProperty(
                name="Include UVs",
                description="Write out the active UV coordinates",
                default=True,
                )
        use_materials_setting : BoolProperty(
                name="Write Materials",
                description="Write out the MTL file",
                default=True,
                )
        use_triangles_setting : BoolProperty(
                name="Triangulate Faces",
                description="Convert all faces to triangles",
                default=False,
                )
        use_vertex_groups_setting : BoolProperty(
                name="Polygroups",
                description="",
                default=False,
                )

        # grouping group
        use_blen_objects_setting : BoolProperty(
                name="Objects as OBJ Objects",
                description="",
                default=True,
                )
        group_by_object_setting : BoolProperty(
                name="Objects as OBJ Groups ",
                description="",
                default=False,
                )
        group_by_material_setting : BoolProperty(
                name="Material Groups",
                description="",
                default=False,
                )
        keep_vertex_order_setting : BoolProperty(
                name="Keep Vertex Order",
                description="",
                default=True,
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
                default='-Z',
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
                default='Y',
                )
        global_scale_setting : FloatProperty(
                name="Scale",
                min=0.01, max=1000.0,
                default=1.0,
                )

        def execute(self, context):                

            # get the folder
            folder_path = (os.path.dirname(self.filepath))

            # get objects selected in the viewport
            viewport_selection = bpy.context.selected_objects

            # get export objects
            obj_export_list = viewport_selection
            if self.use_selection_setting == False:
                obj_export_list = [i for i in bpy.context.scene.objects]

            # deselect all objects
            bpy.ops.object.select_all(action='DESELECT')

            for item in obj_export_list:
                item.select_set(state=True)
                bpy.context.view_layer.objects.active = item
                if item.type == 'MESH':
                        file_path = os.path.join(folder_path, "{}.obj".format(item.name))
                        bpy.ops.export_scene.obj(filepath=file_path, use_selection=True,
                                                axis_forward=self.axis_forward_setting, 
                                                axis_up=self.axis_up_setting,
                                                use_mesh_modifiers=self.use_mesh_modifiers_setting,
                                                use_edges=self.use_edges_setting, 
                                                use_smooth_groups=self.use_smooth_groups_setting,
                                                use_smooth_groups_bitflags=self.use_smooth_groups_bitflags_setting, 
                                                use_normals=self.use_normals_setting,
                                                use_uvs=self.use_uvs_setting, 
                                                use_materials=self.use_materials_setting, 
                                                use_triangles=self.use_triangles_setting, 
                                                use_vertex_groups=self.use_vertex_groups_setting, 
                                                use_blen_objects=self.use_blen_objects_setting, 
                                                group_by_object=self.group_by_object_setting, 
                                                group_by_material=self.group_by_material_setting, 
                                                keep_vertex_order=self.keep_vertex_order_setting, 
                                                global_scale=self.global_scale_setting)
                item.select_set(state=False)

            # restore viewport selection
            highlightObjects(viewport_selection)

            return {'FINISHED'}

class BR_OT_import_multiple_objs(bpy.types.Operator, ImportHelper):
        """Import Multiple Obj Files at Once"""
        bl_idname = "import_scene.multiple_objs"
        bl_label = ".obj sequence"
        bl_options = {'PRESET', 'UNDO'}

        # ImportHelper mixin class uses this
        filename_ext = ".obj"

        filter_glob : StringProperty(
                default="*.obj",
                options={'HIDDEN'},
                )

        # Selected files
        files : CollectionProperty(type=bpy.types.PropertyGroup)

        # List of operator properties, the attributes will be assigned
        # to the class instance from the operator settings before calling.
        ngons_setting : BoolProperty(
                name="NGons",
                description="Import faces with more than 4 verts as ngons",
                default=True,
                )
        edges_setting : BoolProperty(
                name="Lines",
                description="Import lines and faces with 2 verts as edge",
                default=True,
                )
        smooth_groups_setting : BoolProperty(
                name="Smooth Groups",
                description="Surround smooth groups by sharp edges",
                default=True,
                )

        split_objects_setting : BoolProperty(
                name="Object",
                description="Import OBJ Objects into Blender Objects",
                default=True,
                )
        split_groups_setting : BoolProperty(
                name="Group",
                description="Import OBJ Groups into Blender Objects",
                default=True,
                )

        groups_as_vgroups_setting : BoolProperty(
                name="Poly Groups",
                description="Import OBJ groups as vertex groups",
                default=False,
                )

        image_search_setting : BoolProperty(
                name="Image Search",
                description="Search subdirs for any associated images "
                            "(Warning, may be slow)",
                default=True,
                )

        split_mode_setting : EnumProperty(
                name="Split",
                items=(('ON', "Split", "Split geometry, omits unused verts"),
                       ('OFF', "Keep Vert Order", "Keep vertex order from file"),
                       ),
                default='OFF',
                )

        clamp_size_setting : FloatProperty(
                name="Clamp Size",
                description="Clamp bounds under this value (zero to disable)",
                min=0.0, max=1000.0,
                soft_min=0.0, soft_max=1000.0,
                default=0.0,
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
                default='-Z',
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
                default='Y',
                )

        def draw(self, context):
            layout = self.layout

            row = layout.row(align=True)
            row.prop(self, "ngons_setting")
            row.prop(self, "edges_setting")

            layout.prop(self, "smooth_groups_setting")

            box : layout.box()
            row : box.row()
            row.prop(self, "split_mode_setting", expand=True)

            row : box.row()
            if self.split_mode_setting == 'ON':
                row.label(text="Split by:")
                row.prop(self, "split_objects_setting")
                row.prop(self, "split_groups_setting")
            else:
                row.prop(self, "groups_as_vgroups_setting")

#            row = layout.split(percentage=0.67)
            
            
            
            row.prop(self, "clamp_size_setting")
            layout.prop(self, "axis_forward_setting")
            layout.prop(self, "axis_up_setting")

            layout.prop(self, "image_search_setting")

        def execute(self, context):

            # get the folder
            folder = (os.path.dirname(self.filepath))

            # iterate through the selected files
            for i in self.files:

                # generate full path to file
                path_to_file = (os.path.join(folder, i.name))

                # call obj operator and assign ui values                  
                bpy.ops.import_scene.obj(filepath = path_to_file,
                                    axis_forward = self.axis_forward_setting,
                                    axis_up = self.axis_up_setting, 
                                    use_edges = self.edges_setting,
                                    use_smooth_groups = self.smooth_groups_setting, 
                                    use_split_objects = self.split_objects_setting,
                                    use_split_groups = self.split_groups_setting,
                                    use_groups_as_vgroups = self.groups_as_vgroups_setting,
                                    use_image_search = self.image_search_setting,
                                    split_mode = self.split_mode_setting,
                                    global_clamp_size = self.clamp_size_setting)


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





def menu_import_draw(self, context):
    self.layout.operator(BR_OT_load_obj_as_shapekey.bl_idname)
    self.layout.operator(BR_OT_import_multiple_objs.bl_idname)

    
def menu_export_draw(self, context):
    self.layout.operator(BR_OT_export_shapekey_as_obj.bl_idname)
    self.layout.operator(BR_OT_export_selected_as_obj.bl_idname)


classes = (
    BR_OT_load_obj_as_shapekey,
    BR_OT_export_shapekey_as_obj,
    BR_OT_export_selected_as_obj,
    BR_OT_import_multiple_objs,
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
