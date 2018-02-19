import axi
import sys
import textwrap

NUMBER = '34'
LABEL = '#%s' % NUMBER

TITLE = textwrap.wrap(
    "Beta Subunit of the 20S Proteasome from T. acidophilum"
, 36)

SUBTITLE = textwrap.wrap(
    "These coordinates are from the 1995 crystal structure by Lowe et al. (Lowe et al., 1995). PDB entry 1PMA."
    # "Coordinates from the 1995 crystal structure by Lowe et al. PDB entry 1PMA."
, 60)

def concat(ds):
    result = axi.Drawing()
    for d in ds:
        result.add(d)
    return result

def stack_drawings(ds, spacing=0):
    result = axi.Drawing()
    y = 0
    for d in ds:
        d = d.origin().translate(-d.width / 2, y)
        result.add(d)
        y += d.height + spacing
    return result

def grid_drawings(ds, columns, spacing=0):
    result = axi.Drawing()
    w = max(d.width for d in ds) + spacing
    h = max(d.height for d in ds) + spacing
    for i, d in enumerate(ds):
        r = i / columns
        c = i % columns
        x = c * w + (w - d.width) / 2
        y = r * h + (h - d.height) / 2
        d = d.origin().translate(x, y)
        result.add(d)
    return result

def title():
    ds = [axi.Drawing(axi.text(line, axi.TIMESIB)) for line in TITLE]
    spacing = max(d.height for d in ds) * 1.5
    ds = [d.translate(-d.width / 2, i * spacing) for i, d in enumerate(ds)]
    d = concat(ds)
    d = d.scale_to_fit_width(8.5 * 4 / 5)
    d = d.scale_to_fit_height(0.8)
    d = d.join_paths(0.01)
    return d

def subtitle():
    # ds = [axi.Drawing(p) for p in axi.justify_text(SUBTITLE, axi.TIMESR)]
    # spacing = max(d.height for d in ds) * 1.5
    # ds = [d.translate(0, i * spacing) for i, d in enumerate(ds)]
    ds = [axi.Drawing(axi.text(line, axi.TIMESR)) for line in SUBTITLE]
    spacing = max(d.height for d in ds) * 1.5
    ds = [d.translate(-d.width / 2, i * spacing) for i, d in enumerate(ds)]
    d = concat(ds)
    d = d.scale_to_fit_width(8.5 * 2 / 3)
    d = d.scale_to_fit_height(0.4)
    d = d.join_paths(0.01)
    return d    

def label():
    d = axi.Drawing(axi.text(LABEL, axi.FUTURAL))
    d = d.scale_to_fit_height(0.125)
    d = d.rotate(-90)
    d = d.move(12, 8.5, 1, 1)
    d = d.join_paths(0.01)
    return d

def main():
    text = stack_drawings([title(), subtitle()], 0.3125)
    text = text.rotate(-90)
    text = text.move(12, 8.5 / 2, 1, 0.5)
    # text = title()

    filenames = [
        sys.argv[1],
        # 'ribbon/1j1c.txt',
        # 'ribbon/amyloid-beta/1mwp.txt',
        # 'ribbon/amyloid-beta/1owt.txt',
        # 'ribbon/amyloid-beta/1rw6.txt',
        # 'ribbon/amyloid-beta/1iyt.txt',
    ]
    angles = [90, 90, 75, 60]
    print 'loading paths'
    ds = []
    for filename, angle in zip(filenames, angles):
        ds.append(axi.Drawing(axi.load_paths(filename)).scale(1, -1))
    # d = grid_drawings(ds, 2, 1)
    d = ds[0]
    print len(d.paths)
    print 'joining paths'
    d = d.join_paths(0.01)
    print len(d.paths)
    print 'transforming paths'
    # d = d.scale(1, -1)
    d = d.rotate(180)
    d = d.rotate_and_scale_to_fit(8.5, 12 - text.height)
    # d = d.origin()
    print 'sorting paths'
    d = d.sort_paths()
    print 'joining paths'
    d = d.join_paths(0.01)
    print len(d.paths)
    print 'simplifying paths'
    d = d.simplify_paths(0.001)

    # add title and label and fit to page
    # d = stack_drawings([d, text], 1)
    # d = d.rotate(-90)
    # d = d.center(12, 8.5)
    d = d.rotate_and_scale_to_fit(12, 8.5).translate(-text.width * 0.6666, 0)
    d.add(text)
    # d.add(title())
    d.add(label())

    print 'rendering paths'
    d.render(line_width=0.25/25.4).write_to_png('out.png')
    # axi.draw(d)

    print d.bounds

    d.dump('out.axi')
    d.dump_svg('out.svg')

if __name__ == '__main__':
    main()
