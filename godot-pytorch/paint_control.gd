extends Control


# A constant for whether or not we're needing to undo a shape.
const UNDO_MODE_SHAPE = -2
# A constant for whether or not we can undo.
const UNDO_NONE = -1

# A list to hold all of the dictionaries that make up each brush.
var brush_data_list: Array[Dictionary] = []

# A boolean to hold whether or not the mouse is inside the drawing area, the mouse position last _process call
# and the position of the mouse when the left mouse button was pressed.
var is_mouse_in_drawing_area := false
var last_mouse_pos := Vector2()
var mouse_click_start_pos := Vector2.INF

# A boolean to tell whether we've set undo_elements_list_num, which holds the size of draw_elements_list
# before a new stroke is added (unless the current brush mode is 'rectangle shape' or 'circle shape', in
# which case we do things a litte differently. See the undo_stroke function for more details).
var undo_set := false
var undo_element_list_num := -1

# The current brush settings: The mode, size, color, and shape we have currently selected.
var brush_size := 32
var brush_color := Color.BLACK

# The color of the background. We need this for the eraser (see the how we handle the eraser
# in the _draw function for more details).
var bg_color := Color.WHITE

@onready var drawing_area: Panel = $"../DrawingAreaBG"
@onready var image_evaluator: Node2D = $"../Evaluator"

func _process(_delta: float) -> void:
	var mouse_pos := get_viewport().get_mouse_position()

	# Check if the mouse is currently inside the canvas/drawing-area.
	var drawing_area_rect := Rect2(drawing_area.position, drawing_area.size)
	is_mouse_in_drawing_area = drawing_area_rect.has_point(mouse_pos)

	if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		# If we do not have a position for when the mouse was first clicked, then this must
		# be the first time is_mouse_button_pressed has been called since the mouse button was
		# released, so we need to store the position.
		if mouse_click_start_pos.is_equal_approx(Vector2.INF):
			mouse_click_start_pos = mouse_pos

		# If the mouse is inside the canvas and the mouse is 1px away from the position of the mouse last _process call.
		if check_if_mouse_is_inside_canvas():
			if mouse_pos.distance_to(last_mouse_pos) >= 1:
				if undo_set == false:
					undo_set = true
					undo_element_list_num = brush_data_list.size()
				# Add the brush object to draw_elements_array.
				add_brush(mouse_pos)

	else:
		# We've finished our stroke, so we can set a new undo (if a new storke is made).
		undo_set = false

		# Since we've released the left mouse, we need to get a new mouse_click_start_pos next time
		# is_mouse_button_pressed is true.
		mouse_click_start_pos = Vector2.INF

	# Store mouse_pos as last_mouse_pos now that we're done with _process.
	last_mouse_pos = mouse_pos


func check_if_mouse_is_inside_canvas() -> bool:
	# Make sure we have a mouse click starting position.
	if mouse_click_start_pos != null:
		# Make sure the mouse click starting position is inside the canvas.
		# This is so if we start out click outside the canvas (say chosing a color from the color picker)
		# and then move our mouse back into the canvas, it won't start painting.
		if Rect2(drawing_area.position, drawing_area.size).has_point(mouse_click_start_pos):
			# Make sure the current mouse position is inside the canvas.
			if is_mouse_in_drawing_area:
				return true
	return false


func undo_stroke() -> void:
	# Only undo a stroke if we have one.
	if undo_element_list_num == UNDO_NONE:
		return

	# Figure out how many elements/brushes we've added in the last stroke.
	var elements_to_remove := brush_data_list.size() - undo_element_list_num
	# Remove all of the elements we've added this in the last stroke.
	for _elment_num in elements_to_remove:
		brush_data_list.pop_back()

	# Now that we've undone a stoke, we cannot undo again until another stoke is added.
	undo_element_list_num = UNDO_NONE

	# Redraw the brushes.
	queue_redraw()


func add_brush(mouse_pos: Vector2) -> void:
	# Make new brush dictionary that will hold all of the data we need for the brush.
	var new_brush := {}

	# Populate the dictionary with values based on the global brush variables.
	# We will override these as needed if the brush is a rectange or circle.
	new_brush.brush_pos = mouse_pos
	new_brush.brush_size = brush_size
	new_brush.brush_color = brush_color


	# Add the brush and update/draw all of the brushes.
	brush_data_list.append(new_brush)
	queue_redraw()


func _draw() -> void:
	for brush in brush_data_list:
		draw_circle(brush.brush_pos, brush.brush_size / 2, brush.brush_color)


func evaluate_image():
	print("evalutate")
	var img := get_viewport().get_texture().get_image()
	var cropped_image := img.get_region(Rect2(drawing_area.position, drawing_area.size))

	var number = image_evaluator.evaluate_image(cropped_image)
	return number
