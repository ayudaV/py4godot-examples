import math
import random
from py4godot.classes import gdclass
from py4godot.classes.AudioStreamPlayer import AudioStreamPlayer
from py4godot.classes.CanvasLayer import CanvasLayer
from py4godot.classes.Marker2D import Marker2D
from py4godot.classes.Node import Node
from py4godot.classes.Node2D import Node2D
from py4godot.classes.PackedScene import PackedScene
from py4godot.classes.PathFollow2D import PathFollow2D
from py4godot.classes.ResourceLoader import ResourceLoader
from py4godot.classes.RigidBody2D import RigidBody2D
from py4godot.classes.Timer import Timer
from py4godot.classes.core import StringName, NodePath, Vector2
from py4godot.utils.utils import get_tree

from python_scripts.hud import hud

mob_scene_path: str = "res://pymob.tscn"


def load_mob_scene(path):
	resource = ResourceLoader.instance().load(path)
	mob_scene: PackedScene = PackedScene.cast(resource)
	return mob_scene


@gdclass
class main(Node):
	def _ready(self):
		self.score = 0
		self._score_timer = Timer.cast(self.get_node(NodePath.new2("ScoreTimer")))
		self._start_timer = Timer.cast(self.get_node(NodePath.new2("StartTimer")))
		self._mob_timer = Timer.cast(self.get_node(NodePath.new2("MobTimer")))
		self._music = AudioStreamPlayer.cast(self.get_node(NodePath.new2("Music")))
		self._death_sound = AudioStreamPlayer.cast(self.get_node(NodePath.new2("DeathSound")))
		self._hud = CanvasLayer.cast(self.get_node(NodePath.new2("HUD")))
		self._start_position = Marker2D.cast(self.get_node(NodePath.new2("StartPosition")))
		self._mob_scene = load_mob_scene(mob_scene_path)
		self._player = self.get_node(NodePath.new2("Player")).get_pyscript()
		self.create_mob()
	
	def create_mob(self):
		val = self._mob_scene.instantiate()
		return val

	def game_over(self):
		self._mob_timer.stop()
		self._score_timer.stop()
		self._hud.get_pyscript().show_game_over()
		self._music.stop()
		self._death_sound.play()

	def new_game(self):
		get_tree(self).call_group(StringName.new2("mobs"),
								   StringName.new2("queue_free"))
		self.score = 0
		self._player.start(self._start_position.position)
		self._start_timer.start()
		self._hud.get_pyscript().update_score(self.score)
		self._hud.get_pyscript().show_message("Get Ready")
		self._music.play()

	def _on_MobTimer_timeout(self):
		mob = RigidBody2D.cast(self.create_mob())
		mob_spawn_location = PathFollow2D.cast(self.get_node(NodePath.new2("MobPath/MobSpawnLocation")))
		mob_spawn_location.progress_ratio = random.random()
		mob.position = mob_spawn_location.position
		direction: float = mob_spawn_location.rotation + math.pi/2
		velocity: Vector2 = Vector2.new3(random.random()*100 + 150, 0)
		mob.linear_velocity = velocity.rotated(direction)
		self.add_child(mob)

	def _on_ScoreTimer_timeout(self):
		self.score += 1
		self._hud.get_pyscript().update_score(self.score)

	def on_StartTimer_timeout(self):
		self._mob_timer.start()
		self._score_timer.start()
