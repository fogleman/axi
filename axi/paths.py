from math import hypot
from shapely.geometry import LineString

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
    line = LineString(points)
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
    t1 = (x1 - ax) / (bx - ax)
    t2 = (y1 - ay) / (by - ay)
    t3 = (x2 - ax) / (bx - ax)
    t4 = (y2 - ay) / (by - ay)
    ts = [t1, t2, t3, t4]
    ts = [t for t in ts if t >= 0 and t <= 1]
    t = min(ts)
    x = ax + (bx - ax) * t
    y = ay + (by - ay) * t
    return (x, y)

def crop_path(path, x1, y1, x2, y2):
    result = []
    buf = []
    previous_point = None
    previous_inside = False
    for x, y in path:
        inside = x >= x1 and y >= y1 and x <= x2 and y <= y2
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
