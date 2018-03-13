import axi
import heapq
import layers
import random

from collections import defaultdict
from math import pi, sin, cos, hypot, floor
from shapely.geometry import LineString

W, H = axi.A3_SIZE

def make_layer():
    x = layers.Noise(8).add(layers.Constant(0.6)).clamp()
    x = x.translate(random.random() * 1000, random.random() * 1000)
    x = x.scale(0.25, 0.25)
    x = x.power(1.5)
    # x = x.subtract(layers.Distance(W / 2, H / 2, min(W, H) / 2, 4))
    return x

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

def new_angle(a, d):
    if d < 0.1:
        return random.random() * 2 * pi
    else:
        return random.gauss(a, pi / 12)

def poisson_disc(layer, x1, y1, x2, y2, r, n):
    grid = Grid(r)
    active = []
    g = 0
    while len(active) < 1:
    # for i in range(1):
        x = x1 + random.random() * (x2 - x1)
        y = y1 + random.random() * (y2 - y1)
        score = layer.get(x, y)
        if score < 0.9:
            continue
        # x = (x1 + x2) / 2.0
        # y = (y1 + y2) / 2.0
        a = random.random() * 2 * pi
        if grid.insert(x, y):
            print(x, y)
            heapq.heappush(active, (-score, x, y, a, 0, 0, g))
            g += 1
    pairs = []
    while active:
        ascore, ax, ay, aa, ai, ad, ag = active[0]
        for i in range(n):
            a = new_angle(aa, ad)
            d = random.random() * r + r
            x = ax + cos(a) * d
            y = ay + sin(a) * d
            if x < x1 or y < y1 or x > x2 or y > y2:
                continue
            pair = ((ax, ay), (x, y))
            line = LineString(pair)
            if not grid.insert(x, y, line):
                continue
            score = layer.get(x, y)
            # if score < 0.25:
            #     continue
            if random.random() < 0.75 and random.random() ** 3 > score:
                heapq.heappop(active)
                break
            pairs.append(pair)
            heapq.heappush(active, (-score, x, y, a, ai + 1, ad + d, ag))
            break
        else:
            heapq.heappop(active)
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
    layer = make_layer()
    layer.save('layer.png', 0, 0, W, H, 50)
    points, pairs = poisson_disc(layer, 0, 0, W, H, 0.05, 8)
    path = make_path(pairs)
    d = axi.Drawing([path])
    # d = d.rotate_and_scale_to_fit(W, H, step=90)
    d = d.scale_to_fit(W, H)
    d.dump('growth.axi')
    d.render(bounds=(0, 0, W, H)).write_to_png('growth.png')
    # axi.draw(d)

if __name__ == '__main__':
    main()
