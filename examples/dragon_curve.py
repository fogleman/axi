import axi

def main(iteration):
    turtle = axi.Turtle()
    for i in range(1, 2 ** iteration):
        turtle.forward(1)
        if (((i & -i) << 1) & i) != 0:
            turtle.circle(-1, 90, 36)
        else:
            turtle.circle(1, 90, 36)
    drawing = turtle.drawing.rotate_and_scale_to_fit(11, 8.5, step=90)
    axi.draw(drawing)

if __name__ == '__main__':
    main(12)
