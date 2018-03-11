import axi
import math
import random

H, W = axi.A3_SIZE

def text(font):
    text = ''.join(map(chr, range(32, 128)))
    n = 96 // 3
    text = '\n'.join(text[i:i+n] for i in range(0, 96, n))
    d = font.wrap(text, W, 1.5)
    d = d.center(12, 8.5)
    return d

def vertical_stack(ds, spacing=0):
    result = axi.Drawing()
    y = 0
    for d in ds:
        d = d.origin().translate(-d.width / 2, y)
        result.add(d)
        y += d.height + spacing
    return result

def horizontal_stack(ds, spacing=0):
    result = axi.Drawing()
    x = 0
    for d in ds:
        d = d.origin().translate(x, -d.height / 2)
        result.add(d)
        x += d.width + spacing
    return result

def circle(cx, cy, r, revs, points_per_rev):
    points = []
    a0 = random.random() * 2 * math.pi
    n = int(revs * points_per_rev)
    for i in range(n + 1):
        a = a0 + revs * 2 * math.pi * i / n
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        points.append((x, y))
    return points

def fill_circle(cx, cy, r1, r2, revs, points_per_rev):
    points = []
    a0 = random.random() * 2 * math.pi
    n = int(revs * points_per_rev)
    for i in range(n + 1):
        a = a0 + revs * 2 * math.pi * i / n
        r = r1 + (r2 - r1) * min(1, float(i) / (n - points_per_rev))
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        points.append((x, y))
    return points

def circles():
    x = 0
    r = 0
    paths = []
    while x + r < W:
        paths.append(circle(x, 0, r, 2, 360))
        x += r
        r += 0.0025
        x += r
        x += 0.1
    return axi.Drawing(paths)

def fill_circles():
    x = 0
    r = 0
    paths = []
    while x + r < W:
        revs = (r * 80) + 2
        paths.append(fill_circle(W - x, 0, 0, r, revs, 360))
        x += r
        r += 0.0025
        x += r
        x += 0.1
    return axi.Drawing(paths)

def line():
    return axi.Drawing([[(0, 0), (W, 0)]])

def lines():
    x = 0
    s0 = 0.01 / 25.4
    s1 = 3 / 25.4
    h = 0.5
    paths = []
    i = 0
    while x < W:
        if i % 2 == 0:
            paths.append([(x, 0), (x, h)])
        else:
            paths.append([(x, h), (x, 0)])
        pct = x / W
        # pct = pct ** 2
        s = s0 + (s1 - s0) * pct
        x += s
        i += 1
    # print(len(paths))
    return axi.Drawing(paths).join_paths(100)

def title(name):
    font = axi.Font(axi.FUTURAL, 18)
    d = font.wrap(name, W, 1.5)
    return d

def main():
    name = 'Rapidograph 0.1mm'
    ds = []
    for font in [axi.FUTURAL, axi.TIMESR, axi.TIMESIB]:
        d = text(axi.Font(font, 13))
        ds.append(d)
    d = horizontal_stack(ds, 0.2).center(W, H)
    d = vertical_stack([title(name), d], 0.2)
    d = vertical_stack([d, line()], 0.2)
    d = vertical_stack([d, line()], 0.1)
    d = vertical_stack([d, circles()], 0.2)
    d = vertical_stack([d, fill_circles()], 0.1)
    d = vertical_stack([d, lines()], 0.2)
    d = d.move(W / 2, 0, 0.5, 0)
    d = d.translate(0, 0)
    print(d.bounds)

    # d = d.sort_paths()
    # d = d.join_paths(0.01)
    d = d.simplify_paths(0.001)
    d = d.rotate(-90).move(0, W / 2, 0, 0.5)
    print(d.bounds)

    d.dump('out.axi')
    d.render(bounds=axi.A3_BOUNDS).write_to_png('out.png')

if __name__ == '__main__':
    main()
