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
    planner = Planner(
        acceleration=100, max_velocity=200, corner_factor=1, jerk=5000)
    plan = planner.jerk_plan(points)
    print 'var PIECES = ['
    for b in plan.blocks:
        record = (b.p1.x, b.p1.y, b.p2.x, b.p2.y, b.j, b.t)
        print '[%s],' % ','.join(map(str, record))
    print '];'

if __name__ == '__main__':
    main()
