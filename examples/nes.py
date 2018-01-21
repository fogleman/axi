from __future__ import division

import axi
import numpy as np
import sys

COLUMNS = 8
SECONDS = 5

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
    d = d.scale(12 / d.width, 8.5 / d.height)
    print 'sorting paths'
    d = d.sort_paths()
    print 'rendering paths'
    d.render(scale=109 * 1, line_width=0.3/25.4).write_to_png('out.png')
    d.dump_svg('out.svg')
    # axi.draw(d)

if __name__ == '__main__':
    main()
