from math import sin, cos, radians

class Drawing(object):
    def __init__(self, paths=None):
        self.paths = paths or []
        self._bounds = None

    @property
    def bounds(self):
        if not self._bounds:
            points = [(x, y) for path in self.paths for x, y in path]
            if points:
                x1 = min(x for x, y in points)
                x2 = max(x for x, y in points)
                y1 = min(y for x, y in points)
                y2 = max(y for x, y in points)
            else:
                x1 = x2 = y1 = y2 = 0
            self._bounds = (x1, y1, x2, y2)
        return self._bounds

    @property
    def width(self):
        x1, y1, x2, y2 = self.bounds
        return x2 - x1

    @property
    def height(self):
        x1, y1, x2, y2 = self.bounds
        return y2 - y1

    # def sort_paths_greedy(self, reversable=True):
    #     return Drawing(planner.sort_paths_greedy(self.paths, reversable))

    # def join_paths(self, tolerance=0.05):
    #     return Drawing(util.join_paths(self.paths, tolerance))

    # def remove_duplicates(self):
    #     return Drawing(util.remove_duplicates(self.paths))

    # def simplify_paths(self, tolerance=0.05):
    #     return Drawing(util.simplify_paths(self.paths, tolerance))

    def transform(self, func):
        return Drawing([[func(x, y) for x, y in path] for path in self.paths])

    def translate(self, dx, dy):
        def func(x, y):
            return (x + dx, y + dy)
        return self.transform(func)

    def scale(self, sx, sy):
        def func(x, y):
            return (x * sx, y * sy)
        return self.transform(func)

    def rotate(self, angle):
        c = cos(radians(angle))
        s = sin(radians(angle))
        def func(x, y):
            return (x * c - y * s, y * c + x * s)
        return self.transform(func)

    def move(self, x, y, ax, ay):
        x1, y1, x2, y2 = self.bounds
        dx = x1 + (x2 - x1) * ax - x
        dy = y1 + (y2 - y1) * ay - y
        return self.translate(-dx, -dy)

    def origin(self):
        return self.move(0, 0, 0, 0)

    def rotate_to_fit(self, width, height, step=5):
        for angle in range(0, 180, step):
            drawing = self.rotate(angle)
            if drawing.width <= width and drawing.height <= height:
                return drawing.origin()
        return None

    def scale_to_fit(self, width, height, padding=0):
        width -= padding * 2
        height -= padding * 2
        scale = min(width / self.width, height / self.height)
        return self.scale(scale, scale).origin()

    def rotate_and_scale_to_fit(self, width, height, padding=0, step=5):
        drawings = []
        width -= padding * 2
        height -= padding * 2
        for angle in range(0, 180, step):
            drawing = self.rotate(angle)
            scale = min(width / drawing.width, height / drawing.height)
            drawings.append((scale, drawing))
        scale, drawing = max(drawings)
        return drawing.scale(scale, scale).origin()
