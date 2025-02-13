import bpy
import os
from .. import utils

class LINK_MAKE_FP_OT_AOV_NODE(bpy.types.Operator):
    bl_idname = "freepencil4.link_button"
    bl_label = "freepencil4"
    bl_description = "Generate Sample Node"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        def ShowMessageBox(message="", title="Message Box", icon='INFO'):
            def draw(self, context):
                self.layout.label(text=message)
            bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
        context = bpy.context

        if len(context.selected_objects) == 0:
            ShowMessageBox("Select a mesh.")
            return {'FINISHED'}

        o = context.selected_objects[0]
        if bpy.app.version < (3, 4, 0):
            vcs = o.data.vertex_colors
        else:
            vcs = o.data.color_attributes
        vnFlag = 0
        for vn in vcs:
            if vn.name == "mecha_color":
                vnFlag = 1
                break
        if vnFlag == 0:
            ShowMessageBox("Execute from STEP1")
            return {'FINISHED'}

        select_cash = context.selected_objects
        node_aov_ver_name = 'FreePencil_aov_Group_v1_1_0'
        NG_flag = 0
        for n in bpy.data.node_groups:
            if n.name == node_aov_ver_name:
                NG_flag = 1
        if NG_flag == 0:
            file_path = os.path.join(os.path.dirname(__file__), "..", "resources", "freepencil_node_2_9_3.blend")
            inner_path = 'NodeTree'
            object_name = node_aov_ver_name
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )

        for so in select_cash:
            bpy.data.objects[so.name].select_set(True)

        context.view_layer.objects.active = select_cash[-1]

        mp_cnt = 0
        if context.scene.fp_mat_count:
            for ms in bpy.data.materials:
                if not ms.grease_pencil or ms.use_nodes:
                    ms.pass_index = mp_cnt
                    mp_cnt += 1

        for ms in bpy.data.materials:
            node_tree_ms = ms.node_tree
            if not ms.grease_pencil or ms.use_nodes:
                nm_flag = 0
                if ms.use_nodes:
                    nodes = node_tree_ms.nodes
                    for a in bpy.data.node_groups:
                        if a.name == node_aov_ver_name:
                            aov_object = a
                            if context.scene.fp_mat_count:
                                a.nodes["Map Range"].inputs[2].default_value = mp_cnt
                    aov_flag = 0
                    for ng in node_tree_ms.nodes:
                        if ng.type == "GROUP":
                            if ng.node_tree.name == node_aov_ver_name:
                                aov_flag = 1
                            elif "FreePencil" in ng.node_tree.name:
                                node_tree_ms.nodes.remove(ng)
                    if aov_flag == 0:
                        aov_group_set = nodes.new(type='ShaderNodeGroup')
                        aov_group_set.node_tree = aov_object
                        aov_group_set.location[0] = 10
                        aov_group_set.location[1] = 400
                        aov_group_set.width = 240

        v_name = context.view_layer.name
        vc_flag = 0
        vc_cnt = 0
        for v in context.scene.view_layers[v_name].aovs:
            if v.name == "mecha_color":
                vc_flag = 1
                break
            vc_cnt += 1
        if vc_flag == 0:
            bpy.ops.scene.view_layer_add_aov()
            context.scene.view_layers[v_name].active_aov_index = vc_cnt
            context.scene.view_layers[v_name].active_aov.name = "mecha_color"

        if context.scene.fp_bone_color:
            bc_flag = 0
            bc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "bone_color":
                    bc_flag = 1
                    break
                bc_cnt += 1
            if bc_flag == 0:
                bpy.ops.scene.view_layer_add_aov()
                context.scene.view_layers[v_name].active_aov_index = bc_cnt
                context.scene.view_layers[v_name].active_aov.name = "bone_color"
        else:
            bc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "bone_color":
                    context.scene.view_layers[v_name].active_aov_index = bc_cnt
                    bpy.ops.scene.view_layer_remove_aov()
                bc_cnt += 1

        if context.scene.fp_gen_color:
            gc_flag = 0
            gc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "gen_color":
                    gc_flag = 1
                    break
                gc_cnt += 1
            if gc_flag == 0:
                bpy.ops.scene.view_layer_add_aov()
                context.scene.view_layers[v_name].active_aov_index = gc_cnt
                context.scene.view_layers[v_name].active_aov.name = "gen_color"
        else:
            gc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "gen_color":
                    context.scene.view_layers[v_name].active_aov_index = gc_cnt
                    bpy.ops.scene.view_layer_remove_aov()
                gc_cnt += 1

        if context.scene.fp_mask_color:
            mc_flag = 0
            mc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "mask_color":
                    mc_flag = 1
                    break
                mc_cnt += 1
            if mc_flag == 0:
                bpy.ops.scene.view_layer_add_aov()
                context.scene.view_layers[v_name].active_aov_index = mc_cnt
                context.scene.view_layers[v_name].active_aov.name = "mask_color"
        else:
            mc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "mask_color":
                    context.scene.view_layers[v_name].active_aov_index = mc_cnt
                    bpy.ops.scene.view_layer_remove_aov()
                mc_cnt += 1

        if context.scene.fp_line_color:
            lc_flag = 0
            lc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "line_color":
                    lc_flag = 1
                    break
                lc_cnt += 1
            if lc_flag == 0:
                bpy.ops.scene.view_layer_add_aov()
                context.scene.view_layers[v_name].active_aov_index = lc_cnt
                context.scene.view_layers[v_name].active_aov.name = "line_color"
        else:
            lc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "line_color":
                    context.scene.view_layers[v_name].active_aov_index = lc_cnt
                    bpy.ops.scene.view_layer_remove_aov()
                lc_cnt += 1

        if context.scene.fp_mat_color:
            mc_flag = 0
            mc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "mat_color":
                    mc_flag = 1
                    break
                mc_cnt += 1
            if mc_flag == 0:
                bpy.ops.scene.view_layer_add_aov()
                context.scene.view_layers[v_name].active_aov_index = mc_cnt
                context.scene.view_layers[v_name].active_aov.name = "mat_color"
        else:
            mc_cnt = 0
            for v in context.scene.view_layers[v_name].aovs:
                if v.name == "mat_color":
                    context.scene.view_layers[v_name].active_aov_index = mc_cnt
                    bpy.ops.scene.view_layer_remove_aov()
                mc_cnt += 1

        context.scene.render.film_transparent = True
        context.scene.view_settings.view_transform = 'Standard'
        bpy.context.area.spaces[0].shading.type = 'RENDERED'
        bpy.context.area.spaces[0].shading.render_pass = 'mecha_color'

        return {'FINISHED'}
