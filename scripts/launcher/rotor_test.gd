extends SceneTree
## Headless check: godot --headless --path . --script res://scripts/launcher/rotor_test.gd
func _initialize() -> void:
	var rig: Rotor = load("res://scenes/launcher/tower.tscn").instantiate()
	rig.spin_up_time = 1.0
	root.add_child(rig)
	for i in 400:
		await physics_frame
	for tip in rig.tips:
		print("%s speed = %.2f m/s (target %.0f)" % [tip.name, rig.tip_velocity(tip).length(), rig.tip_speed_target])
	print("omega = %.3f rad/s, tip height = %.1f m" % [rig.omega, rig.tips[0].global_position.y])
	quit()
