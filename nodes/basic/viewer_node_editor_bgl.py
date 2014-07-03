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
from bpy.props import BoolProperty, FloatVectorProperty, StringProperty, EnumProperty

from node_tree import SverchCustomTreeNode, MatrixSocket, VerticesSocket, StringsSocket
from data_structure import dataCorrect, node_id, updateNode, SvGetSocketAnyType
from utils import nodeview_bgl_viewer_draw as nvBGL
from mathutils import Vector

# status colors
FAIL_COLOR = (0.1, 0.05, 0)
READY_COLOR = (1, 0.3, 0)


class BGL_demo_Node(SverchCustomTreeNode):
    bl_idname = 'BGLdemoNode'
    bl_label = 'BGL demo Node'
    bl_icon = 'OUTLINER_OB_EMPTY'

    # node id
    n_id = StringProperty(default='')

    text_color = FloatVectorProperty(
        name="Color", description='Text color',
        size=3, min=0.0, max=1.0,
        default=(.1, .1, .1), subtype='COLOR',
        update=updateNode)

    activate = BoolProperty(
        name='Show', description='Activate node?',
        default=True,
        update=updateNode)

    
    def avail_nodes(self, context):
        ng = self.id_data
        return [(n.name,n.name,"") for n in ng.nodes]
         
    def avail_sockets(self, context):
        if self.node_name:
            node = self.id_data.nodes.get(self.node_name)
            if node:
                return [(s.name,s.name,"") for s in node.inputs if s.links]
        else:
            return [("","","")]
    
    node_name = EnumProperty(items=avail_nodes, name="Node") 
    socket_name = EnumProperty(items=avail_sockets, name="Sockets",update=updateNode)
    state = StringProperty(default="NOT_READY", name = 'state')

        
    def init(self, context):
        self.inputs.new('StringsSocket', 'Data')
        self.state = "INACTIVE"
        
    # reset n_id on copy
    def copy(self, node):
        self.n_id = ''

    def draw_buttons(self, context, layout):
        row = layout.row()
        icon='RESTRICT_VIEW_OFF' if self.activate else 'RESTRICT_VIEW_ON'
        row.separator()
        row.prop(self, "activate", icon=icon, text='')
        row.prop(self, "text_color",text='')
#        layout.prop(self, "node_name")
#        layout.prop(self, "socket_name")
    
    def update(self):
        if self.inputs[0].links:
            self.state = "ACTIVE"
        else:
            self.state = "INACTIVE"
    
    def process(self):
        inputs = self.inputs
        n_id = node_id(self)

        # end early
        nvBGL.callback_disable(n_id)
        if not all([inputs[0], self.id_data.sv_show]):
            return

        in_links = inputs[0].links

        self.use_custom_color = True
        if self.activate and in_links:

            # gather vertices from input
            lines = nvBGL.parse_socket(inputs[0])

            draw_data = {
                'content': lines,
                'location': (self.location + Vector((self.width+20, 0)))[:],
                'color': self.text_color[:],
                }
            nvBGL.callback_enable(n_id, draw_data)
            self.color = READY_COLOR
        else:
            self.color = FAIL_COLOR

    def update_socket(self, context):
        print("update socket {0}}".format(self.name))
        self.update()

    def free(self):
        nvBGL.callback_disable(node_id(self))
    
        

def register():
    bpy.utils.register_class(BGL_demo_Node)


def unregister():
    bpy.utils.unregister_class(BGL_demo_Node)
