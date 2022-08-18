bl_info = {
        'name': 'CrotchRig',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 93, 0),
        'category': 'Pose',
        'location': 'Pose > Crotch Rig',
        'wiki_url': ''}

from locale import normalize
from os import name
import bpy
import mathutils
import string
import bmesh
import math
from mathutils import Vector

def get_leaf_bone_names(c_bone_names):
    c_bones = []
    for c in c_bone_names:
        c_bones.append(bpy.context.selected_objects[0].data.bones[c])
    armt = bpy.context.selected_objects[0]
    result = []
    if armt is not None :
        root_bone = armt.data.bones[0]
        for poseBone in root_bone.children_recursive:
            is_hidden = False
            is_not_crotchbone = False
            if poseBone.hide:
                is_hidden = True
            if not is_hidden:
                if not poseBone.children:
                    parent_bone_name = poseBone.parent.name
                    for crotch_bone in c_bones:
                        crotch_bone_name = crotch_bone.name
                        if parent_bone_name != crotch_bone_name:
                            is_not_crotchbone = True
                if is_not_crotchbone:
                    result.append(poseBone.name)
    return result


def get_crotch_bone_names():
    armt = bpy.context.selected_objects[0]
    crotch_bone_names = []
    if armt is not None :
        root_bone = armt.data.bones[0]
        root_bone_name = root_bone.name
        crotch_bone_names.append(root_bone_name)
        for p_bone in root_bone.children_recursive:
            if p_bone.children:
                num_children = len(p_bone.children)
                if num_children >= 2:
                    is_hidden = False
                    for c in p_bone.children:
                        if c.hide:
                            is_hidden = True
                    if not is_hidden:
                        p_bone_name = p_bone.name
                        crotch_bone_names.append(p_bone_name)
    return crotch_bone_names


def get_chain_bones(self, context, armt, crotch_bone, leaf_bones):
    result = []
    if armt is not None :
        for pb in crotch_bone.children:
            result.append(pb)
        for pb in crotch_bone.children_recursive:
            pb_name = pb.name
            for child in pb.children:
                if len(child.children) <= 1:
                    child_name = child.name
                    for lb in leaf_bones:
                        lb_name = lb.name
                        if lb_name != child_name:
                            result.append(child)
                else:
                    break
        return result
    if result:
        # self.report({'INFO'}, 'Found chain bones')
        return result
    else:
        self.report({'ERROR'}, "No chain bones found!")

# def get_crotch_chain_terminators(self, context, armt, crotch_bone, leaf_bones, crotch_bones):
#     result = []
#     if armt is not None :
#         for pb in crotch_bone.children_recursive:
#             for lb in leaf_bones:
#                 lb_name = lb.name
#                 if lb_name == child_name:
#                     result.append(child)



#         return result
#     if result:
#         self.report({'INFO'}, 'Found chain bones')
#         return result
#     else:
#         self.report({'ERROR'}, "No chain bones found!")



# def add_crotch_control_bones(self, context, armt, bones):
#     return result

# def add_leaf_control_bones(self, context, armt, bones):
#     return result

# def add_crotch_constraints(self, context):
#     return {'FINISHED'}

# def add_leaf_constraints(self, context):
#     return {'FINISHED'}


def get_parent_names(bone_name):
    b = bpy.context.selected_objects[0].data.bones[bone_name]
    parent = b.parent
    if parent:
        return [parent.name] + get_parent_names(parent.name)
    else:
        return []


def get_ancestor_crotch_bone_name(bone_name, c_bone_names):
    c_bones = []
    for c in c_bone_names:
        c_bones.append(bpy.context.selected_objects[0].data.bones[c])
    i = 0
    found = False
    ancestors = []
    ancestor_names = get_parent_names(bone_name)
    for bone_name in ancestor_names:
        ancestors.append(bpy.context.selected_objects[0].data.bones[bone_name])
    for ancestor in ancestors:
        ancestor_name = ancestor.name
        if not found:
            i+=1
            for crotch_bone in c_bones:
                crotch_bone_name = crotch_bone.name
                # print("::::::::::::::::")
                # print(crotch_bone_name + " AND " + ancestor_name)
                # print("::::::::::::::::")
                if ancestor_name in crotch_bone_name:
                    found = True
                    return crotch_bone_name


def get_ancestor_crotch_bone_depth(bone_name, crotch_ancestor_name):
    i = 0
    found = False
    ancestors = []
    ancestor_names = get_parent_names(bone_name)
    for bone_name in ancestor_names:
        ancestors.append(bpy.context.selected_objects[0].data.bones[bone_name])
    for ancestor in ancestors:
        ancestor_name = ancestor.name
        if not found:
            i+=1
            if ancestor_name in crotch_ancestor_name:
                found = True
                return i - 1

def get_chain_root_name(bone_name):
    armt = bpy.context.selected_objects[0]
    b = armt.data.bones[bone_name]
    root_bone_name = armt.data.bones[0].name
    # parent_list.append(bone_name)
    if not bone_name in root_bone_name:
        parent_bone = b.parent
        crotch_found = False 
        while parent_bone:
            if not crotch_found:
                if parent_bone.children:
                    num_children = len(parent_bone.children)
                    if not num_children <= 1:
                        crotch_bone_name = parent_bone.name
                        crotch_found = True
                        if crotch_bone_name:
                            return crotch_bone_name
                    parent_bone = parent_bone.parent
    else:
        return root_bone_name

