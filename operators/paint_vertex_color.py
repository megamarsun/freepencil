import bpy

class LINK_MAKE_FP_OT_VCOLOR(bpy.types.Operator):
    bl_idname = "freepencil3.link_button"
    bl_label = "freepencil3"
    bl_description = "Paint Vertex Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        def ShowMessageBox(message="", title="Message Box", icon='INFO'):
            def draw(self, context):
                self.layout.label(text=message)
            bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

        o = bpy.context.selected_objects[0]
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

        color_type = bpy.context.scene.fp_color_type

        if len(context.selected_objects) == 0:
            ShowMessageBox("Select a mesh.")
            return {'FINISHED'}

        if context.active_object.type != 'MESH':
            ShowMessageBox("Active object is not a mesh.")
            return {'FINISHED'}

        selected_mesh_objects = [o for o in context.selected_objects if o.type == 'MESH']
        o = selected_mesh_objects[0]

        bpy.ops.object.mode_set(mode="VERTEX_PAINT")
        bpy.context.object.data.use_paint_mask = True
        bpy.ops.paint.face_select_all(action='SELECT')

        if bpy.app.version < (3, 4, 0):
            vcs = o.data.vertex_colors
        else:
            vcs = o.data.color_attributes
        v_cnt = 0
        for vn in vcs:
            if vn.name.find(".") == -1:
                if vn.name == color_type:
                    bpy.context.area.spaces[0].shading.type = 'SOLID'
                    bpy.context.area.spaces[0].shading.light = 'FLAT'
                    bpy.context.area.spaces[0].shading.color_type = 'VERTEX'
                    if bpy.app.version < (3, 4, 0):
                        vn.active_render = True
                        o.data.vertex_colors.active_index = v_cnt
                    else:
                        bpy.ops.geometry.color_attribute_render_set(name=color_type)
                        o.data.color_attributes.active_color_index = v_cnt
                    break
                v_cnt += 1

        return {'FINISHED'}
