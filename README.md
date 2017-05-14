# axi

Unofficial Python library for working with the [AxiDraw v3](http://www.axidraw.com/) pen plotter.

### Features

- control AxiDraw v3 directly from Python with a simple API
- convenient command-line utility
- constant acceleration (trapezoidal velocity) motion planning
- path drawing order optimization
- drawing transformations
  - translate, scale, rotate
  - scale and/or rotate to fit page
  - move to origin or center of page
- preview drawing (render to png)
- [turtle graphics](https://en.wikipedia.org/wiki/Turtle_graphics)

### Command Line Utility

Once `pip install'd`, you can run the axi command-line utility. Here are the supported commands:

```
axi on         # enable the motors
axi off        # disable the motors
axi up         # move the pen up
axi down       # move the pen down
axi zero       # set current position as (0, 0)
axi home       # return to the (0, 0) position
axi move DX DY # move (DX, DY) inches, relative
axi goto X Y   # move to the (X, Y) absolute position
```

### TODO

- primitives
  - circles, arcs, beziers
- svg support

### Installation

`axi` is not yet available on PyPI, so installation works like this:

    git clone https://github.com/fogleman/axi.git
    cd axi
    pip install -e .

Of course, installing in a `virtualenv` is always a good idea.

Then you can try the examples...

    python examples/dragon_curve.py

### Example

Use the turtle to draw a dragon curve, filling a standard US letter page.

```python
import axi

def main(iteration):
    turtle = axi.Turtle()
    for i in range(1, 2 ** iteration):
        turtle.forward(1)
        if (((i & -i) << 1) & i) != 0:
            turtle.circle(-1, 90, 36)
        else:
            turtle.circle(1, 90, 36)
    drawing = turtle.drawing.rotate_and_scale_to_fit(11, 8.5, step=90)
    axi.draw(drawing)

if __name__ == '__main__':
    main(12)
```
