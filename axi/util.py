from .device import Device

def reset():
    d = Device()
    d.disable_motors()
    d.pen_up()

def draw(drawing, progress=True):
    # TODO: support drawing, list of paths, or single path
    d = Device()
    d.enable_motors()
    d.run_drawing(drawing, progress)
    d.disable_motors()
