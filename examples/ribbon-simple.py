from __future__ import division, print_function

import axi
import math
import random
import sys

BOUNDS = axi.A3_BOUNDS

def main():
    d = axi.Drawing.load(sys.argv[1]).scale(1, -1)
    print(len(d.paths))
    d = d.join_paths(0.005)
    d = d.rotate_and_scale_to_fit(*BOUNDS[-2:])
    d = d.sort_paths()
    d = d.join_paths(0.005)
    d = d.simplify_paths(0.0001)
    print(len(d.paths))
    print(d.bounds)
    d.dump('out.axi')
    d.render(bounds=BOUNDS).write_to_png('out.png')

if __name__ == '__main__':
    main()
