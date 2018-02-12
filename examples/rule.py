from collections import defaultdict
from shapely import geometry

import axi
import math
import random

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

def random_row(n):
    return bin(random.getrandbits(n) | (1 << n))[3:]

def compute_row(rule, previous):
    row = []
    previous = '00' + previous + '00'
    for i in range(len(previous) - 2):
        x = int(previous[i:i+3], 2)
        y = '1' if rule & (1 << x) else '0'
        row.append(y)
    return ''.join(row)

def compute_rows(rule, w, h):
    rows = [random_row(w * 16)]
    for _ in range(h - 1):
        rows.append(compute_row(rule, rows[-1]))
    return rows

def pad(rows):
    result = []
    n = len(max(rows, key=len))
    for row in rows:
        p = (n - len(row)) / 2 + 1
        row = '.' * p + row + '.' * p
        result.append(row)
    return result

def trim(rows):
    return [row.strip('.') for row in rows]

def crop(rows, n):
    w = len(rows[0])
    h = len(rows)
    i = w / 2 - n / 2
    j = i + n
    return [row[i:j] for row in rows]

def crop_diagonal(rows):
    rows = trim(rows)
    result = []
    for i, row in enumerate(rows):
        if i < len(rows) / 2:
            result.append(row)
        else:
            j = 2 * (i - len(rows) / 2 + 1)
            result.append(row[j:-j])
    return result

def trim_pair(pair, d):
    line = geometry.LineString(pair)
    p1 = line.interpolate(d)
    p2 = line.interpolate(line.length - d)
    return ((p1.x, p1.y), (p2.x, p2.y))

def form_pairs(rows):
    pairs = []
    rows = pad(rows)
    for y, row in enumerate(rows):
        if y == 0:
            continue
        for x, value in enumerate(row):
            if value != '1':
                continue
            i = x - len(rows[-1]) / 2
            j = y
            if rows[y - 1][x - 1] == '1':
                pairs.append(((i - 1, j - 1), (i, j)))
            if rows[y - 1][x] == '1':
                pairs.append(((i, j - 1), (i, j)))
            if rows[y - 1][x + 1] == '1':
                pairs.append(((i + 1, j - 1), (i, j)))
    points = set()
    for (x1, y1), (x2, y2) in pairs:
        points.add((x1, y1))
        points.add((x2, y2))
    return pairs, points

def create_drawing(rule, w, h):
    # print rule
    rows = compute_rows(rule, w, h)
    rows = pad(rows)
    rows = crop(rows, w)
    # rows = pad(rows)
    print len(rows[0]), len(rows)
    pairs, points = form_pairs(rows)
    counts = defaultdict(int)
    for a, b in pairs:
        counts[a] += 1
        counts[b] += 1
    # paths = [trim_pair(x, 0.25) for x in pairs]
    paths = pairs
    circle = axi.Drawing([fill_circle(0, 0, 0, 0.2, 2.5, 100)])
    # paths = []
    # paths = random.sample(pairs, len(pairs) / 2)
    for x, y in points:
        if counts[(x, y)] != 1:
            continue
        paths.extend(circle.translate(x, y).paths)
    d = axi.Drawing(paths)
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

def title(rule):
    d1 = axi.Drawing(axi.text('Rule %d' % rule, axi.FUTURAM))
    d1 = d1.scale_to_fit_height(0.25)
    d2 = axi.Drawing(axi.text('Elementary Cellular Automaton', axi.FUTURAL))
    d2 = d2.scale_to_fit_height(0.1875)
    ds = [d1, d2]
    d = vertical_stack(ds, 0.125)
    d = d.join_paths(0.01)
    return d

def decoder(rule):
    paths = []
    for i in range(8):
        for j in range(3):
            x = i * 4 + j
            on = i & (1 << j)
            if on:
                paths.append(fill_circle(x, 0, 0, 0.4, 8.5, 100))
            else:
                paths.append(circle(x, 0, 0.4, 2.5, 100))
        x = i * 4 + 1
        on = rule & (1 << i)
        if on:
            paths.append(fill_circle(x, 1, 0, 0.4, 8.5, 100))
        else:
            paths.append(circle(x, 1, 0.4, 2.5, 100))
    d = axi.Drawing(paths)
    d = d.scale_to_fit_width(8.5 * 2 / 3)
    d = d.scale(-1, 1)
    return d

def single():
    rule = 150
    seed = 37
    random.seed(seed)
    h = 128

    # rules = [30, 60, 90, 106, 150, 105, 122, 154]
    # ds = []
    # for rule in rules:
    #     d = create_drawing(rule, h)
    #     ds.append(d)
    # d = horizontal_stack(ds, 2)

    d = create_drawing(rule, h)
    d = d.scale_to_fit_width(8.5)
    d = vertical_stack([title(rule), d, decoder(rule)], 0.25)
    d = d.rotate(-90)
    d = d.scale_to_fit(12, 8.5)
    print 'sorting paths'
    d = d.sort_paths()
    print 'joining paths'
    d = d.join_paths(0.01)
    print 'simplifying paths'
    d = d.simplify_paths(0.001)
    print d.bounds
    d.dump('out.axi')
    im = d.render(scale=109 * 1, line_width=0.3/25.4, show_axi_bounds=False)
    im.write_to_png('out.png')
    # axi.draw(d)

def multiple():
    w = 32
    h = 137

    # rules = [x for x in range(256) if bin(x).count('1') == 4]
    # rules = [18, 22, 26, 30, 41, 45, 54, 60, 73, 90, 105, 106, 110, 122, 126, 146, 150, 154]
    # rules = sorted(random.sample(rules, 6))
    # print rules

    # rules = sorted([22, 30, 60, 90, 106, 150, 105, 122, 154])
    rules = sorted([22, 30, 60, 90, 106, 150])
    ds = []
    for rule in rules:
        d1 = create_drawing(rule, w, h)
        d1 = d1.scale_to_fit_height(8)
        d2 = axi.Drawing(axi.text('Rule %d' % rule, axi.FUTURAL))
        d2 = d2.scale_to_fit_height(0.125)
        d = vertical_stack([d1, d2], 0.125)
        ds.append(d)
    title = axi.Drawing(axi.text('Elementary Cellular Automata', axi.FUTURAM))
    title = title.scale_to_fit_height(0.25)
    d = horizontal_stack(ds, 0.25)
    d = vertical_stack([title, d], 0.2)
    d = d.scale_to_fit(12, 8.5)
    # print 'sorting paths'
    # d = d.sort_paths()
    # print 'joining paths'
    # d = d.join_paths(0.01)
    # print 'simplifying paths'
    # d = d.simplify_paths(0.001)
    print d.bounds
    d.dump('out.axi')
    im = d.render(scale=109 * 1, line_width=0.3/25.4, show_axi_bounds=False)
    im.write_to_png('out.png')
    # axi.draw(d)

def main():
    # single()
    multiple()

if __name__ == '__main__':
    main()
