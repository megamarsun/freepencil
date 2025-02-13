import bpy
import inspect

def show_message_box(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def ensure_vertex_color(obj, color_name, default_color=(0.0, 0.0, 0.0, 1.0)):
    if bpy.app.version < (3, 4, 0):
        vcols = obj.data.vertex_colors
    else:
        vcols = obj.data.color_attributes
    for i, v in enumerate(vcols):
        if v.name == color_name:
            if bpy.app.version < (3, 4, 0):
                v.active_render = True
                obj.data.vertex_colors.active_index = i
            else:
                bpy.ops.geometry.color_attribute_render_set(name=color_name)
                obj.data.color_attributes.active_color_index = i
            return i
    if bpy.app.version < (3, 4, 0):
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.vertex_color_add()
        i_new = len(vcols) - 1
        vcols[i_new].name = color_name
        vcols[i_new].active_render = True
        obj.data.vertex_colors.active_index = i_new
        bpy.ops.object.mode_set(mode="OBJECT")
    else:
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.geometry.color_attribute_add(name=color_name, domain='CORNER', data_type='BYTE_COLOR', color=default_color)
        bpy.ops.geometry.color_attribute_render_set(name=color_name)
        i_new = len(vcols) - 1
        obj.data.color_attributes.active_color_index = i_new
        bpy.ops.object.mode_set(mode="OBJECT")
    return i_new

def find_connected_faces_bfs(bm, start_face, visited):
    queue = [start_face]
    visited[start_face.index] = True
    island = [start_face]
    while queue:
        f = queue.pop(0)
        for loop in f.loops:
            edge = loop.edge
            if not edge.smooth:
                continue
            linked_faces = [face for face in edge.link_faces if face != f]
            for lf in linked_faces:
                if not visited[lf.index]:
                    visited[lf.index] = True
                    queue.append(lf)
                    island.append(lf)
    return island

def apply_face_colors(obj, vcol_index, face_colors_r, face_colors_g, face_colors_b):
    if bpy.app.version < (3, 4, 0):
        vc_data = obj.data.vertex_colors[vcol_index].data
    else:
        vc_data = obj.data.color_attributes[vcol_index].data
    for poly_idx, poly in enumerate(obj.data.polygons):
        r = face_colors_r[poly_idx]
        g = face_colors_g[poly_idx]
        b = face_colors_b[poly_idx]
        for li in poly.loop_indices:
            vc_data[li].color = (r, g, b, 1.0)
