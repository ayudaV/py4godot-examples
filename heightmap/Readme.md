
# Height Map Generation Example

This project generates height maps in Python and visualizes them in Godot.

## Installation

Follow these steps to set up the project. If you have already run `setup_examples.py`, you can skip this section.

### Windows

1. **Clone this repository.**
2. **Open the project in Godot.**
3. **Download "Python for Godot" from the AssetLib.**  
    ![Python for Godot](https://github.com/user-attachments/assets/f3db74df-ec6c-49e6-9287-b79541b93178)
4. **Navigate to the appropriate directory based on your platform:**  
    `py4godot-examples\heightmap\addons\py4godot\cpython-3.12.4-windows64\python`
5. **Download and install `pip`**:
    - Download `get-pip.py` from: [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py)
    - Run the following command:
        
        ```shell
        python get-pip.py
        ```
        
6. **Install required dependencies:**
    
    ```shell
    python -m pip install numpy noise
    ```
    
7. **Run the project in Godot.** If everything is set up correctly, the demo should look like this: ![Demo](https://github.com/user-attachments/assets/70191611-57ce-44ee-8564-81acaba9594e)

---

## How It Works

### `height_map_creator.gd`

This script handles the height map display. Although it could be fully implemented in Python, a mix of GDScript and Python is used for demonstration purposes.
It looks like this:
```GDScript
@tool  
extends Node3D  
  
var heightmap_path = "res://heightmap_pillow.png"  
var displacement_factor = 10.0  
  
var vertices = PackedVector3Array()  
var heightmap = Image.new()  
  
var SCALE = 0.1  
var DISPLACEMENT = 2  
var generator_path:NodePath = "Generator"  
var generator:Node  
  
func _ready() -> void:  
    generator = get_node(generator_path)  
    generate_terrain_from_buffer()  
  
func generate_height_value(val:float):  
    return (val - 0.5) * DISPLACEMENT   
  
func add_triangles(current, left, bottom, bottom_left):  
    # first triangle  
    vertices.append(left)  
    vertices.append(current)  
    vertices.append(bottom)  
      
    # second triangle  
    vertices.append(left)  
    vertices.append(bottom)  
    vertices.append(bottom_left)  
      
  
func generate_triangles_for_pixel(x:int, y:int, image:Image):  
    var current = image.get_pixel(x,y).r  
    var left = image.get_pixel(x-1,y).r  
    var bottom = image.get_pixel(x,y+1).r  
    var bottom_left = image.get_pixel(x-1,y+1).r  
      
    var vertice_current = Vector3((x - image.get_width()/2)*SCALE, generate_height_value(current), (y - image.get_height()/2)*SCALE    )  
    var vertice_left = Vector3(vertice_current.x - 1 * SCALE, generate_height_value(left) ,vertice_current.z)  
    var vertice_bottom = Vector3(vertice_current.x, generate_height_value(bottom) ,vertice_current.z+1 * SCALE)  
    var vertice_bottom_left = Vector3(vertice_current.x - 1 * SCALE, generate_height_value(bottom_left) ,vertice_current.z+1 * SCALE)  
      
    add_triangles(vertice_current, vertice_left, vertice_bottom, vertice_bottom_left)  
      
func generate_terrain_from_buffer():  
    var width = 512  
    var height = 512  
      
    heightmap = Image.create(width, height, true, Image.FORMAT_RGB8)  
    generator.call("fill_height_map", width, height, heightmap)  
      
    for x in range(1, width):  
       for y in range(0, height - 1):  
          generate_triangles_for_pixel(x, y, heightmap)  
      
    var array_mesh = ArrayMesh.new()  
    var arrays = []  
    arrays.resize(Mesh.ARRAY_MAX)  
    arrays[Mesh.ARRAY_VERTEX] = vertices  
  
    array_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)  
  
    var terrain_mesh = MeshInstance3D.new()  
    terrain_mesh.mesh = array_mesh  
  
    var material = StandardMaterial3D.new()  
    material.albedo_color = Color(0.8, 0.8, 0.8)  # Set the color to gray (or any other color)  
    terrain_mesh.material_override = material  
    add_child(terrain_mesh)
```
#### Key Functions:

Here are the most important parts for us. The rest of the code is for handling the generated image and creating a heightmap from it.

- **Initialization:**
    
    ```gdscript
    func _ready() -> void:
        generator = get_node(generator_path)
        generate_terrain_from_buffer()
    ```
    
    This retrieves the `generator` node, which is implemented in Python.
    
- **Calling the Python Generator:**
    
    ```gdscript
    func generate_terrain_from_buffer():
        var width = 512
        var height = 512
        
        heightmap = Image.create(width, height, true, Image.FORMAT_RGB8)
        generator.call("fill_height_map", width, height, heightmap)
    ```
    
    Here, the script passes the required dimensions to the Python function `fill_height_map`, which fills the height map using NumPy. The rest of the script processes this data into a 3D mesh.
    

---

### `HeightMapGenerator.py`

This script implements the generation of the heightmap and looks like this:
```Python
from py4godot import gdproperty, signal, private, gdclass, SignalArg  
  
from py4godot.classes.Image import Image  
from py4godot.classes.Node3D import Node3D  
import noise  
import numpy as np  
  
from py4godot.classes.core import Color  
  
def create_sinusoidal_heightmap(width:int, height:int) -> np.ndarray:  
    scale = 0.1  
  
    # Generate sinusoidal heightmap  
    x = np.linspace(0, width * scale, width)  
    y = np.linspace(0, height * scale, height)  
    X, Y = np.meshgrid(x, y)  
  
    heightmap = np.sin(X) * np.cos(Y)  
  
    # Normalize to [0, 1] range  
    heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))  
    return heightmap  
  
def create_perlin_heightmap(width:int, height:int) -> np.ndarray:  
    scale = 100.0  # Adjust for the "zoom" of the noise  
  
    # Generate heightmap    heightmap = np.zeros((width, height))  
  
    for x in range(width):  
       for y in range(height):  
          # Perlin noise: octaves, persistence, and lacunarity can tweak the result  
          heightmap[x][y] = noise.pnoise2(x / scale,  
                                  y / scale,  
                                  octaves=6,  
                                  persistence=0.5,  
                                  lacunarity=2.0,  
                                  repeatx=1024,  
                                  repeaty=1024,  
                                  base=42)  
  
    # Normalize to [0, 1] range  
    heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))  
    return heightmap  
def create_for_godot_image(width:int,height:int,gd_heightmap:Image)->None:  
    heightmap = create_sinusoidal_heightmap(width, height)  
    for x in range(width):  
       for y in range(height):  
          numpy_color = heightmap[x,y]  
          gd_heightmap.set_pixel(x,y, Color.new3(numpy_color, numpy_color, numpy_color))  
  
@gdclass  
class HeightMapGenerator(Node3D):  
    def fill_height_map(self,width:int, height:int, heightmap:Image) -> None:  
       create_for_godot_image(width, height, heightmap)
```
#### Key Functions:

- **Generating a Sinusoidal Height Map:**
    
    ```python
    def create_sinusoidal_heightmap(width:int, height:int) -> np.ndarray:
        scale = 0.1
        x = np.linspace(0, width * scale, width)
        y = np.linspace(0, height * scale, height)
        X, Y = np.meshgrid(x, y)
        heightmap = np.sin(X) * np.cos(Y)
        heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))
        return heightmap
    ```
    
    This function generates a smooth, wavy height map using sine and cosine functions.
    
- **Generating a Perlin Noise Height Map:**
    
    ```python
    def create_perlin_heightmap(width:int, height:int) -> np.ndarray:
        scale = 100.0
        heightmap = np.zeros((width, height))
        for x in range(width):
            for y in range(height):
                heightmap[x][y] = noise.pnoise2(
                    x / scale, y / scale, octaves=6, persistence=0.5, lacunarity=2.0,
                    repeatx=1024, repeaty=1024, base=42
                )
        heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap))
        return heightmap
    ```
    
    This function generates a more natural-looking terrain using Perlin noise.
    
- **Integrating with Godot:**
    
    ```python
    @gdclass
    class HeightMapGenerator(Node3D):
        def fill_height_map(self, width:int, height:int, heightmap:Image) -> None:
            create_for_godot_image(width, height, heightmap)
    ```
    
    The `@gdclass` decorator is essential for exposing this class to Godot. Without it, GDScript would not be able to call the `fill_height_map` function directly. By defining `HeightMapGenerator` as a `Node3D` subclass and using `@gdclass`, we make it accessible within the Godot engine.
    
    The function `fill_height_map` serves as a bridge between GDScript and Python. It calls `create_for_godot_image`, which generates the heightmap using NumPy and then populates the Godot `Image` object with the computed values. This allows GDScript to retrieve and utilize the heightmap data efficiently.
    