def check_string(string, substring_list):
    for substring in substring_list:
        if substring in string:
            return True
    return False


def getClosestAxis(n):
    if abs(n.x) > abs(n.y):
        if abs(n.x) > abs(n.z):
            return mathutils.Vector((1, 0, 0))
        else:
            return mathutils.Vector((0, 0, 1))
    else:
        if abs(n.y) > abs(n.z):
            return mathutils.Vector((0, 1, 0))
        else:
            return mathutils.Vector((0, 0, 1))

def getNormal(p1, p2, p3):
    v1 = p2 - p1
    v2 = p3 - p1
    return v1.cross(v2).normalized()

def getTriDir(p1, vn, p3):
    v1 = p3 - p1
    v2 = v1 - vn
    return v2.normalized()


def lock_unbent_axis(locked_bone, plane_bone1, plane_bone2, plane_bone3):
    #get the bone names
    armt = bpy.context.selected_objects[0]

    locked_bone_name = locked_bone.name
    bone1_name = plane_bone1.name
    bone2_name = plane_bone2.name
    bone3_name = plane_bone3.name

    #get the bone locations
    loc1 = armt.pose.bones[bone1_name].matrix.translation
    loc2 = armt.pose.bones[bone2_name].matrix.translation
    loc3 = armt.pose.bones[bone3_name].matrix.translation


    n = getNormal(loc1, loc2, loc3)
    vec = getClosestAxis(n)
    max_index = 0
    max_value = vec[0]
    for i in range(1, len(vec)):
        if vec[i] > max_value:
            max_value = vec[i]
            max_index = i
    if max_index == 0:
        armt.pose.bones[locked_bone_name].lock_ik_x = False
        armt.pose.bones[locked_bone_name].lock_ik_y = True
        armt.pose.bones[locked_bone_name].lock_ik_z = True
    if max_index == 1:
        armt.pose.bones[locked_bone_name].lock_ik_x = True
        armt.pose.bones[locked_bone_name].lock_ik_y = False
        armt.pose.bones[locked_bone_name].lock_ik_z = True
    if max_index == 2:
        armt.pose.bones[locked_bone_name].lock_ik_x = True
        armt.pose.bones[locked_bone_name].lock_ik_y = True
        armt.pose.bones[locked_bone_name].lock_ik_z = False
    # return {'FINISHED'}

def get_pole_dir(plane_bone1, plane_bone2, plane_bone3):
    armt = bpy.context.selected_objects[0]
    bone1_name = plane_bone1.name
    bone2_name = plane_bone2.name
    bone3_name = plane_bone3.name

    #get the bone locations
    loc1 = armt.pose.bones[bone1_name].matrix.translation
    loc2 = armt.pose.bones[bone2_name].matrix.translation
    loc3 = armt.pose.bones[bone3_name].matrix.translation


    n = getTriDir(loc1, loc2, loc3)
    vec = getClosestAxis(n)
    return mathutils.Vector((vec))


