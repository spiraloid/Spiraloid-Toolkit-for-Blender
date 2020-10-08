bl_info = {
    "name": "Add Camera to View",
    "author": "SayPRODUCTIONS",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Camera > Camera to View",
    "description": "Add Camera to View",
    "warning": "",
    "wiki_url": "",
    "category": "Camera",
    }

import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add

def CamToView(self, context):
    #--------------------------------------------------------
    def camera_position(matrix):
        t= (matrix[0][3],matrix[1][3],matrix[2][3])
        r=((matrix[0][0],matrix[0][1],matrix[0][2]),
           (matrix[1][0],matrix[1][1],matrix[1][2]),
           (matrix[2][0],matrix[2][1],matrix[2][2]))

        rp=((-r[0][0],-r[1][0],-r[2][0]),
            (-r[0][1],-r[1][1],-r[2][1]),
            (-r[0][2],-r[1][2],-r[2][2]))

        output=(rp[0][0]*t[0]+rp[0][1]*t[1]+rp[0][2]*t[2],
                rp[1][0]*t[0]+rp[1][1]*t[1]+rp[1][2]*t[2],
                rp[2][0]*t[0]+rp[2][1]*t[1]+rp[2][2]*t[2])
        return output

    for     v in bpy.context.window.screen.areas:
        if  v.type=='VIEW_3D':

            L=v.spaces[0].region_3d.view_location
            M=v.spaces[0].region_3d.view_matrix
            R=v.spaces[0].region_3d.view_rotation
            P=camera_position(M)

            cam   =bpy.data.cameras.new("Camera")
            cam_ob=bpy.data.objects.new("Camera",cam)
            bpy.context.scene.collection.objects.link(cam_ob)

            bpy.context.scene.camera=cam_ob

            cam_ob.location=P
            cam_ob.rotation_mode='QUATERNION'
            cam_ob.rotation_quaternion=R
            cam_ob.rotation_mode='XYZ'

            v.spaces[0].region_3d.view_perspective = 'CAMERA'

            override = {
                'area': v,
                'region': v.regions[0],
            }
            if bpy.ops.view3d.view_center_camera.poll(override):
                bpy.ops.view3d.view_center_camera(override)




    #--------------------------------------------------------

class OBJECT_OT_cam2view(Operator, AddObjectHelper):
    bl_idname = "add.cam2view"
    bl_label  = "Camera to View"
    bl_options={'REGISTER', 'UNDO'}

    def execute(self, context):
        CamToView(self, context)
        return {'FINISHED'}

# - Registration
def cam2view(self, context):
    self.layout.operator(OBJECT_OT_cam2view.bl_idname,text="Add Camera to View",icon='OUTLINER_DATA_CAMERA')
def register(  ):bpy.utils.register_class(  OBJECT_OT_cam2view);bpy.types.VIEW3D_MT_camera_add.append(cam2view)
def unregister():bpy.utils.unregister_class(OBJECT_OT_cam2view);bpy.types.VIEW3D_MT_camera_add.remove(cam2view)
if __name__ == "__main__":
    register()
