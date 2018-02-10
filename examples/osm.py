from shapely import geometry, ops, affinity

import axi
import math
import osm2shapely
import sys

import logging
logging.basicConfig()

HOME = 35.768616, -78.844005
RALEIGH = 35.777486, -78.635794
DURHAM = 35.999392, -78.919217
PARIS = 48.856744, 2.351248
HOLBROOK = 32.422131, -80.713289
FORMLABS = 42.374414, -71.087908
PINE_RIDGE_ROAD = 42.427164, -71.143553
TIMES_SQUARE = 40.758582, -73.985066

LAT, LNG = TIMES_SQUARE
LANDSCAPE = False
PAGE_WIDTH_IN = 12
PAGE_HEIGHT_IN = 8.5
MAP_WIDTH_KM = 1.61
LANE_WIDTH_M = 3.7
EARTH_RADIUS_KM = 6371

WEIGHTS = {
    'motorway': 2,
    'motorway_link': 2,
    'trunk_link': 2,
    'trunk': 2,
    'primary_link': 1.75,
    'primary': 1.75,
    'secondary': 1.5,
    'secondary_link': 1.5,
    'tertiary_link': 1.25,
    'tertiary': 1.25,
    'living_street': 1,
    'unclassified': 1,
    'residential': 1,
    # 'service': 0,
    # 'railway': 0,
    # 'pedestrian': 0,
    # 'footway': 0,
    # 'natural': 0,
}

def paths_to_shapely(paths):
    return geometry.MultiLineString(paths)

def shapely_to_paths(g):
    if isinstance(g, geometry.Point):
        return []
    elif isinstance(g, geometry.LineString):
        return [list(g.coords)]
    elif isinstance(g, (geometry.MultiPoint, geometry.MultiLineString, geometry.MultiPolygon, geometry.collection.GeometryCollection)):
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

def follow(g, step):
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

def hatch(g, angle, step):
    print g.area
    x0, y0, x1, y1 = g.bounds
    d = max(x1 - x0, y1 - y0) * 2
    lines = []
    x = 0
    while x < d:
        lines.append(geometry.LineString([(x - d / 2, -d / 2), (x - d / 2, d / 2)]))
        x += step
    if not lines:
        return None
    lines = geometry.collection.GeometryCollection(lines)
    lines = affinity.rotate(lines, angle)
    lines = affinity.translate(lines, (x0 + x1) / 2, (y0 + y1) / 2)
    return g.intersection(lines)

def crop(g, w, h):
    return g.intersection(geometry.Polygon(box(w, h)))

def box(w, h):
    w *= 0.5
    h *= 0.5
    return [(-w, -h), (w, -h), (w, h), (-w, h), (-w, -h)]

def haversine(lat1, lng1, lat2, lng2):
    lng1, lat1, lng2, lat2 = map(math.radians, [lng1, lat1, lng2, lat2])
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    return math.asin(math.sqrt(a)) * 2 * EARTH_RADIUS_KM

class LambertAzimuthalEqualAreaProjection(object):
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng
        self.angle = math.radians(29)
        self.scale = 1
        self.scale = self.kilometer_scale()
    def project(self, lng, lat):
        lng, lat = math.radians(lng), math.radians(lat)
        clng, clat = math.radians(self.lng), math.radians(self.lat)
        k = math.sqrt(2 / (1 + math.sin(clat)*math.sin(lat) + math.cos(clat)*math.cos(lat)*math.cos(lng-clng)))
        x = k * math.cos(lat) * math.sin(lng-clng)
        y = k * (math.cos(clat)*math.sin(lat) - math.sin(clat)*math.cos(lat)*math.cos(lng-clng))
        rx = x * math.cos(self.angle) - y * math.sin(self.angle)
        ry = y * math.cos(self.angle) + x * math.sin(self.angle)
        x = rx
        y = ry
        s = self.scale
        return (x * s, -y * s)
    def kilometer_scale(self):
        e = 1e-3
        lat, lng = self.lat, self.lng
        km_per_lat = haversine(lat - e, lng, lat + e, lng) / (2 * e)
        km_per_lng = haversine(lat, lng - e, lat, lng + e) / (2 * e)
        x1, y1 = self.project(lng - 1 / km_per_lng, lat - 1 / km_per_lat)
        x2, y2 = self.project(lng + 1 / km_per_lng, lat + 1 / km_per_lat)
        sx = 2 / (x2 - x1)
        sy = 2 / (y1 - y2)
        return (sx + sy) / 2
    def transform(self, g):
        result = ops.transform(self.project, g)
        result.tags = g.tags
        return result

