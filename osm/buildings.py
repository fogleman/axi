from shapely import geometry

def create_geometry(geoms):
    gs = []
    for g in geoms:
        if 'building' not in g.tags:
            continue
        if g.tags['building'].lower() == 'no':
            continue
        gs.append(g)
    return geometry.collection.GeometryCollection(gs)
