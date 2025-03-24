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