def add_chain_constraints(crotch_bone_names, l_bone_names):
    armt = bpy.context.selected_objects[0]
    banned_strings = ['head', 'hand', 'foot']
    limb_strings = ['calf', 'lowerleg', 'foot', 'hand', 'wrist', 'heel', 'ankle', 'paw']
    toe_strings = ['toe']

    for cb in crotch_bone_names:
        l_bone_names.append(armt.data.bones[cb].name)

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.select_all(action='DESELECT')
    armt.select_set(state=True)
    bpy.context.view_layer.objects.active = armt
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    if armt is not None :
        rigged_bones = []
        root_bone = armt.data.bones[0]
        root_bone_name = root_bone.name
        root_pose_bone = armt.pose.bones[root_bone_name]

        control_bone_name = "CTRL_" + root_bone_name
        bpy.ops.pose.select_all(action='DESELECT')
        root_pose_bone.bone.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.bone_primitive_add(name=control_bone_name)
        bone_e = armt.data.edit_bones[root_bone_name]
        c_bone = armt.data.edit_bones[control_bone_name]
        c_bone.head = bone_e.head
        c_bone.tail = bone_e.tail
        c_bone.roll = bone_e.roll
        c_bone.head_radius = bone_e.head_radius
        c_bone.tail_radius = bone_e.tail_radius
        c_bone.envelope_distance = bone_e.envelope_distance

        c_bone.envelope = bone_e.envelope
        c_bone.envelope = bone_e.envelope
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        constraint = root_pose_bone.constraints.new('COPY_TRANSFORMS')
        constraint.target = armt
        constraint.subtarget = control_bone_name

        for l_bone_name in l_bone_names:
            is_riggable = True
            if is_riggable:
                if not l_bone_name in rigged_bones:
                    current_crotch_name = get_chain_root_name(l_bone_name)
                    formatted_current_crotch_name = current_crotch_name.lower()


                    if not check_string(formatted_current_crotch_name, banned_strings):
                        if l_bone_name != current_crotch_name:
                            is_riggable = False
                            print("::::::::::::::::")
                            print("going to create an IK chain from " + current_crotch_name + " to " + l_bone_name)
                            print("::::::::::::::::")
                            terminator_bone = armt.pose.bones[l_bone_name]
                            # terminator_bone = armt.data.bones[l_bone_name]
                            terminator_bone_name = l_bone_name
                            formatted_terminator_bone_name = terminator_bone_name.lower()
                            pole_vector_control_bone_name = ""

                            if check_string(formatted_terminator_bone_name, limb_strings):
                                parent_bone = terminator_bone.parent
                                parent_bone_name = parent_bone.name
                                c_bone_child = terminator_bone.children[0]
                                if c_bone_child and parent_bone:  
                                    lock_unbent_axis(terminator_bone, parent_bone, terminator_bone, c_bone_child)
                                    pole_vector_control_bone_name = "CTRL_PV_" + terminator_bone_name
                            if check_string(formatted_terminator_bone_name, toe_strings):
                                terminator_bone = terminator_bone.parent
                                terminator_bone_name = terminator_bone.name

                            control_bone_name = "CTRL_" + terminator_bone_name
                            bpy.ops.pose.select_all(action='DESELECT')
                            terminator_bone.bone.select = True
                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.armature.bone_primitive_add(name=control_bone_name)
                            bone_e = armt.data.edit_bones[terminator_bone_name]
                            c_bone = armt.data.edit_bones[control_bone_name]
                            c_bone.head = bone_e.head
                            c_bone.tail = bone_e.tail
                            c_bone.roll = bone_e.roll

                            if pole_vector_control_bone_name:
                                    pole_position  = get_pole_dir(parent_bone, terminator_bone, c_bone_child)
                                    bpy.ops.object.mode_set(mode='POSE')
                                    bpy.ops.pose.select_all(action='DESELECT')
                                    parent_bone.bone.select = True
                                    bpy.ops.object.mode_set(mode='EDIT')
                                    bpy.ops.armature.bone_primitive_add(name=pole_vector_control_bone_name)
                                    bone_e = armt.data.edit_bones[parent_bone_name]
                                    c_bone = armt.data.edit_bones[pole_vector_control_bone_name]
                                    c_bone.head = bone_e.head
                                    c_bone.roll = bone_e.roll
                                    c_bone.tail = bone_e.matrix.translation + pole_position


                            # #add a constraint to bone
                            bpy.ops.object.mode_set(mode='POSE')
                            bpy.ops.pose.select_all(action='DESELECT')
                            # bpy.context.object.data.bones.active = terminator_bone
                            terminator_bone.bone.select = True

                            # raise KeyboardInterrupt()
                            # bpy.ops.pose.constraint_add(type='IK')
                            # constraint = bpy.context.object.pose.bones[terminator_bone_name].constraints["IK"]
                            constraint = terminator_bone.constraints.new('IK')
                            constraint.target = armt
                            constraint.subtarget = control_bone_name
                            if pole_vector_control_bone_name:  
                                constraint.pole_target = armt
                                constraint.pole_subtarget = pole_vector_control_bone_name  

                            # print("::::::::::::::::")
                            # print(terminator_bone_name)
                            # print("::::::::::::::::")                

                            # print("::::::::::::::::")
                            # print(crotch_ancestor_name)
                            # print("::::::::::::::::")
                            ik_chain_count = get_ancestor_crotch_bone_depth(terminator_bone_name, current_crotch_name)
                            constraint.chain_count = ik_chain_count
                            constraint.use_tail = False
                            constraint = terminator_bone.constraints.new('COPY_TRANSFORMS')
                            constraint.target = armt
                            constraint.subtarget = control_bone_name
                            rigged_bones.append(terminator_bone_name)


        return {'FINISHED'}


# def add_chain_constraints(self, context, armt, crotch_bone_names, l_bone_names):
#     l_bones = []
#     for lb in l_bone_names:
#         l_bones.append(bpy.context.selected_objects[0].data.bones[lb])
#     c_bones = []
#     for cb in crotch_bone_names:
#         c_bones.append(bpy.context.selected_objects[0].data.bones[cb])
#     bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
#     bpy.ops.object.select_all(action='DESELECT')
#     armt.select_set(state=True)
#     bpy.context.view_layer.objects.active = armt
#     bpy.ops.object.mode_set(mode='POSE', toggle=False)
#     if armt is not None :
#         rigged_bones = []
#         root_bone = armt.data.bones[0]
#         current_crotch = root_bone
#         current_crotch_name = current_crotch.name
#         immidiate_children = root_bone.children

#         for main_branch_bone in immidiate_children:
#             terminator_bone = ""
#             is_riggable = True
#             all_branch_children = main_branch_bone.children_recursive
#             for c_bone in all_branch_children:
#                 query_bone = ""
#                 found_terminator = False
#                 c_bone_name = c_bone.name

#                 if not found_terminator:
#                     for cb in c_bones:
#                         cb_name = cb.name
#                         if cb_name in c_bone_name:
#                             query_bone = c_bone
#                             found_terminator = True
#                             crotch_terminator =True

#                 if not found_terminator:
#                     for leaf_bone in l_bones:
#                         leaf_bone_name = leaf_bone.name 
#                         if leaf_bone_name in c_bone_name:
#                             query_bone = c_bone
#                             found_terminator = True

#                 if found_terminator:
#                     if "Calf" in c_bone_name or "calf" in c_bone_name or "lowerLeg" in c_bone_name or "lowerleg" in c_bone_name :
#                         parent_bone = c_bone.parent
#                         c_bone_child = c_bone.children[0]
#                         if c_bone_child and parent_bone:  
#                             lock_unbent_axis(armt, c_bone, parent_bone, c_bone, c_bone_child)
#                     if query_bone:
#                         query_bone_name = query_bone.name

#                         # if crotch_terminator:
#                         #     current_branch_children = query_bone.children_recursive
#                         #     current_crotch_name = get_ancestor_crotch_bone_name(terminator_bone_name, crotch_bone_names)

