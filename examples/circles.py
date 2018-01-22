import axi
import math
import random
import sys

def circle(cx, cy, r, n):
    points = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        points.append((x, y))
    return points

def random_points_on_circle(cx, cy, r, n):
    result = []
    a = random.random() * 2 * math.pi
    da = 2 * math.pi / n
    for i in range(n):
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        result.append((x, y))
        a += da
    return result

def add(x, y, r, paths):
    if r < 1:
        return
    paths.append(circle(x, y, r, 90))
    points = random_points_on_circle(x, y, r, 2)
    for x, y in points:
        add(x, y, r / 2, paths)

def main():
    paths = []
    add(0, 0, 64, paths)
    drawing = axi.Drawing(paths).rotate_and_scale_to_fit(11, 8.5).sort_paths()
    im = drawing.render()
    if len(sys.argv) > 1 and sys.argv[1].endswith(".png"):
        drawing.render().write_to_png(sys.argv[1])
    else:
        axi.draw(drawing)

if __name__ == '__main__':
    main()
