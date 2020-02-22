bl_info = {
    "name": "Convert Armature to Mesh",
    "author": "Bay Raitt",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Convert to > Armature to Mesh",
    "description": "Adds a new wire skinned objects with a mirror modifier",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}

# # how to list all menus
# for menu in bpy.types.Menu.__subclasses__():
#     print(menu.bl_label,menu)

import bpy, bmesh

class OBJECT_OT_Armature_to_Mesh(bpy.types.Operator):
    """Create a new Mesh Object"""
    bl_idname = "mesh.armature_to_mesh"
    bl_label = "Generate Skin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.object
        isMirror = obj.data.use_mirror_x


        if obj is not None :
            if obj.type == 'ARMATURE':
                armt = obj.data
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                # this actually return STRING NAME of bone
                boneNames = armt.bones.keys()
                
                # the actual data to each 
                myBones = armt.bones


                # bpy.ops.object.select_all(action='DESELECT')
                # obj.select_set(state=True)
                # bpy.context.view_layer.objects.active = obj
                # bpy.ops.object.mode_set(mode='POSE', toggle=False)
                bpy.ops.object.location_clear(clear_delta=False)



                for i, bone in enumerate(myBones):
                    print(bone.name, bone.vector)
                    # every bone has HEAD and TAIL
                
                    #loc = bone.vector
                    head_loc = bone.head_local
                    tail_loc = bone.tail_local
                    
                    Verts = [head_loc, tail_loc]
                    Edges = [[0,1]]

                    profile_mesh = bpy.data.meshes.new("Edge_Profile_Data")
                    profile_object = bpy.data.objects.new("Edge_Profile", profile_mesh)
                    profile_object.data = profile_mesh

                    profile_mesh.from_pydata(Verts, Edges, [])
                    profile_mesh.update()
                    bpy.context.collection.objects.link(profile_object)
                    profile_object.select_set(state=True)
                    bpy.context.view_layer.objects.active = profile_object

                    #create duplicate parents wires too in case of offset
                    if bone.parent:
                        head_loc = bone.head_local
                        tail_loc = bone.parent.tail_local

                        Verts = [head_loc, tail_loc]
                        Edges = [[0,1]]

                        profile_mesh = bpy.data.meshes.new("Edge_Profile_Data")
                        profile_object = bpy.data.objects.new("Edge_Profile", profile_mesh)
                        profile_object.data = profile_mesh
                        profile_mesh.from_pydata(Verts, Edges, [])
                        profile_mesh.update()
                        bpy.context.collection.objects.link(profile_object)
                        profile_object.select_set(state=True)
                        bpy.context.view_layer.objects.active = profile_object

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.select_all(action='DESELECT')
                objects = bpy.data.objects
                s = [item for item in objects if "Edge_Profile" in item.name]
                for item in s:
                    item.select_set(state=True)
                    bpy.context.view_layer.objects.active = item
                bpy.ops.object.join()
                wireMesh = bpy.context.object
                wireMesh.name = (armt.name + "_wire")

                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = wireMesh
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles(threshold=0.005)
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                # setup skinning modifier
                skin_mod = wireMesh.modifiers.new(name = 'Skin', type = 'SKIN')                        
                skin_mod.use_smooth_shade = True
                skin_mod.branch_smoothing = 1

                if isMirror:
                    skin_mod.use_x_symmetry = True

                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = wireMesh
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                bpy.ops.mesh.select_all(action='SELECT')
                # bpy.ops.object.skin_loose_mark_clear(action='MARK')
                bpy.ops.transform.skin_resize(value=(1.5, 1.5, 1.5), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='INVERSE_SQUARE', proportional_size=0.101089, use_proportional_connected=False, use_proportional_projected=True)
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


                if isMirror:
                    for mod in [m for m in wireMesh.modifiers if m.type == 'SKIN']:
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.view_layer.objects.active = wireMesh
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), threshold=0.0001, xstart=1339, xend=1341, ystart=776, yend=679)

                    #delete half the mesh -x
                    mesh = bmesh.from_edit_mesh(wireMesh.data)
                    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    for v in mesh.verts:
                        if v.co[0] < 0:
                            v.select = True        
                    bpy.ops.mesh.delete(type='VERT')

                    # setup mirror modifier
                    mirror_mod = wireMesh.modifiers.new(name = 'Mirror', type = 'MIRROR')
                    mirror_mod.use_bisect_axis[0] = True
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                #     for mod in [m for m in wireMesh.modifiers if m.type == 'MIRROR']:
                #         bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

                #setup skeleton
                armt.display_type = 'WIRE'
                obj.show_in_front = True

                # setup skinning
                bpy.ops.object.select_all(action='DESELECT')
                wireMesh.select_set(state=True)
                obj.select_set(state=True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.parent_set(type='ARMATURE_AUTO')

                subd_mod = wireMesh.modifiers.new(name = 'Subdivision', type = 'SUBSURF')                        
                subd_mod.show_on_cage = True

                # # set pose mode
                # bpy.ops.object.select_all(action='DESELECT')
                # obj.select_set(state=True)
                # bpy.context.view_layer.objects.active = obj
                # bpy.ops.object.mode_set(mode='POSE', toggle=False)
                # bpy.ops.pose.select_all(action='SELECT')
                # bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'

                # set edit mode
                bpy.ops.object.select_all(action='DESELECT')
                wireMesh.select_set(state=True)
                bpy.context.view_layer.objects.active = wireMesh
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)




        else :
            self.report({'WARNING'}, 'Armature must be active object')

        return {'FINISHED'}



# Registration



def menu_draw(self, context):
    self.layout.operator(OBJECT_OT_Armature_to_Mesh.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_Armature_to_Mesh)
    bpy.types.VIEW3D_MT_edit_armature.append(menu_draw)  

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_Armature_to_Mesh)
    bpy.types.VIEW3D_MT_edit_armature.remove(menu_draw)  


if __name__ == "__main__":
    register()
