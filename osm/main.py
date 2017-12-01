from __future__ import division

from shapely import geometry

import axi
import buildings
import parser
import projections
import roads
import sys
import util
import water

LAT, LNG = 35.787196, -78.783337
ROTATION_DEGREES = 0
MAP_WIDTH_KM = 3
PAGE_WIDTH_IN = 12
PAGE_HEIGHT_IN = 8.5
ASPECT_RATIO = PAGE_WIDTH_IN / PAGE_HEIGHT_IN

def crop_geom(g, w, h):
    result = util.centered_crop(g, w, h)
    if result.is_empty:
        return None
    result.tags = g.tags
    return result

def main():
    args = sys.argv[1:]
    filename = args[0]
    proj = projections.LambertAzimuthalEqualArea(LNG, LAT, ROTATION_DEGREES)
    geoms = parser.parse(filename, transform=proj.project)
    print len(geoms)
    w = MAP_WIDTH_KM
    h = w / ASPECT_RATIO
    geoms = filter(None, [crop_geom(g, w * 1.1, h * 1.1) for g in geoms])
    # g = geometry.collection.GeometryCollection(geoms)
    # g = roads.create_geometry(geoms)
    g = geometry.collection.GeometryCollection([
        roads.create_geometry(geoms),
        buildings.create_geometry(geoms),
        water.create_geometry(geoms),
    ])
    g = util.centered_crop(g, w, h)
    paths = util.shapely_to_paths(g)
    # paths.append(util.centered_rectangle(w, h))
    d = axi.Drawing(paths)
    d = d.translate(w / 2, h / 2)
    d = d.scale(PAGE_WIDTH_IN / w)
    d = d.sort_paths().join_paths(0.002).simplify_paths(0.002)
    im = d.render(line_width=0.25/25.4)
    im.write_to_png('out.png')
    # axi.draw(d)

if __name__ == '__main__':
    main()
