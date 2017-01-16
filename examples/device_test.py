import axi
import time

from math import sin, cos, pi

def circle(cx, cy, r, n):
    points = []
    for i in range(n + 1):
        a = 2 * pi * i / n
        x = cx + cos(a) * r
        y = cy + sin(a) * r
        points.append((x, y))
    return points

def main():
    path = []
    for i in range(10):
        path.extend(circle(4, 4, (i + 1) * 0.2, 3600))
    drawing = axi.Drawing([path]).simplify_paths(0.001)
    axi.draw(drawing)

if __name__ == '__main__':
    main()
