"""Hardware store target: building + parking-lot catcher pad (Phase 2).

  /Applications/Blender.app/Contents/MacOS/Blender --background --python blender/scripts/build_store.py

Hierarchy: HardwareStore > Building, Sign, Lot, LandingZone (EMPTY at lot centre).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bs_common as c

c.reset()
wall, roof, asphalt, red = (c.mat("wall", (0.8, 0.78, 0.7)), c.mat("roof", (0.35, 0.35, 0.38)),
                            c.mat("asphalt", (0.12, 0.12, 0.13)), c.mat("sign", (0.8, 0.1, 0.1)))
root = c.empty("HardwareStore")
c.box("Lot", (160.0, 100.0, 0.4), root, (0, -70, 0.2), asphalt)
c.box("Building", (80.0, 40.0, 10.0), root, (0, 0, 5.0), wall)
c.box("Roof", (82.0, 42.0, 1.0), root, (0, 0, 10.5), roof)
c.box("Sign", (30.0, 1.0, 6.0), root, (0, -21, 13.0), red)
c.empty("LandingZone", root, (0, -70, 0.4))
c.save_and_export(c.ROOT / "blender/models/environment/hardware_store_v01.blend", c.ROOT / "assets/models/hardware_store.glb")
