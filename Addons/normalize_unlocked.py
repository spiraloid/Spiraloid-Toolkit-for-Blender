# Normalize Unlocked
# Script Copyright (C) 2018 Rafael Navega
# https://gumroad.com/rafaelnavega

# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
    'name': 'Normalize Unlocked',
    'author': 'Rafael Navega (2018)',
    'description': 'Normalize all weights of all unlocked vertex groups',
    'version': (1, 0, 1),
    'blender': (2, 80, 0),
    'location': 'View3D Header (Weight Paint) > Weights > Normalize Unlocked',
    'warning': '',
    'category': 'Paint',
}


# Changelog:
# 1.0.1
#   - Minor change for when all weights are zero.
#
# 1.0.0
#   - Initial release.


import bpy
from math import fsum


def clamp( val, vMin, vMax ):
    return max( min( val, vMax ), vMin )


class OBJECT_OT_vertex_group_normalize_unlocked( bpy.types.Operator ):
    '''Normalize all weights of all unlocked vertex groups'''
    bl_idname = 'object.vertex_group_normalize_unlocked'
    bl_label = 'Normalize Unlocked'
    bl_options = {'REGISTER', 'UNDO'}

    lockActive = bpy.props.BoolProperty(
        name = 'Lock Active',
        description = 'Preserve the values of the active group while normalizing others (Default: on)',
        default = True
    )

    def normalizeUnlocked( self, vertices, unlockedVGroupIndices, activeIndex ):
        if self.lockActive:
            for v in vertices:
                activeWeight = 0.0
                otherGroupElements = [ ]
                otherWeights = 0.0
                for g in v.groups:
                    if g.group in unlockedVGroupIndices:
                        if g.group == activeIndex:
                            activeWeight = g.weight
                        else:
                            otherGroupElements.append( g )
                            otherWeights += g.weight

                if otherWeights > 0.0:
                    available = 1.0 - activeWeight
                    normFactor = available / otherWeights
                    for g in otherGroupElements:
                        g.weight *= normFactor
        else:
            for v in vertices:
                groupElements = [ g for g in v.groups if g.group in unlockedVGroupIndices ]
                weightTotal = fsum( [ g.weight for g in groupElements ] )
                if weightTotal > 0.0:
                    normFactor = 1.0 / weightTotal
                    for g in groupElements:
                        g.weight *= normFactor


    def invoke( self, context, event ):
        return self.execute( context )


    def execute( self, context ):
        obj = context.object
        if not obj or obj.type != 'MESH':
            return {'CANCELLED'}

        allVertexGroups = obj.vertex_groups
        if not len( allVertexGroups ):
            self.report( {'WARNING'}, 'This mesh doesn\'t have any vertex groups' )
            return {'CANCELLED'}

        activeIndex = allVertexGroups.active_index
        unlockedVGroupIndices = set( ( i for i in range( len(allVertexGroups) ) if not allVertexGroups[i].lock_weight ) )

        if self.lockActive:
            if activeIndex < 0:
                self.report( {'WARNING'}, 'No vertex group is set as active' )
                return {'CANCELLED'}

            if allVertexGroups[ activeIndex ].lock_weight:
                self.report( {'WARNING'}, 'Active group is locked, aborting' )
                return {'CANCELLED'}

        self.normalizeUnlocked( obj.data.vertices, unlockedVGroupIndices, activeIndex )
        return {'FINISHED'}


def menu_draw( self, context ):
    layout = self.layout
    layout.separator()
    layout.operator( OBJECT_OT_vertex_group_normalize_unlocked.bl_idname )


classes = (
    OBJECT_OT_vertex_group_normalize_unlocked,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_paint_weight.append(menu_draw)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.VIEW3D_MT_paint_weight.remove(menu_draw)



if __name__ == '__main__':
    register()