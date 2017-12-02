from __future__ import division

from shapely import geometry

import axi
import layers
import parser
import projections
import sys
import util

CARY = 35.787196, -78.783337
BOSTON = 42.3583, -71.0610
BUDAPEST = 47.498206, 19.052509
SONG_SPARROW = 36.1143248, -79.9575
NEW_ORLEANS = 29.9432062,-90.1002717
FRENCH_QUARTER = 29.9588, -90.0641

LAT, LNG = FRENCH_QUARTER

ROTATION_DEGREES = 0
MAP_WIDTH_KM = 2.5
PAGE_WIDTH_IN = 12
PAGE_HEIGHT_IN = 8.5
ASPECT_RATIO = PAGE_WIDTH_IN / PAGE_HEIGHT_IN

def crop_geom(g, w, h):
    tags = g.tags
    if not g.is_valid:
        g = g.buffer(0)
    if g.is_empty:
        return None
    g = util.centered_crop(g, w, h)
    if g.is_empty:
        return None
    g.tags = tags
    return g

def main():
    args = sys.argv[1:]
    filename = args[0]
    proj = projections.LambertAzimuthalEqualArea(LNG, LAT, ROTATION_DEGREES)
    geoms = parser.parse(filename, transform=proj.project)
    print len(geoms)
    w = MAP_WIDTH_KM
    h = w / ASPECT_RATIO
    geoms = filter(None, [crop_geom(g, w + 0.1, h + 0.1) for g in geoms])
    print len(geoms)
    # g = geometry.collection.GeometryCollection(geoms)
    g = geometry.collection.GeometryCollection([
        layers.roads(geoms),
        layers.railroads(geoms),
        layers.buildings(geoms),
        layers.water(geoms),
    ])
    paths = util.shapely_to_paths(g)
    paths.append(util.centered_rectangle(w, h))
    d = axi.Drawing(paths)
    d = d.translate(w / 2, h / 2)
    d = d.scale(PAGE_WIDTH_IN / w)
    d = d.crop_paths(0, 0, PAGE_WIDTH_IN, PAGE_HEIGHT_IN)
    d = d.sort_paths().join_paths(0.002).simplify_paths(0.002)
    im = d.render(line_width=0.25/25.4)
    im.write_to_png('out.png')
    # raw_input('Press ENTER to continue!')
    # axi.draw(d)

if __name__ == '__main__':
    main()
