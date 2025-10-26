extends VBoxContainer

@export var show_labels: bool = true
@export var max_distance: float = 1.0 # normalized screen-space distance (0..~1.414). Use 1.0 by default

var _python_node: Node

func _ready() -> void:
	_python_node = WebcamSocket
	# Initial UI
	_rebuild_header()
	print(WebcamSocket.get_hand_labels())

func _process(delta: float) -> void:
	if _python_node == null:
		return
	# Update MediaPipe results (and optionally a texture we ignore here)
	if _python_node.has_method("get_handtracked_image"):
		_python_node.call("get_handtracked_image")

	var distances := {}
	if _python_node.has_method("get_thumb_tip_distances"):
		distances = _python_node.call("get_thumb_tip_distances")
	_update_ui(distances)

func _rebuild_header() -> void:
	# Optional: a small header label
	if show_labels and not _find_child_by_name(self, "HeaderLabel"):
		var lbl := Label.new()
		lbl.name = "HeaderLabel"
		lbl.text = "Thumb → Fingertip distances"
		add_child(lbl)

func _update_ui(distances: Dictionary) -> void:
	# Clear previous hand sections (keep header if present)
	for child in get_children():
		if child is Label and child.name == "HeaderLabel":
			continue
		remove_child(child)
		child.queue_free()

	var hands: Array = distances.get("hands", [])
	if hands.is_empty():
		var empty_lbl := Label.new()
		empty_lbl.text = "No hands detected"
		add_child(empty_lbl)
		return

	for hand in hands:
		var label_text := str(hand.get("label", "Unknown"))
		var distances_map: Dictionary = hand.get("distances", {})

		var hand_box := VBoxContainer.new()
		hand_box.custom_minimum_size = Vector2(0, 8)
		add_child(hand_box)

		if show_labels:
			var title := Label.new()
			title.text = "Hand: %s" % label_text
			hand_box.add_child(title)

		# Ordered fingertip keys we output from Python
		var fingers := [
			"INDEX_FINGER_TIP",
			"MIDDLE_FINGER_TIP",
			"RING_FINGER_TIP",
			"PINKY_TIP",
		]
		var pretty_names := {
			"INDEX_FINGER_TIP": "Index",
			"MIDDLE_FINGER_TIP": "Middle",
			"RING_FINGER_TIP": "Ring",
			"PINKY_TIP": "Pinky",
		}

		for key in fingers:
			var row := HBoxContainer.new()
			row.custom_minimum_size = Vector2(0, 24)
			hand_box.add_child(row)

			if show_labels:
				var lbl := Label.new()
				lbl.text = pretty_names.get(key, key) + ":"
				lbl.custom_minimum_size = Vector2(80, 0)
				row.add_child(lbl)

			var pb := ProgressBar.new()
			pb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			pb.min_value = 0.0
			pb.max_value = max_distance
			var val := float(distances_map.get(key, 0.0))
			pb.value = clamp(val, 0.0, pb.max_value)
			pb.show_percentage = true
			row.add_child(pb)

			# Numeric label
			var val_lbl := Label.new()
			val_lbl.text = "%.3f" % val
			val_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			val_lbl.custom_minimum_size = Vector2(60, 0)
			row.add_child(val_lbl)

func _find_child_by_name(p: Node, n: String) -> Node:
	for c in p.get_children():
		if c.name == n:
			return c
	return null
