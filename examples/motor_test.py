import axi
import math
import random
import time

def circle(cx, cy, radius, n, rotation):
    points = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n + rotation
        x = cx + math.cos(a) * radius
        y = cy + math.sin(a) * radius
        points.append((x, y))
    return points

def main():
    d = axi.Device()
    d.pen_up()
    d.enable_motors()
    time.sleep(0.2)
    points = []
    points.append((0, 0))
    for i in range(10):
        while True:
            x = random.random() * 11
            y = random.random() * 8.5
            r = random.random() * 4
            if x - r < 0 or x + r > 11:
                continue
            if y - r < 0 or y + r > 8.5:
                continue
            break
        rotation = random.random() * 2 * math.pi
        c = circle(x, y, r, 90, rotation)
        if random.random() < 0.5:
            c = list(reversed(c))
        points.extend(c)
    points.append((0, 0))
    d.run_path(points)
    d.wait()
    d.disable_motors()

if __name__ == '__main__':
    main()
