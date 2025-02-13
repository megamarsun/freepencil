bl_info = {
    "name": "FreePencil",
    "author": "Your Name",
    "version": (1, 0, 9),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > FreePencil",
    "description": "FreePencil: Vertex Colors and Node Generation Tools",
    "warning": "",
    "category": "Object",
}

import os
import bpy
from bpy.props import (
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    BoolProperty,
)
import sys
import typing
import inspect
import pkgutil
import importlib
from pathlib import Path

__all__ = (
    "init",
    "register",
    "unregister",
)

# Blender のバージョン情報
blender_version = bpy.app.version

# グローバル変数（サブモジュール一覧と登録すべきクラスの順序）
modules = None
ordered_classes = None

def init():
    global modules
    global ordered_classes
    modules = get_all_submodules(Path(__file__).parent)
    ordered_classes = get_ordered_classes_to_register(modules)

def register():
    # 初期化を呼び出して ordered_classes などをセット
    init()
    bpy.app.translations.register(__name__, translation_dict)
    # 依存関係に従った順序で各クラスを登録
    for cls in ordered_classes:
        bpy.utils.register_class(cls)
    # 各サブモジュールに register() があれば呼び出す
    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register"):
            module.register()
    init_props()

def unregister():
    bpy.app.translations.unregister(__name__)
    # 依存関係の逆順で各クラスを解除
    for cls in reversed(ordered_classes):
        bpy.utils.unregister_class(cls)
    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister"):
            module.unregister()
    # 必要に応じてプロパティを削除（clear_props() を呼ぶ場合）
    # clear_props()

# ------------------------------------------------------------
# サブモジュールの自動探索
# ------------------------------------------------------------

def get_all_submodules(directory):
    return list(iter_submodules(directory, directory.name))

def iter_submodules(path, package_name):
    for name in sorted(iter_submodule_names(path)):
        yield importlib.import_module("." + name, package_name)

def iter_submodule_names(path, root=""):
    for _, module_name, is_package in pkgutil.iter_modules([str(path)]):
        if is_package:
            sub_path = path / module_name
            sub_root = root + module_name + "."
            yield from iter_submodule_names(sub_path, sub_root)
        else:
            yield root + module_name

# ------------------------------------------------------------
# 登録対象クラスの依存関係解決と順序決定
# ------------------------------------------------------------

def get_ordered_classes_to_register(modules):
    return toposort(get_register_deps_dict(modules))

def get_register_deps_dict(modules):
    my_classes = set(iter_my_classes(modules))
    my_classes_by_idname = {cls.bl_idname: cls for cls in my_classes if hasattr(cls, "bl_idname")}
    deps_dict = {}
    for cls in my_classes:
        deps_dict[cls] = set(iter_my_register_deps(cls, my_classes, my_classes_by_idname))
    return deps_dict

def iter_my_register_deps(cls, my_classes, my_classes_by_idname):
    yield from iter_my_deps_from_annotations(cls, my_classes)
    yield from iter_my_deps_from_parent_id(cls, my_classes_by_idname)

def iter_my_deps_from_annotations(cls, my_classes):
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None:
            if dependency in my_classes:
                yield dependency

def get_dependency_from_annotation(value):
    if blender_version >= (2, 93):
        if isinstance(value, bpy.props._PropertyDeferred):
            return value.keywords.get("type")
    else:
        if isinstance(value, tuple) and len(value) == 2:
            if value[0] in (bpy.props.PointerProperty, bpy.props.CollectionProperty):
                return value[1]["type"]
    return None

def iter_my_deps_from_parent_id(cls, my_classes_by_idname):
    if bpy.types.Panel in cls.__bases__:
        parent_idname = getattr(cls, "bl_parent_id", None)
        if parent_idname is not None:
            parent_cls = my_classes_by_idname.get(parent_idname)
            if parent_cls is not None:
                yield parent_cls

def iter_my_classes(modules):
    base_types = get_register_base_types()
    for cls in get_classes_in_modules(modules):
        if any(base in base_types for base in cls.__bases__):
            if not getattr(cls, "is_registered", False):
                yield cls

