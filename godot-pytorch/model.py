import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os
import sys

class StderrRedirector:
	def write(self, message = ""):
		# Replace this with logging or printing inside Godot if needed
		if message:
			print_error(f"[Captured stderr]: {message}", end="")
	@staticmethod
	def flush():
		pass  # Required for compatibility

sys.stderr = StderrRedirector

# Set random seed for reproducibility
torch.manual_seed(42)

# Define hyperparameters
BATCH_SIZE = 64
EPOCHS = 10
LEARNING_RATE = 0.001
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_SAVE_PATH = "models"  # Directory to save models

# Define the CNN model
class MNISTNet(nn.Module):
	def __init__(self):
		super(MNISTNet, self).__init__()
		# First convolutional layer: 1 input channel (grayscale), 32 output channels, 3x3 kernel
		self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
		self.bn1 = nn.BatchNorm2d(32)
		# Second convolutional layer: 32 input channels, 64 output channels, 3x3 kernel
		self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
		self.bn2 = nn.BatchNorm2d(64)
		# Third convolutional layer: 64 input channels, 64 output channels, 3x3 kernel
		self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
		self.bn3 = nn.BatchNorm2d(64)

		# Fully connected layers
		self.fc1 = nn.Linear(3 * 3 * 64, 128)
		self.dropout1 = nn.Dropout(0.5)
		self.fc2 = nn.Linear(128, 10)

	def forward(self, x):
		# First convolutional block
		x = self.bn1(self.conv1(x))
		x = F.relu(x)
		x = F.max_pool2d(x, 2)

		# Second convolutional block
		x = self.bn2(self.conv2(x))
		x = F.relu(x)
		x = F.max_pool2d(x, 2)

		# Third convolutional block
		x = self.bn3(self.conv3(x))
		x = F.relu(x)
		x = F.max_pool2d(x, 2)

		# Flatten the feature maps
		x = x.view(-1, 3 * 3 * 64)

		# Fully connected layers
		x = self.fc1(x)
		x = F.relu(x)
		x = self.dropout1(x)
		x = self.fc2(x)

		return F.log_softmax(x, dim=1)
# Function to load model
def load_model(model, optimizer=None, filepath=None):
	if filepath is None:
		filepath = os.path.join(MODEL_SAVE_PATH, "mnist_cnn_best.pt")

	if not os.path.exists(filepath):
		print(f"No saved model found at {filepath}")
		return model, optimizer, 0, 0

	# Load checkpoint
	checkpoint = torch.load(filepath)

	# Load model state
	model.load_state_dict(checkpoint['model_state_dict'])

	# Load optimizer state if provided
	if optimizer is not None and 'optimizer_state_dict' in checkpoint:
		optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

	# Get metadata
	epoch = checkpoint.get('epoch', 0)
	accuracy = checkpoint.get('accuracy', 0)

	print(f"Loaded model from {filepath} (Epoch: {epoch}, Accuracy: {accuracy:.2f}%)")
	return model, optimizer, epoch, accuracy

# Function to use a trained model for prediction
def predict_digit(model, image_tensor):
	model.eval()
	with torch.no_grad():
		# Make sure the image is properly formatted (1, 1, 28, 28)
		if image_tensor.dim() == 3:  # Add batch dimension if missing
			image_tensor = image_tensor.unsqueeze(0)

		# Move to the same device as model
		image_tensor = image_tensor.to(next(model.parameters()).device)

		# Get prediction
		output = model(image_tensor)
		prediction = output.argmax(dim=1, keepdim=True)

		# Get probability distribution
		probabilities = torch.exp(output)

		return prediction.item(), probabilities[0]

def preprocess_image(image_array):
	"""
	Convert a heightxwidth list into a PyTorch tensor with the expected format.
	"""
	# Convert list to numpy array if needed
	if isinstance(image_array, list):
		image_array = np.array(image_array, dtype=np.float32)

	# Normalize (assuming input is in range 0-255)
	image_array = image_array / 255.0

	# Convert to tensor and add batch dimension
	transform = transforms.Compose([
		transforms.ToTensor(),  # Converts (H, W) -> (1, H, W) and normalizes
		transforms.Normalize((0.1307,), (0.3081,))  # MNIST mean and std
	])

	image = transform(image_array).unsqueeze(0)  # Add batch dimension (1, 1, 28, 28)
	return image.to(DEVICE)


def evaluate_custom_image(image_array):
	"""
	Evaluate a custom image on the trained model.
	"""
	# Load model
	model = MNISTNet().to(DEVICE)
	model, _, _, _ = load_model(model)

	model.eval()  # Set model to evaluation mode
	image = preprocess_image(image_array)
	print(image.shape)

	with torch.no_grad():
		output = model(image)
		probabilities = torch.nn.functional.softmax(output, dim=1)
		predicted_digit = torch.argmax(probabilities, dim=1).item()

	print(f"Predicted digit: {predicted_digit}")
	print("Probability distribution:")
	for i, prob in enumerate(probabilities.squeeze()):
		print(f"Digit {i}: {prob.item():.4f}")

	return predicted_digit, probabilities.squeeze().cpu().numpy()
