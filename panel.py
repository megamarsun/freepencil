import bpy
from .operators.vertex_color import LINK_MAKE_OT_FP
from .operators.sample_node import LINK_MAKE_FP_OT_NODE
from .operators.aov_node import LINK_MAKE_FP_OT_AOV_NODE
from .operators.paint_vertex_color import LINK_MAKE_FP_OT_VCOLOR

class FP_PT_Line(bpy.types.Panel):
    bl_label = "FreePencil v1_0_9"
    bl_idname = "FREEPENCIL_PT_LINE"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FreePencil"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="STEP1:Auto Vertex Color Settings:")
        layout.prop(scene, "fp_sharp_clear", text="Erase Sharp Edges")
        layout.prop(scene, "fp_to_quads", text="This to Quads")
        layout.prop(scene, "fp_mat_count", text="Add the material ID")
        layout.prop(scene, "fp_sharp_edges", slider=True, text="Edge Angle")
        text_1 = bpy.app.translations.pgettext("Separate Paint Vertex Colors")
        layout.operator(LINK_MAKE_OT_FP.bl_idname, text=text_1, icon="MESH_CUBE")

        layout.separator()
        layout.separator()

        layout.label(text="STEP2:AOV Settings:")
        layout.prop(scene, "fp_bone_color", text="AOV Bone Color")
        layout.prop(scene, "fp_gen_color", text="AOV Generate Color")
        layout.prop(scene, "fp_mask_color", text="AOV Mask Color(White erases lines)")
        layout.prop(scene, "fp_line_color", text="AOV Line Color")
        layout.prop(scene, "fp_mat_color", text="AOV Material Boundary Color")
        text_6 = bpy.app.translations.pgettext("Generate AOV Node")
        layout.operator(LINK_MAKE_FP_OT_AOV_NODE.bl_idname, text=text_6, icon="NODETREE")

        layout.separator()
        layout.separator()

        layout.label(text="STEP3:Generate Sample Node")
        text_5 = bpy.app.translations.pgettext("Select Node Type")
        layout.prop(scene, "fp_node_type", text=text_5)
        text_2 = bpy.app.translations.pgettext("Generate Sample Node")
        layout.operator(LINK_MAKE_FP_OT_NODE.bl_idname, text=text_2, icon="NODETREE")

        layout.separator()
        layout.separator()

        layout.label(text="STEP4:Manual Vertex Color Settings:")
        text_3 = bpy.app.translations.pgettext("Vertex Color Type")
        layout.prop(scene, "fp_color_type", text=text_3)
        text_4 = bpy.app.translations.pgettext("Paint Vertex Color")
        layout.operator(LINK_MAKE_FP_OT_VCOLOR.bl_idname, text=text_4, icon="VPAINT_HLT")

        layout.separator()
