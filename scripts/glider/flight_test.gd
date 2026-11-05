extends SceneTree
## Headless: godot --headless --fixed-fps 120 --path . --script res://scripts/glider/flight_test.gd
## Releases from the tower tip at 1,500 m altitude and compares range with sim/range_budget.py (64.2 km).
var result := {}

func _initialize() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var ground := StaticBody3D.new()
	var col := CollisionShape3D.new()
	col.shape = WorldBoundaryShape3D.new()
	ground.add_child(col)
	world.add_child(ground)
	var rig: Rotor = load("res://scenes/launcher/tower.tscn").instantiate()
	rig.spin_up_time = 1.0
	rig.position.y = 1000.0 - 4.0 + 0.0  # tip ends up ~1500 m (hub is 504 m up the model)
	world.add_child(rig)
	var rel := Release.new()
	rel.rotor = rig
	rel.glider_scene = load("res://scenes/glider/glider.tscn")
	world.add_child(rel)
	for i in 240:
		await physics_frame
	var start := rig.tips[0].global_position
	var g := rel.release(0, 0.0)
	g.landed.connect(func(p: Vector3, t: float): result = {"pos": p, "t": t})
	var n := 0
	while result.is_empty() and n < 600000:
		await physics_frame
		n += 1
		if n % 12000 == 0:
			print("t=%ds alt=%.0f speed=%.1f dist=%.1f km" % [n / 120, g.global_position.y, g.linear_velocity.length(), Vector2(g.global_position.x - start.x, g.global_position.z - start.z).length() / 1000.0])
	var d := Vector2(result.pos.x - start.x, result.pos.z - start.z).length()
	print("release alt %.0f m, speed %.1f m/s" % [start.y, rig.tip_velocity(rig.tips[0]).length()])
	print("range %.1f km after %.0f s (sim predicts ~64.2 km)" % [d / 1000.0, result.t])
	quit()