def circle(cx, cy, r, n, revs=5):
    points = []
    n *= revs
    for i in range(n + 1):
        a = revs * math.pi * i / n
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        points.append((x, y))
    return points

def main():
    # parse osm file into shapely geometries
    geometries = osm2shapely.parse(sys.argv[1])

    # setup map projection
    projection = LambertAzimuthalEqualAreaProjection(LAT, LNG)
    geometries = [projection.transform(g) for g in geometries]

    # determine width and height of map
    w = MAP_WIDTH_KM
    if LANDSCAPE:
        h = float(w) * PAGE_HEIGHT_IN / PAGE_WIDTH_IN
    else:
        h = float(w) * PAGE_WIDTH_IN / PAGE_HEIGHT_IN

    # process geometries
    gs = []
    roads = []
    for g in geometries:
        highway = g.tags.get('highway')
        if highway and highway in WEIGHTS:
            weight = WEIGHTS[highway]
            if weight:
                g = g.buffer(LANE_WIDTH_M / 1000.0 * weight)
            g = crop(g, w * 1.1, h * 1.1)
            roads.append(g)
        # elif 'natural' in g.tags:
        #     gs.append(g)
        elif 'building' in g.tags:
            gs.append(g)

    print 'crop'
    gs = [crop(g, w * 1.1, h * 1.1) for g in gs]
    roads = [crop(g, w * 1.1, h * 1.1) for g in roads]

    # gs = []
    # for key, ways in handler.ways.items():
    #     if key not in WEIGHTS:
    #         print 'skip', key, len(ways)
    #         continue
    #     print 'layer', key, len(ways)
    #     ggs = []
    #     for way in ways:
    #         coords = [projection.project(*handler.coords[x]) for x in way]
    #         if key == 'natural' and coords[0] == coords[-1]:
    #             ggs.append(geometry.Polygon(coords))
    #         else:
    #             ggs.append(geometry.LineString(coords))
    #     # g = paths_to_shapely(paths)
    #     g = geometry.collection.GeometryCollection(ggs)
    #     if key == 'railway':
    #         paths = shapely_to_paths(g)
    #         g = paths_to_shapely(paths)
    #         points = follow(g, 20 / 1000.0)
    #         s = 4 / 1000.0
    #         for x, y, a in points:
    #             x1 = x + math.cos(a + math.pi / 2) * s
    #             y1 = y + math.sin(a + math.pi / 2) * s
    #             x2 = x + math.cos(a - math.pi / 2) * s
    #             y2 = y + math.sin(a - math.pi / 2) * s
    #             paths.append([(x1, y1), (x2, y2)])
    #         g = paths_to_shapely(paths)
    #     if key == 'natural':
    #         gs.append(crop(paths_to_shapely(shapely_to_paths(g)), w * 1.1, h * 1.1))
    #         paths = hatch(g, 45, 10 / 1000.0)
    #         g = paths_to_shapely(paths)
    #     weight = WEIGHTS[key]
    #     if weight:
    #         g = g.buffer(LANE_WIDTH_M / 1000.0 * weight)
    #     g = crop(g, w * 1.1, h * 1.1)
    #     gs.append(g)

    print 'union'
    roads = ops.cascaded_union(roads)
    all_roads = []
    while not roads.is_empty:
        all_roads.append(roads)
        roads = roads.buffer(-LANE_WIDTH_M / 1000.0 / 3)
    g = geometry.collection.GeometryCollection(gs + all_roads)
    g = paths_to_shapely(shapely_to_paths(g))

    print 'crop'
    g = crop(g, w, h)

    paths = shapely_to_paths(g)

    # dot at origin
    # s = 3 / 1000.0 / 3
    # for i in range(4):
    #     paths.append(circle(0, 0, i * s, 360))

    # border around map
    s = 6 / 1000.0 / 2
    for m in range(1):
        paths.append(box(w - s * m, h - s * m))

    print 'axi'
    d = axi.Drawing(paths)
    d = d.rotate_and_scale_to_fit(PAGE_WIDTH_IN, PAGE_HEIGHT_IN, step=90)
    d = d.sort_paths().join_paths(0.002).simplify_paths(0.002)
    im = d.render()
    im.write_to_png('out.png')
    axi.draw(d)

if __name__ == '__main__':
    main()
