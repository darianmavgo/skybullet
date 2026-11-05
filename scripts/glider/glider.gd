class_name Glider
extends RigidBody3D
## Unpowered glider. Same point-mass aero model as sim/range_budget.py:
## parabolic drag polar, exponential atmosphere, load-factor cap (zoom climb after fast release).

signal landed(landing_position: Vector3, flight_time: float)

@export var wing_area := 2.5            ## m^2
@export var aspect_ratio := 20.0
@export var cd0 := 0.012
@export var oswald := 0.9
@export var max_load_factor := 3.0      ## g cap on lift
@export var max_climb_deg := 30.0       ## trim: holds the zoom-climb angle instead of looping
@export var sea_level_density := 1.225  ## kg/m^3
@export var scale_height := 8500.0      ## m

var flight_time := 0.0
var has_landed := false


func _ready() -> void:
	linear_damp_mode = RigidBody3D.DAMP_MODE_REPLACE   # Godot's default damping would act as extra drag
	linear_damp = 0.0
	angular_damp_mode = RigidBody3D.DAMP_MODE_REPLACE
	angular_damp = 0.0
	continuous_cd = true                # fast body: avoid tunnelling through thin catchers
	contact_monitor = true
	max_contacts_reported = 4
	body_entered.connect(_on_body_entered)


func _integrate_forces(state: PhysicsDirectBodyState3D) -> void:
	var v := state.linear_velocity
	var speed := v.length()
	if has_landed or speed < 1.0:
		return
	flight_time += state.step
	var q := 0.5 * sea_level_density * exp(-maxf(state.transform.origin.y, 0.0) / scale_height) * speed * speed
	var k := 1.0 / (PI * oswald * aspect_ratio)
	var cl_best := sqrt(cd0 / k)
	var cl := minf(cl_best, max_load_factor * mass * 9.81 / maxf(q * wing_area, 1e-6))
	var vhat := v / speed
	var gamma := asin(clampf(vhat.y, -1.0, 1.0))
	if gamma > deg_to_rad(max_climb_deg):
		cl = minf(cl, mass * 9.81 * cos(gamma) / maxf(q * wing_area, 1e-6))
	var lift := q * wing_area * cl
	var drag := q * wing_area * (cd0 + k * cl * cl)
	var up_perp := Vector3.UP - vhat * Vector3.UP.dot(vhat)
	var lift_dir := up_perp.normalized() if up_perp.length_squared() > 1e-6 else Vector3.ZERO
	state.apply_central_force(lift_dir * lift - vhat * drag)


func _physics_process(_delta: float) -> void:
	if has_node("Model") and linear_velocity.length() > 1.0 and not has_landed:
		$Model.look_at(global_position + linear_velocity)


func _on_body_entered(_body: Node) -> void:
	if has_landed:
		return
	has_landed = true
	landed.emit(global_position, flight_time)
