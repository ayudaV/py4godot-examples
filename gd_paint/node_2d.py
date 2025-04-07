
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

	def evaluate_image(self, image):
		print(f"Original Image Size: {image.get_width()} x {image.get_height()}")


		img_array = np.zeros((image.get_height(), image.get_width(), 1), dtype=np.uint8)

		for y in range(image.get_height()):
			for x in range(image.get_width()):
				color = image.get_pixel(x, y)
				val = color.to_rgba32()
				# Assuming val contains your 32-bit RGBA value
				r = (val >> 24) & 0xFF  # Extract red component
				g = (val >> 16) & 0xFF  # Extract green component
				b = (val >> 8) & 0xFF  # Extract blue component
				a = val & 0xFF  # Extract alpha component

				# Now r, g, b, and a contain the individual components
				#print(f"Red: {r}, Green: {g}, Blue: {b}, Alpha: {a}")
				normalized_val = (r +g +b) / 3
				img_array[y][x] = normalized_val
		print(img_array.shape)

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
		self.evaluate_with_pytorch(pixels_list)

	def evaluate_with_pytorch(self, pixels):
		model.evaluate_custom_image(pixels)
		#return predicted_digit  # Return the prediction if needed
				
