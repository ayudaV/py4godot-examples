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
		# Initialize MediaPipe Pose to infer handedness from wrist positions
		self._mp_pose = mp.solutions.pose
		self._pose = self._mp_pose.Pose(
			model_complexity=1,
			min_detection_confidence=0.5,
			min_tracking_confidence=0.5,
		)
		# Storage for last computed hand labels via pose ('Left'/'Right')
		self._last_hand_labels = []
		self._last_hand_landmarks = []

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

		# Also run pose on the same flipped RGB image to get wrist reference points
		pose_res = self._pose.process(image_rgb)

		# Determine hand labels ('Left'/'Right') by nearest pose wrist
		self._last_hand_labels = []
		left_wrist_xy = None
		right_wrist_xy = None
		if pose_res and getattr(pose_res, 'pose_landmarks', None):
			try:
				lw = pose_res.pose_landmarks.landmark[self._mp_pose.PoseLandmark.LEFT_WRIST.value]
				left_wrist_xy = (lw.x, lw.y)
			except Exception:
				left_wrist_xy = None
			try:
				rw = pose_res.pose_landmarks.landmark[self._mp_pose.PoseLandmark.RIGHT_WRIST.value]
				right_wrist_xy = (rw.x, rw.y)
			except Exception:
				right_wrist_xy = None

		# Convert back to BGR for drawing
		image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

		# Draw landmarks and compute labels
		self._last_hand_landmarks = []
		if results and results.multi_hand_landmarks:
			for hand_landmarks in results.multi_hand_landmarks:
				self._mp_draw.draw_landmarks(
					image_bgr,
					hand_landmarks,
					self._mp_hands.HAND_CONNECTIONS,
				)
				# Compute nearest pose wrist for this hand to label Left/Right
				try:
					hw = hand_landmarks.landmark[self._mp_hands.HandLandmark.WRIST.value]
					hw_xy = (hw.x, hw.y)
					# Compare squared distances to avoid sqrt
					d_left = None if left_wrist_xy is None else (hw_xy[0]-left_wrist_xy[0])**2 + (hw_xy[1]-left_wrist_xy[1])**2
					d_right = None if right_wrist_xy is None else (hw_xy[0]-right_wrist_xy[0])**2 + (hw_xy[1]-right_wrist_xy[1])**2
					label = 'Unknown'
					if d_left is not None and d_right is not None:
						label = 'Left' if d_left <= d_right else 'Right'
					elif d_left is not None:
						label = 'Left'
					elif d_right is not None:
						label = 'Right'
					self._last_hand_labels.append(label)
				except Exception:
					self._last_hand_labels.append('Unknown')
				# Keep a copy of landmarks in the same order as labels
				self._last_hand_landmarks.append(hand_landmarks)

		# Convert to RGB for Godot and build ImageTexture
		frame_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
		height, width = frame_rgb.shape[:2]
		frame_rgb = np.ascontiguousarray(frame_rgb, dtype=np.uint8)
		pba = PackedByteArray.from_memory_view(memoryview(frame_rgb))
		_image = Image.create_from_data(width, height, False, FORMAT_RGB8, pba)
		img_texture = ImageTexture.create_from_image(_image)
		return img_texture

	def get_hands_points_struct(self):
		"""
		Return a structure grouping landmarks by LEFT_HAND / RIGHT_HAND using the provided
		landmark names list. Each hand maps point name -> [x, y, z]. Example:
		{
			"LEFT_HAND": {"WRIST": [x,y,z], "THUMB_CMC": [x,y,z], ...},
			"RIGHT_HAND": { ... }
		}
		Only present keys for detected hands.
		"""
		# Names by index as provided
		point_names = [
			"WRIST",
			"THUMB_CMC",
			"THUMB_MCP",
			"THUMB_IP",
			"THUMB_TIP",
			"INDEX_FINGER_MCP",
			"INDEX_FINGER_PIP",
			"INDEX_FINGER_DIP",
			"INDEX_FINGER_TIP",
			"MIDDLE FINGER_MCP",
			"MIDDLE_FINGER_PIP",
			"MIDDLE FINGER_DIP",
			"MIDDLE FINGER_TIP",
			"RING FINGER_MCP",
			"RING FINGER_PIP",
			"RING FINGER_DIP",
			"RING FINGER_TIP",
			"PINKY_MCP",
			"PINKY_PIP",
			"PINKY_DIP",
			"PINKY_TIP",
		]

		result = {}
		labels = self._last_hand_labels or []
		hands = self._last_hand_landmarks or []
		for idx, hand_landmarks in enumerate(hands):
			label = 'Unknown'
			if idx < len(labels):
				label = labels[idx]
			key = 'LEFT_HAND' if label == 'Left' else ('RIGHT_HAND' if label == 'Right' else 'UNKNOWN_HAND')
			points_map = {}
			# 21 landmarks expected
			for i in range(min(21, len(hand_landmarks.landmark))):
				name = point_names[i] if i < len(point_names) else str(i)
				lm = hand_landmarks.landmark[i]
				points_map[name] = [lm.x, lm.y, lm.z]
			result[key] = points_map

		return result

	def get_hand_labels(self):
		"""
		Return a list of labels (strings) for the last-detected hands in order: ['Left', 'Right', ...].
		Labels are computed by comparing each hand's WRIST landmark to pose wrists.
		"""
		return self._last_hand_labels
