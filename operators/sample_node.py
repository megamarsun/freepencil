import bpy
import os
from .. import utils

class LINK_MAKE_FP_OT_NODE(bpy.types.Operator):
    bl_idname = "freepencil2.link_button"
    bl_label = "freepencil2"
    bl_description = "Generate Sample Node"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        def ShowMessageBox(message="", title="Message Box", icon='INFO'):
            def draw(self, context):
                self.layout.label(text=message)
            bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

        v_name = bpy.context.view_layer.name
        vc_flag = 0
        for v in bpy.context.scene.view_layers[v_name].aovs:
            if v.name == "mecha_color":
                vc_flag = 1
        if vc_flag == 0:
            ShowMessageBox("Execute from STEP2")
            return {'FINISHED'}

        node_type = bpy.context.scene.fp_node_type
        node_ver_name = 'FreePencil_v1_1_0_' + node_type

        NG_flag = 0
        for n in bpy.data.node_groups:
            if n.name == node_ver_name:
                NG_flag = 1
        if NG_flag == 0:
            file_path = os.path.join(os.path.dirname(__file__), "..", "resources", "freepencil_node_2_9_3.blend")
            inner_path = 'NodeTree'
            object_name = node_ver_name
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )

        bpy.context.view_layer.use_pass_z = True
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='MESH')

        scene = context.scene

        if not bpy.context.scene.use_nodes:
            bpy.context.scene.use_nodes = True
            for n in bpy.context.scene.node_tree.nodes:
                bpy.context.scene.node_tree.nodes.remove(n)

        tree = bpy.context.scene.node_tree
        fp_cnt = 0
        for n in tree.nodes:
            if n.label == node_ver_name:
                fp_cnt += 1
            elif "FreePencil" in n.label:
                tree.nodes.remove(n)

        if fp_cnt != 3:
            for n in tree.nodes:
                if n.label == node_ver_name:
                    tree.nodes.remove(n)

            node_tree = scene.node_tree

            # レンダーレイヤーノード
            CNRL = node_tree.nodes.new('CompositorNodeRLayers')
            CNRL.label = node_ver_name
            CNRL.location[0] = -40
            CNRL.location[1] = 400

            # グループノードを配置
            group_node = node_tree.nodes.new('CompositorNodeGroup')
            group_node.node_tree = bpy.data.node_groups[node_ver_name]
            group_node.label = node_ver_name
            group_node.location[0] = 270
            group_node.location[1] = 500

            # コンポジット出力ノード
            CNC = node_tree.nodes.new('CompositorNodeComposite')
            CNC.label = node_ver_name
            CNC.location[0] = 500
            CNC.location[1] = 600

            if node_type == "pro":
                node_tree.links.new(CNRL.outputs[0], group_node.inputs[0])
                node_tree.links.new(CNRL.outputs[2], group_node.inputs[2])
                node_tree.links.new(CNRL.outputs[1], group_node.inputs[1])
            else:
                node_tree.links.new(CNRL.outputs[1], group_node.inputs[0])

            if node_type == "pro":
                range_size = 9
            else:
                range_size = 2
            for i in range(range_size):
                for j, o in enumerate(CNRL.outputs):
                    if o.name == group_node.inputs[i].name:
                        node_tree.links.new(CNRL.outputs[j], group_node.inputs[i])

            node_tree.links.new(group_node.outputs[0], CNC.inputs[0])

        bpy.ops.wm.window_new()
        bpy.context.area.ui_type = 'CompositorNodeTree'
        return {'FINISHED'}
