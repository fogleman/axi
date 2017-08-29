import axi
import sys

def main():
    system = axi.LSystem({
        'A': 'A-B--B+A++AA+B-',
        'B': '+A-BB--B-A++A+B',
    })
    d = system.run('A', 5, 60)
    # system = axi.LSystem({
    #     'X': 'F-[[X]+X]+F[+FX]-X',
    #     'F': 'FF',
    # })
    # d = system.run('X', 6, 20)
    d = d.rotate_and_scale_to_fit(12, 8.5, step=90)
    # d = d.sort_paths()
    # d = d.join_paths(0.015)
    if len(sys.argv) > 1 and sys.argv[1].endswith(".png"):
        d.render().write_to_png(sys.argv[1])
    else:
        axi.draw(d)

if __name__ == '__main__':
    main()
