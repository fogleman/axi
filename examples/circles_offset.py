import axi
import math
import random

W, H = axi.A3_SIZE

def circle_ray_intersection(cx, cy, cr, ox, oy, dx, dy):
    xd = ox - cx
    yd = oy - cy
    a = dx * dx + dy * dy
    b = 2 * (dx * (ox - cx) + dy * (oy - cy))
    c = xd * xd + yd * yd - cr * cr
    d = b * b - 4 * a * c
    if d < 0:
        return None
    t = (-b + math.sqrt(d)) / (2 * a)
    x = ox + dx * t
    y = oy + dy * t
    return (x, y)

def path(x0, y0, r0, x1, y1, r1):
    t = random.random()
    a0 = random.random() * 2 * math.pi
    a1 = a0 + math.radians(10)
    n = 100
    result = []
    for i in range(n + 1):
        u = i / n
        a = a0 + (a1 - a0) * u
        dx = math.cos(a)
        dy = math.sin(a)
        ax, ay = circle_ray_intersection(x0, y0, r0, x0, y0, dx, dy)
        bx, by = circle_ray_intersection(x1, y1, r1, x0, y0, dx, dy)
        x = ax + (bx - ax) * t
        y = ay + (by - ay) * t
        result.append((x, y))
    return result

def main():
    x0 = 0
    y0 = 0
    r0 = 1.5
    x1 = -0.25
    y1 = 0
    r1 = 2
    paths = []
    for i in range(500):
        paths.append(path(x0, y0, r0, x1, y1, r1))
    d = axi.Drawing(paths).rotate_and_scale_to_fit(W, H)#.sort_paths()
    im = d.render()
    im.write_to_png('circles_offset.png')
    d.dump('circles_offset.axi')
    # axi.draw(d)

if __name__ == '__main__':
    main()
