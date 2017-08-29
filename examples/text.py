import axi
import sys

LINES = [
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor',
    'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis',
    'nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
    'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu',
    'fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in',
    'culpa qui officia deserunt mollit anim id est laborum.',
]

LINES = [
    'When you wish upon a star',
    'Makes no difference who you are',
    'Anything your heart desires will come to you',
]

def stack_drawings(ds, spacing=0):
    result = axi.Drawing()
    y = 0
    for d in ds:
        d = d.origin().translate(-d.width / 2, y)
        result.add(d)
        y += d.height + spacing
    return result

def main():
    font = axi.SCRIPTS
    ds = [axi.Drawing(axi.text(line, font)).scale_to_fit_height(1) for line in LINES]
    d = stack_drawings(ds, 0.1)
    # d = d.rotate_and_scale_to_fit(12, 8.5, step=90)
    # d = d.scale(0.02, 0.02)
    # d = d.center(12, 8.5)
    # d = d.move(0, 0, 0, 0)
    d = d.scale_to_fit(12, 8.5)
    # d = d.center(12, 8.5)
    d = d.move(6, 0, 0.5, 0)
    d = d.translate(0, 0.01)
    d = d.join_paths(0.01)
    d.render().write_to_png('out.png')
    print sum(x.t for x in axi.Device().plan_drawing(d))
    if len(sys.argv) > 1 and sys.argv[1].endswith(".png"):
        d.render().write_to_png(sys.argv[1])
    else:
        axi.draw(d)

if __name__ == '__main__':
    main()
