from __future__ import division

from itertools import groupby
from PIL import Image

Image.MAX_IMAGE_PIXELS = 1000000000

import axi
import numpy as np
import sys

WIDTH = 12
HEIGHT = 8.5
LANDSCAPE = False
ROWS = 36

if not LANDSCAPE:
    WIDTH, HEIGHT = HEIGHT, WIDTH

def remove_flats(path):
    paths = []
    for k, g in groupby(path, lambda p: p[1]):
        if k > 0:
            paths.append(list(g))
    return paths

def main():
    paths = []
    im = Image.open(sys.argv[1])
    w, h = im.size
    data = np.asarray(im) / 255
    # data = data ** 0.5
    lines_per_row = int(h / ROWS)
    for j in range(0, ROWS, 1):
        y0 = j * lines_per_row
        y1 = y0 + lines_per_row
        d = data[y0:y1]
        for q in range(0, 101, 25):
            print j, q
            values = np.percentile(d, q, axis=0) * 0.9
            path = enumerate(values)
            for path in remove_flats(path):
                x = np.array([p[0] for p in path]) * WIDTH / w
                y = (j - np.array([p[1] for p in path])) * HEIGHT / ROWS
                path = zip(x, y)
                path = axi.simplify_paths([path], 0.001)[0]
                paths.append(path)
    d = axi.Drawing(paths)
    im = d.render(
        scale=109 * 1, line_width=0.3/25.4,
        show_axi_bounds=False, use_axi_bounds=False)
    im.write_to_png('out.png')

if __name__ == '__main__':
    main()
