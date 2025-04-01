# Introduction

This repository shows various examples on how Python can be used inside Godot by using the "Python for Godot" plugin. If you want to see an example on how to do a project with Python, you can look at the [Dodge the Creeps](https://github.com/niklas2902/py4godot-examples/tree/main/dodge_the_creeps) example, which shows how the demo game from Godot, [Dodge the Creeps](https://docs.godotengine.org/en/3.1/getting_started/step_by_step/your_first_game.html), looks in Python. If you want to see how Python and GDScript can interoperate, look here: [Godot-Python Interaction](https://github.com/niklas2902/py4godot-examples/tree/main/godot-python-interaction).

If you want to see how NumPy can be used in Godot to create a simple heightmap, look here: [Heightmap](https://github.com/niklas2902/py4godot-examples/tree/main/heightmap).

## Prerequisites

- Python (Recommended version: 3.x)
- Godot (Recommended version: 4.4, based on plugin compatibility)
- `py4godot` plugin

# Installation

To set up the example projects, ensure you have Python installed. Then, run the following command in your terminal:
## Windows

```bash
python -m venv venv 
venv\Scripts\activate.bat
pip install -r requirements.txt
python setup_examples.py
```

## Linux or MacOs
```bash
python3 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt
python setup_examples.py
```

This script will download the latest release of `py4godot` and copy it to all the example projects.
