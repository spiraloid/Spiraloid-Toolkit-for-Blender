bl_info = {
        'name': 'SeamToCloth',
        'author': 'Thomas Kole',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'Cloth',
        'location': 'Object > Quick Effects > Quick Cloth from Seams',
        'wiki_url': ''}

import bpy
import bmesh
import mathutils
import math


def main(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')

        obj = bpy.context.edit_object
        me = obj.data

        bpy.ops.mesh.select_mode(type="EDGE")

        # select all seams

        bm = bmesh.from_edit_mesh(me)
        for e in bm.edges:
            if e.seam:
                e.select = True
                
        bpy.ops.mesh.bevel(affect='EDGES', offset=0.001)
        bpy.ops.mesh.delete(type='ONLY_FACE')

        bpy.ops.mesh.select_mode(type="FACE")
        faceGroups = []

        # isolate all face islands, and UV unwrap each island

        faces = set(bm.faces[:])
        while faces:
            bpy.ops.mesh.select_all(action='DESELECT')  
            face = faces.pop() 
            face.select = True
            bpy.ops.mesh.select_linked()
            selected_faces = {f for f in faces if f.select}
            selected_faces.add(face) # this or bm.faces above?
            faceGroups.append(selected_faces)
            faces -= selected_faces
            # bpy.ops.uv.unwrap()    
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.05)

        bpy.ops.mesh.select_all(action='SELECT') 
        bpy.ops.uv.select_all(action='SELECT')
        bmesh.update_edit_mesh(me, False)    



        uv_layer = bm.loops.layers.uv.active
            
        for g in faceGroups:
            previous_area = 0
            bpy.ops.mesh.select_mode(type='FACE')
            bpy.ops.mesh.select_all(action='DESELECT')
            average_position = mathutils.Vector((0,0,0))
            facenum = 0
            average_normal = mathutils.Vector((0,0,0))
            
            # calculate the area, average position, and average normal
            
            for f in g:
                f.select = True
                previous_area += f.calc_area()
                average_position += f.calc_center_median()
                average_normal += f.normal
                facenum += 1
                        
            average_normal.normalize()
            
            average_position /= facenum

            average_tangent = mathutils.Vector((0,0,0))
            average_bitangent = mathutils.Vector((0,0,0))

            # calculate a rough tangent and a bitangent

            for face in g:
                for loop in face.loops:       
                    uv = loop[uv_layer].uv
                    delta = loop.vert.co - average_position
                    average_tangent += delta * (uv.x - 0.5)
                    average_bitangent += delta * (uv.y - 0.5)
                    
            # reorient the tangent and bitangent
            
            average_normal = average_normal.normalized()
            average_tangent = average_tangent.normalized()
            average_bitangent = average_bitangent.normalized()
            halfvector = average_bitangent + average_tangent
            halfvector /= 2
            halfvector.normalize()
            #straighten out half vector
            halfvector = average_normal.cross(halfvector)
            halfvector = average_normal.cross(halfvector)
            cw = mathutils.Matrix.Rotation(math.radians(45.0), 4, average_normal)
            ccw = mathutils.Matrix.Rotation(math.radians(-45.0), 4, average_normal)
            
            average_tangent = mathutils.Vector(halfvector)
            average_tangent.rotate(ccw)
            
            average_bitangent = mathutils.Vector(halfvector)
            average_bitangent.rotate(cw)
            
            # offset each face island by their UV value, using the tangent and bitangent
                
            for face in g:
                for loop in face.loops:       
                    uv = loop[uv_layer].uv
                    vert = loop.vert
                    pos = mathutils.Vector((0,0,0))
                    pos += average_position
                    pos += average_tangent * -(uv.x - 0.5)
                    pos += average_bitangent * -(uv.y - 0.5)
                    pos += average_normal * 0.3 #arbitrary - should probably depend on object scale?
                    vert.co = pos;
            
            bmesh.update_edit_mesh(me, False)
            
            #resize to match previous area
            
            new_area = sum(f.calc_area() for f in g)
            
            area_ratio = previous_area / new_area
            area_ratio = math.sqrt(area_ratio)
            bpy.ops.transform.resize(value=(area_ratio, area_ratio, area_ratio))
            
        # done
            
        bmesh.update_edit_mesh(me, False)
        bpy.ops.mesh.select_all(action='SELECT') 

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        objects = bpy.context.selected_objects
        if objects is not None :
            for obj in objects:
                    cloth_mod = obj.modifiers.new(name = 'Cloth', type = 'CLOTH')
                    cloth_mod.settings.use_pressure = True
                    cloth_mod.settings.uniform_pressure_force = 10
                    cloth_mod.settings.use_sewing_springs = True
                    cloth_mod.settings.sewing_force_max = 5
                    cloth_mod.settings.fluid_density = 0.25
                    cloth_mod.settings.effector_weights.gravity = 0




        return{'FINISHED'}


class BR_OT_seam_to_cloth(bpy.types.Operator):
    """Convert closed mesh seams to cloth """
    bl_idname = "view3d.seam_to_cloth"
    bl_label = "Quick Cloth from Seams"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}


def menu_draw_seam_to_cloth(self, context):
    self.layout.operator(BR_OT_seam_to_cloth.bl_idname)


classes = (
    BR_OT_seam_to_cloth,
)

def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.VIEW3D_MT_object_quick_effects.append(menu_draw_seam_to_cloth)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    bpy.types.VIEW3D_MT_object_quick_effects.remove(menu_draw_seam_to_cloth)

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_object_quick_effects.remove(menu_draw_seam_to_cloth)

if __name__ == "__main__":
    register()

