# Project structure

```
skybullet/                 Repo root is also the Godot 4.7 project (project.godot)
├── assets/                Exported models, textures, audio (imported by Godot)
│   └── models/            launcher.glb, polypizza/ (downloaded CC models)
├── scenes/                .tscn files: launcher, glider, catcher, world
├── scripts/               GDScript: physics (lift/drag), glider, launcher
├── resources/             .tres files: aero curves, glider parameters
├── addons/
├── blender/               Source art (Godot ignores this folder via .gdignore)
│   ├── models/            launcher, glider, catcher, environment (.blend)
│   ├── scripts/           build_launcher.py (headless Blender builds)
│   ├── textures/  reference/  renders/ (renders git-ignored)
├── tools/                 polypizza.py (model downloads, reads .env)
│   └── viewer/            serve.py + index.html: dev dashboard with hot reload
├── sim/                   Python scripts for quick trajectory and g-load checks
├── docs/                  Concept docs and SVG schematics (.gdignore)
└── IMG_227x.JPG           Original handwritten notes
```

## Conventions
- **Units:** metric, 1 Blender unit = 1 m. Godot also uses meters.
- **Names:** `snake_case` files. Blender sources are `<part>_v01.blend`, exports are `<part>.glb`.
- **Export:** Blender → glTF 2.0 (`.glb`) into `assets/models/`. Apply transforms first (Ctrl+A), and keep forward axis -Z and up axis +Y in the export settings.
- **Origins:** put each part's origin at its pivot. The tube's origin is the spin axis, and the glider's is its centre of mass.
- **Collision:** add simple convex or box shapes in Godot instead of using the render mesh.
- **Workflow:** edit in `blender/`, export to `assets/`, and never edit the exported `.glb` by hand.

## Running and viewing
- **Game demo:** `/Applications/Godot.app/Contents/MacOS/Godot --path .` (or F5 in the editor). Keys: 1/2/3/4 = 1x/10x/50x/200x time, R = relaunch, Esc = quit.
- **Dashboard:** `python3 tools/viewer/serve.py`, then open http://127.0.0.1:8765. It shows the schematics, 3D models, the sim table and build logs, and reloads itself when files change. Editing `blender/scripts/build_*.py` re-runs headless Blender and re-exports the `.glb`.
- **Godot hot reload:** in the editor, use the Debug menu toggles "Synchronize Scene Changes" and "Synchronize Script Changes" so a running game picks up edits. The editor re-imports a changed `.glb` when it regains focus.
- **Headless tests:** `godot --headless --path . --script res://scripts/launcher/rotor_test.gd` (tip speed), and `--fixed-fps 120 ... res://scripts/glider/flight_test.gd` (range vs sim).
