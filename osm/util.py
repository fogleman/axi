from __future__ import division

from shapely import geometry
import math

def rectangle(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]

def centered_rectangle(w, h):
    return rectangle(-w / 2, -h / 2, w, h)

def centered_crop(g, w, h):
    return g.intersection(geometry.Polygon(centered_rectangle(w, h)))

def circle(cx, cy, r, revs=1, points_per_rev=360):
    n = points_per_rev * revs
    return arc(cx, cy, r, 0, 2 * math.pi * revs, n)

def arc(cx, cy, r, a1, a2, n=360):
    points = []
    for i in range(n + 1):
        a = a1 + (a2 - a1) * i / n
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        points.append((x, y))
    return points

def star(x, y, r):
    sides = 5
    a = -math.pi / 2
    angle = 2 * math.pi / sides
    angles = [angle * i + a for i in range(sides)]
    points = [(x + math.cos(a) * r, y + math.sin(a) * r) for a in angles]
    points.append(points[0])
    return points[0::2] + points[1::2]

def wave(px, py, r, n=360):
    p1 = arc(px - r, py, r, math.pi / 2, 0, n)
    p2 = arc(px + r, py, r, -math.pi, -3 * math.pi / 2, n)
    return p1 + p2

def waves(g, r, s):
    lines = []
    x0, y0, x1, y1 = g.bounds
    y = y0
    i = 0
    while y < y1:
        x = x0
        if i % 2:
            x += s / 2
        while x < x1:
            lines.append(wave(x, y, r))
            x += s
        y += s
        i += 1
    lines = geometry.MultiLineString(lines)
    return g.intersection(lines)

def paths_to_shapely(paths):
    return geometry.MultiLineString(paths)

def shapely_to_paths(g):
    iterables = (
        geometry.MultiPoint,
        geometry.MultiLineString,
        geometry.MultiPolygon,
        geometry.collection.GeometryCollection)
    if isinstance(g, geometry.Point):
        return []
    elif isinstance(g, geometry.LineString):
        return [list(g.coords)]
    elif isinstance(g, iterables):
        paths = []
        for x in g:
            paths.extend(shapely_to_paths(x))
        return paths
    elif isinstance(g, geometry.Polygon):
        paths = []
        paths.append(list(g.exterior.coords))
        for interior in g.interiors:
            paths.extend(shapely_to_paths(interior))
        return paths
    else:
        raise Exception('unhandled shapely geometry: %s' % type(g))

def interpolated_points(g, step):
    result = []
    d = step
    e = 1e-3
    l = g.length
    while d < l:
        p = g.interpolate(d)
        a = g.interpolate(d - e)
        b = g.interpolate(d + e)
        angle = math.atan2(b.y - a.y, b.x - a.x)
        result.append((p.x, p.y, angle))
        d += step
    return result
