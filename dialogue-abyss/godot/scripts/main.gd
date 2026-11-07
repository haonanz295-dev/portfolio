extends Node3D

const NPC_SCENE := preload("res://scenes/npc.tscn")
@onready var diver: CharacterBody3D = $Diver
@onready var camera_rig: Node3D = $CameraRig
@onready var camera: Camera3D = $CameraRig/Camera3D
@onready var message: Label = $UI/HUD/Message
var npcs: Array[Area3D] = []
var selected_index := 0
var photo_mode := false
var sonar_rings: Array[MeshInstance3D] = []
var bubble_particles: Array[MeshInstance3D] = []
var beacons: Array[Area3D] = []
var beacon_count := 0
var game_started := false

func _exit_tree() -> void:
	$BGM.stop()
	$SonarSFX.stop()
	$ConfirmSFX.stop()

func _ready() -> void:
	$BGM.finished.connect(func(): $BGM.play())
	build_seafloor()
	spawn_npcs()
	spawn_bubbles()
	spawn_beacons()
	diver.sonar_emitted.connect(_on_sonar)
	$UI/TitleOverlay/Start.pressed.connect(start_game)
	$UI/PausePanel/VBox/Resume.pressed.connect(toggle_pause)
	$UI/PausePanel/VBox/ReturnTitle.pressed.connect(return_title)
	$UI/PausePanel/VBox/Volume.value_changed.connect(set_music_volume)
	$UI/Completion/VBox/Continue.pressed.connect(func(): $UI/Completion.hide(); get_tree().paused=false)
	get_tree().paused = true
	select_npc(0)

func build_seafloor() -> void:
	var floor_body := StaticBody3D.new(); floor_body.name = "SeafloorCollision"; add_child(floor_body)
	var floor_shape := CollisionShape3D.new(); var box := BoxShape3D.new(); box.size = Vector3(80,1,80); floor_shape.shape = box; floor_shape.position.y = -3.5; floor_body.add_child(floor_shape)
	var floor_mesh := MeshInstance3D.new(); var plane := PlaneMesh.new(); plane.size = Vector2(80,80); floor_mesh.mesh = plane; floor_mesh.position.y = -3.0; floor_mesh.material_override = make_mat(Color(0.03,0.16,0.17)); add_child(floor_mesh)
	var rng := RandomNumberGenerator.new(); rng.seed = 20261107
	for i in 22:
		var rock := StaticBody3D.new(); rock.name = "Rock_%02d" % i; rock.position = Vector3(rng.randf_range(-24,24),-2.3,rng.randf_range(-24,15)); add_child(rock)
		var radius := rng.randf_range(0.5,1.8)
		var collision := CollisionShape3D.new(); var sphere := SphereShape3D.new(); sphere.radius = radius; collision.shape = sphere; rock.add_child(collision)
		var visual := MeshInstance3D.new(); visual.mesh = SphereMesh.new(); visual.scale = Vector3(radius,rng.randf_range(0.45,1.1)*radius,radius); visual.material_override = make_mat(Color(0.06,0.23,0.22)); rock.add_child(visual)
	for i in 42:
		var weed := MeshInstance3D.new(); var mesh := CylinderMesh.new(); mesh.top_radius=0.035;mesh.bottom_radius=0.12;mesh.height=rng.randf_range(1.0,3.1); weed.mesh=mesh;weed.position=Vector3(rng.randf_range(-25,25),-2.5,rng.randf_range(-25,16));weed.rotation.z=rng.randf_range(-0.2,0.2);weed.material_override=make_mat(Color(0.08,0.48+rng.randf_range(0,0.2),0.36));weed.set_meta("phase",rng.randf_range(0,TAU));weed.add_to_group("seaweed");add_child(weed)

