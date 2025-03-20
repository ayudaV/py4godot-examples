extends Node3D

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# Load the scene
	var scene = load("res://python_prefab.tscn")
	
	# Check if scene is loaded properly
	if scene == null or not (scene is PackedScene):
		print("Error: Failed to load scene or scene is not a PackedScene.")
		return
	
	# Instantiate the scene
	var instance = scene.instantiate()
	
	# Check if instantiation was successful
	if instance == null:
		print("Error: Failed to instantiate scene.")
		return
	
	# Add the instance as a child
	add_child(instance)
	
	# Get the Python child
	var python_node = instance.get_node_or_null("PythonNode")
	
	var python_ret_val = python_node.test_method() #Here we are calling a method from our Python class
	print("Value from Python:", python_ret_val)
	
