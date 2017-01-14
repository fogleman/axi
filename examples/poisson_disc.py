import random

from math import pi, sin, cos, hypot, floor

class Grid(object):
    def __init__(self, r):
        self.r = r
        self.size = r / 2 ** 0.5
        self.cells = {}

    def points(self):
        return self.cells.values()

    def normalize(self, x, y):
        i = int(floor(x / self.size))
        j = int(floor(y / self.size))
        return (i, j)

    def nearby(self, x, y):
        result = []
        i, j = self.normalize(x, y)
        for p in xrange(i - 2, i + 3):
            for q in xrange(j - 2, j + 3):
                if (p, q) in self.cells:
                    result.append(self.cells[(p, q)])
        return result

    def insert(self, x, y):
        for bx, by in self.nearby(x, y):
            if hypot(x - bx, y - by) < self.r:
                return False
        i, j = self.normalize(x, y)
        self.cells[(i, j)] = (x, y)
        return True

def poisson_disc(x1, y1, x2, y2, r, n):
    x = x1 + (x2 - x1) / 2.0
    y = y1 + (y2 - y1) / 2.0
    active = [(x, y)]
    grid = Grid(r)
    grid.insert(x, y)
    while active:
        ax, ay = random.choice(active)
        for i in xrange(n):
            a = random.random() * 2 * pi
            d = random.random() * r + r
            x = ax + cos(a) * d
            y = ay + sin(a) * d
            if x < x1 or y < y1 or x > x2 or y > y2:
                continue
            if not grid.insert(x, y):
                continue
            active.append((x, y))
            break
        else:
            active.remove((ax, ay))
    return grid.points()
