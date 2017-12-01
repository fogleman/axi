from __future__ import division

from shapely import geometry

def create_geometry(geoms):
    gs = []
    for g in geoms:
        if g.tags.get('natural') != 'water':
            continue
        gs.append(g)
        # while not g.is_empty:
        #     gs.append(g)
        #     g = g.buffer(-20 / 1000)
    return geometry.collection.GeometryCollection(gs)
