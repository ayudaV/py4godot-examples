from py4godot.classes.Image import Image
from py4godot.methods import private
from py4godot.signals import signal, SignalArg
from py4godot.classes import gdclass
from py4godot.classes.core import Vector3
from py4godot.classes.Node2D import Node2D
from py4godot.utils.print_tools import print_error
import numpy as np
import torch
import torch.nn as nn
import cv2
import sys
import io
import model


@gdclass
class node_2d(Node2D):
	import numpy as np
	import cv2

	def evaluate_image(self, image:Image):
		print(f"Original Image Size: {image.get_width()} x {image.get_height()}")

		array_from_data = np.frombuffer(image.get_data().get_memory_view(), dtype=np.uint8)
		array_from_data_reshaped = array_from_data.reshape((-1,4))
		img_array = array_from_data_reshaped[:, :3]
		# **Step 1: Find the bounding box of the digit**
		_, thresh = cv2.threshold(img_array, 50, 255, cv2.THRESH_BINARY_INV)  # Invert: Black background, white text
		coords = cv2.findNonZero(thresh)  # Find all non-zero pixels
		x, y, w, h = cv2.boundingRect(coords)  # Get bounding box

		# **Step 2: Crop the digit**
		#cropped_digit = img_array[y:y + h, x:x + w]

		# **Step 3: Resize the cropped digit to 28x28**
		resized_img = cv2.resize(img_array, (28, 28), interpolation=cv2.INTER_AREA)

		inverted_img = 255 - resized_img

		# Convert image to list
		pixels_list = inverted_img.tolist()

		# Send to PyTorch evaluation
		return self.evaluate_with_pytorch(pixels_list)

	def evaluate_with_pytorch(self, pixels):
		result = model.evaluate_custom_image(pixels)
		print(f"result:{result}")
		return result[0]
		#return predicted_digit  # Return the prediction if needed
				
