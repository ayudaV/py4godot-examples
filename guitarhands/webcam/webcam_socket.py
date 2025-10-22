from py4godot.classes import gdclass
from py4godot.classes.Image import Image
from py4godot.classes.ImageTexture import ImageTexture
from py4godot.classes.core import Array, PackedByteArray
from py4godot.classes.Node import Node
import cv2
import mediapipe as mp
import numpy as np

FORMAT_RGB8 = 4

@gdclass
class webcam_socket(Node):
	def _ready(self, camera_index: int = 0) -> None:
		self.camera_index = camera_index
		self.image_quality = 90  # JPEG quality
		self.cap = cv2.VideoCapture(self.camera_index)
		if not self.cap.isOpened():
			print(f"Error: cannot open camera index {self.camera_index}")
		# Initialize MediaPipe Hands once to avoid per-frame setup cost
		self._mp_hands = mp.solutions.hands
		self._mp_draw = mp.solutions.drawing_utils
		self._hands = self._mp_hands.Hands(
			model_complexity=1,
			min_detection_confidence=0.5,
			min_tracking_confidence=0.5,
		)

	def get_frame(self) -> np.ndarray:
		if not self.cap.isOpened():
			print(f"Error: cannot open camera index {self.camera_index}")
			return None
		ret, frame = self.cap.read()
		if not ret:
			print("Error: failed to capture image")
			return None
		return frame

	def get_image(self) -> ImageTexture:
		_image = Image.new()
		if not self.cap.isOpened():
			print(f"Error: cannot open camera index {self.camera_index}")
			return _image
		frame = self.get_frame()
		if frame is None:
			return _image

		# Convert BGR (OpenCV) to RGB (Godot expects RGB pixel data)
		frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		height, width = frame_rgb.shape[:2]
		frame_rgb = np.ascontiguousarray(frame_rgb, dtype=np.uint8)
		pba = PackedByteArray.from_memory_view(memoryview(frame_rgb))
		# Create image from raw RGB8 pixel data
		_image = Image.create_from_data(width, height, False, FORMAT_RGB8, pba)
		img_texture = ImageTexture.create_from_image(_image)
		return img_texture

	def get_handtracked_image(self) -> ImageTexture:
		"""
		Return an ImageTexture with hand landmarks drawn using MediaPipe Hands.
		- Captures a frame from the camera
		- Runs hand tracking (RGB input)
		- Draws landmarks on the frame (BGR)
		- Converts to RGB8 and returns as ImageTexture
		"""
		_image = Image.new()
		if not self.cap.isOpened():
			print(f"Error: cannot open camera index {self.camera_index}")
			return _image

		frame = self.get_frame()
		if frame is None:
			return _image

		# Prepare for MediaPipe (expects RGB, optionally flip for selfie view)
		image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		image_rgb = cv2.flip(image_rgb, 1)
		image_rgb.flags.writeable = False
		results = self._hands.process(image_rgb)
		image_rgb.flags.writeable = True

		# Convert back to BGR for drawing
		image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

		# Draw landmarks
		if results and results.multi_hand_landmarks:
			for hand_landmarks in results.multi_hand_landmarks:
				self._mp_draw.draw_landmarks(
					image_bgr,
					hand_landmarks,
					self._mp_hands.HAND_CONNECTIONS,
				)

		# Convert to RGB for Godot and build ImageTexture
		frame_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
		height, width = frame_rgb.shape[:2]
		frame_rgb = np.ascontiguousarray(frame_rgb, dtype=np.uint8)
		pba = PackedByteArray.from_memory_view(memoryview(frame_rgb))
		_image = Image.create_from_data(width, height, False, FORMAT_RGB8, pba)
		img_texture = ImageTexture.create_from_image(_image)
		return img_texture
