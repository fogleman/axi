import axi
import sys

def prepare():
    d = axi.Drawing.load(sys.argv[1])
    print len(d.paths)
    print 'transforming'
    d = d.rotate_and_scale_to_fit(12, 8.5)
    print 'sorting'
    d = d.sort_paths()
    print 'joining'
    d = d.join_paths(0.01)
    print len(d.paths)
    print 'simplifying'
    d = d.simplify_paths(0.005)
    print 'rendering'
    im = d.render(
        scale=109 * 1, line_width=0.3/25.4,
        show_axi_bounds=False, use_axi_bounds=False)
    im.write_to_png('isolines.png')
    d.dump('isolines.axi')

def vertical_stack(ds, spacing=0, center=True):
    result = axi.Drawing()
    y = 0
    for d in ds:
        x = 0
        if center:
            x = -d.width / 2
        d = d.origin().translate(x, y)
        result.add(d)
        y += d.height + spacing
    return result

def title():
    d1 = axi.Drawing(axi.text('Topography of', axi.METEOROLOGY))
    d1 = d1.scale_to_fit_height(0.25)
    d2 = axi.Drawing(axi.text('Vancouver Island', axi.METEOROLOGY))
    d2 = d2.scale_to_fit_height(0.375)
    d = vertical_stack([d1, d2], 0.125, False)
    d = d.join_paths(0.01)
    d = d.simplify_paths(0.001)
    d = d.move(0, 8.5, 0, 1)
    return d

def main():
    d = axi.Drawing.load(sys.argv[1])
    d.add(title())
    im = d.render(
        scale=109 * 1, line_width=0.3/25.4,
        show_axi_bounds=False, use_axi_bounds=False)
    im.write_to_png('out.png')
    d.dump('out.axi')

if __name__ == '__main__':
    prepare()
    # main()
