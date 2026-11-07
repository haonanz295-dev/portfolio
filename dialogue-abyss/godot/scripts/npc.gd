extends Area3D

@export_enum("jelly", "ray", "seahorse", "octopus") var species := "jelly"
@export var display_name := "微光水母"
@export var dialogue := "有些话落进水里，还是会刺一下。"
var follow_target: Node3D
var selected := false
var phase := 0.0

func _ready() -> void:
	build_visual()

func configure(kind: String, title: String, words: String, tint: Color) -> void:
	species = kind; display_name = title; dialogue = words
	$Glow.light_color = tint
	build_visual()

func build_visual() -> void:
	for child in $Visual.get_children(): child.queue_free()
	var mat := StandardMaterial3D.new()
	mat.albedo_color = $Glow.light_color
	mat.emission_enabled = true; mat.emission = $Glow.light_color; mat.emission_energy_multiplier = 1.4
	if species == "jelly":
		add_part(SphereMesh.new(), Vector3(0,0.25,0), Vector3(1.1,0.65,1.1), mat)
		for x in [-0.42,-0.14,0.14,0.42]: add_part(CylinderMesh.new(), Vector3(x,-0.75,0), Vector3(0.08,0.9,0.08), mat)
	elif species == "ray":
		add_part(SphereMesh.new(), Vector3.ZERO, Vector3(2.0,0.22,1.15), mat)
		add_part(CylinderMesh.new(), Vector3(0,0,1.35), Vector3(0.08,0.08,1.6), mat)
	elif species == "seahorse":
		add_part(CapsuleMesh.new(), Vector3.ZERO, Vector3(0.5,1.15,0.5), mat)
		add_part(SphereMesh.new(), Vector3(0.25,0.75,0), Vector3(0.55,0.42,0.42), mat)
	else:
		add_part(SphereMesh.new(), Vector3(0,0.3,0), Vector3(1.0,0.8,1.0), mat)
		for i in 8: add_part(CylinderMesh.new(), Vector3(cos(i*TAU/8.0)*0.55,-0.65,sin(i*TAU/8.0)*0.55), Vector3(0.12,0.75,0.12), mat)

func add_part(mesh: PrimitiveMesh, pos: Vector3, scale_value: Vector3, mat: Material) -> void:
	var part := MeshInstance3D.new(); part.mesh = mesh; part.position = pos; part.scale = scale_value; part.material_override = mat; $Visual.add_child(part)

func _process(delta: float) -> void:
	phase += delta
	$Visual.position.y = sin(phase * 1.4) * 0.16
	$Visual.rotation.y += delta * 0.12
	if follow_target:
		var target := follow_target.global_position + Vector3(2.2,1.2,2.4)
		global_position = global_position.lerp(target, delta * 0.75)
	$Glow.light_energy = 2.2 if selected else 1.2