#                         for rb in rigged_bones:
#                             rb_name = rb.name
#                             if rb_name in query_bone_name:
#                                 is_riggable = False
#                         if is_riggable:
#                             if "toe" in query_bone_name or "Toe" in query_bone_name:
#                                 terminator_bone = query_bone.parent
#                             else:
#                                 terminator_bone = query_bone

#                             if terminator_bone:
#                                 terminator_bone_name = terminator_bone.name
#                                 control_bone_name = "CTRL_" + terminator_bone_name
#                                 print("::::::::::::::::")
#                                 print("going to createn IK chain from " + current_crotch_name + " to " + terminator_bone_name)
#                                 print("::::::::::::::::")


#                                 bpy.ops.pose.select_all(action='DESELECT')
#                                 terminator_bone.select = True
#                                 bpy.ops.object.mode_set(mode='EDIT')
#                                 bpy.ops.armature.bone_primitive_add(name=control_bone_name)
#                                 bone_e = armt.data.edit_bones[terminator_bone_name]
#                                 c_bone = armt.data.edit_bones[control_bone_name]
#                                 c_bone.head = bone_e.head
#                                 c_bone.tail = bone_e.tail
#                                 c_bone.roll = bone_e.roll

#                                 # #add a constraint to bone
#                                 bpy.ops.object.mode_set(mode='POSE')
#                                 bpy.ops.pose.select_all(action='DESELECT')
#                                 terminator_bone.select = True


#                                 # raise KeyboardInterrupt()

#                                 constraint = terminator_bone.constraints.new('IK')
#                                 constraint.target = armt
#                                 constraint.subtarget = control_bone_name  
#                                 # print("::::::::::::::::")
#                                 # print(terminator_bone_name)
#                                 # print("::::::::::::::::")                

#                                 # print("::::::::::::::::")
#                                 # print(crotch_ancestor_name)
#                                 # print("::::::::::::::::")
#                                 ik_chain_count = get_ancestor_crotch_bone_depth(terminator_bone_name, current_crotch_name)
#                                 constraint.chain_count = ik_chain_count
#                                 constraint.use_tail = False
#                                 constraint = terminator_bone.constraints.new('COPY_TRANSFORMS')
#                                 constraint.target = armt
#                                 constraint.subtarget = control_bone_name
#                                 rigged_bones.append(query_bone)

#         return {'FINISHED'}

