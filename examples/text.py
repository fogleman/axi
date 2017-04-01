import axi

def main():
    text = 'Hello, world!'
    font = axi.FUTURAL
    d = axi.Drawing(axi.text(text, font))
    # d = d.rotate_and_scale_to_fit(12, 8.5, step=90)
    d = d.scale(0.01, 0.01)
    d = d.center(12, 8.5)
    d.render().write_to_png('out.png')
    # axi.draw(d)

if __name__ == '__main__':
    main()
