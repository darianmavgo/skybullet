# Project structure

```
skybullet/
├── docs/                  Concept docs and SVG schematics
├── IMG_227x.JPG           Original handwritten notes
├── blender/               Source art (edit here)
│   ├── models/
│   │   ├── launcher/      Platform, rotating tube, elevator/magazine
│   │   ├── glider/        Sky bullet, frisbee variant
│   │   ├── catcher/       Skid, belly-flop pad, balloon bungee
│   │   └── environment/   Sky, clouds, ground station
│   ├── textures/
│   ├── reference/         Images and measurements for modeling
│   └── renders/           Preview renders (git-ignored)
├── sky-bullet/            Godot 4.7 project (open this folder in Godot)
│   ├── assets/            Exported models, textures, audio (imported by Godot)
│   ├── scenes/            .tscn files: launcher, glider, catcher, world
│   ├── scripts/           GDScript: physics (lift/drag), glider, launcher
│   ├── resources/         .tres files: aero curves, glider parameters
│   └── addons/
└── sim/                   Python scripts for quick trajectory and g-load checks
```

## Conventions
- **Units:** metric, 1 Blender unit = 1 m. Godot also uses meters.
- **Names:** `snake_case` files. Blender sources are `<part>_v01.blend`, exports are `<part>.glb`.
- **Export:** Blender → glTF 2.0 (`.glb`) into `sky-bullet/assets/models/`. Apply transforms first (Ctrl+A), and keep forward axis -Z and up axis +Y in the export settings.
- **Origins:** put each part's origin at its pivot. The tube's origin is the spin axis, and the glider's is its centre of mass.
- **Collision:** add simple convex or box shapes in Godot instead of using the render mesh.
- **Workflow:** edit in `blender/`, export to `sky-bullet/assets/`, and never edit the exported `.glb` by hand.
