from py4godot.classes import gdclass
from py4godot.classes.core import Vector2, Rect2
from py4godot.classes.Button import Button

@gdclass
class button(Button):
	def _has_point(self, point):
		return Rect2.new3(Vector2.new0(), self.get_size()).has_point(point)

	# This works handles clicks, when connecting the signal pressed()
	def _on_pressed(self):
		print("Hello world")
	
	# You could also do it like this, if you don't want to connect the signal pressed()
	# def _pressed(self):
	# 	print("Hello world")
