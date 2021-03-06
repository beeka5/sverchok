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
from bpy.props import StringProperty

from node_tree import SverchCustomTreeNode
from data_structure import multi_socket

# Warning, changing this node without modifying the update system might break functionlaity
# bl_idname and var_name is used by the update system

READY_COLOR = (0.674, 0.242, 0.363)
FAIL_COLOR =  (0.536, 0.242, 0.674)



def name_seq():
    for i in range(ord('a'),ord('z')): 
        yield chr(i)
    for i in range(1000):
        yield "a.".join(str(i))

class WifiInNode(bpy.types.Node, SverchCustomTreeNode):
    ''' Wifi Input '''
    bl_idname = 'WifiInNode'
    bl_label = 'Wifi input'
    bl_icon = 'OUTLINER_OB_EMPTY'

    def change_var_name(self, context):
        # no change
        if self.base_name == self.var_name:
            return
        ng = self.id_data
        wifi_in_list = [node for node in ng.nodes
                           if node.bl_idname == 'WifiInNode']
        for node in wifi_in_list:
            if node.name != self.name:
                if node.var_name == self.var_name:
                    self.var_name = self.base_name
                    return
        self.base_name = self.var_name
        self.inputs.clear()
        self.inputs.new('StringsSocket', self.var_name+"[0]")
        
    var_name = StringProperty(name='var_name', update=change_var_name)

    base_name = StringProperty(default='')
    multi_socket_type = StringProperty(default='StringsSocket')

    def draw_buttons(self, context, layout):
        layout.prop(self, "var_name", text="Var")

    def init(self, context):
        self.use_custom_color = True
        self.color = FAIL_COLOR
        ng = self.id_data
        var_set = {node.var_name for node in ng.nodes
                           if node.bl_idname == 'WifiInNode'}
        for name in name_seq(): 
            if not name in var_set:
                self.var_name = name
                return
                
    def copy(self, node):
        ng = self.id_data
        var_set = {node.var_name for node in ng.nodes
                           if node.bl_idname == 'WifiInNode'}
        for name in name_seq():
            if not name in var_set:
                self.var_name = name
                return

    def gen_var_name(self):
        #from socket
        if self.inputs:
            n = self.inputs[0].name.rstrip("[0]")
            self.base_name = n
            self.var_name = n
        else: 
            ng = self.id_data
            var_set = {node.var_name for node in ng.nodes
                           if node.bl_idname == 'WifiInNode'}
            for name in name_seq():
                if not name in var_set:
                    self.var_name = name
                    return
        
    def update(self):
        # ugly hack to get var name sometimes with old layouts
        if not self.var_name:
            self.gen_var_name()
                
        self.base_name = self.var_name
        multi_socket(self, min=1, breck=True)
        if any(s.links for s in self.inputs):
            self.color = READY_COLOR

def register():
    bpy.utils.register_class(WifiInNode)


def unregister():
    bpy.utils.unregister_class(WifiInNode)
