from py4godot.classes import gdclass
from py4godot.classes.core import Vector2, Rect2
from py4godot.classes.Button import Button

@gdclass
class button(Button):
	def _ready(self) -> None:
		print("hello")
	
	
	def _pressed(self) -> None:
		print("Pressed")

	def _has_point(self, point):
		return Rect2.new3(Vector2.new0(), self.get_size()).has_point(point)
