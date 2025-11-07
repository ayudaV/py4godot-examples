extends HBoxContainer

func _input(event: InputEvent) -> void:
	print(event)
	$LTrack.button_pressed = true if event.is_action_pressed("H") else false
	$MLTrack.button_pressed = true if event.is_action_pressed("U") else false
	$MRTrack.button_pressed = true if event.is_action_pressed("I") else false
	$RTrack.button_pressed = true if event.is_action_pressed("L") else false
