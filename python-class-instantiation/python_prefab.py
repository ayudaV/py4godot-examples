
from py4godot.methods import private
from py4godot.signals import signal, SignalArg
from py4godot.classes import gdclass
from py4godot.classes.core import Vector3
from py4godot.classes.Node3D import Node3D

@gdclass
class python_prefab(Node3D):
	
	def test_method(self):
		return 1
