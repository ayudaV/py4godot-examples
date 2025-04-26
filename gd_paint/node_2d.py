import cv2
import model
import numpy as np
from py4godot.classes import gdclass
from py4godot.classes.Image import Image
from py4godot.classes.Node2D import Node2D
import matplotlib.pyplot as plt

@gdclass
class node_2d(Node2D):

	def evaluate_image(self, image: Image):
		"""
		Process and evaluate an image containing a digit.
		Uses a more conservative approach that preserves more original image characteristics.
		
		Args:
			image (Image): The input image to be evaluated
			
		Returns:
			The evaluation result from PyTorch model
		"""
		# Get image dimensions
		width = image.get_width()
		height = image.get_height()
		print(f"Original Image Size: {width} x {height}")
		
		# Extract image data safely
		data = image.get_data()
		array_from_data = np.frombuffer(data.get_memory_view(), dtype=np.uint8)
		
		# Reshape data properly to get correct image representation
		array_from_data_reshaped = array_from_data.reshape((height, width, 4))
		img_array = array_from_data_reshaped[:, :, :3]  # Extract RGB channels
		
		# Convert to grayscale
		grayscale_array = np.mean(img_array, axis=2).astype(np.uint8)
		
		# Find the bounding box just for centering purposes
		_, thresh = cv2.threshold(grayscale_array, 50, 255, cv2.THRESH_BINARY_INV)
		coords = cv2.findNonZero(thresh)
		
		# Handle case where no non-zero pixels are found
		if coords is None or len(coords) == 0:
			print("No digit detected in the image")
			return None
		
		x, y, w, h = cv2.boundingRect(coords)
		
		# Option 1: Use the full original image, just resized to 28x28
		# This preserves aspect ratio but might make digits too small
		resized_full = cv2.resize(grayscale_array, (28, 28), interpolation=cv2.INTER_AREA)
		
		# Option 2: Center the digit in a square canvas with significant padding
		# This approach keeps more context while ensuring the digit is centered
		
		# Find the center of the digit
		center_x = x + w // 2
		center_y = y + h // 2
		
		# Determine the size of the square region to extract (the larger of width or height, plus padding)
		size = max(w, h)
		square_size = int(size * 1.8)  # 80% extra padding around the digit
		
		# Calculate square boundaries
		half_size = square_size // 2
		square_x1 = max(0, center_x - half_size)
		square_y1 = max(0, center_y - half_size)
		square_x2 = min(width, center_x + half_size)
		square_y2 = min(height, center_y + half_size)
		
		# Extract the square region
		square_region = grayscale_array[square_y1:square_y2, square_x1:square_x2]
		
		# Create a square canvas with black background
		canvas_size = max(square_region.shape)
		square_canvas = np.zeros((canvas_size, canvas_size), dtype=np.uint8)
		
		# Paste the square region onto the canvas
		offset_y = (canvas_size - square_region.shape[0]) // 2
		offset_x = (canvas_size - square_region.shape[1]) // 2
		square_canvas[offset_y:offset_y+square_region.shape[0], offset_x:offset_x+square_region.shape[1]] = square_region
		
		# Resize to 28x28
		resized_img = cv2.resize(square_canvas, (28, 28), interpolation=cv2.INTER_AREA)
		
		# Invert image (ensure white digit on black background for MNIST compatibility)
		inverted_img = 255 - resized_img
		
		# Optional: Apply slight Gaussian blur to reduce noise (can help some models)
		# blurred_img = cv2.GaussianBlur(inverted_img, (3, 3), 0)
		
		# Convert to format expected by PyTorch model
		processed_img = inverted_img.reshape(28, 28).tolist()
		
		# Send to PyTorch evaluation
		return self.evaluate_with_pytorch(processed_img)
	def evaluate_with_pytorch(self, pixels):
		result = model.evaluate_custom_image(pixels)
		print(f"result:{result}")
		return result[0]
		#return predicted_digit  # Return the prediction if needed
				
