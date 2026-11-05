extends SceneTree
func _initialize() -> void:
	var d = load("res://scenes/world/demo.tscn").instantiate()
	root.add_child(d)
	for i in 600000:
		await physics_frame
		if d.glider != null and d.glider.has_landed:
			break
	print(d.result_text)
	quit()
