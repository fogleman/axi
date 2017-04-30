import axi
import csv
import math

MIN_SIZE = 0.01
MAX_SIZE = 0.8

def circle(cx, cy, r, n):
    points = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        points.append((x, y))
    return points

def fill_circle(cx, cy, cr, n):
    result = []
    r = cr
    while r > 0:
        result.append(circle(cx, cy, r, n))
        r -= 0.05
    result[-1].append((cx, cy))
    return result

def punchcard_from_csv(csv_path):
    with open(csv_path, 'rb') as fp:
        reader = csv.reader(fp)
        csv_rows = list(reader)
    row_labels = [x[0] for x in csv_rows[1:]]
    col_labels = csv_rows[0][1:]
    data = []
    for csv_row in csv_rows[1:]:
        row = []
        for value in csv_row[1:]:
            try:
                value = float(value)
            except ValueError:
                value = None
            row.append(value)
        data.append(row)
    lo = min(x for row in data for x in row if x)
    hi = max(x for row in data for x in row if x)
    min_area = math.pi * (MIN_SIZE / 2.0) ** 2
    max_area = math.pi * (MAX_SIZE / 2.0) ** 2
    paths = []
    for r, row in enumerate(data):
        for c, value in enumerate(row):
            if not value:
                continue
            pct = 1.0 * (value - lo) / (hi - lo)
            pct = pct ** 0.5
            area = pct * (max_area - min_area) + min_area
            radius = (area / math.pi) ** 0.5
            paths.extend(fill_circle(c, r, radius, 90))
    for r, label in enumerate(row_labels):
        d = axi.Drawing(axi.text(label.upper(), axi.TIMESR))
        d = d.scale(0.02, 0.02).move(-1, r, 0.5, 0.5)
        paths.extend(d.paths)
    for c, label in enumerate(col_labels):
        d = axi.Drawing(axi.text(label.upper(), axi.TIMESR))
        d = d.scale(0.02, 0.02).move(c, -1, 0.5, 0.5)
        paths.extend(d.paths)
    d = axi.Drawing(paths)
    d = d.scale_to_fit(12, 8.5)

    print 'joining paths'
    d = d.join_paths(0.02)
    print 'simplifying paths'
    d = d.simplify_paths(0.001)

    d.render().write_to_png('out.png')
    axi.draw(d)

if __name__ == '__main__':
    import sys
    punchcard_from_csv(sys.argv[1])
