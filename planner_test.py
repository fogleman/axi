from axi import Planner
from math import pi, sin, cos

def circle(cx, cy, r, n):
    points = []
    for i in range(n + 1):
        a = 2 * pi * i / n
        x = cx + cos(a) * r
        y = cy + sin(a) * r
        points.append((x, y))
    return points

def main():
    points = circle(0, 0, 100, 90)
    points = [(-100, -100), (100, -100)] + points + [(100, 100), (-100, 100), (-100, -100)]
    for r in range(20, 100, 20):
        points = circle(0, 0, r, 90) + points
    planner = Planner(acceleration=50, max_velocity=200, corner_factor=1, jerk=100)
    pieces = planner.plan(points)
    print 'var PIECES = ['
    for p in pieces:
        record = (p.p1.x, p.p1.y, p.p2.x, p.p2.y, p.acceleration, p.duration)
        print '[%s],' % ','.join(map(str, record))
    print '];'
    # pieces = planner.smooth(pieces)
    # for p in pieces:
    #     print p.acceleration, p.duration

if __name__ == '__main__':
    main()
