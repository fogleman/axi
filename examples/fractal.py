from shapely import geometry
import axi
import sys

def main():
    size = axi.A3_SIZE
    bounds = axi.A3_BOUNDS
    d = axi.Drawing.load(sys.argv[1])
    print(len(d.paths[0]))
    d = d.scale_to_fit(*size).center(*size)
    d = d.simplify_paths(0.01 / 25.4)
    print(len(d.paths[0]))

    g = geometry.Polygon(d.paths[0])
    while True:
        b = -0.25 / 25.4
        g = g.buffer(b)
        if g.is_empty:
            break
        g = g.simplify(0.01 / 25.4)
        d.paths.extend(axi.shapely_to_paths(g))

    print(d.bounds)
    d.dump('out.axi')
    d.render(bounds=bounds, line_width=0.2/25.4).write_to_png('out.png')

if __name__ == '__main__':
    main()
