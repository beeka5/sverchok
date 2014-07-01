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
from bpy.props import StringProperty, EnumProperty

from node_tree import SverchCustomTreeNode
from data_structure import updateNode, SvSetSocketAnyType, SvGetSocketAnyType

# Warning, changing this node without modifying the update system might break functionlaity
# bl_idname and var_name is used by the update system

READY_COLOR = (0.674, 0.242, 0.363)
FAIL_COLOR =  (0.536, 0.242, 0.674)


class WifiOutNode(bpy.types.Node, SverchCustomTreeNode):
    ''' WifiOutNode '''
    bl_idname = 'WifiOutNode'
    bl_label = 'Wifi output'
    bl_icon = 'OUTLINER_OB_EMPTY'

    var_name = StringProperty(name='var_name',
                              default='')

    def avail_var_name(self, context):
        ng = self.id_data
        out = [(n.var_name, n.var_name, "") for n in ng.nodes
               if n.bl_idname == 'WifiInNode']
        if out:
            out.sort(key=lambda n: n[0])
        return out

    var_names = EnumProperty(items=avail_var_name, name="var names")

    def set_var_name(self):
        self.var_name = self.var_names
        ng = self.id_data
        wifi_dict = {node.var_name: node
                     for node in ng.nodes
                     if node.bl_idname == 'WifiInNode'}
        self.outputs.clear()
        if self.var_name in wifi_dict:
            self.outputs.clear()
            node = wifi_dict[self.var_name]
            while len(self.outputs) != len(node.inputs):
                socket = node.inputs[-1]
                self.outputs.new(socket.bl_idname, socket.name)
        else:
            self.outputs.clear()

    def reset_var_name(self):
        self.var_name = ""
        self.color = FAIL_COLOR
        self.outputs.clear()

    def draw_buttons(self, context, layout):
        op_name = 'node.sverchok_generic_callback'
        if self.var_name:
            row = layout.row()
            row.label(text="Var:")
            row.label(text=self.var_name)
            op = layout.operator(op_name, text='Unlink')
            op.fn_name = "reset_var_name"
        else:
            layout.prop(self, "var_names")
            op = layout.operator(op_name, text='Link')
            op.fn_name = "set_var_name"

    def init(self, context):
        self.use_custom_color = True
        self.color = FAIL_COLOR

    def gen_var_name(self):
        #from socket
        if self.outputs:
            n = self.outputs[0].name.rstrip("[0]")
            self.var_name = n

    def update(self):
        if not self.var_name and self.outputs:
            self.gen_var_name()
        ng = self.id_data
        wifi_dict = {node.var_name: node
                     for name, node in ng.nodes.items()
                     if node.bl_idname == 'WifiInNode'}

        node = wifi_dict.get(self.var_name)
        if node:
            inputs = node.inputs
            outputs = self.outputs
            if any(s.links for s in outputs):
                self.color = READY_COLOR
            #node is the wifi node
            inputs = node.inputs
            outputs = self.outputs

            # match socket type
            for idx, i_o in enumerate(zip(inputs, outputs)):
                i_socket, o_socket = i_o
                if i_socket.links:
                    f_socket = i_socket.links[0].from_socket
                    if f_socket.bl_idname != o_socket.bl_idname:
                        outputs.remove(o_socket)
                        outputs.new(f_socket.bl_idname, i_socket.name)
                        outputs.move(len(self.outputs)-1, idx)

            # adjust number of inputs
            while len(outputs) != len(inputs):
                if len(outputs) > len(inputs):
                    outputs.remove(outputs[-1])
                else:
                    n = len(outputs)
                    socket = inputs[n]
                    if socket.links:
                        s_type = socket.links[0].from_socket.bl_idname
                    else:
                        s_type = 'StringsSocket'
                    s_name = socket.name
                    outputs.new(s_type, s_name)

            # transfer data
            for in_socket, out_socket in zip(node.inputs, self.outputs):
                if in_socket.links and out_socket.links:
                    data = SvGetSocketAnyType(node, in_socket, deepcopy=False)
                    SvSetSocketAnyType(self, out_socket.name, data)


def register():
    bpy.utils.register_class(WifiOutNode)


def unregister():
    bpy.utils.unregister_class(WifiOutNode)
