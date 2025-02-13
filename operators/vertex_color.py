import bpy
import bmesh
import random
import math
import time
from .. import utils

class LINK_MAKE_OT_FP(bpy.types.Operator):
    bl_idname = "freepencil1.link_button"
    bl_label = "freepencil1"
    bl_description = "Separate Paint Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        time_sta = time.time()
        scene = context.scene

        if len(context.selected_objects) == 0:
            utils.show_message_box("Select a mesh.")
            return {'FINISHED'}

        if not context.active_object or context.active_object.type != 'MESH':
            utils.show_message_box("Active object is not a mesh.")
            return {'FINISHED'}

        line_edges = math.radians(scene.fp_sharp_edges)

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_all(action='SELECT')
        if scene.fp_sharp_clear:
            bpy.ops.mesh.mark_sharp(clear=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp(sharpness=line_edges)
        bpy.ops.mesh.mark_sharp(clear=False)
        bpy.ops.object.mode_set(mode="OBJECT")

        selected_mesh_objects = [o for o in context.selected_objects if o.type == 'MESH']
        wm = bpy.context.window_manager
        wm.progress_begin(0, len(selected_mesh_objects))

        for o in selected_mesh_objects:
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o

            if not o.active_material:
                if len(o.material_slots) == 0:
                    bpy.ops.object.material_slot_add()
                mat_flag = False
                mat = None
                for ms in bpy.data.materials:
                    if ms.name == 'FreePencil_Material':
                        mat_flag = True
                        mat = ms
                        break
                if not mat_flag:
                    mat = bpy.data.materials.new(name='FreePencil_Material')
                o.active_material_index = 0
                o.active_material = mat
                o.active_material.use_nodes = True
                bpy.ops.object.material_slot_assign()

            wm.progress_update(len(selected_mesh_objects))

            arm_obj = None
            for om in o.modifiers:
                if om.type == "ARMATURE" and om.show_viewport and om.object:
                    arm_obj = om.object
                    break

            bpy.ops.object.mode_set(mode="OBJECT")

            if arm_obj:
                bone_index = utils.ensure_vertex_color(o, "bone_color", (0, 0, 0, 1))
                vcount = len(o.data.vertices)
                rc = [0.0] * vcount
                gc = [0.0] * vcount
                bc = [0.0] * vcount
                vg_count = len(o.vertex_groups)
                color_R = [random.randint(16, 60) for _ in range(vg_count)]
                color_G = [random.randint(16, 60) for _ in range(vg_count)]
                color_B = [random.randint(16, 60) for _ in range(vg_count)]
                for idx, vert in enumerate(o.data.vertices):
                    for g in vert.groups:
                        vg_name = o.vertex_groups[g.group].name
                        if vg_name in arm_obj.data.bones:
                            w = g.weight
                            rc[idx] += (color_R[g.group] / 90.0) * w
                            gc[idx] += (color_G[g.group] / 90.0) * w
                            bc[idx] += (color_B[g.group] / 90.0) * w
                    rc[idx] += 0.1
                    gc[idx] += 0.1
                    bc[idx] += 0.1

                if bpy.app.version < (3, 4, 0):
                    vc_data = o.data.vertex_colors[bone_index].data
                else:
                    vc_data = o.data.color_attributes[bone_index].data

                for poly in o.data.polygons:
                    for li, vert_idx in zip(poly.loop_indices, poly.vertices):
                        vc_data[li].color = (rc[vert_idx], gc[vert_idx], bc[vert_idx], 1.0)

            utils.ensure_vertex_color(o, "mask_color", (0, 0, 0, 1))
            utils.ensure_vertex_color(o, "line_color", (0, 0, 0, 1))
            mecha_index = utils.ensure_vertex_color(o, "mecha_color", (1, 1, 1, 1))

            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(type='FACE')
            if scene.fp_to_quads:
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.tris_convert_to_quads()
                bpy.ops.mesh.select_all(action='DESELECT')

            bm = bmesh.from_edit_mesh(o.data)
            bm.faces.ensure_lookup_table()

            face_count = len(bm.faces)
            visited = [False] * face_count
            color_r_list = [random.randint(16, 60) for _ in range(face_count)]
            color_g_list = [random.randint(16, 60) for _ in range(face_count)]
            color_b_list = [random.randint(16, 60) for _ in range(face_count)]
            face_colors_r = [0.0] * face_count
            face_colors_g = [0.0] * face_count
            face_colors_b = [0.0] * face_count
            color_index = 0
            for f in bm.faces:
                if not visited[f.index]:
                    if color_index >= face_count:
                        color_index = 0
                    cr = color_r_list[color_index] / 60.0
                    cg = color_g_list[color_index] / 60.0
                    cb = color_b_list[color_index] / 60.0
                    color_index += 1
                    island = utils.find_connected_faces_bfs(bm, f, visited)
                    for isf in island:
                        face_colors_r[isf.index] = cr
                        face_colors_g[isf.index] = cg
                        face_colors_b[isf.index] = cb

            bpy.ops.object.mode_set(mode="OBJECT")
            utils.apply_face_colors(o, mecha_index, face_colors_r, face_colors_g, face_colors_b)

            if hasattr(bpy.context.area, "spaces") and len(bpy.context.area.spaces) > 0:
                space = bpy.context.area.spaces[0]
                space.shading.type = 'SOLID'
                space.shading.light = 'FLAT'
                space.shading.color_type = 'VERTEX'

        wm.progress_end()
        time_end = time.time()
        print("For coloring process " + str(round(time_end - time_sta, 3)) + " seconds")
        return {'FINISHED'}
