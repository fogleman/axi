from .device import Device

def reset():
    d = Device()
    d.disable_motors()
    d.pen_up()

def draw(drawing):
    # TODO: support drawing, list of paths, or single path
    d = Device()
    d.enable_motors()
    d.run_drawing(drawing)
    d.disable_motors()
