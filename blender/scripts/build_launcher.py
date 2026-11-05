"""Build the Sky Bullet launcher (Blender 4/5, run headless):

  /Applications/Blender.app/Contents/MacOS/Blender --background --python blender/scripts/build_launcher.py

Units: 1 BU = 1 m. Hierarchy (names are what Godot will see):
  Launcher
  ├── Platform          hovering disc
  ├── Cable             tether hanging below the platform
  └── TubeSpin          EMPTY at the spin axis: rotate THIS node in Godot (Y axis)
      ├── Hub
      ├── Tube          two-armed launch tube (opposed pair), 100 m tip to tip
      └── Magazine      elevator/magazine block at the hub
"""
import bpy, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BLEND = ROOT / "blender/models/launcher/launcher_v01.blend"
GLB = ROOT / "assets/models/launcher.glb"

PLATFORM_R, PLATFORM_H = 12.0, 3.0
TUBE_LEN, TUBE_R = 100.0, 1.5
CABLE_LEN, CABLE_R = 150.0, 0.3

bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
    return m


def finish(obj, name, material, parent):
    obj.name = name
    obj.data.materials.append(material)
    obj.parent = parent
    bpy.ops.object.shade_smooth()
    return obj


grey, blue, orange, dark = (mat("hull", (0.55, 0.57, 0.6)), mat("tube", (0.25, 0.4, 0.75)),
                            mat("magazine", (0.9, 0.55, 0.15)), mat("cable", (0.1, 0.1, 0.1)))

root = bpy.data.objects.new("Launcher", None)
bpy.context.collection.objects.link(root)

# Platform: top surface at z=0 is NOT used; origin is the platform centre.
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=PLATFORM_R, depth=PLATFORM_H, location=(0, 0, 0))
finish(bpy.context.object, "Platform", grey, root)

bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=CABLE_R, depth=CABLE_LEN,
                                    location=(0, 0, -PLATFORM_H / 2 - CABLE_LEN / 2))
finish(bpy.context.object, "Cable", dark, root)

# Spin axis empty sits on the platform top; everything that spins is its child.
spin = bpy.data.objects.new("TubeSpin", None)
spin.location = (0, 0, PLATFORM_H / 2 + 1.5)
spin.parent = root
bpy.context.collection.objects.link(spin)


def child_at_axis(obj_name, material):
    obj = bpy.context.object
    obj.name = obj_name
    obj.data.materials.append(material)
    obj.parent = spin
    obj.matrix_parent_inverse = spin.matrix_world.inverted()
    bpy.ops.object.shade_smooth()


z = spin.location.z
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=3.0, depth=3.0, location=(0, 0, z))
child_at_axis("Hub", grey)

bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=TUBE_R, depth=TUBE_LEN, location=(0, 0, z),
                                    rotation=(0, math.radians(90), 0))
child_at_axis("Tube", blue)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z + 2.8))
bpy.context.object.scale = (6, 3, 2.4)
bpy.ops.object.transform_apply(scale=True)
child_at_axis("Magazine", orange)

BLEND.parent.mkdir(parents=True, exist_ok=True)
GLB.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.export_scene.gltf(filepath=str(GLB), export_format="GLB", export_apply=True, export_yup=True)
print("WROTE", BLEND, GLB)
