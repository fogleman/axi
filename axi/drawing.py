from __future__ import division

from math import sin, cos, radians

from .paths import simplify_paths, sort_paths, join_paths, crop_paths

try:
    import cairo
except ImportError:
    cairo = None

class Drawing(object):
    def __init__(self, paths=None):
        self.paths = paths or []
        self._bounds = None

    @classmethod
    def loads(cls, data):
        paths = []
        for line in data.split('\n'):
            points = line.strip().split()
            points = [map(float, x.split(',')) for x in points]
            if points:
                paths.append(points)
        return cls(paths)

    @classmethod
    def load(cls, filename):
        with open(filename, 'r') as fp:
            return cls.loads(fp.read())

    def dumps(self):
        lines = []
        for path in self.paths:
            lines.append(' '.join('%f,%f' % (x, y) for x, y in path))
        return '\n'.join(lines)

    def dump(self, filename):
        with open(filename, 'w') as fp:
            fp.write(self.dumps())

    def dumps_svg(self, scale=96):
        lines = []
        w = (self.width + 2) * scale
        h = (self.height + 2) * scale
        lines.append('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="%g" height="%g">' % (w, h))
        lines.append('<g transform="scale(%g) translate(1 1)">' % scale)
        for path in self.paths:
            p = []
            c = 'M'
            for x, y in path:
                p.append('%s%g %g' % (c, x, y))
                c = 'L'
            d = ' '.join(p)
            lines.append('<path d="%s" fill="none" stroke="black" stroke-width="0.01" stroke-linecap="round" stroke-linejoin="round" />' % d)
        lines.append('</g>')
        lines.append('</svg>')
        return '\n'.join(lines)

    def dump_svg(self, filename):
        with open(filename, 'w') as fp:
            fp.write(self.dumps_svg())

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

    @property
    def all_paths(self):
        result = []
        position = (0, 0)
        for path in self.paths:
            result.append([position, path[0]])
            result.append(path)
            position = path[-1]
        result.append([position, (0, 0)])
        return result

    def simplify_paths(self, tolerance):
        return Drawing(simplify_paths(self.paths, tolerance))

    def sort_paths(self, reversable=True):
        return Drawing(sort_paths(self.paths, reversable))

    def join_paths(self, tolerance):
        return Drawing(join_paths(self.paths, tolerance))

    def crop_paths(self, x1, y1, x2, y2):
        return Drawing(crop_paths(self.paths, x1, y1, x2, y2))

    # def remove_duplicates(self):
    #     return Drawing(util.remove_duplicates(self.paths))

    def add(self, drawing):
        self.paths.extend(drawing.paths)
        self._bounds = None

    def transform(self, func):
        return Drawing([[func(x, y) for x, y in path] for path in self.paths])

    def translate(self, dx, dy):
        def func(x, y):
            return (x + dx, y + dy)
        return self.transform(func)

    def scale(self, sx, sy=None):
        if sy is None:
            sy = sx
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

    def center(self, width, height):
        return self.move(width / 2, height / 2, 0.5, 0.5)

    def rotate_to_fit(self, width, height, step=5):
        for angle in range(0, 180, step):
            drawing = self.rotate(angle)
            if drawing.width <= width and drawing.height <= height:
                return drawing.center(width, height)
        return None

    def scale_to_fit_height(self, height, padding=0):
        return self.scale_to_fit(1e9, height, padding)

    def scale_to_fit_width(self, width, padding=0):
        return self.scale_to_fit(width, 1e9, padding)

    def scale_to_fit(self, width, height, padding=0):
        s_width = width - padding * 2
        s_height = height - padding * 2
        scale = min(s_width / self.width, s_height / self.height)
        return self.scale(scale, scale).center(width, height)

    def rotate_and_scale_to_fit(self, width, height, padding=0, step=5):
        drawings = []
        s_width = width - padding * 2
        s_height = height - padding * 2
        for angle in range(0, 180, step):
            drawing = self.rotate(angle)
            scale = min(s_width / drawing.width, s_height / drawing.height)
            drawings.append((scale, drawing))
        scale, drawing = max(drawings)
        return drawing.scale(scale, scale).center(width, height)

    def crop(self, width, height):
        paths = []
        for path in self.paths:
            ok = True
            new_path = []
            for x, y in path:
                if x < 0 or y < 0 or x > width or y > height:
                    if new_path:
                        paths.append(new_path)
                        new_path = []
                else:
                    new_path.append((x,y))
            if new_path:
                paths.append(new_path)
        return Drawing(paths)

    def remove_paths_outside(self, width, height):
        e = 1e-8
        paths = []
        for path in self.paths:
            ok = True
            for x, y in path:
                if x < -e or y < -e or x > width + e or y > height + e:
                    ok = False
                    break
            if ok:
                paths.append(path)
        return Drawing(paths)

    def render(self, scale=109, margin=30, line_width=0.5/25.4):
        if cairo is None:
            raise Exception('Drawing.render() requires cairo')
        # x1, y1, x2, y2 = self.bounds
        x1, y1, x2, y2 = (0, 0, 12, 8.5)
        w = x2 - x1
        h = y2 - y1
        width = int(scale * w + margin * 2)
        height = int(scale * h + margin * 2)
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        dc = cairo.Context(surface)
        dc.set_line_cap(cairo.LINE_CAP_ROUND)
        dc.set_line_join(cairo.LINE_JOIN_ROUND)
        dc.translate(margin, margin)
        dc.scale(scale, scale)
        dc.translate(-x1, -y1)
        dc.set_source_rgb(1, 1, 1)
        dc.paint()
        dc.set_source_rgb(0.5, 0.5, 0.5)
        dc.set_line_width(1 / scale)
        dc.rectangle(x1, y1, w, h)
        dc.stroke()
        dc.set_source_rgb(0, 0, 0)
        dc.set_line_width(line_width)
        for path in self.paths:
            dc.move_to(*path[0])
            for x, y in path:
                dc.line_to(x, y)
        dc.stroke()
        return surface
