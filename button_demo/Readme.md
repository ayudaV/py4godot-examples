# Button Demo

This demo showcases an example of a Python script integrated into a button using py4godot. The script demonstrates handling button presses and custom behavior in Godot.

## Script Overview

Below is the Python script used in this demo:
``` Python
from py4godot.classes import gdclass
from py4godot.classes.core import Vector2, Rect2
from py4godot.classes.Button.Button import Button

@gdclass
class CustomButton(Button):
    def _has_point(self, point):
        return Rect2.new3(Vector2.new0(), self.get_size()).has_point(point)

    # Handles clicks when the "pressed" signal is connected
    def _on_pressed(self):
        print("Hello, world!")
    
    # Alternatively, you can handle button presses like this:
    # def _pressed(self):
    #     print("Hello, world!")
```
##  Notes

- The _has_point method is currently required to make the button functional. Future updates will remove this necessity.

- The _on_pressed method prints Hello, world! when the button is clicked. You can also use _pressed as an alternative if you don't want to connect the pressed signal manually.

## Future Improvements

- Removal of the _has_point requirement in later versions.

- Enhancements to button functionality and flexibility.

- Feel free to modify and expand upon this script to fit your project's needs!