class BR_OT_generate_twist_bones(bpy.types.Operator):
    """Create an driven twist bone foreach of the selected bones"""
    bl_idname = "view3d.generate_twist_bones"
    bl_label = "Insert Twist Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objects = bpy.context.selected_objects
        starting_mode = bpy.context.object.mode
        if objects is not None :
            for obj in objects:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(state=True)
                bpy.context.view_layer.objects.active = obj
                
                if "POSE" in starting_mode:
                    bpy.ops.object.mode_set(mode='POSE')
                    armature = obj
                    is_mirror = armature.pose.use_mirror_x
                    bpy.context.object.pose.use_mirror_x = False
                    bpy.context.object.use_mesh_mirror_x = False
                    
                    selected_bones = bpy.context.selected_pose_bones
                    if selected_bones:
                        bones_to_process = []
                        for selected_bone in selected_bones:
                            selected_bone_name = selected_bone.name
                            helper_bone_name = "TWST_" + selected_bone_name
                            for bone in armature.pose.bones:
                                if helper_bone_name in bone.name:
                                    self.report({'Error'}, "Helper bone already exists")

                        pose_bones_to_process = [selected_bone]
                        if is_mirror:
                            if selected_bone_name.endswith("_L"):
                                bone_base_name = selected_bone_name.replace("_L", "")
                                for bone in armature.pose.bones:
                                    if bone.name.startswith(bone_base_name) and bone.name.endswith("_R"):
                                        pose_bones_to_process.append(bone)
                            
                            if selected_bone_name.endswith("_R"):
                                bone_base_name = selected_bone_name.replace("_R", "")
                                for bone in armature.pose.bones:
                                    if bone.name.startswith(bone_base_name) and bone.name.endswith("_L"):
                                        pose_bones_to_process.append(bone)

                        for current_pose_bone in pose_bones_to_process:
                            current_pose_bone_name = current_pose_bone.name

                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.armature.select_all(action='DESELECT')
                            current_edit_bone = armature.data.bones[current_pose_bone_name]
                            first_child_bone = ""
                            first_child_bone_name = ""
                            if current_edit_bone.children:
                                first_child_bone = current_edit_bone.children[0]
                                if first_child_bone:
                                    first_child_bone_name = first_child_bone.name
                                    
                            else:
                                self.report({'ERROR'}, 'Active bone has no child bones found!') 

                            parent_bone = current_edit_bone.parent
                            parent_bone_name = parent_bone.name

                            helper_bone_name = "TWST_" + current_pose_bone_name

                            c_bone = armature.data.bones[current_pose_bone_name]
                            armature.data.bones.active = c_bone
                            
                            # bpy.ops.pose.select_all(action='DESELECT')
                            c_bone.select = True
                            bpy.ops.object.mode_set(mode='EDIT')
                            # bpy.ops.armature.select_all(action='DESELECT')
                            current_edit_bone = armature.data.edit_bones[current_pose_bone_name]
                            parent_bone = c_bone.parent
                            parent_bone_name = parent_bone.name
                            # armature.data.bones.active = armature.data.edit_bones[current_pose_bone_name]
                            bpy.ops.armature.bone_primitive_add(name=helper_bone_name)
                            helper_edit_bone = armature.data.edit_bones[helper_bone_name]
                            # helper_bone = armature.data.bones[helper_bone_name]
                            helper_edit_bone.head = current_edit_bone.head
                            helper_edit_bone.tail = current_edit_bone.tail
                            helper_edit_bone.roll = current_edit_bone.roll
                            helper_edit_bone.head_radius = current_edit_bone.head_radius
                            helper_edit_bone.tail_radius = current_edit_bone.tail_radius
                            helper_edit_bone.envelope_distance = current_edit_bone.envelope_distance
                            helper_edit_bone.parent = current_edit_bone



                            # create the helper bone constraint
                            bpy.ops.object.mode_set(mode='POSE')
                            h_pose_bone = obj.pose.bones[helper_bone_name]
                            h_bone = obj.data.bones[helper_bone_name]
                            bpy.context.object.data.bones.active = h_bone
                            constraint = h_pose_bone.constraints.new('COPY_ROTATION')
                            constraint.target = obj
                            constraint.subtarget = first_child_bone_name
                            constraint.influence = 0.5
                            constraint.use_x = False
                            constraint.use_y = True
                            constraint.use_z = False
                            constraint.target_space = 'LOCAL'
                            constraint.owner_space = 'LOCAL'
                            h_bone.hide = True
                            h_pose_bone.rotation_mode = 'XYZ'
                            h_pose_bone.lock_rotation[0] = True
                            h_pose_bone.lock_rotation[2] = True

                            # create helper bone skin groups.
                            ch = []
                            for laob in bpy.data.objects:
                                if laob.type == "MESH" or laob.type == "CURVE":
                                    # print (">>>>>>>>>>> >>>>>> >>>>>" + laob.modifiers[0].name)
                                    for mod in laob.modifiers:
                                        if mod.type == "ARMATURE":
                                            if mod.object == armature:
                                                ch.append(laob)

                            for mesh in ch:
                                bpy.ops.object.mode_set(mode='OBJECT')
                                bpy.ops.object.select_all(action='DESELECT')
                                mesh.select_set(state=True)
                                bpy.context.view_layer.objects.active = mesh
                                
                                bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                                bpy.context.object.data.use_paint_mask = False
                                bpy.context.object.data.use_paint_mask_vertex = True
                                bpy.context.object.vertex_groups.active = mesh.vertex_groups[current_pose_bone_name]
                                current_bone_vertex_group = mesh.vertex_groups[current_pose_bone_name]
                                bpy.ops.paint.vert_select_all(action='DESELECT')
                                bpy.ops.object.vertex_group_select()

                                # bpy.ops.object.vertex_group_copy()
                                # helper_bone_vertex_group = mesh.vertex_groups.active
                                # helper_bone_vertex_group.name = helper_bone_name


                                mesh.vertex_groups.new(name=helper_bone_name)
                                helper_bone_vertex_group = bpy.context.object.vertex_groups.active

                                # raise KeyboardInterrupt()

                                # falloff the bone weight by distance
                                # distance = current_edit_bone.envelope_distance + current_edit_bone.head_radius

                                bone_e = armature.data.bones[helper_bone_name]
                                omx = mesh.matrix_world
                                bone_pos = armature.data.bones[helper_bone_name].matrix_local.to_translation()
                                bone_length = bone_e.length


                                # bpy.ops.object.mode_set(mode='EDIT')
                                # bpy.ops.mesh.select_all(action='DESELECT')
                                # bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[helper_bone_name]
                                # # bpy.ops.object.vertex_group_select()
                                # # bpy.ops.mesh.select_all(action='INVERT')

                                # bone = armature.data.bones[helper_bone_name]
                                # midpoint = (bone.head + bone.tail) / 2
                                # # print(">>>>>>>>>>>>>>> " + str(midpoint))
                                
                                # bpy.ops.object.mode_set(mode='WEIGHT_PAINT')


                                # for vert in mesh.data.vertices:
                                distance = 0.0
                                vertex_group_verts = [v for v in mesh.data.vertices if v.select and current_bone_vertex_group.index in [vg.group for vg in v.groups]]
                                for vert in vertex_group_verts:
                                # for vert in mesh.data.vertices:
                                    vert_pos = omx @ vert.co
                                    # print(">>>>>>>>>>>>>>>" + str(vert_pos))
                                    # print(">>>>>>>>>>>>>>>" + str(bone_pos))
                                    distance = math.dist(vert_pos, bone_pos)
                                    value = 1.0 - (distance / bone_length)
                                    region_of_effect =  bone_length

                                    if distance >= region_of_effect:
                                        helper_bone_vertex_group.add([vert.index], 0.0, 'REPLACE')
                                    else:
                                        helper_bone_vertex_group.add([vert.index], value, 'REPLACE')



                                # for vert in mesh.data.vertices:
                                #     region_of_effect = (vert.co - midpoint) 
                                #     # if region_of_effect >= distance:
                                #         # helper_bone_vertex_group.remove([vert.index])
                                #     if distance >= region_of_effect:
                                #         helper_bone_vertex_group.add([vert.index], 0.0, 'REPLACE')

                                bpy.ops.object.vertex_group_clean(group_select_mode='ACTIVE', limit=0.25)


                                bpy.ops.object.vertex_group_normalize()
                                # bpy.ops.object.vertex_group_invert()
                                bpy.ops.object.vertex_group_smooth(repeat=3, expand=-0.5)
                                bpy.ops.object.vertex_group_normalize()
                                # bpy.ops.object.vertex_group_levels(offset=0.75, gain=0.66)
                                # bpy.ops.object.vertex_group_smooth(factor=1, expand=-0.75)
                                # bpy.ops.object.vertex_group_levels(offset=1, gain=0.5)





                                # bpy.ops.object.mode_set(mode='EDIT')
                                # bpy.ops.mesh.select_all(action='DESELECT')
                                # bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[first_child_bone_name]
                                # bpy.ops.object.vertex_group_select()
                                # bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[helper_bone_name]
                                # bpy.ops.object.vertex_group_remove_from(use_all_groups=False, use_all_verts=False)
                                # # bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[parent_bone_name]
                                # # bpy.ops.object.vertex_group_remove_from(use_all_groups=False, use_all_verts=False)

                                # bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                                # bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[helper_bone_name]
                                # bpy.ops.object.vertex_group_clean(group_select_mode='ACTIVE', limit=0.25)


                                bpy.ops.object.mode_set(mode='OBJECT')
                                # helper_bone.hide = True

                            bpy.ops.object.mode_set(mode='OBJECT')
                            bpy.ops.object.select_all(action='DESELECT')
                            armature.select_set(state=True)
                            bpy.context.view_layer.objects.active = armature

                        # reselect bones at the start
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')
                        for current_bone in selected_bones:
                            current_bone.bone.select = True
                            bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[helper_bone_name].bone
                        if is_mirror:
                            armature.pose.use_mirror_x = True
                    else:
                        self.report({'ERROR'}, "No bone selected!")
        else:
            self.report({'ERROR'}, "you must select a bone in pose mode")

        self.report({'INFO'}, 'Twist Bones Inserted!')
        return {'FINISHED'}

