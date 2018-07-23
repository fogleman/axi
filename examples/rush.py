from collections import *
from math import *
import axi
import fileinput

BOUNDS = axi.A3_BOUNDS
X, Y, W, H = BOUNDS
P = 0.125
R = 0.25
COLS = 16
ROWS = 24
N = ROWS * COLS

def rectangle(x, y, w, h):
    return [
        (x, y),
        (x + w, y),
        (x + w, y + h),
        (x, y + h),
        (x, y),
    ]

def padded_rectangle(x, y, w, h, p):
    x += p
    y += p
    w -= p * 2
    h -= p * 2
    return rectangle(x, y, w, h)

def arc(cx, cy, r, a0, a1, n):
    path = []
    for i in range(n+1):
        t = i / n
        a = a0 + (a1 - a0) * t
        x = cx + r * cos(a)
        y = cy + r * sin(a)
        path.append((x, y))
    return path

def rounded_rectangle(x, y, w, h, r):
    n = 18
    x0, x1, x2, x3 = x, x + r, x + w - r, x + w
    y0, y1, y2, y3 = y, y + r, y + h - r, y + h
    path = []
    path.extend([(x1, y0), (x2, y0)])
    path.extend(arc(x2, y1, r, radians(270), radians(360), n))
    path.extend([(x3, y1), (x3, y2)])
    path.extend(arc(x2, y2, r, radians(0), radians(90), n))
    path.extend([(x2, y3), (x1, y3)])
    path.extend(arc(x1, y2, r, radians(90), radians(180), n))
    path.extend([(x0, y2), (x0, y1)])
    path.extend(arc(x1, y1, r, radians(180), radians(270), n))
    return path

def padded_rounded_rectangle(x, y, w, h, r, p):
    x += p
    y += p
    w -= p * 2
    h -= p * 2
    return rounded_rectangle(x, y, w, h, r)

def wall(x, y):
    x0 = x + P
    y0 = y + P
    x1 = x + 1 - P
    y1 = y + 1 - P
    paths = [rectangle(x0, y0, x1 - x0, y1 - y0)]
    paths.append([(x0, y0), (x1, y1)])
    paths.append([(x0, y1), (x1, y0)])
    return paths

def xy(i):
    x = i % 6
    y = i // 6
    return (x, y)

def desc_paths(desc):
    paths = []
    lookup = defaultdict(list)
    for i, c in enumerate(desc):
        lookup[c].append(i)
    for c in sorted(lookup):
        ps = lookup[c]
        if c == 'o':
            continue
        elif c == 'x':
            for i in ps:
                x, y = xy(i)
                paths.extend(wall(x, y))
        else:
            stride = ps[1] - ps[0]
            i0 = ps[0]
            i1 = ps[-1]
            x0, y0 = xy(i0)
            x1, y1 = xy(i1)
            dx = x1 - x0
            dy = y1 - y0
            paths.append(padded_rounded_rectangle(x0, y0, dx + 1, dy + 1, R, P))
            # if c == 'A':
            #     paths.append(padded_rounded_rectangle(x0, y0, dx + 1, dy + 1, R, P*2))
            #     paths.append(padded_rounded_rectangle(x0, y0, dx + 1, dy + 1, R, P*3))
    return paths

def main():
    drawing = axi.Drawing()
    n = 0
    for line in fileinput.input():
        desc = line.strip().split()[1]
        if 'x' in desc:
            continue
        paths = desc_paths(desc)
        d = axi.Drawing(paths)
        i = n % COLS
        j = n // COLS
        d = d.translate(i * 7, j * 7)
        drawing.add(d)
        n += 1
        if n == N:
            break
    # d = axi.Drawing(paths)
    d = drawing
    d = d.rotate_and_scale_to_fit(W, H, step=90)
    d.dump('rush.axi')
    d.render(bounds=BOUNDS).write_to_png('rush.png')

if __name__ == '__main__':
    main()
