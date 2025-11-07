extends VBoxContainer

# Create a new InputEventKey
@onready var _LTrack = InputEventKey.new()
@onready var _MLTrack = InputEventKey.new()
@onready var _MRTrack = InputEventKey.new()
@onready var _RTrack = InputEventKey.new()

func _ready() -> void:
	# Configure the event
	_LTrack.keycode = KEY_H  
	_MLTrack.keycode = KEY_U  
	_MRTrack.keycode = KEY_I  
	_RTrack.keycode = KEY_L  
	
func _process(delta: float) -> void:
	
	if Input.is_action_just_pressed("Calibrate"):
		$RIndex.min_value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "INDEX_FINGER_TIP", "RIGHT_HAND")
		$RMiddle.min_value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "MIDDLE_FINGER_TIP", "RIGHT_HAND")
		$RRing.min_value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "RING_FINGER_TIP", "RIGHT_HAND")
		$RPinky.min_value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "PINKY_TIP", "RIGHT_HAND")
		$LIndex.min_value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "INDEX_FINGER_TIP", "LEFT_HAND")
		$LMiddle.min_value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "MIDDLE_FINGER_TIP", "LEFT_HAND")
		$LRing.min_value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "RING_FINGER_TIP", "LEFT_HAND")
		$LPinky.min_value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "PINKY_TIP", "LEFT_HAND")
	
	if Input.is_action_just_released("Calibrate"):
		$RIndex.max_value = 0.9/WebcamSocket.get_landmark_distance("THUMB_TIP", "INDEX_FINGER_TIP", "RIGHT_HAND")
		$RMiddle.max_value = 0.9/WebcamSocket.get_landmark_distance("THUMB_TIP", "MIDDLE_FINGER_TIP", "RIGHT_HAND")
		$RRing.max_value = 0.9/WebcamSocket.get_landmark_distance("THUMB_TIP", "RING_FINGER_TIP", "RIGHT_HAND")
		$RPinky.max_value = 0.8/WebcamSocket.get_landmark_distance("THUMB_TIP", "PINKY_TIP", "RIGHT_HAND")
		$LIndex.max_value = 0.9/WebcamSocket.get_landmark_distance("THUMB_TIP", "INDEX_FINGER_TIP", "LEFT_HAND")
		$LMiddle.max_value = 0.9/WebcamSocket.get_landmark_distance("THUMB_TIP", "MIDDLE_FINGER_TIP", "LEFT_HAND")
		$LRing.max_value = 0.9/WebcamSocket.get_landmark_distance("THUMB_TIP", "RING_FINGER_TIP", "LEFT_HAND")
		$LPinky.max_value = 0.8/WebcamSocket.get_landmark_distance("THUMB_TIP", "PINKY_TIP", "LEFT_HAND")
		
	$RIndex.value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "INDEX_FINGER_TIP", "RIGHT_HAND")
	$RMiddle.value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "MIDDLE_FINGER_TIP", "RIGHT_HAND")
	$RRing.value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "RING_FINGER_TIP", "RIGHT_HAND")
	$RPinky.value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "PINKY_TIP", "RIGHT_HAND")
	$LIndex.value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "INDEX_FINGER_TIP", "LEFT_HAND")
	$LMiddle.value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "MIDDLE_FINGER_TIP", "LEFT_HAND")
	$LRing.value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "RING_FINGER_TIP", "LEFT_HAND")
	$LPinky.value = 1/WebcamSocket.get_landmark_distance("THUMB_TIP", "PINKY_TIP", "LEFT_HAND")
	
	if $RIndex.value >= $RIndex.max_value and not _LTrack.pressed: 
		print("press")
		_LTrack.pressed = true # Simulate a key press
		get_tree().root.push_input(_LTrack) # Push the event to the Viewport
	elif $RIndex.value < $RIndex.max_value and _LTrack.pressed:
		print("release")
		_LTrack.pressed = false
		get_tree().root.push_input(_LTrack)
