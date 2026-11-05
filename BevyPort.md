# Plan: Move SkyBullet from Godot 4.7 to Bevy + Blender

## Context
SkyBullet is early-stage: the Godot side is tiny (`scripts/launcher/rotor.gd` 32 lines, `rotor_test.gd`, `scenes/launcher/tower.tscn`, `project.godot`). Real substance lives in Blender build scripts (`blender/scripts/build_*.py`, `bs_common.py`), exported `.glb` files (`assets/models/{tower,launcher,hardware_store}.glb`, `polypizza/`), and the Python physics sim (`sim/range_budget.py`). Switching now is cheap. Blender stays the asset source; only the engine changes. glTF 2.0 is the bridge.

Decisions made: Godot files are **left untouched** during this plan (user: "don't touch"; deletion is deferred and not part of this work). Physics uses **avian3d** from the start.

## Approach
Add a Cargo project alongside the existing tree (same repo root, no Godot files modified). Pin Bevy and avian3d to a compatible pair (check crates.io for the current matching versions at start). `cargo` is installed; Blender CLI is not on PATH, so use `/Applications/Blender.app/Contents/MacOS/Blender` for headless runs.

### Phase 0 – Scaffold
- `Cargo.toml` (bevy, avian3d, bevy_gltf via default features), `src/main.rs`, `src/lib.rs` with plugins: `LauncherPlugin`, `GliderPlugin`, `WorldPlugin`.
- Bevy reads assets from `assets/`, which already exists with `.glb` files, so no move is needed. Godot `.import` sidecars are simply ignored.
- Update `.gitignore` for `target/`. Dev profile: `opt-level=1`, deps `opt-level=3`; enable `dynamic_linking` feature for dev iteration.
- Set `Time::<Fixed>` to 120 Hz (matches `physics_ticks_per_second=120`) and avian's schedule to run in `FixedPostUpdate`.

### Phase 1 – Blender pipeline (assets)
- Keep `blender/models/*.blend` and `blender/scripts/` as is. Units (1 BU = 1 m) are unchanged.
- Axis: Bevy is Y-up, right-handed, forward -Z, same as glTF, so exports need no conversion. Keep export `export_yup=True`.
- Add `blender/scripts/export_glb.py` (headless: open .blend, export glTF binary to `assets/models/<name>.glb`, apply transforms). Reuse `ROOT` and helpers in `bs_common.py`. Add a `tools/export_all.sh` loop over the blend files.
- Replace Godot node-name conventions with Bevy ones: Empties like `TipBay_A`, `RotorSpin`, `Blade_A` survive as glTF nodes with `Name` components. Look them up after scene spawn via a `SceneInstanceReady` observer.
- Collision: use simple primitives defined in Rust (avian `Collider::cuboid`/`cylinder`), or Blender objects named `COL_*` that a startup system converts to `Collider::convex_hull_from_mesh`. Start with the former.
- Update `PROJECT_STRUCTURE.md` and `docs/README.md` to describe the Bevy layout.

### Phase 2 – Port the rotor (parity milestone)
Port `rotor.gd` to `src/launcher/rotor.rs`:
- `Rotor` component: `tip_speed_target=100.0`, `blade_length=100.0`, `spin_up_time=20.0`, `spinning`, `omega`.
- `spin_rotor` system in `FixedUpdate`: `move_toward` omega (write a small `move_toward` helper in `src/util.rs`), then `transform.rotate_local_y(omega*dt)` on the `RotorSpin` entity.
- `tip_velocity(tip, spin)` = `(axis*omega).cross(tip_pos - spin_pos)` using `GlobalTransform`.
- Load `tower.glb` via `SceneRoot(asset_server.load(GltfAssetLabel::Scene(0).from_asset("models/tower.glb")))`. Replaces `tower.tscn`.
- Make the spinning entity kinematic (`RigidBody::Kinematic`, `AngularVelocity`) so avian carries children correctly.
- `rotor_test.gd` becomes a Rust unit/integration test (headless `App` with `MinimalPlugins`; assert omega reaches 1 rad/s after 20 s and tip speed ≈ 100 m/s).

### Phase 3 – Glider and aero on avian3d
- Port the `fly()` model from `sim/range_budget.py` to `src/glider/aero.rs`: `rho(h)` exponential atmosphere, parabolic polar (`cd0`, `e`, aspect ratio), load-factor cap `n_max`, `cl_best`.
- Glider = `RigidBody::Dynamic` + `Collider` + `Mass`; a `FixedUpdate` system computes lift and drag from velocity and applies via avian `ExternalForce`. Disable avian default gravity scaling issues by using `Gravity(Vec3::NEG_Y * 9.81)`.
- Release: glider attached to a TipBay, detaches with `tip_velocity` as initial `LinearVelocity`. Release angle sets bearing.
- Validation: a test replaying the sim's scenarios (same h0/v0) and comparing range within a tolerance (~5%) against `sim/range_budget.py` output. Keep the Python sim as the reference oracle.
- Models: `assets/models/polypizza/{paper_airplane,hang_glider}.glb` as placeholders; build a proper glider .blend later.

### Phase 4 – World, camera, catcher
- `hardware_store.glb` environment scene, a free-fly or chase camera (add `bevy_flycam` or write ~40 lines), a catcher sensor volume (`Sensor` collider + collision events), HUD text for speed/altitude/g-load via Bevy UI.
- 30-mile range (`TARGET_M`) needs large-world care: f32 precision. Use `big_space` or floating-origin around the glider if range tests show jitter; defer until observed.

### Phase 5 – Tooling and docs
- `tools/polypizza.py` unchanged (engine-agnostic). Update `ASSETS_LICENSES.md` only if new assets are added.
- Update `.editorconfig`/`.gitattributes` for `.rs` and `.glb` binary.
- Add `cargo fmt`, `cargo clippy`, `cargo test` instructions to `docs/README.md`.
- Godot files remain in the tree, untouched, until the user chooses to remove them.

## Critical files
- Read/port: `scripts/launcher/rotor.gd`, `scripts/launcher/rotor_test.gd`, `scenes/launcher/tower.tscn`, `sim/range_budget.py`, `project.godot` (physics Hz).
- Modify: `.gitignore`, `PROJECT_STRUCTURE.md`, `docs/README.md`, `.gitattributes`.
- New: `Cargo.toml`, `src/{main,lib,util}.rs`, `src/launcher/rotor.rs`, `src/glider/aero.rs`, `src/world.rs`, `blender/scripts/export_glb.py`, `tools/export_all.sh`.

## Verification
1. `cargo build` and `cargo test` pass (rotor spin-up test, aero parity test vs. `python3 sim/range_budget.py`).
2. `cargo run`: tower.glb loads, blades spin up to 1 rad/s over 20 s; debug-print tip speed ≈ 100 m/s.
3. Run the Blender export script headless; confirm regenerated `.glb` loads in Bevy with node names (`RotorSpin`, `TipBay_A/B`) found.
4. Launch a glider from a tip bay; compare range/flight time with the Python sim and visually in-game.
5. `git status` shows no Godot file modified or deleted.

## Risks
- Bevy and avian3d release in lockstep and APIs shift each release; pin exact versions.
- Bevy has no editor; scene composition is code/glTF-driven (Blender is the layout tool). Accepted tradeoff.
- Large-world f32 precision for 48 km flights.
