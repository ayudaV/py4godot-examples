# Godot-Python-Interaction

This project showcases the interaction between Godot and Python using `py4godot`. It provides an example of how Python scripts can extend functionality and enable communication between the two environments.

## Project Overview

This project consists of the following key components:

- **`gd_node.gd`**: A Godot script responsible for calling Python methods and handling their returned values.
- **`python_node.py`**: A Python script that defines a custom `Node3D` class with methods that can be invoked from Godot.

## Godot Script (`gd_node.gd`)

The `gd_node.gd` script interacts with the Python script by invoking its methods and printing their outputs:

```gdscript
extends Node3D


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	%"PythonNode".called_from_godot_with_value("test value")
	
	var return_value = %"PythonNode".called_from_godot_return_value()
	print("Return value from Python:", return_value)

func called_from_python():
	print("called from python")
	return 1

```

### Functionality
- Calls `called_from_godot_with_value(42)`, which prints the received value in Python.
- Calls `called_from_godot_return_value()`, which returns a `Vector3` object to Godot and prints the result.

## Python Script (`python_node.py`)

The `python_node.py` script provides Python-side functionality for interaction with Godot:

```python
from py4godot.classes import gdclass
from py4godot.classes.core import Vector3
from py4godot.classes.Node3D.Node3D import Node3D

@gdclass
class python_node(Node3D):	
	def called_from_godot_with_value(self, value):
		print(f"Called from godot with value: {value}")
	
	def called_from_godot_return_value(self):
		value = Vector3.new3(1,2,3)
		print(f"called from godot returned {value}")
		return value
```

### Functionality
- **`called_from_godot_with_value(value)`**: Accepts a parameter from Godot and prints it in the Python console.
- **`called_from_godot_return_value()`**: Generates a `Vector3` object in Python, prints it, and returns it to Godot.