func make_mat(color: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new(); mat.albedo_color=color;mat.roughness=0.8;return mat

func spawn_npcs() -> void:
	var definitions := [
		["jelly","微光水母","有些话落进水里，还是会刺一下。你愿意在这里停一会儿吗？",Color(0.35,0.95,0.87),Vector3(-7,1,-8)],
		["ray","暮光鳐","我会在宽阔的水里绕一圈，再决定靠近。",Color(0.93,0.70,0.32),Vector3(8,3,-14)],
		["seahorse","守望海马","慢一点也算前进。我可以陪你看一会儿水流。",Color(0.80,0.48,0.92),Vector3(-12,0,-18)],
		["octopus","多面章鱼","边界不是拒绝，它只是告诉我们怎样靠近。",Color(0.95,0.38,0.42),Vector3(11,-0.5,-22)]
	]
	for d in definitions:
		var npc := NPC_SCENE.instantiate(); add_child(npc); npc.global_position=d[4]; npc.configure(d[0],d[1],d[2],d[3]); npcs.append(npc)

func spawn_bubbles() -> void:
	var rng:=RandomNumberGenerator.new();rng.seed=88
	for i in 34:
		var b:=MeshInstance3D.new();var sphere:=SphereMesh.new();sphere.radius=.045;sphere.height=.09;b.mesh=sphere;b.material_override=make_mat(Color(0.45,0.9,0.9,0.6));b.position=Vector3(rng.randf_range(-18,18),rng.randf_range(-2,10),rng.randf_range(-25,8));b.set_meta("speed",rng.randf_range(.25,.9));add_child(b);bubble_particles.append(b)

func spawn_beacons() -> void:
	var positions := [Vector3(-4,0,-5),Vector3(6,2,-10),Vector3(-10,-1,-14),Vector3(12,1,-18),Vector3(0,4,-24)]
	for i in positions.size():
		var area:=Area3D.new();area.name="ResonanceBeacon_%d"%i;area.position=positions[i];add_child(area)
		var shape:=CollisionShape3D.new();var sphere_shape:=SphereShape3D.new();sphere_shape.radius=.75;shape.shape=sphere_shape;area.add_child(shape)
		var visual:=MeshInstance3D.new();var sphere:=SphereMesh.new();sphere.radius=.28;sphere.height=.56;visual.mesh=sphere;var mat:=make_mat(Color(0.96,0.72,0.24));mat.emission_enabled=true;mat.emission=Color(0.96,0.48,0.10);mat.emission_energy_multiplier=3.0;visual.material_override=mat;area.add_child(visual)
		area.body_entered.connect(func(body): if body==diver: collect_beacon(area))
		beacons.append(area)

func collect_beacon(area: Area3D) -> void:
	if not is_instance_valid(area) or area.get_meta("collected",false):return
	area.set_meta("collected",true);beacon_count+=1;$ConfirmSFX.play();$UI/HUD/Objective.text="共鸣微光 %d / 5"%beacon_count;message.text="你收起了一枚微光。它不是分数，只是一段靠近的痕迹。";area.queue_free()
	if beacon_count>=5:get_tree().paused=true;$UI/Completion.show()

func _process(delta: float) -> void:
	var target_pos := diver.global_position + Vector3(0,3.8,8.5).rotated(Vector3.UP,diver.rotation.y)
	camera_rig.global_position = camera_rig.global_position.lerp(target_pos,delta*2.2)
	camera.look_at(diver.global_position+Vector3(0,.4,0),Vector3.UP)
	for weed in get_tree().get_nodes_in_group("seaweed"): weed.rotation.z=sin(Time.get_ticks_msec()/1000.0+float(weed.get_meta("phase")))*.10
	for b in bubble_particles:
		b.position.y += delta*float(b.get_meta("speed")); if b.position.y>11:b.position.y=-2.5
	for ring in sonar_rings.duplicate():
		ring.scale += Vector3.ONE*delta*5.0; ring.transparency += delta*.65
		if ring.transparency>=1.0: sonar_rings.erase(ring);ring.queue_free()
	if Input.is_action_just_pressed("interact"): interact_selected()
	if Input.is_action_just_pressed("toggle_follow"): toggle_follow()
	if Input.is_action_just_pressed("photo_mode"): toggle_photo_mode()
	if Input.is_action_just_pressed("cancel"):
		if photo_mode:toggle_photo_mode()
		elif game_started:toggle_pause()

func _on_sonar(origin: Vector3) -> void:
	$SonarSFX.play()
	var ring:=MeshInstance3D.new();var torus:=TorusMesh.new();torus.inner_radius=.95;torus.outer_radius=1.0;ring.mesh=torus;ring.position=origin;ring.rotation.x=PI/2;var mat:=make_mat(Color(0.35,1.0,.9));mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA;ring.material_override=mat;add_child(ring);sonar_rings.append(ring)
	var nearest:=0;var best:=INF
	for i in npcs.size():
		var distance:=diver.global_position.distance_to(npcs[i].global_position)
		if distance<best:best=distance;nearest=i
	select_npc(nearest);message.text="声呐回应 · %s：%s"%[npcs[nearest].display_name,npcs[nearest].dialogue]

func select_npc(index: int) -> void:
	selected_index=clampi(index,0,npcs.size()-1)
	for i in npcs.size():npcs[i].selected=i==selected_index

func interact_selected() -> void:
	var npc:=npcs[selected_index]
	if diver.global_position.distance_to(npc.global_position)>7.0:message.text="距离还有一点远。你可以先靠近，也可以继续观察。";return
	message.text="%s：%s"%[npc.display_name,npc.dialogue]

func toggle_follow() -> void:
	var npc:=npcs[selected_index]
	npc.follow_target=null if npc.follow_target else diver
	message.text="%s %s"%[npc.display_name,"开始陪你游动。" if npc.follow_target else "停在了自己的水域。"]

func toggle_photo_mode() -> void:
	photo_mode=not photo_mode;diver.input_enabled=not photo_mode;$UI/HUD/Title.visible=not photo_mode;$UI/HUD/Status.visible=not photo_mode;$UI/HUD/Depth.visible=not photo_mode;$UI/HUD/Message.visible=not photo_mode;$UI/HUD/PhotoHint.text="摄影模式 · P / Esc 返回" if photo_mode else ""

func start_game() -> void:
	game_started=true;$UI/TitleOverlay.hide();get_tree().paused=false;message.text="发出声呐，看看谁愿意回应。"

func toggle_pause() -> void:
	var next:=not get_tree().paused;get_tree().paused=next;$UI/PausePanel.visible=next

func return_title() -> void:
	$UI/PausePanel.hide();$UI/TitleOverlay.show();game_started=false;get_tree().paused=true

func set_music_volume(value: float) -> void:
	$BGM.volume_db=linear_to_db(maxf(value,.001))
