from __future__ import division

from itertools import groupby
from PIL import Image

Image.MAX_IMAGE_PIXELS = 1000000000

import axi
import math
import numpy as np
import sys

LNG1 = -125
LNG2 = -100
LAT1 = 49
LAT2 = 31

WIDTH = 13
HEIGHT = 8.5
LANDSCAPE = True
ROWS = LAT1 - LAT2

if not LANDSCAPE:
    WIDTH, HEIGHT = HEIGHT, WIDTH

def remove_flats(path):
    # return [list(path)]
    paths = []
    for k, g in groupby(path, lambda p: p[1] > 0):
        if k:
            paths.append(list(g))
    return paths

def crop(im):
    w, h = im.size
    lng1 = LNG1 + 180
    lng2 = LNG2 + 180
    lat1 = 90 - LAT1
    lat2 = 90 - LAT2
    pix_per_lng = int(w / 360)
    pix_per_lat = int(h / 180)
    x1 = lng1 * pix_per_lng
    x2 = lng2 * pix_per_lng
    y1 = lat1 * pix_per_lat
    y2 = lat2 * pix_per_lat
    return im.crop((x1, y1, x2, y2))

def circle(cx, cy, r, n):
    points = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        points.append((x, y))
    return points

def lat_label(text, y):
    d = axi.Drawing(axi.text(text, axi.FUTURAL))
    d = d.scale_to_fit_height(0.1)
    d = d.move(WIDTH + 1 / 8, y, 0, 1)
    # d.paths.append(circle(12.125 + d.width + 1 / 16, y - d.height, 1 / 48, 36))
    d = d.join_paths(0.01)
    d = d.simplify_paths(0.001)
    paths = d.paths
    # paths.append([(WIDTH, y), (WIDTH + 1 / 16, y)])
    return paths

def lng_label(text, x):
    d = axi.Drawing(axi.text(text, axi.FUTURAL))
    d = d.scale_to_fit_height(0.1)
    d = d.move(x, HEIGHT + 0.125, 0.5, 1)
    # d.paths.append(circle(x + d.width / 2 + 1 / 16, 8.5 + 0.125 - d.height, 1 / 48, 36))
    d = d.join_paths(0.01)
    d = d.simplify_paths(0.001)
    paths = d.paths
    paths.append([(x, HEIGHT - 1 / 8), (x, HEIGHT - 1 / 16)])
    return paths

def vertical_stack(ds, spacing=0):
    result = axi.Drawing()
    y = 0
    for d in ds:
        d = d.origin().translate(-d.width / 2, y)
        result.add(d)
        y += d.height + spacing
    return result

def title():
    d = axi.Drawing(axi.text('Topography of the Western United States', axi.FUTURAM))
    d = d.scale_to_fit_height(0.25)
    d = d.join_paths(0.01)
    d = d.simplify_paths(0.001)
    return d

def main():
    paths = []
    im = Image.open(sys.argv[1])
    im = im.convert('L')
    im = crop(im)
    # im.save('crop.png')
    print im.size
    w, h = im.size
    data = np.asarray(im)
    data = data / np.amax(data)
    # data = data ** 0.5
    lines_per_row = int(h / ROWS)
    for j in range(0, ROWS, 1):
        y0 = j * lines_per_row
        y1 = y0 + lines_per_row
        d = data[y0:y1]
        for q in range(0, 101, 25):
            print j, q
            values = np.percentile(d, q, axis=0) * 1.2
            path = enumerate(values)
            for path in remove_flats(path):
                x = np.array([p[0] for p in path]) * WIDTH / w
                y = (j - np.array([p[1] for p in path])) * HEIGHT / ROWS
                path = zip(x, y)
                path = axi.simplify_paths([path], 0.005)[0]
                paths.append(path)
        lat = LAT1 + (LAT2 - LAT1) * j / (ROWS)
        paths.extend(lat_label('%g' % lat, j * HEIGHT / ROWS))
    for lng in range(LNG1, LNG2 + 1):
        x = (lng - LNG1) / (LNG2 - LNG1) * WIDTH
        paths.extend(lng_label('%g' % abs(lng), x))
    d = axi.Drawing(paths)
    print len(d.paths)
    print 'joining paths'
    d = d.join_paths(0.01)
    print len(d.paths)
    print 'sorting paths'
    d = d.sort_paths()
    print 'joining paths'
    d = d.join_paths(0.01)
    print len(d.paths)

    d = vertical_stack([title(), d], 0.25)

    # d = d.rotate(180)
    d = d.rotate_and_scale_to_fit(12, 8.5, step=90)

    im = d.render(
        scale=109 * 1, line_width=0.3/25.4,
        )#show_axi_bounds=False, use_axi_bounds=False)
    im.write_to_png('out.png')
    # d = d.rotate_and_scale_to_fit(12, 8.5, step=90)
    d.dump('out.axi')

if __name__ == '__main__':
    main()
