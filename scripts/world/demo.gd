extends Node3D
## Demo: tower spins up, releases a glider toward the hardware store 30 miles (48.3 km) away.
## Run:  /Applications/Godot.app/Contents/MacOS/Godot --path . res://scenes/world/demo.tscn
## Keys: 1 = 1x, 2 = 10x, 3 = 50x, 4 = 200x time   |   R = relaunch   |   Esc = quit

const STORE_DIST := 48280.0                 # 30 mi, store lies along -Z
const BASE_ELEVATION := 540.0               # mesa under the tower; tip release ~1,044 m (sim/range_budget.py)
const AIM := Vector3(0, 0, -1)
const BASE_HZ := 120                        # project physics rate

var rig: Rotor
var rel: Release
var glider: Glider
var cam: Camera3D
var hud: Label
var ground_vis: MeshInstance3D
var start_pos := Vector3.ZERO
var manual_scale := false
var result_text := ""
var released_at := 0.0


func _ready() -> void:
	Engine.max_physics_steps_per_frame = 2000
	_set_speed(5.0)
	_build_world()
	rig = load("res://scenes/launcher/tower.tscn").instantiate()
	rig.position.y = BASE_ELEVATION
	add_child(rig)
	rel = Release.new()
	rel.rotor = rig
	rel.glider_scene = load("res://scenes/glider/glider.tscn")
	add_child(rel)
	cam = Camera3D.new()
	cam.far = 200000.0
	cam.current = true
	add_child(cam)
	var layer := CanvasLayer.new()
	hud = Label.new()
	hud.position = Vector2(16, 12)
	hud.add_theme_font_size_override("font_size", 20)
	layer.add_child(hud)
	add_child(layer)


func _build_world() -> void:
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_SKY
	env.environment.sky = Sky.new()
	env.environment.sky.sky_material = ProceduralSkyMaterial.new()
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, 30, 0)
	add_child(sun)
	var ground := StaticBody3D.new()
	var col := CollisionShape3D.new()
	col.shape = WorldBoundaryShape3D.new()
	ground.add_child(col)
	add_child(ground)
	ground_vis = _mesh(PlaneMesh.new(), Color(0.35, 0.5, 0.3), Vector3.ZERO)
	(ground_vis.mesh as PlaneMesh).size = Vector2(60000, 60000)   # follows the glider
	add_child(ground_vis)
	var mesa := CylinderMesh.new()
	mesa.top_radius = 150.0
	mesa.bottom_radius = 400.0
	mesa.height = BASE_ELEVATION
	add_child(_mesh(mesa, Color(0.55, 0.42, 0.3), Vector3(0, BASE_ELEVATION / 2.0, 0)))
	var store: Node3D = load("res://assets/models/hardware_store.glb").instantiate()
	store.position = Vector3(0, 0, -STORE_DIST)
	add_child(store)
	var beacon := CylinderMesh.new()
	beacon.top_radius = 6.0
	beacon.bottom_radius = 6.0
	beacon.height = 400.0
	add_child(_mesh(beacon, Color(0.9, 0.1, 0.1), Vector3(0, 200, -STORE_DIST - 120)))


func _mesh(m: Mesh, color: Color, pos: Vector3) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = m
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mi.material_override = mat
	mi.position = pos
	return mi


func _physics_process(delta: float) -> void:
	if glider == null:
		var v := rig.tip_velocity(rig.tips[0])
		if rig.omega >= rig.tip_speed_target / rig.blade_length * 0.999 \
				and absf(v.signed_angle_to(AIM, Vector3.UP)) <= rig.omega * delta * 0.5:
			start_pos = rig.tips[0].global_position
			glider = rel.release(0, 0.0)
			glider.landed.connect(_on_landed)
			released_at = Time.get_ticks_msec()
		return
	if not manual_scale and glider.flight_time > 10.0 and not glider.has_landed:
		_set_speed(30.0)
	if glider.has_landed:
		_set_speed(1.0)


func _process(_delta: float) -> void:
	if glider == null:
		var hub := rig.spin.global_position
		cam.global_position = hub + Vector3(450, 120, 250)
		cam.look_at(hub + Vector3(0, -40, 0))
		hud.text = "Spinning up...  tip speed %.0f m/s  (%.1fx time)" % [rig.omega * rig.blade_length, Engine.time_scale]
		return
	var v := glider.linear_velocity
	var dir := v.normalized() if v.length() > 1.0 else Vector3(0, 0, -1)
	if glider.has_landed:
		cam.global_position = glider.global_position + Vector3(60, 25, 60)
	else:
		cam.global_position = glider.global_position - dir * 45.0 + Vector3.UP * 12.0
	cam.look_at(glider.global_position)
	ground_vis.global_position = Vector3(glider.global_position.x, 0, glider.global_position.z)
	var to_store := Vector2(glider.global_position.x, glider.global_position.z + STORE_DIST)
	hud.text = "alt %.0f m   speed %.0f m/s   flown %.1f km   to store %.1f km   t=%.0f s   (%.0fx time)\n%s" % [
		glider.global_position.y, v.length(),
		Vector2(glider.global_position.x - start_pos.x, glider.global_position.z - start_pos.z).length() / 1000.0,
		to_store.length() / 1000.0, glider.flight_time, Engine.time_scale, result_text]


func _on_landed(pos: Vector3, t: float) -> void:
	var miss := Vector2(pos.x, pos.z + STORE_DIST).length()
	result_text = "LANDED after %.0f s, %.0f m from the hardware store %s" % [t, miss, "- DELIVERED!" if miss < 80.0 else "- missed"]
	print(result_text)


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		match event.keycode:
			KEY_1: _scale(1.0)
			KEY_2: _scale(10.0)
			KEY_3: _scale(50.0)
			KEY_4: _scale(200.0)
			KEY_R:
				_set_speed(1.0)
				get_tree().reload_current_scene()
			KEY_ESCAPE: get_tree().quit()


func _scale(s: float) -> void:
	manual_scale = true
	_set_speed(s)


## Fast-forward WITHOUT coarser physics: Engine.time_scale alone also scales the physics step
## (0.083 s at 10x), which wrecks the glider integration. Scale the tick rate with it so each
## step stays 1/120 s and only more steps run per second.
func _set_speed(s: float) -> void:
	if is_equal_approx(Engine.time_scale, s):
		return
	Engine.time_scale = s
	Engine.physics_ticks_per_second = int(round(BASE_HZ * s))


func _exit_tree() -> void:
	Engine.time_scale = 1.0
	Engine.physics_ticks_per_second = BASE_HZ
