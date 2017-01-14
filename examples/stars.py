import axi
import math
import random

from axi.spatial import Index
from poisson_disc import poisson_disc

def perturb_points(points, deviation):
    result = []
    for x, y in points:
        a = random.random() * 2 * math.pi
        r = random.gauss(0, deviation)
        x += math.cos(a) * r
        y += math.sin(a) * r
        result.append((x, y))
    return result

def star(x, y, r):
    sides = 5
    a = random.random() * 2 * math.pi
    angle = 2 * math.pi / sides
    angles = [angle * i + a for i in range(sides)]
    points = [(x + math.cos(a) * r, y + math.sin(a) * r) for a in angles]
    points = perturb_points(points, 0.04)
    points.append(points[0])
    return points[0::2] + points[1::2]

def main():
    points = poisson_disc(0, 0, 11, 8.5, 0.4, 64)
    index = Index(points)
    paths = []
    for x1, y1 in points:
        index.remove((x1, y1))
        x2, y2 = index.nearest((x1, y1))
        index.insert((x1, y1))
        d = math.hypot(x2 - x1, y2 - y1)
        paths.append(star(x1, y1, d / 2))
    drawing = axi.Drawing(paths)
    drawing = drawing.remove_paths_outside(11, 8.5)
    drawing = drawing.sort_paths()
    # im = drawing.render()
    # im.write_to_png('out.png')
    axi.draw(drawing)

if __name__ == '__main__':
    main()
