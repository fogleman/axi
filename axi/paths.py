from math import hypot
from shapely import geometry

from .spatial import Index

def load_paths(filename):
    paths = []
    with open(filename) as fp:
        for line in fp:
            points = filter(None, line.strip().split(';'))
            if not points:
                continue
            path = [tuple(map(float, x.split(','))) for x in points]
            paths.append(path)
    return paths

def simplify_path(points, tolerance):
    if len(points) < 2:
        return points
    line = geometry.LineString(points)
    line = line.simplify(tolerance, preserve_topology=False)
    return list(line.coords)

def simplify_paths(paths, tolerance):
    return [simplify_path(x, tolerance) for x in paths]

def sort_paths(paths, reversable=True):
    first = paths[0]
    paths.remove(first)
    result = [first]
    points = []
    for path in paths:
        x1, y1 = path[0]
        x2, y2 = path[-1]
        points.append((x1, y1, path, False))
        if reversable:
            points.append((x2, y2, path, True))
    index = Index(points)
    while index.size > 0:
        x, y, path, reverse = index.nearest(result[-1][-1])
        x1, y1 = path[0]
        x2, y2 = path[-1]
        index.remove((x1, y1, path, False))
        if reversable:
            index.remove((x2, y2, path, True))
        if reverse:
            result.append(list(reversed(path)))
        else:
            result.append(path)
    return result

def join_paths(paths, tolerance):
    if len(paths) < 2:
        return paths
    result = [list(paths[0])]
    for path in paths[1:]:
        x1, y1 = result[-1][-1]
        x2, y2 = path[0]
        d = hypot(x2 - x1, y2 - y1)
        if d <= tolerance:
            result[-1].extend(path)
        else:
            result.append(list(path))
    return result

def crop_interpolate(x1, y1, x2, y2, ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay
    t1 = (x1 - ax) / dx if dx else -1
    t2 = (y1 - ay) / dy if dy else -1
    t3 = (x2 - ax) / dx if dx else -1
    t4 = (y2 - ay) / dy if dy else -1
    ts = [t1, t2, t3, t4]
    ts = [t for t in ts if t >= 0 and t <= 1]
    t = min(ts)
    x = ax + (bx - ax) * t
    y = ay + (by - ay) * t
    return (x, y)

def crop_path(path, x1, y1, x2, y2):
    e = 1e-9
    result = []
    buf = []
    previous_point = None
    previous_inside = False
    for x, y in path:
        inside = x >= x1 - e and y >= y1 - e and x <= x2 + e and y <= y2 + e
        if inside:
            if not previous_inside and previous_point:
                px, py = previous_point
                ix, iy = crop_interpolate(x1, y1, x2, y2, x, y, px, py)
                buf.append((ix, iy))
            buf.append((x, y))
        else:
            if previous_inside and previous_point:
                px, py = previous_point
                ix, iy = crop_interpolate(x1, y1, x2, y2, x, y, px, py)
                buf.append((ix, iy))
                result.append(buf)
                buf = []
        previous_point = (x, y)
        previous_inside = inside
    if buf:
        result.append(buf)
    return result

def crop_paths(paths, x1, y1, x2, y2):
    result = []
    for path in paths:
        result.extend(crop_path(path, x1, y1, x2, y2))
    return result

def convex_hull(points):
    hull = geometry.MultiPoint(points).convex_hull
    if isinstance(hull, geometry.Polygon):
        return list(hull.exterior.coords)
    if isinstance(hull, geometry.LineString):
        return list(hull.coords)
    if isinstance(hull, geometry.Point):
        return list(hull.coords)
    raise Exception('unhandled convex hull geometry')

def quadratic_path(x0, y0, x1, y1, x2, y2):
    n = int(hypot(x1 - x0, y1 - y0) + hypot(x2 - x1, y2 - y1))
    n = max(n, 4)
    points = []
    m = 1 / float(n - 1)
    for i in range(n):
        t = i * m
        u = 1 - t
        a = u * u
        b = 2 * u * t
        c = t * t
        x = a * x0 + b * x1 + c * x2
        y = a * y0 + b * y1 + c * y2
        points.append((x, y))
    return points

def expand_quadratics(path):
    result = []
    previous = (0, 0)
    for point in path:
        if len(point) == 2:
            result.append(point)
            previous = point
        elif len(point) == 4:
            x0, y0 = previous
            x1, y1, x2, y2 = point
            result.extend(quadratic_path(x0, y0, x1, y1, x2, y2))
            previous = (x2, y2)
        else:
            raise Exception('invalid point: %r' % point)
    return result
