from PIL import Image

import axi
import random
import sys

def main():
    filename = sys.argv[1]
    print 'loading image'
    im = Image.open(filename)
    im = im.convert('L')
    w, h = im.size
    data = list(im.getdata())
    paths = []
    for y in xrange(h):
        for x in xrange(w):
            if data[y*w+x] == 0:
                paths.append([(x, y), (x, y)])
    random.shuffle(paths)
    print len(paths)
    d = axi.Drawing(paths)
    print 'transforming paths'
    # d = d.scale(1, -1)
    d = d.rotate_and_scale_to_fit(12, 8.5, step=90)
    # print 'sorting paths'
    # d = d.sort_paths()
    # print 'joining paths'
    # d = d.join_paths(0.05)
    # print len(d.paths)
    print 'sorting paths'
    d = d.sort_paths()
    print 'joining paths'
    d = d.join_paths(0.03)
    print len(d.paths)
    d.paths = [x for x in d.paths if len(x) > 2]
    print 'simplifying paths'
    d = d.simplify_paths(0.002)
    print len(d.paths)
    print 'rendering paths'
    d.render(line_width=0.3/25.4).write_to_png('out.png')
    axi.draw(d)

if __name__ == '__main__':
    main()
