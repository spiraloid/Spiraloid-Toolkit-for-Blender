bl_info = {
        'name': 'ToggleDefaultWeights',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'View',
        'location': 'View > Weights > Toggle Default Weights',
        'wiki_url': ''}

import bpy



isWeightToggled = True


def main(context):
    global isWeightToggled
    
    if not isWeightToggled:
        # bpy.context.scene.tool_settings.unified_paint_settings.weight = 0
        bpy.data.brushes['Brush'].weight = 0

  
    if isWeightToggled:    
        # bpy.context.scene.tool_settings.unified_paint_settings.weight = 1
        bpy.data.brushes['Brush'].weight = 1

        
    isWeightToggled = not isWeightToggled
                
class BR_OT_toggle_weights(bpy.types.Operator):
    """Toggle Default Weights"""
    bl_idname = "view3d.toggle_default_weights"
    bl_label = "Toggle Default Weights"

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def menu_draw(self, context):
    self.layout.operator(BR_OT_toggle_weights.bl_idname)



def register():
    bpy.utils.register_class(BR_OT_toggle_weights)
    bpy.types.VIEW3D_MT_paint_weight.prepend(menu_draw)  

def unregister():
    bpy.utils.unregister_class(BR_OT_toggle_weights)
    bpy.types.VIEW3D_MT_paint_weight.remove(menu_draw)  

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_paint_weight.remove(menu_draw)

if __name__ == "__main__":
    register()

