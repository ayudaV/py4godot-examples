
# MNIST Digit Evaluation from Godot Paint


This example is based on the `Godot Paint` project. In this setup, we allow the user to draw digits, which are then evaluated by a PyTorch model that has been trained on the MNIST dataset.

## Demo
Here you can see a demo of the application in action.
![Aufzeichnung 2025-04-26 180919(1)](https://github.com/user-attachments/assets/c981434c-d745-429b-beae-aa034d2bf2fc)


## Python Evaluation Function

```python
def evaluate_image(self, image: Image):
    """
    Process and evaluate an image containing a digit.
    Uses a conservative approach that preserves more of the original image characteristics.

    Args:
        image (Image): The input image to be evaluated.

    Returns:
        The evaluation result from the PyTorch model.
    """
    # Extract image data safely
    data = image.get_data()
    array_from_data = np.frombuffer(data.get_memory_view(), dtype=np.uint8)

    # Reshape data properly to get the correct image representation
    array_from_data_reshaped = array_from_data.reshape((image.get_height(), image.get_width(), 4))
    img_array = array_from_data_reshaped[:, :, :3]  # Extract RGB channels (ignore alpha)

    # Convert to grayscale
    grayscale_array = np.mean(img_array, axis=2).astype(np.uint8)

    # Find the bounding box for centering the digit
    _, thresh = cv2.threshold(grayscale_array, 50, 255, cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(thresh)

    # Handle the case where no non-zero pixels are found
    if coords is None or len(coords) == 0:
        print("No digit detected in the image")
        return None

    x, y, w, h = cv2.boundingRect(coords)

    # Compute the center of the digit
    center_x = x + w // 2
    center_y = y + h // 2

    # Determine the size of the square region to extract (with padding)
    size = max(w, h)
    square_size = int(size * 1.8)  # Add 80% padding around the digit

    # Calculate square region boundaries
    half_size = square_size // 2
    square_x1 = max(0, center_x - half_size)
    square_y1 = max(0, center_y - half_size)
    square_x2 = min(image.get_width(), center_x + half_size)
    square_y2 = min(image.get_height(), center_y + half_size)

    # Extract the square region
    square_region = grayscale_array[square_y1:square_y2, square_x1:square_x2]

    # Create a square canvas with a black background
    canvas_size = max(square_region.shape)
    square_canvas = np.zeros((canvas_size, canvas_size), dtype=np.uint8)

    # Paste the extracted region into the center of the canvas
    offset_y = (canvas_size - square_region.shape[0]) // 2
    offset_x = (canvas_size - square_region.shape[1]) // 2
    square_canvas[offset_y:offset_y+square_region.shape[0], offset_x:offset_x+square_region.shape[1]] = square_region

    # Resize to 28x28 pixels (MNIST standard)
    resized_img = cv2.resize(square_canvas, (28, 28), interpolation=cv2.INTER_AREA)

    # Invert image: ensure white digit on black background for MNIST compatibility
    inverted_img = 255 - resized_img

    # Prepare image format expected by PyTorch model
    processed_img = np.array(inverted_img.reshape(28, 28), dtype=np.float32)

    results = model.evaluate_custom_image(processed_img)
    return results[0]
```

## Explanation

The `evaluate_image` function is the entry point for processing and classifying the image drawn in Godot. Let's break it down further:

```python
    # Extract image data safely
    data = image.get_data()
    array_from_data = np.frombuffer(data.get_memory_view(), dtype=np.uint8)

    # Reshape data properly to get correct image representation
    array_from_data_reshaped = array_from_data.reshape((image.get_height(), image.get_width(), 4))
    img_array = array_from_data_reshaped[:, :, :3]  # Extract RGB channels
```

Here we are converting the Godot `Image` object into a NumPy array. Be **careful**: the `data` object is a `memory_view`, so it must remain valid while you're accessing its contents—if it goes out of scope, `np.frombuffer` might produce invalid results.

After retrieving the raw buffer, we reshape the one-dimensional array into a 3D shape that corresponds to `[height, width, 4]`, where 4 represents the RGBA channels. Since we only need the RGB data, we slice out the first three channels.

### Additional Notes

- **Grayscale conversion**: We average the RGB channels to get a grayscale image, which simplifies the image while preserving the digit structure.
- **Bounding box**: The thresholding and `cv2.findNonZero` are used to find where the digit is in the image. This allows us to center it on a square canvas.
- **Padding and resizing**: The digit is padded for better visual balance and then resized to 28x28 pixels—the standard MNIST input size.
- **Inversion**: MNIST digits are white on black, so we invert the colors to match that format.
- **Model inference**: Finally, the processed image is passed into the neural network for prediction.
