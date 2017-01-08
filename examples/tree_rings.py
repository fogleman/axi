import axi
import math
import sys

from PIL import Image

def create_paths(im):
    f = (255 * 255 * 3) ** 0.5
    paths = []
    w, h = im.size
    for m in [-2, -1, 0, 1, 2]:
        for radius in range(0, w, 8):
            path = []
            for a in range(1800):
                a = math.radians(a / 10.0)
                x = w / 2 + int(math.cos(a) * radius)
                y = h - int(math.sin(a) * radius)
                if x < 0 or x >= w:
                    continue
                if y < 0 or y >= h:
                    continue
                r, g, b = im.getpixel((x, y))
                p = (r * r + g * g + b * b) ** 0.5
                p = 1 - (p / f)
                p = p ** 2
                if p < 0.05:
                    if len(path) > 1:
                        paths.append(path)
                    path = []
                else:
                    x = w / 2 + math.cos(a) * (radius + m * p * 1.5)
                    y = h - math.sin(a) * (radius + m * p * 1.5)
                    path.append((x, y))
            if len(path) > 1:
                paths.append(path)
    return paths

def main():
    paths = create_paths(Image.open(sys.argv[1]))
    drawing = axi.Drawing(paths).rotate_and_scale_to_fit(11, 8.5, step=90)
    drawing = drawing.sort_paths().join_paths(0.02)
    axi.draw(drawing)

if __name__ == '__main__':
    main()
