import axi
import sys
import textwrap

NUMBER = 'XX'
LABEL = '#%s' % NUMBER

TITLE = textwrap.wrap(
    "X-ray structure of human beta3beta3 alcohol dehydrogenase"
, 40)

ABSTRACT = textwrap.wrap(
    "The three-dimensional structure of the human beta3beta3 dimeric alcohol dehydrogenase (beta3) was determined to 2.4-A resolution. beta3 was crystallized as a ternary complex with the coenzyme NAD+ and the competitive inhibitor 4-iodopyrazole. beta3 is a polymorphic variant at ADH2 that differs from beta1 by a single amino acid substitution of Arg-369 --> Cys. The available x-ray structures of mammalian alcohol dehydrogenases show that the side chain of Arg-369 forms an ion pair with the NAD(H) pyrophosphate to stabilize the E.NAD(H) complex. The Cys-369 side chain of beta3 cannot form this interaction. The three-dimensional structures of beta3 and beta1 are virtually identical, with the exception that Cys-369 and two water molecules in beta3 occupy the position of Arg-369 in beta1. The two waters occupy the same positions as two guanidino nitrogens of Arg-369. Hence, the number of hydrogen bonding interactions between the enzyme and NAD(H) are the same for both isoenzymes. However, beta3 differs from beta1 by the loss of the electrostatic interaction between the NAD(H) pyrophosphate and the Arg-369 side chain. The equilibrium dissociation constants of beta3 for NAD+ and NADH are 350-fold and 4000-fold higher, respectively, than those for beta1. These changes correspond to binding free energy differences of 3.5 kcal/mol for NAD+ and 4.9 kcal/mol for NADH. Thus, the Arg-369 --> Cys substitution of beta3 isoenzyme destabilizes the interaction between coenzyme and beta3 alcohol dehydrogenase."
, 120)

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
    d = d.scale_to_fit_width(8.5)
    d = d.join_paths(0.01)
    return d

def abstract():
    ds = [axi.Drawing(p) for p in axi.justify_text(ABSTRACT, axi.TIMESR)]
    spacing = max(d.height for d in ds) * 1.5
    ds = [d.translate(0, i * spacing) for i, d in enumerate(ds)]
    d = concat(ds)
    d = d.scale_to_fit_width(8.5)
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
    # text = stack_drawings([title(), abstract()], 0.25)
    text = title()

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
        ds.append(axi.Drawing(axi.load_paths(filename)).scale_to_fit(8.5, 12).scale(1, -1))
    d = grid_drawings(ds, 2, 1)
    print len(d.paths)
    print 'joining paths'
    d = d.join_paths(0.01)
    print len(d.paths)
    print 'transforming paths'
    # d = d.scale(1, -1)
    d = d.rotate_and_scale_to_fit(8.5, 12 - text.height - 0.75, step=5)
    d = d.origin()
    print 'sorting paths'
    d = d.sort_paths()
    print 'joining paths'
    d = d.join_paths(0.01)
    print len(d.paths)
    print 'simplifying paths'
    d = d.simplify_paths(0.001)

    # add title and label and fit to page
    d = stack_drawings([d, text], 0.75)
    d = d.rotate(-90)
    # d = d.center(12, 8.5)
    d = d.scale_to_fit(12, 8.5)
    # d.add(title())
    # d.add(label())

    print 'rendering paths'
    d.render(line_width=0.25/25.4).write_to_png('out.png')
    # axi.draw(d)

    print d.bounds

    d.dump('out.axi')
    d.dump_svg('out.svg')

if __name__ == '__main__':
    main()
