# axi

Python library for working with the AxiDraw v3 pen plotter.

### Features

- control AxiDraw v3 directly from Python
- constant acceleration (trapezoidal velocity) motion planning
- path drawing order optimization
- drawing transformations
  - translate, scale, rotate
  - scale and/or rotate to fit page
  - move to origin or center of page
- [turtle graphics](https://en.wikipedia.org/wiki/Turtle_graphics)

### TODO / Coming Soon

- primitives
  - circles, arcs, beziers
- svg support
- preview (render to png)
- progress / status while drawing

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
