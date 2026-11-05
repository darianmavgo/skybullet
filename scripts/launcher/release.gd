class_name Release
extends Node
## Releases a glider from a blade tip, inheriting the tip velocity (omega x r).

@export var rotor: Rotor
@export var glider_scene: PackedScene


## Release from tip `tip_index` (0 = Blade_A, 1 = Blade_B). `pitch_deg` tilts the launch up from the tangent.
func release(tip_index: int, pitch_deg := 0.0) -> Glider:
	var tip := rotor.tips[tip_index]
	var vel := rotor.tip_velocity(tip)
	var flat := Vector3(vel.x, 0.0, vel.z)
	var pitch := deg_to_rad(pitch_deg)
	var glider: Glider = glider_scene.instantiate()
	rotor.get_parent().add_child(glider)
	glider.global_position = tip.global_position
	glider.linear_velocity = flat.normalized() * vel.length() * cos(pitch) + Vector3.UP * vel.length() * sin(pitch)
	return glider
