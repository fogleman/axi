import axi
import math
import random

RULE = '23/3'

class Generation(object):
    def __init__(self, grid=None):
        self.grid = grid or set()
    def randomize(self, w, h, p, seed=None):
        random.seed(seed)
        self.grid.clear()
        for y in range(-h, h+1):
            for x in range(-w, w+1):
                d = math.hypot(x, y)
                p = 1 - d / 24
                p = p * 0.8
                p = max(0, p)
                p = p ** 1.5
                if random.random() < p:
                    self.set(x, y)
    def set(self, x, y):
        self.grid.add((x, y))
    def unset(self, x, y):
        self.grid.discard((x, y))
    def get(self, x, y):
        return (x, y) in self.grid
    def count_neighbors(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if (dx or dy) and (x + dx, y + dy) in self.grid:
                    count += 1
        return count
    def next(self):
        xs = [x for x, y in self.grid]
        ys = [y for x, y in self.grid]
        minx = min(xs) - 1
        maxx = max(xs) + 1
        miny = min(ys) - 1
        maxy = max(ys) + 1
        grid = set()
        keep, spawn = RULE.split('/')
        keep = map(int, keep)
        spawn = map(int, spawn)
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                n = self.count_neighbors(x, y)
                if (x, y) in self.grid:
                    if n in keep:
                        grid.add((x, y))
                else:
                    if n in spawn:
                        grid.add((x, y))
        return Generation(grid)

def circle(cx, cy, r, n):
    points = []
    a0 = random.random() * 2 * math.pi
    for i in range(n + 1):
        a = 4.5 * math.pi * i / n + a0
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        points.append((x, y))
    return points

def circles(generations):
    paths = []
    n = len(generations)
    for i, g in enumerate(generations):
        p = float(i) / (n - 1)
        # print i, p, len(g.grid)
        # r = 1 - p * 0.85 - 0.1
        r = p * 0.85 + 0.05
        r = r * 0.5
        for x, y in g.grid:
            if x < 36 or y < 40 or x >= 64 or y >= 60:
                continue
            paths.append(circle(x, y, r, 200))
    return axi.Drawing(paths)

def lines(generations):
    paths = []
    n = len(generations)
    for i, g in enumerate(generations):
        p = float(i) / n
        a = p * 2 * math.pi
        for x, y in g.grid:
            x2 = x + math.cos(a) * 0.45
            y2 = y + math.sin(a) * 0.45
            dx1 = random.gauss(0, 0.015)
            dy1 = random.gauss(0, 0.015)
            dx2 = random.gauss(0, 0.09)
            dy2 = random.gauss(0, 0.09)
            paths.append([(x + dx1, y + dy1), (x2 + dx2, y2 + dy2)])
    return axi.Drawing(paths)

def main(seed):
    n = 90/2
    gs = []
    g = Generation()
    g.randomize(24, 24, 0.3, seed)
    for i in range(n + 10):
        gs.append(g)
        g = g.next()
    d = lines(gs[-n:])
    d = d.rotate_and_scale_to_fit(12, 8.5, step=90)
    d = d.sort_paths().join_paths(0.02)
    im = d.render()
    im.write_to_png('%06d.png' % seed)
    axi.draw(d)

if __name__ == '__main__':
    main(16)
    # for i in range(100):
    #     main(i)
    #     print i