class BR_OT_generate_helper_bones(bpy.types.Operator):
    """Create an driven helper bone foreach of the selected object"""
    bl_idname = "view3d.generate_helper_bones"
    bl_label = "Insert Helper Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objects = bpy.context.selected_objects
        starting_mode = bpy.context.object.mode
        if objects is not None :
            for obj in objects:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(state=True)
                bpy.context.view_layer.objects.active = obj
                if "POSE" in starting_mode:
                    bpy.ops.object.mode_set(mode='POSE')
                    armature = obj
                    is_mirror = armature.pose.use_mirror_x
                    bpy.context.object.pose.use_mirror_x = False
                    bpy.context.object.use_mesh_mirror_x = False
                    selected_bones = bpy.context.selected_pose_bones
                    if selected_bones:
                        bones_to_process = []
                        for selected_bone in selected_bones:
                            selected_bone_name = selected_bone.name
                            helper_bone_name = "HLP_" + selected_bone_name

                            for bone in armature.pose.bones:
                                if helper_bone_name in bone.name:
                                    self.report({'Error'}, "Helper bone already exists")

                            pose_bones_to_process = [selected_bone]
                            if is_mirror:
                                if selected_bone_name.endswith("_L"):
                                    bone_base_name = selected_bone_name.replace("_L", "")
                                    for bone in armature.pose.bones:
                                        if bone.name.startswith(bone_base_name) and bone.name.endswith("_R"):
                                            pose_bones_to_process.append(bone)

                                if selected_bone_name.endswith("_R"):
                                    bone_base_name = selected_bone_name.replace("_R", "")
                                    for bone in armature.pose.bones:
                                        if bone.name.startswith(bone_base_name) and bone.name.endswith("_L"):
                                            pose_bones_to_process.append(bone)

                            for current_pose_bone in pose_bones_to_process:
                                current_pose_bone_name = current_pose_bone.name
                                helper_bone_name = "HLP_" + current_pose_bone_name

                                c_bone = armature.data.bones[current_pose_bone_name]
                                armature.data.bones.active = c_bone
                                
                                # bpy.ops.pose.select_all(action='DESELECT')
                                c_bone.select = True
                                bpy.ops.object.mode_set(mode='EDIT')
                                # bpy.ops.armature.select_all(action='DESELECT')
                                current_edit_bone = armature.data.edit_bones[current_pose_bone_name]
                                parent_bone = c_bone.parent
                                parent_bone_name = parent_bone.name
                                # armature.data.bones.active = armature.data.edit_bones[current_pose_bone_name]
                                bpy.ops.armature.bone_primitive_add(name=helper_bone_name)
                                helper_edit_bone = armature.data.edit_bones[helper_bone_name]
                                # helper_bone = armature.data.bones[helper_bone_name]
                                helper_edit_bone.head = current_edit_bone.head
                                helper_edit_bone.tail = current_edit_bone.tail
                                helper_edit_bone.roll = current_edit_bone.roll
                                helper_edit_bone.head_radius = current_edit_bone.head_radius
                                helper_edit_bone.tail_radius = current_edit_bone.tail_radius
                                helper_edit_bone.envelope_distance = current_edit_bone.envelope_distance
                                helper_edit_bone.parent = current_edit_bone.parent


                                # bpy.ops.armature.select_all(action='DESELECT')
                                # helper_edit_bone.select = True
                                # armature.data.bones.active = helper_bone

                                # # parent the new helper bone to the current bone's parent
                                # bpy.ops.object.mode_set(mode='POSE')
                                # bpy.ops.pose.select_all(action='DESELECT')
                                # parent_bone.select = True
                                # bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[parent_bone_name].bone
                                # bpy.ops.object.mode_set(mode='EDIT')
                                # armature.data.bones.active = helper_bone
                                # armature.data.edit_bones[helper_bone_name].select = True
                                # armature.data.edit_bones[parent_bone_name].select = True
                                # bpy.ops.armature.parent_set(type='OFFSET')

                                # raise KeyboardInterrupt()

                                # armature.data.bones.active = armature.data.bones[helper_bone_name]


                                bpy.ops.armature.select_all(action='DESELECT')
                                bpy.ops.object.mode_set(mode='POSE')

                                # create the helper bone constraint
                                h_pose_bone = armature.pose.bones[helper_bone_name]
                                h_bone = armature.data.bones[helper_bone_name]
                                bpy.context.object.data.bones.active = h_bone
                                constraint = h_pose_bone.constraints.new('COPY_ROTATION')
                                constraint.target = armature
                                constraint.subtarget = current_pose_bone_name
                                constraint.target_space = 'WORLD'
                                constraint.owner_space = 'WORLD'
                                constraint.influence = 0.5
                                # bpy.context.active_bone.hide = True
                                h_bone.hide = True


                                # create helper bone skin groups.
                                ch = []
                                for laob in bpy.data.objects:
                                    if laob.type == "MESH" or laob.type == "CURVE":
                                        print (">>>>>>>>>>> >>>>>> >>>>>" + laob.modifiers[0].name)
                                        for mod in laob.modifiers:
                                            if mod.type == "ARMATURE":
                                                if mod.object == armature:
                                                    ch.append(laob)
                                # for mesh in ch:
                                #     bpy.ops.object.mode_set(mode='OBJECT')
                                #     bpy.ops.object.select_all(action='DESELECT')
                                #     mesh.select_set(state=True)
                                #     bpy.context.view_layer.objects.active = mesh
                                #     vertices = []
                                #     mesh.vertex_groups.new(name=helper_bone_name)
                                #     distance = c_bone.envelope_distance + c_bone.head_radius
                                #     bone_location = armature.pose.bones[helper_bone_name].matrix_basis.translation
                                #     for vert in mesh.data.vertices:
                                #         if (vert.co - bone_location).length <= distance:
                                #             vertices.append(vert)
                                #     for vert in vertices:
                                #         for group in mesh.vertex_groups:
                                #             if group.name == helper_bone_name:
                                #                 group.add([vert.index], 1.0, 'REPLACE')

                                #     bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                                #     bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=1.0, repeat=1, expand=0)
                                #     bpy.ops.object.mode_set(mode='OBJECT')

                                for mesh in ch:
                                    bpy.ops.object.mode_set(mode='OBJECT')
                                    bpy.ops.object.select_all(action='DESELECT')
                                    mesh.select_set(state=True)
                                    bpy.context.view_layer.objects.active = mesh
                                    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                                    bpy.context.object.data.use_paint_mask_vertex = False
                                    bpy.context.object.data.use_paint_mask = False
                                    mesh.vertex_groups.new(name=helper_bone_name)
                                    helper_bone_vertex_group = bpy.context.object.vertex_groups.active

                                    # falloff the bone weight by distance

                                    bone_e = armature.data.bones[helper_bone_name]
                                    omx = mesh.matrix_world
                                    bone_pos = armature.data.bones[helper_bone_name].matrix_local.to_translation()
                                    bone_length = bone_e.length
                                    for vert in mesh.data.vertices:
                                    # vertex_group_verts = [v for v in mesh.data.vertices if v.select and helper_bone_vertex_group.index in [vg.group for vg in v.groups]]
                                    # for vert in vertex_group_verts:
                                        vert_pos = omx @ vert.co
                                        # print(">>>>>>>>>>>>>>>" + str(vert_pos))
                                        # print(">>>>>>>>>>>>>>>" + str(bone_pos))
                                        distance = math.dist(vert_pos, bone_pos)
                                        value = 1.0 - (distance / bone_length)
                                        helper_bone_vertex_group.add([vert.index], 1.0, 'REPLACE')

                                        region_of_effect = bone_length / 4
                                        if distance >= region_of_effect:
                                            # helper_bone_vertex_group.remove([vert.index])
                                            helper_bone_vertex_group.add([vert.index], 0.0, 'REPLACE')
                                    bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[helper_bone_name]
                                    # bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', factor=1, repeat=1, expand=0)
                                    # bpy.ops.object.vertex_group_levels(offset=-0.25, gain=1.0)
                                    # bpy.ops.object.vertex_group_normalize()
                                    # bpy.ops.object.vertex_group_smooth(repeat=3, expand=-0.5)
                                    # bpy.ops.object.vertex_group_normalize()
                                    # bpy.ops.object.vertex_group_clean(group_select_mode='ACTIVE', limit=0.25)
                                    # bpy.ops.object.vertex_group_levels(offset=0.75, gain=0.66)
                                    # bpy.ops.object.vertex_group_smooth(factor=1, expand=-0.75)
                                    # bpy.ops.object.vertex_group_levels(offset=1, gain=0.5)
                                    bpy.ops.object.vertex_group_clean(group_select_mode='ACTIVE', limit=0.25)


                                    bpy.ops.object.mode_set(mode='EDIT')
                                    bpy.ops.mesh.select_all(action='DESELECT')
                                    bpy.ops.object.vertex_group_select()
                                    bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[current_pose_bone_name]
                                    bpy.ops.object.vertex_group_remove_from(use_all_groups=False, use_all_verts=False)
                                    bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[parent_bone_name]
                                    bpy.ops.object.vertex_group_remove_from(use_all_groups=False, use_all_verts=False)

                                    bpy.ops.mesh.select_all(action='DESELECT')

                                    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                                    bpy.context.object.vertex_groups.active = bpy.context.object.vertex_groups[helper_bone_name]
                                    bpy.context.object.data.use_paint_mask_vertex = True
                                    bpy.ops.object.vertex_group_select()
                                    vertex_group_verts = [v for v in mesh.data.vertices if v.select and helper_bone_vertex_group.index in [vg.group for vg in v.groups]]
                                    for vert in vertex_group_verts:
                                        mesh.vertex_groups[current_pose_bone_name].add([vert.index], 0.5, 'REPLACE')

                                    bpy.ops.object.mode_set(mode='OBJECT')

                                    
                                bpy.ops.object.mode_set(mode='OBJECT')
                                bpy.ops.object.select_all(action='DESELECT')
                                armature.select_set(state=True)
                                bpy.context.view_layer.objects.active = armature
                        
                        # reselect bones at the start
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')
                        for current_bone in selected_bones:
                            current_bone.bone.select = True
                            bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[helper_bone_name].bone
                        if is_mirror:
                            armature.pose.use_mirror_x = True
                else:
                    self.report({'error'}, "No bone selected!")
        else:
            self.report({'INFO'}, "you must select a bone in pose mode")
        self.report({'INFO'}, 'Helper Bones Inserted!')
        return {'FINISHED'}