def get_classes_in_modules(modules):
    classes = set()
    for module in modules:
        for cls in iter_classes_in_module(module):
            classes.add(cls)
    return classes

def iter_classes_in_module(module):
    for value in module.__dict__.values():
        if inspect.isclass(value):
            yield value

def get_register_base_types():
    return set(getattr(bpy.types, name) for name in [
        "Panel", "Operator", "PropertyGroup",
        "AddonPreferences", "Header", "Menu",
        "Node", "NodeSocket", "NodeTree",
        "UIList", "RenderEngine",
        "Gizmo", "GizmoGroup",
    ])

# ------------------------------------------------------------
# トポロジカルソート（依存関係解決）
# ------------------------------------------------------------

def toposort(deps_dict):
    sorted_list = []
    sorted_values = set()
    while len(deps_dict) > 0:
        unsorted = []
        for value, deps in deps_dict.items():
            if len(deps) == 0:
                sorted_list.append(value)
                sorted_values.add(value)
            else:
                unsorted.append(value)
        deps_dict = {value: deps_dict[value] - sorted_values for value in unsorted}
    return sorted_list

# ------------------------------------------------------------
# シーンプロパティの登録
# ------------------------------------------------------------

def init_props():
    scene = bpy.types.Scene
    scene.fp_sharp_clear = BoolProperty(
        name="clear sharp",
        description="Erase outline's sharp edges",
        default=False
    )
    scene.fp_to_quads = BoolProperty(
        name="to quads",
        description="Join triangles into quads",
        default=False
    )
    scene.fp_mat_count = BoolProperty(
        name="material ID",
        description="Add the material ID",
        default=False
    )
    scene.fp_sharp_edges = FloatProperty(
        name="Line sharp edges",
        description="Outline's angle threshold.",
        default=30.0,
        min=0.0,
        max=180.0
    )
    scene.fp_color_type = EnumProperty(
        name="Vertex color type",
        description="Select vertex color type.",
        items=[
            ('mecha_color', "Mecha Color", "Mecha Color"),
            ('bone_color', "Bone Color", "Bone Color"),
            ('mask_color', "Mask Color(White erases lines)", "Mask Color(White erases lines)"),
            ('line_color', "Line Color", "Line Color")
        ],
        default='mecha_color'
    )
    scene.fp_node_type = EnumProperty(
        name="Select node type",
        description="Select Node Type",
        items=[
            ('test', "Test Node", "Test Node"),
            ('pro', "Pro Node", "Pro Node")
        ],
        default='test'
    )
    scene.fp_bone_color = BoolProperty(
        name="bone color",
        description="AOV Bone Color",
        default=False
    )
    scene.fp_gen_color = BoolProperty(
        name="generator color",
        description="AOV Generator Color",
        default=False
    )
    scene.fp_mask_color = BoolProperty(
        name="mask color",
        description="AOV Mask Color(White erases lines)",
        default=False
    )
    scene.fp_line_color = BoolProperty(
        name="line color",
        description="AOV Line Color",
        default=False
    )
    scene.fp_mat_color = BoolProperty(
        name="material color",
        description="AOV Material Boundary Color",
        default=False
    )

def clear_props():
    scene = bpy.types.Scene
    del scene.fp_sharp_edges
    del scene.fp_to_quads 
    del scene.fp_sharp_clear
    del scene.fp_color_type
    del scene.fp_mat_count
    del scene.fp_bone_color
    del scene.fp_gen_color
    del scene.fp_mask_color
    del scene.fp_line_color
    del scene.fp_mat_color

