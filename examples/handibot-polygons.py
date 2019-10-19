from math import *
from shapely import geometry, ops
import axi

W = 6
H = 8
BOUNDS = (0, 0, W, H)

BIT_RADIUS = 0.125

def regular_polygon(n, x, y, r):
    points = []
    for i in range(n):
        t = 2 * pi / n * i
        points.append((x + r * cos(t), y + r * sin(t)))
    points.append(points[0])
    return points

def polygon_splits(n, x, y, r, b):
    lines = []
    for i in range(n):
        t = 2 * pi / n * (i + 0.5)
        lines.append([(x, y), (x + r * cos(t), y + r * sin(t))])
    return geometry.MultiLineString(lines).buffer(b)

def polygon(n, r, br, notch=False):
    p = regular_polygon(n, 0, 0, r)
    g = geometry.Polygon(p)
    g = g.buffer(br).exterior
    if notch:
        g = g.difference(polygon_splits(n, 0, 0, r * 2, br * 2))
        g = ops.linemerge(g)
    p = axi.shapely_to_paths(g)
    return axi.Drawing(p).origin()

def drawings_to_gcode(ds, zs, z0, f):
    lines = []
    lines.append('G90') # absolute coordinates
    lines.append('G20') # inches
    lines.append('G0 Z%g' % z0) # jog to z0
    lines.append('M4') # turn on router
    lines.append('G4 P2.0') # dwell for N seconds
    lines.append('F%g' % f) # set feed rate (inches per minute)
    for d, z in zip(ds, zs):
        for path in d.paths:
            # jog to first point
            x, y = path[0]
            lines.append('G0 X%g Y%g' % (x, y))
            # move z down
            lines.append('G1 Z%g' % z)
            # draw path
            for x, y in path[1:]:
                lines.append('G1 X%g Y%g' % (x, y))
            # move z up
            lines.append('G1 Z%g' % z0)
    lines.append('M8')
    lines.append('G0 X0 Y0')
    return '\n'.join(lines)

def main():
    d0 = polygon(3, 3 / sqrt(3), BIT_RADIUS, False)
    d1 = polygon(3, 3 / sqrt(3), BIT_RADIUS, True)

    ds = [d0, d0, d1]
    ds = [d.translate(1, 1) for d in ds]
    zs = [-0.25, -0.5, -0.75]

    g = drawings_to_gcode(ds, zs, 0.5, 30)
    print(g)

    for i, (d, z) in enumerate(zip(ds, zs)):
        d.render(bounds=BOUNDS).write_to_png('z%g.png' % z)

if __name__ == '__main__':
    main()
