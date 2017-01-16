import axi
import sys

def main():
    filename = sys.argv[1]
    d = axi.Drawing(axi.load_paths(filename))
    d = d.scale(1, -1)
    d = d.scale_to_fit(12, 8.5)
    d = d.sort_paths()
    d = d.join_paths(0.001)
    d = d.simplify_paths(0.001)
    d.render().write_to_png('out.png')
    axi.draw(d)

if __name__ == '__main__':
    main()
