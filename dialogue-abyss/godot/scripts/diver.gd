extends CharacterBody3D

signal sonar_emitted(origin: Vector3)
@export var swim_speed := 5.5
@export var vertical_speed := 3.8
@export var turn_speed := 4.0
var input_enabled := true
var photo_mode := false
var swim_phase := 0.0

func _physics_process(delta: float) -> void:
	if not input_enabled:
		velocity = velocity.move_toward(Vector3.ZERO, delta * 5.0)
		move_and_slide()
		return
	var input_2d := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var vertical := Input.get_axis("move_down", "move_up")
	var direction := Vector3(input_2d.x, vertical * 0.75, input_2d.y)
	if direction.length() > 0.05:
		direction = direction.normalized()
		velocity = velocity.lerp(direction * Vector3(swim_speed, vertical_speed, swim_speed), delta * 3.5)
		var flat := Vector3(direction.x, 0, direction.z)
		if flat.length() > 0.1:
			rotation.y = lerp_angle(rotation.y, atan2(-flat.x, -flat.z), delta * turn_speed)
		swim_phase += delta * 7.0
	else:
		velocity = velocity.move_toward(Vector3.ZERO, delta * 2.4)
		swim_phase += delta * 2.0
	animate_rig(delta, input_2d.length())
	move_and_slide()
	if Input.is_action_just_pressed("sonar"):
		sonar_emitted.emit($SonarOrigin.global_position)

func animate_rig(_delta: float, effort: float) -> void:
	var kick := sin(swim_phase) * (0.25 + effort * 0.35)
	$Rig/LegL.rotation.x = kick
	$Rig/LegR.rotation.x = -kick
	$Rig/ArmL.rotation.x = -kick * 0.7
	$Rig/ArmR.rotation.x = kick * 0.7
	$Rig.rotation.z = sin(swim_phase * 0.5) * 0.025
