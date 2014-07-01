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
from bpy.props import BoolProperty, BoolVectorProperty, StringProperty

from node_tree import SverchCustomTreeNode
from data_structure import multi_socket, SvGetSocketAnyType, updateNode


class SvDebugPrintNode(SverchCustomTreeNode):
    ''' SvDebugPrintNode '''
    bl_idname = 'SvDebugPrintNode'
    bl_label = 'Debug print'
    bl_icon = 'OUTLINER_OB_EMPTY'

    # I wanted to show the bool so you could turn off and on individual sockets
    # but needs changes in node_s, want to think a bit more before adding an index option to
    # stringsockets, for now draw_button_ext
    defaults = [True for i in range(32)]
    print_socket = BoolVectorProperty(name='Print',
                                      default=defaults, size=32,
                                      update=updateNode)
    base_name = 'Data '
    multi_socket_type = 'StringsSocket'
    print_data = BoolProperty(name='Active', description='Turn on/off printing to stdout',
                              default=True,
                              update=updateNode)
    state = StringProperty(default="NOT_READY", name = 'state')


    def init(self, context):
        socket = self.inputs.new('StringsSocket', "Data 0")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'print_data')

    def draw_buttons_ext(self, context, layout):
        layout.label(text='Print?')
        for i, socket in enumerate(self.inputs):
            layout.prop(self, "print_socket", index=i, text=socket.name)

    def update(self):
        print("update called {0} {1}".format(self.name,self.state))
        if self.inputs[-1].links:
            self.state = "NOT_READY"
        multi_socket(self, min=1)
            
        if all((self.print_data, any((s.links for s in self.inputs)),any(self.print_socket))):
            self.state = "ACTIVE"
        else:
            self.state= "INACTIVE"
            
        if self.state == "ACTIVE":
            self.use_custom_color = True
            self.color = (0.5,0.5,1)
        else:
            self.use_custom_color = True
            self.color = (0.05,0.05,0.1)
        
    def process(self):
        if not self.print_data:
            return
        
        for i, socket in enumerate(self.inputs):
            if socket.links and self.print_socket[i]:
                print(SvGetSocketAnyType(self, socket, deepcopy=False))
            


def register():
    bpy.utils.register_class(SvDebugPrintNode)


def unregister():
    bpy.utils.unregister_class(SvDebugPrintNode)

if __name__ == '__main__':
    register()
