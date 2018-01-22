from __future__ import division

import axi
import numpy as np
import sys

NUMBER = 1
TITLE = 'Five Seconds of Donkey Kong'
LABEL = '#%d' % NUMBER

COLUMNS = 6
SECONDS = 5

def stack_drawings(ds, spacing=0):
    result = axi.Drawing()
    y = 0
    for d in ds:
        d = d.origin().translate(-d.width / 2, y)
        result.add(d)
        y += d.height + spacing
    return result

def title():
    d = axi.Drawing(axi.text(TITLE, axi.FUTURAM))
    d = d.scale_to_fit_height(0.25)
    d = d.move(6, 8.5, 0.5, 1)
    d = d.join_paths(0.01)
    return d

def label():
    d = axi.Drawing(axi.text(LABEL, axi.FUTURAL))
    d = d.scale_to_fit_height(0.125)
    d = d.rotate(-90)
    d = d.move(12, 8.5, 1, 1)
    d = d.join_paths(0.01)
    return d

def main():
    with open(sys.argv[1], 'r') as fp:
        data = fp.read()
    lines = data.split('\n')
    lines = [x.strip() for x in lines]
    lines = [x.strip(',') for x in lines]
    lines = filter(None, lines)
    data = [map(int, line.split(',')) for line in lines]
    data = np.transpose(data)

    print len(data)

    n = len(data[0])
    m = SECONDS * 60 / 2
    a = max(0, int(n // 2 - m))
    b = min(n, int(n // 2 + m))
    data = [x[a:b] for x in data]

    data = [x for x in data if not all(q == x[0] for q in x)]

    print len(data)

    data = data[:int((len(data) // COLUMNS) * COLUMNS)]

    print len(data)

    paths = []
    for i, row in enumerate(data):
        r = i // COLUMNS
        c = i % COLUMNS
        lo = min(row)
        hi = max(row)
        if lo == hi:
            row = [0 for x in row]
        else:
            row = [(x - lo) / float(hi - lo) for x in row]
        path = []
        for j, value in enumerate(row):
            x = (j / len(row) + c * 1.1)
            y = 1-value + r * 1.5
            path.append((x, y))
        paths.append(path)
    d = axi.Drawing(paths)
    print 'transforming paths'
    d = d.scale(8.5 / d.width, (12 - 0.5) / d.height)
    print 'sorting paths'
    d = d.sort_paths()
    print 'rendering paths'

    d = stack_drawings([d, title()], 0.25)
    d = d.rotate(-90)
    d = d.center(12, 8.5)
    d.add(label())

    print d.bounds

    d.render(scale=109 * 1, line_width=0.3/25.4).write_to_png('nes/%d.png' % NUMBER)
    d.dump_svg('nes/%d.svg' % NUMBER)
    d.dump('nes/%d.axi' % NUMBER)
    # print sum(x.t for x in axi.Device().plan_drawing(d)) / 60
    # axi.draw(d)

if __name__ == '__main__':
    main()
