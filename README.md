# Sky Bullet

Godot 4.7 game (the repo root is the Godot project) with Blender source art.
A glider is released from the tip of a rotor on a 500 m tower and flies unpowered to a hardware store 30 mi away.

## Launching from the command line (macOS)

`godot` and `blender` are not on your PATH by default, so `blender: command not found` is expected until you set them up.
Run all commands below from the project folder (`cd ~/Documents/skybullet`).

Add these aliases to `~/.zshrc` once, then open a new terminal (or run `source ~/.zshrc`):

```sh
echo 'alias godot=/Applications/Godot.app/Contents/MacOS/Godot' >> ~/.zshrc
echo 'alias blender=/Applications/Blender.app/Contents/MacOS/Blender' >> ~/.zshrc
source ~/.zshrc
```

No setup needed: use the full path instead, e.g.
`/Applications/Blender.app/Contents/MacOS/Blender SkyBullet.blend`.

### Godot

```sh
godot --path .                  # run the game (main scene: scenes/world/demo.tscn)
godot --path . --editor         # open the project in the Godot editor
godot --path . res://scenes/world/demo.tscn   # run a specific scene
godot --headless --path . --script res://scripts/launcher/rotor_test.gd   # headless test
```

Auto-restart on save (scripts, scenes, resources, `.glb`):

```sh
python3 tools/watch_run.py
```

Demo keys: `1`/`2`/`3`/`4` = 1x/10x/50x/200x time, `R` = relaunch, `Esc` = quit.

### Blender

```sh
blender SkyBullet.blend                       # WHOLE SCENE, static overview: tower on mesa, store 48 km away, glide line
blender blender/models/launcher/launcher_v01.blend   # the launcher part
blender blender/models/launcher/tower_v01.blend             # open a part, e.g. the tower
blender blender/models/environment/hardware_store_v01.blend  # or the hardware store

# Rebuild a model headlessly (re-exports the .glb into assets/models/)
blender --background --python blender/scripts/build_scene.py   # regenerate SkyBullet.blend (run after the part builds)
blender --background --python blender/scripts/build_tower.py
blender --background --python blender/scripts/build_store.py
blender --background --python blender/scripts/build_launcher.py
```

Or, without aliases: `open -a Blender SkyBullet.blend` / `open -a Godot --args --path . --editor`.

### Dev dashboard

```sh
python3 tools/viewer/serve.py   # then open http://127.0.0.1:8765
```

Shows schematics, 3D models and build logs, and re-runs the Blender builds when `blender/scripts/build_*.py` change.

See `PROJECT_STRUCTURE.md` for the folder layout and conventions.
