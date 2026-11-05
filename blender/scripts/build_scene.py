"""Static overview of the whole Sky Bullet scene -> SkyBullet.blend (repo root).

  /Applications/Blender.app/Contents/MacOS/Blender --background --python blender/scripts/build_scene.py

Appends the tower and hardware store from their part files and lays them out like
scenes/world/demo.gd (Blender +Y = Godot -Z): tower on a 540 m mesa, store 48.28 km away,
plus a schematic straight glide line from the blade tip to the store. Not exported to Godot.
"""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy, bs_common as c

STORE_DIST = 48280.0
MESA_H = 540.0

c.reset()
scene = bpy.context.scene


def append_all(blend, offset):
    """Append every object of `blend`, shift the top-level ones by `offset`; return them."""
    with bpy.data.libraries.load(str(blend)) as (src, dst):
        dst.objects = list(src.objects)
    objs = [o for o in dst.objects if o]
    for o in objs:
        scene.collection.objects.link(o)
        if o.parent is None:
            o.location = (o.location[0] + offset[0], o.location[1] + offset[1], o.location[2] + offset[2])
    return objs


tower = append_all(c.ROOT / "blender/models/launcher/tower_v01.blend", (0, 0, MESA_H))
store = append_all(c.ROOT / "blender/models/environment/hardware_store_v01.blend", (0, STORE_DIST, 0))

# Ground and mesa
ground = c.cylinder("Ground", 70000, 1, None, (0, STORE_DIST / 2, -0.5), c.mat("Ground", (0.30, 0.42, 0.22)), verts=64)
ground.scale = (0.45, 0.9, 1)
c.cylinder("Mesa", 350, MESA_H, None, (0, 0, MESA_H / 2), c.mat("Mesa", (0.55, 0.40, 0.28)), radius2=250)

# Release point = blade tip A; find it for the glide line
tip = next(o for o in tower if o.name == "TipBay_A")
bpy.context.view_layer.update()
start = tip.matrix_world.translation.copy()
end = (0, STORE_DIST, 2)

curve = bpy.data.curves.new("GlidePath", "CURVE")
curve.dimensions = "3D"
curve.bevel_depth = 4  # visible from far away, still slim up close
sp = curve.splines.new("POLY")
sp.points.add(1)
sp.points[0].co = (*start, 1)
sp.points[1].co = (*end, 1)
path = bpy.data.objects.new("GlidePath_schematic", curve)
scene.collection.objects.link(path)
path.data.materials.append(c.mat("Path", (1.0, 0.8, 0.1)))

# Beacon so the 48 km-away store is findable from the tower
c.box("StoreBeacon", (150, 150, 3000), None, (0, STORE_DIST, 1500), c.mat("Beacon", (0.9, 0.1, 0.1)))

# Sun + camera
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sun.rotation_euler = (math.radians(50), 0, math.radians(30))
sun.data.energy = 4
scene.collection.objects.link(sun)
cam = bpy.data.objects.new("Cam_Tower", bpy.data.cameras.new("Cam_Tower"))
cam.data.clip_start = 5
cam.data.clip_end = 200000
cam.location = (500, -500, 1000)
cam.rotation_euler = (math.radians(90), 0, math.radians(45))
scene.collection.objects.link(cam)
scene.camera = cam

# Big viewport clip range so the 48 km span is visible in the editor
for win in bpy.context.window_manager.windows:
    for area in win.screen.areas:
        if area.type == "VIEW_3D":
            area.spaces[0].clip_start = 5
            area.spaces[0].clip_end = 200000
            area.spaces[0].shading.type = "SOLID"

bpy.ops.wm.save_as_mainfile(filepath=str(c.ROOT / "SkyBullet.blend"))
print("WROTE SkyBullet.blend; objects:", len(bpy.data.objects), "tip", tuple(start))
