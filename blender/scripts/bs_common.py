"""Shared helpers for headless Blender build scripts (1 BU = 1 m)."""
import bpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
    return m


def empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(e)
    e.parent = parent
    e.location = loc
    return e


def box(name, size, parent, loc, material, pivot_shift=None):
    """Axis-aligned box of `size` (x,y,z). Mesh pivot sits at `loc` (parent-local)."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if pivot_shift:  # move geometry relative to the pivot
        o.data.transform(__import__("mathutils").Matrix.Translation(pivot_shift))
    return _place(o, name, parent, loc, material)


def cylinder(name, radius, depth, parent, loc, material, radius2=None, rot=(0, 0, 0), verts=32):
    if radius2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=radius, radius2=radius2, depth=depth)
    o = bpy.context.object
    o.rotation_euler = rot
    return _place(o, name, parent, loc, material)


def _place(o, name, parent, loc, material):
    o.name = name
    o.data.materials.append(material)
    o.parent = parent
    o.location = loc
    bpy.ops.object.shade_smooth()
    return o


def save_and_export(blend, glb):
    blend.parent.mkdir(parents=True, exist_ok=True)
    glb.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", export_apply=True, export_yup=True)
    print("WROTE", blend, glb)
