extends Node3D


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	%"PythonNode".called_from_godot_with_value("test value")
	
	var return_value = %"PythonNode".called_from_godot_return_value()
	print("Return value from Python:", return_value)

func called_from_python():
	print("called from python")
	return 1
