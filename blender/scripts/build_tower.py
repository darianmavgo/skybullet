"""Sky Bullet tower: mast + horizontal 2-blade rotor facing the sky (Phase 2).

  /Applications/Blender.app/Contents/MacOS/Blender --background --python blender/scripts/build_tower.py

Numbers come from sim/range_budget.py: 500 m tower, 100 m blades, 100 m/s tip speed
(omega = 1 rad/s about the vertical axis). Hierarchy seen in Godot (Blender Z = Godot Y):
  Tower
  ├── Mast
  └── RotorSpin        EMPTY at hub height. Rotate THIS around Y in Godot.
      ├── Hub
      ├── Blade_A      pivot at hub; extends +X
      │   └── TipBay_A EMPTY at the blade tip: glider release point
      └── Blade_B      opposite blade (extends -X) for opposed-pair launches
          └── TipBay_B
"""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bs_common as c

TOWER_H, BLADE_L = 500.0, 100.0
c.reset()
steel, blue, orange = c.mat("steel", (0.6, 0.62, 0.65)), c.mat("blade", (0.25, 0.4, 0.75)), c.mat("bay", (0.9, 0.55, 0.15))

root = c.empty("Tower")
c.cylinder("Mast", 8.0, TOWER_H, root, (0, 0, TOWER_H / 2), steel, radius2=4.0)
spin = c.empty("RotorSpin", root, (0, 0, TOWER_H + 4))
c.cylinder("Hub", 6.0, 8.0, spin, (0, 0, 0), steel)

for tag, rz in (("A", 0.0), ("B", math.pi)):
    blade = c.box(f"Blade_{tag}", (BLADE_L, 6.0, 1.5), spin, (0, 0, 0), blue, pivot_shift=(BLADE_L / 2, 0, 0))
    blade.rotation_euler = (0, 0, rz)
    c.box(f"BayHousing_{tag}", (8.0, 3.0, 2.5), blade, (BLADE_L, 0, 0), orange, pivot_shift=(-4.0, 0, 0))
    c.empty(f"TipBay_{tag}", blade, (BLADE_L, 0, 0))

c.save_and_export(c.ROOT / "blender/models/launcher/tower_v01.blend", c.ROOT / "assets/models/tower.glb")
