extends Panel

@onready var _parent: Control = get_parent()
@onready var paint_control: Control = _parent.get_node(^"PaintControl")



func _ready() -> void:
	# Assign all of the needed signals for the option buttons.
	$ButtonUndo.pressed.connect(button_pressed.bind("undo_stroke"))
	$ButtonSave.pressed.connect(button_pressed.bind("save_picture"))
	$ButtonClear.pressed.connect(button_pressed.bind("clear_picture"))


func button_pressed(button_name: String) -> void:
	# If a brush mode button is pressed.
	var tool_name := ""
	var shape_name := ""

	if button_name == "mode_pencil":
		paint_control.brush_mode = paint_control.BrushMode.PENCIL
		tool_name = "Pencil"

	# If a opperation button is pressed
	elif button_name == "clear_picture":
		paint_control.brush_data_list.clear()
		paint_control.queue_redraw()
	elif button_name == "save_picture":
		var number = paint_control.evaluate_image()
		$PredictedNumber.text = str(number);
		print("number:", number)
	elif button_name == "undo_stroke":
		paint_control.undo_stroke()


func brush_color_changed(color: Color) -> void:
	# Change the brush color to whatever color the color picker is.
	paint_control.brush_color = color


func background_color_changed(color: Color) -> void:
	# Change the background color to whatever colorthe background color picker is.
	get_parent().get_node(^"DrawingAreaBG").modulate = color
	paint_control.bg_color = color
	# Because of how the eraser works we also need to redraw the paint control.
	paint_control.queue_redraw()


func brush_size_changed(value: float) -> void:
	# Change the size of the brush, and update the label to reflect the new value.
	paint_control.brush_size = ceilf(value)
