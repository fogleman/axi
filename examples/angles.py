from __future__ import division, print_function

import axi
import math
import random
import sys

BOUNDS = axi.A3_BOUNDS
RADIUS = 4
STEP = 5

def main():
    w, h = BOUNDS[-2:]
    paths = []
    r = RADIUS
    for a in range(0, 180, STEP):
        a = math.radians(a)
        c = math.cos(a)
        s = math.sin(a)
        paths.append([(-r * c, -r * s), (r * c, r * s)])
    d = axi.Drawing(paths)
    d = d.center(w, h)
    d = d.sort_paths()
    d.dump('out.axi')
    d.render(bounds=BOUNDS).write_to_png('out.png')

if __name__ == '__main__':
    main()
