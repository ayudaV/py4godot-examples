from py4godot.classes.AnimatedSprite2D import AnimatedSprite2D
from py4godot.classes.RigidBody2D import RigidBody2D
from py4godot.classes.core import Array
from py4godot.classes import gdclass
from py4godot.utils.print_tools import print_error

@gdclass
class mob(RigidBody2D):
	def _ready(self):
		sprite:AnimatedSprite2D = self.get_node("AnimatedSprite2D")
		sprite.play()
		mob_types:Array = Array.new8(sprite.sprite_frames.get_animation_names())
		sprite.animation = mob_types.pick_random()

	def _on_VisibilityNotifier2D_screen_exited(self):
		self.queue_free()
