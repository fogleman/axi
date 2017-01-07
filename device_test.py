from axi import Device, Planner
from math import sin, cos, pi
import time

def circle(cx, cy, r, n):
    points = []
    for i in range(n + 1):
        a = 2 * pi * i / n
        x = cx + cos(a) * r
        y = cy + sin(a) * r
        points.append((x, y))
    return points

def main():
    planner = Planner(acceleration=10, max_velocity=5, corner_factor=0.01)
    path = []
    path.append((0, 0))
    for i in range(10):
        path.extend(circle(4, 4, (i + 1) * 0.2, 72))
    path.append((0, 0))
    plan = planner.plan(path)

    d = Device()
    d.pen_up()
    d.enable_motors()
    time.sleep(0.2)
    d.run_plan(plan)
    d.wait()
    d.disable_motors()

if __name__ == '__main__':
    main()
