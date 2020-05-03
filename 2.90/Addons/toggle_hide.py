# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
bl_info = {
    "name": "Toggle Hide",
    "location": "3D View / Outliner, (Hotkey J)",
    "version": (0, 1, 0),
    "blender": (2, 81, 0),
    "description": "Toggle object visibility of outliner selection",
    "author": "kaio",
    "category": "Object",
}


class OUTLINER_OT_toggle_hide(bpy.types.Operator):
    bl_idname = "outliner.toggle_hide"
    bl_label = "Toggle Hide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        ar = context.screen.areas
        __class__.area = next(
            (a for a in ar if a.type == 'OUTLINER'), None)
        return __class__.area

    def execute(self, context):
        objs = context.view_layer.objects
        sel_objs = {o for o in objs if o.select_get()}
        hid_objs = {o for o in objs if o.hide_get()}

        # Hide selected
        for o in sel_objs:
            o.hide_set(True)

        # Unhide hidden
        for o in hid_objs:
            o.hide_set(False)

        # Select objects marked in outliner
        bpy.ops.outliner.object_operation(
            {'area': __class__.area}, type='SELECT')

        # Re-hide others
        for o in hid_objs:
            if not o.select_get():
                o.hide_set(True)
        return {'FINISHED'}


addon_keymaps = []


def register():
    bpy.utils.register_class(OUTLINER_OT_toggle_hide)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon.keymaps
    km = kc.get("Object Mode")
    if not km:
        km = kc.new("Object Mode")
    kmi = km.keymap_items.new("outliner.toggle_hide", "J", "PRESS")
    addon_keymaps.append((km, kmi))

    km = kc.get("Outliner")
    if not km:
        km = kc.new("Outliner", space_type="OUTLINER")
    kmi = km.keymap_items.new("outliner.toggle_hide", "J", "PRESS")
    addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(OUTLINER_OT_toggle_hide)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()