translation_dict = {
    "en_US": {
        ("*", "STEP1:Auto Vertex Color Settings:"): "STEP1:Auto Vertex Color Settings:",
        ("*", "Erase Sharp Edges"): "Erase Sharp Edges",
        ("*", "Separate Paint Vertex Colors"): "Separate Paint Vertex Colors",
        ("*", "Node Settings:"): "Node Settings:",
        ("*", "STEP3:Generate Sample Node"): "STEP3:Generate Sample Node",
        ("*", "Generate Sample Node"): "Generate Sample Node",
        ("*", "Erase outline's sharp edges"): "Erase outline's sharp edges",
        ("*", "Outline's angle threshold."): "Outline's angle threshold.",
        ("*", "Active object is not a mesh."): "Active object is not a mesh.",
        ("*", "Join triangles into quads"): "Join triangles into quads",
        ("*", "This to Quads"): "This to Quads",
        ("*", "STEP4:Manual Vertex Color Settings:"): "STEP4:Manual Vertex Color Settings:",
        ("*", "Paint Vertex Color"): "Paint Vertex Color",
        ("*", "Vertex Color Type"): "Vertex Color Type",
        ("*", "Mecha Color"): "Mecha Color",
        ("*", "Bone Color"): "Bone Color",
        ("*", "Mask Color(White erases lines)"): "Mask Color(White erases lines)",
        ("*", "Line Color"): "Line Color",
        ("*", "Add the material ID"): "Add the material ID",
        ("*", "Select a mesh."): "Select a mesh.",
        ("*", "Select Node Type"): "Select Node Type",
        ("*", "Test Node"): "Test Node",
        ("*", "Pro Node"): "Pro Node",
        ("*", "STEP2:AOV Settings:"): "STEP2:AOV Settings:",
        ("*", "Generate AOV Node"): "Generate AOV Node",
        ("*", "AOV Bone Color"): "AOV Bone Color",
        ("*", "AOV Generate Color"): "AOV Generate Color",
        ("*", "AOV Mask Color(White erases lines)"): "AOV Mask Color(White erases lines)",
        ("*", "AOV Line Color"): "AOV Line Color",
        ("*", "AOV Material Boundary Color"): "AOV Material Boundary Color",
    },
    "ja_JP": {
        ("*", "STEP1:Auto Vertex Color Settings:"): "STEP1:頂点カラーの自動塗分け設定:",
        ("*", "Erase Sharp Edges"): "シャープを削除",
        ("*", "Separate Paint Vertex Colors"): "頂点カラーを塗り分ける",
        ("*", "Node Settings:"): "ノードの設定:",
        ("*", "STEP3:Generate Sample Node"): "STEP3:サンプルノードを生成",
        ("*", "Generate Sample Node"): "サンプルノードを生成",
        ("*", "Erase outline's sharp edges"): "輪郭線を出すためのシャープを削除",
        ("*", "Outline's angle threshold."): "輪郭を出したい辺の角度",
        ("*", "Active object is not a mesh."): "アクティブオブジェクトがメッシュではありません。",
        ("*", "Join triangles into quads"): "三角形面を四角形面に統合します。",
        ("*", "This to Quads"): "三角面を四角面に",
        ("*", "STEP4:Manual Vertex Color Settings:"): "STEP4:頂点カラーの手動塗分け設定:",
        ("*", "Paint Vertex Color"): "頂点カラーを塗る",
        ("*", "Vertex Color Type"): "頂点カラーのタイプ",
        ("*", "Mecha Color"): "メカ",
        ("*", "Bone Color"): "ボーン",
        ("*", "Mask Color(White erases lines)"): "線をマスク（白で線を消す）",
        ("*", "Line Color"): "線の色",
        ("*", "Add the material ID"): "マテリアルIDを加算",
        ("*", "Select a mesh."): "メッシュを選択してください。",
        ("*", "Select Node Type"): "ノードを選択",
        ("*", "Test Node"): "テストノード",
        ("*", "Pro Node"): "プロノード",
        ("*", "STEP2:AOV Settings:"): "STEP2:AOVを設定:",
        ("*", "Generate AOV Node"): "AOVノードを生成",
        ("*", "AOV Bone Color"): "AOV ボーン",
        ("*", "AOV Generate Color"): "AOV 布など",
        ("*", "AOV Mask Color(White erases lines)"): "AOV 線をマスク（白で線を消す）",
        ("*", "AOV Line Color"): "AOV 線色",
        ("*", "AOV Material Boundary Color"): "AOV マテリアル境界",
    }
}
