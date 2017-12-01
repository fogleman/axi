from __future__ import division

from shapely import geometry, ops

LANE_WIDTH_M = 3.7

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
    'service': 0,
    # 'pedestrian': 0,
    # 'footway': 0,
}

def create_geometry(geoms):
    lookup = {}
    for g in geoms:
        highway = g.tags.get('highway')
        if highway not in WEIGHTS:
            continue
        lookup.setdefault(WEIGHTS[highway], []).append(g)
    result = []
    for weight, gs in lookup.items():
        g = geometry.collection.GeometryCollection(gs)
        if weight > 0:
            g = g.buffer(weight * LANE_WIDTH_M / 1000)
        result.append(g)
    return ops.cascaded_union(result)
