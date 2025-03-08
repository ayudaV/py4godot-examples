from py4godot import signal
from py4godot.classes import gdclass
from py4godot.classes.Area2D import Area2D
from py4godot.classes.Input import Input
from py4godot.classes.core import Vector2, NodePath


@gdclass
class player(Area2D):
	hit = signal([])
	speed = 400  # How fast the player will move (pixels/sec)
	screen_size = None  # Size of the game window
	hello = 5

	def _ready(self) -> None:
		self.screen_size = self.get_viewport_rect().size
		self.hide()
		self._input_singleton = Input.instance()

	def _process(self, delta: float) -> None:
		zero = Vector2.new3(0,0)
		velocity = zero  # The player's movement vector
		_input = self._input_singleton
		if _input.is_action_pressed("move_right"):
			velocity.x += 1
		if _input.is_action_pressed("move_left"):
			velocity.x -= 1
		if _input.is_action_pressed("move_down"):
			velocity.y += 1
		if _input.is_action_pressed("move_up"):
			velocity.y -= 1
		if velocity.length() > 0:
			velocity = velocity.normalized() * self.speed
			sprite = self.get_node("AnimatedSprite2D")
			sprite.play("")
		else:
			self.get_node("AnimatedSprite2D").stop()

		self.position += velocity * delta
		self.position = self.position.clamp(zero, self.screen_size)

		animated_sprite = self.get_node("AnimatedSprite2D")
		trail = self.get_node("Trail")

		if velocity.x != 0:
			animated_sprite.animation = "right"
			animated_sprite.flip_v = False
			trail.rotation = 0
			animated_sprite.flip_h = velocity.x < 0
		elif velocity.y != 0:
			animated_sprite.animation = "up"
			self.rotation = 3.14159 if velocity.y > 0 else 0

	def start(self, pos: Vector2) -> None:
		self.position = pos
		self.rotation = 0
		self.show()
		self.get_node("CollisionShape2D").disabled = False

	def _on_body_entered(self, _body) -> None:
		self.hide()  # Player disappears after being hit
		self.hit.emit()

		# Must be deferred as we can't change physics properties on a physics callback
		self.get_node(NodePath.new2("CollisionShape2D")).set_deferred("disabled", True)