class BR_OT_detach_crotch_rig(bpy.types.Operator):
    """Remove IK rig and bake existing rig motion to bones"""
    bl_idname = "view3d.detach_crotch_rig"
    bl_label = "Detach Crotch Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        collection_objects = bpy.context.selected_objects
        return {'FINISHED'}


class BR_OT_attach_crotch_rig(bpy.types.Operator):
    """Create an IK rig controls foreach crotch and leaf bones and then bake existing bone motion to rig controls"""
    bl_idname = "view3d.attach_crotch_rig"
    bl_label = "Attach Crotch Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # global chain_bones
        collection_objects = bpy.context.selected_objects
        for obj in collection_objects:
            obj_type = obj.type
            if obj_type == 'ARMATURE':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.pose.select_all(action='TOGGLE')
                for poseBone in obj.pose.bones:
                    poseBone.bone.select = True
                selected_bones = bpy.context.selected_pose_bones
                bpy.context.object.pose.use_mirror_x = False

                # bpy.ops.object.select_all(action='DESELECT')
                # obj.select_set(state=True)
                # bpy.context.view_layer.objects.active = obj
                crotch_bone_names = get_crotch_bone_names()
                # print("::::::::::::::::")
                # print(crotch_bone_names)
                # print("::::::::::::::::")
                leaf_bone_names = get_leaf_bone_names(crotch_bone_names)
                # print("::::::::::::::::")
                # print(leaf_bone_names)
                # print("::::::::::::::::")
                # crotch_controls = add_crotch_control_bones(self, context, obj, crotch_bones)
                # leaf_controls = add_leaf_control_bones(self, context, obj, leaf_bones)

                # for leaf_control in leaf_controls:
                #     add_leaf_constraints(self, context, obj, leaf_control)
                # for crotch_control in crotch_controls:
                #     add_crotch_constraints(self, context, obj, crotch_control)
                # chain_bones = add_chain_constraints(self, context, obj, crotch_bones, leaf_bones)

                add_chain_constraints(crotch_bone_names, leaf_bone_names)

                for poseBone in selected_bones:
                    # poseBone_name = poseBone.name
                    # bpy.context.object.data.bones[poseBone_name].hide = True
                    bpy.ops.pose.select_all(action='DESELECT')
                    poseBone.bone.select = True
                    bpy.ops.pose.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                    bpy.context.object.data.layers[1] = False
                    bpy.context.object.data.layers[0] = True
                    


                # bpy.ops.pose.select_all(action='DESELECT')
                # for b in leaf_bones:
                #     b_name = b.name
                #     obj.data.bones[b_name].select = True
                    
                # for b in crotch_bones:
                #     b_name = b.name
                #     obj.data.bones[b_name].select = True

                # for b in chain_bones:
                #     b_name = b.name
                #     obj.data.bones[b_name].select = True

        return {'FINISHED'}

# -------------------------

class BR_MT_quick_rig_menu(bpy.types.Menu):
    bl_idname = 'BR_MT_quick_rig_menu'
    bl_label = 'Rig Utilities'
    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.attach_crotch_rig")
        layout.operator("view3d.detach_crotch_rig")
        layout.operator("view3d.generate_helper_bones")
        layout.operator("view3d.generate_twist_bones")


def menu_draw(self, context):
    layout = self.layout
    layout.menu(BR_MT_quick_rig_menu.bl_idname)

# -----------------------

classes = (
    BR_OT_attach_crotch_rig,
    BR_OT_detach_crotch_rig,
    BR_OT_generate_helper_bones,
    BR_OT_generate_twist_bones,
    BR_MT_quick_rig_menu,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_pose.prepend(menu_draw)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_pose.remove(menu_draw)

if __name__ == "__main__":
    register()
