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
from bpy.props import BoolProperty, IntProperty, StringProperty

from node_tree import SverchCustomTreeNode
from data_structure import (updateNode, changable_sockets, repeat_last,
                            SvSetSocketAnyType, SvGetSocketAnyType)

# ListSlice
# by Linus Yng

# Slices a list using function like:
# Slice  = data[start:stop]
# Other = data[:start]+data[stop:]


class ListSliceNode(bpy.types.Node, SverchCustomTreeNode):
    ''' List Slice '''
    bl_idname = 'ListSliceNode'
    bl_label = 'List Slice'
    bl_icon = 'OUTLINER_OB_EMPTY'

    level = IntProperty(name='level_to_count',
                        default=2, min=0,
                        update=updateNode)
    start = IntProperty(name='Start',
                        default=0,
                        update=updateNode)
    stop = IntProperty(name='Stop',
                       default=1,
                       update=updateNode)

    typ = StringProperty(name='typ',
                         default='')
    newsock = BoolProperty(name='newsock',
                           default=False)

    def draw_buttons(self, context, layout):
        layout.prop(self, "level", text="level")

    def init(self, context):
        self.inputs.new('StringsSocket', "Data")
        self.inputs.new('StringsSocket', "Start").prop_name = 'start'
        self.inputs.new('StringsSocket', "Stop").prop_name = 'stop'
        self.outputs.new('StringsSocket', "Slice", "Slice")
        self.outputs.new('StringsSocket', "Other", "Other")

    def update(self):
        if 'Data' in self.inputs and len(self.inputs['Data'].links) > 0:
            inputsocketname = 'Data'
            outputsocketname = ['Slice', 'Other']
            changable_sockets(self, inputsocketname, outputsocketname)

        if 'Slice' in self.outputs and self.outputs['Slice'].links or \
                'Other' in self.outputs and self.outputs['Other'].links:

            if 'Data' in self.inputs and self.inputs['Data'].links:
                data = SvGetSocketAnyType(self, self.inputs['Data'])

                if 'Start' in self.inputs and self.inputs['Start'].links:
                    start = SvGetSocketAnyType(self, self.inputs['Start'])[0]
                else:
                    start = [self.start]

                if 'Stop' in self.inputs and self.inputs['Stop'].links:
                    stop = SvGetSocketAnyType(self, self.inputs['Stop'])[0]
                else:
                    stop = [self.stop]

                if 'Slice' in self.outputs and self.outputs['Slice'].links:
                    if self.level:
                        out = self.get(data, start, stop, self.level, self.slice)
                    else:
                        out = self.slice(data, start[0], stop[0])
                    SvSetSocketAnyType(self, 'Slice', out)
                if 'Other' in self.outputs and self.outputs['Other'].links:
                    if self.level:
                        out = self.get(data, start, stop, self.level, self.other)
                    else:
                        out = self.other(data, start[0], stop[0])
                    SvSetSocketAnyType(self, 'Other', out)

    def slice(self, data, start, stop):
        if type(data) in [tuple, list]:
            return data[start:stop]
        else:
            return None

    def other(self, data, start, stop):
        if type(data) in [tuple, list]:
            return data[:start]+data[stop:]
        else:
            return None

    def get(self, data, start, stop, level, f):
        if level > 1:  # find level to work on
            return [self.get(obj, start, stop, level-1, f) for obj in data]
        elif level == 1:  # execute the chosen function
            start_iter = repeat_last(start)
            stop_iter = repeat_last(stop)
            return [f(obj, next(start_iter), next(stop_iter)) for obj in data]
        else:  # Fail
            return None

    def update_socket(self, context):
        self.update()


def register():
    bpy.utils.register_class(ListSliceNode)


def unregister():
    bpy.utils.unregister_class(ListSliceNode)
