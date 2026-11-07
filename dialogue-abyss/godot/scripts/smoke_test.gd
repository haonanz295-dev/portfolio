extends SceneTree

func _initialize() -> void:
	call_deferred("run_test")

func run_test() -> void:
	for model in ["diver", "ray", "jelly", "seahorse", "octopus", "starfish", "shark", "whale"]:
		var packed = load("res://assets/models/" + model + ".gltf")
		assert(packed is PackedScene)
		var imported = packed.instantiate()
		assert(imported.get_child_count() > 0)
		imported.free()
	print("GLTF_IMPORT_PASS: eight reusable 3D models")
	var scene = load("res://scenes/main.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	scene.start_game()
	var diver = scene.get_node("Diver")
	var start: Vector3 = diver.position
	Input.action_press("move_forward")
	for i in range(90):
		await physics_frame
	Input.action_release("move_forward")
	assert(diver.position.z < start.z - 1.0)
	assert(scene.npcs.size() == 4)
	scene.toggle_follow()
	assert(scene.npcs[scene.selected_index].follow_target == diver)
	scene.toggle_photo_mode()
	assert(scene.photo_mode and not diver.input_enabled)
	scene.toggle_photo_mode()
	diver.position = Vector3(0, 0, 0)
	Input.action_press("move_down")
	for i in range(120):
		await physics_frame
	Input.action_release("move_down")
	assert(diver.position.y > -3.0)
	print("GODOT_SMOKE_PASS: movement, four NPCs, following, photo toggle, seabed collision")
	scene.get_node("BGM").stop()
	scene.get_node("SonarSFX").stop()
	scene.get_node("ConfirmSFX").stop()
	await create_timer(0.3).timeout
	scene.queue_free()
	await process_frame
	quit(0)
