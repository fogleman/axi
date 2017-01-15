import axi
import random

from collections import defaultdict
from math import pi, sin, cos, hypot, floor
from shapely.geometry import LineString

class Grid(object):
    def __init__(self, r):
        self.r = r
        self.size = r / 2 ** 0.5
        self.points = {}
        self.lines = {}

    def normalize(self, x, y):
        i = int(floor(x / self.size))
        j = int(floor(y / self.size))
        return (i, j)

    def nearby(self, x, y):
        points = []
        lines = []
        i, j = self.normalize(x, y)
        for p in range(i - 2, i + 3):
            for q in range(j - 2, j + 3):
                if (p, q) in self.points:
                    points.append(self.points[(p, q)])
                if (p, q) in self.lines:
                    lines.append(self.lines[(p, q)])
        return points, lines

    def insert(self, x, y, line=None):
        points, lines = self.nearby(x, y)
        for bx, by in points:
            if hypot(x - bx, y - by) < self.r:
                return False
        i, j = self.normalize(x, y)
        if line:
            for other in lines:
                if line.crosses(other):
                    return False
            self.lines[(i, j)] = line
        self.points[(i, j)] = (x, y)
        return True

    def remove(self, x, y):
        i, j = self.normalize(x, y)
        self.points.pop((i, j))
        self.lines.pop((i, j))

def max_angle(i, d):
    a1 = 2 * pi
    a2 = pi / 2
    p = min(1, d / 20.0)
    p = p ** 0.5
    return a1 + (a2 - a1) * p

def choice(items):
    # return random.choice(items)
    p = random.random() ** 0.1
    return items[int(p * len(items))]

def poisson_disc(x1, y1, x2, y2, r, n):
    grid = Grid(r)
    active = []
    for i in range(1):
        x = x1 + random.random() * (x2 - x1)
        y = y1 + random.random() * (y2 - y1)
        x = (x1 + x2) / 2.0
        y = (y1 + y2) / 2.0
        a = random.random() * 2 * pi
        if grid.insert(x, y):
            active.append((x, y, a, 0, 0, i))
    pairs = []
    while active:
        ax, ay, aa, ai, ad, ag = record = choice(active)
        for i in range(n):
            # a = random.random() * 2 * pi
            a = aa + (random.random() - 0.5) * max_angle(ai, ad)
            # a = random.gauss(aa, pi / 8)
            d = random.random() * r + r
            x = ax + cos(a) * d
            y = ay + sin(a) * d
            if x < x1 or y < y1 or x > x2 or y > y2:
                continue
            if ad + d > 4.25:
                continue
            pair = ((ax, ay), (x, y))
            line = LineString(pair)
            if not grid.insert(x, y, line):
                continue
            pairs.append(pair)
            active.append((x, y, a, ai + 1, ad + d, ag))
            active.sort(key=lambda x: -x[4])
            # if random.random() < 0.5:
            #     active.remove(record)
            break
        else:
            active.remove(record)
    return grid.points.values(), pairs

def make_path(pairs):
    lookup = defaultdict(list)
    for parent, child in pairs:
        lookup[parent].append(child)
    root = pairs[0][0]
    path = []
    stack = []
    stack.append(root)
    while stack:
        point = stack[-1]
        path.append(point)
        if not lookup[point]:
            stack.pop()
            continue
        child = lookup[point].pop()
        stack.append(child)
    return path

def main():
    random.seed(1182)
    points, pairs = poisson_disc(0, 0, 11, 8.5, 0.05, 24)
    path = make_path(pairs)
    drawing = axi.Drawing([path]).scale_to_fit(11, 8.5)
    # drawing.render().write_to_png('out.png')
    axi.draw(drawing)

if __name__ == '__main__':
    main()
