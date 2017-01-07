from collections import defaultdict
from math import hypot

class Index(object):
    def __init__(self, points, n=100):
        self.n = n
        self.x1 = min(p[0] for p in points)
        self.x2 = max(p[0] for p in points)
        self.y1 = min(p[1] for p in points)
        self.y2 = max(p[1] for p in points)
        self.bins = defaultdict(list)
        self.size = 0
        for point in points:
            self.insert(point)

    def normalize(self, x, y):
        px = (x - self.x1) / (self.x2 - self.x1)
        py = (y - self.y1) / (self.y2 - self.y1)
        i = int(px * self.n)
        j = int(py * self.n)
        return (i, j)

    def insert(self, point):
        x, y = point[:2]
        i, j = self.normalize(x, y)
        self.bins[(i, j)].append(point)
        self.size += 1

    def remove(self, point):
        x, y = point[:2]
        i, j = self.normalize(x, y)
        self.bins[(i, j)].remove(point)
        self.size -= 1

    def nearest(self, point):
        x, y = point[:2]
        i, j = self.normalize(x, y)
        points = []
        r = 0
        while not points:
            points.extend(self.ring(i, j, r))
            r += 1
        points.extend(self.ring(i, j, r))
        return min(points,
            key=lambda p: (hypot(x - p[0], y - p[1]), p[1], p[0]))

    def ring(self, i, j, r):
        if r == 0:
            return self.bins[(i, j)]
        result = []
        for p in range(i - r, i + r + 1):
            result.extend(self.bins[(p, j - r)])
            result.extend(self.bins[(p, j + r)])
        for q in range(j - r + 1, j + r):
            result.extend(self.bins[(i - r, q)])
            result.extend(self.bins[(i + r, q)])
        return result
