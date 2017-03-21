from shapely.geometry import LineString
import axi
import random

X1 = 0
X2 = 11
Y1 = 0
Y2 = 8.5

def make_segment(x1, y1, x2, y2):
    return LineString([(x1, y1), (x2, y2)])

def intersections(segments, segment):
    result = []
    for other in segments:
        x = segment.intersection(other)
        if x:
            try:
                result.append((x.x, x.y))
            except Exception:
                pass
    return result

def new_segment(segments):
    if random.random() < 0.5:
        x = X1 + random.random() * (X2 - X1)
        x = round(x * 5) / 5
        s = make_segment(x, Y1, x, Y2)
        ixs = intersections(segments, s)
        (x1, y1), (x2, y2) = random.sample(ixs, 2)
        return make_segment(x1, y1, x2, y2)
    else:
        y = Y1 + random.random() * (Y2 - Y1)
        y = round(y * 5) / 5
        s = make_segment(X1, y, X2, y)
        ixs = intersections(segments, s)
        (x1, y1), (x2, y2) = random.sample(ixs, 2)
        return make_segment(x1, y1, x2, y2)

def main():
    # seed = random.randint(0, 99999999)
    # print seed
    random.seed(82480774)
    segments = [
        make_segment(X1, Y1, X2, Y1),
        make_segment(X1, Y2, X2, Y2),
        make_segment(X1, Y2, X1, Y1),
        make_segment(X2, Y2, X2, Y1),
    ]
    for i in range(50):
        # print i
        segment = new_segment(segments)
        segments.append(segment)
    paths = []
    for segment in segments:
        paths.append(list(segment.coords))
    d = axi.Drawing(paths)
    d = d.sort_paths()
    d = d.join_paths(0.001)
    d.render().write_to_png('out.png')
    axi.draw(d)

if __name__ == '__main__':
    main()
