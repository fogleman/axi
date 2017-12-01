from __future__ import division

from shapely import geometry

def rectangle(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]

def centered_rectangle(w, h):
    return rectangle(-w / 2, -h / 2, w, h)

def centered_crop(g, w, h):
    return g.intersection(geometry.Polygon(centered_rectangle(w, h)))

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
