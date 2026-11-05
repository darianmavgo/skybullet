class_name Rotor
extends Node3D
## Spins the tower's RotorSpin node about its vertical axis and reports blade-tip velocity.
## Numbers come from sim/range_budget.py (100 m blades, 100 m/s tip speed -> 1 rad/s).

@export var tip_speed_target := 100.0  ## m/s at the blade tip
@export var blade_length := 100.0      ## m, hub axis to TipBay
@export var spin_up_time := 20.0       ## s to reach full speed
@export var spinning := true

var omega := 0.0                       ## rad/s, current
var tips: Array[Node3D] = []

var spin: Node3D


func _ready() -> void:
	# Look up by name: the glTF importer adds its own root node above "Tower".
	spin = $Model.find_child("RotorSpin", true, false)
	for tip_name in ["TipBay_A", "TipBay_B"]:
		tips.append($Model.find_child(tip_name, true, false))


func _physics_process(delta: float) -> void:
	var target := tip_speed_target / blade_length if spinning else 0.0
	var accel := (tip_speed_target / blade_length) / maxf(spin_up_time, 0.001)
	omega = move_toward(omega, target, accel * delta)
	spin.rotate_y(omega * delta)


## World-space velocity of a tip marker: v = omega x r about the rotor axis.
func tip_velocity(tip: Node3D) -> Vector3:
	var axis := spin.global_basis.y.normalized()
	return (axis * omega).cross(tip.global_position - spin.global_position)
