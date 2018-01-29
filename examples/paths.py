import axi
import sys

def main():
    filename = sys.argv[1]
    print 'loading paths'
    d = axi.Drawing(axi.load_paths(filename))
    # print 'eliminating duplicate paths'
    # d.paths = list(set([tuple(x) for x in d.paths]))
    print 'joining paths'
    d = d.join_paths(0.001)
    print 'transforming paths'
    d = d.scale(1, -1)
    d = d.rotate_and_scale_to_fit(12, 8.5, step=90)
    print 'sorting paths'
    d = d.sort_paths()
    print 'joining paths'
    d = d.join_paths(0.01)
    print 'simplifying paths'
    d = d.simplify_paths(0.001)
    print 'rendering paths'
    d.render(line_width=0.25/25.4).write_to_png('out.png')
    # axi.draw(d)

if __name__ == '__main__':
    main()
