import axi
import os

N_PER_ROW = 8
SPACING = 2

def load(path):
    d = axi.Drawing.load(path)
    d = d.scale_to_fit(1.9, 1.9)
    d = d.join_paths(0.5 / 25.4)
    d = d.sort_paths()
    d = d.join_paths(0.5 / 25.4)
    d = d.origin()
    return d

def main():
    dirname = 'overlapping_circles'
    i = 0
    j = 0
    x = 0
    y = 0
    drawing = axi.Drawing([])
    for filename in sorted(os.listdir(dirname)):
        if not filename.endswith('.axi'):
            continue
        path = os.path.join(dirname, filename)
        print(path)
        d = load(path)
        d = d.translate(x, y)
        drawing.add(d)
        x += SPACING
        i += 1
        if i == N_PER_ROW:
            i = 0
            j += 1
            x = 0
            if j % 2:
                x = SPACING / 2
            y += SPACING * 0.866
    d = drawing
    d = d.center(*axi.A3_SIZE)
    print(len(d.paths))
    im = d.render(bounds=axi.A3_BOUNDS, line_width = 0.4 / 25.4)
    im.write_to_png('overlapping_circles.png')
    d.dump('overlapping_circles.axi')

if __name__ == '__main__':
    main()
