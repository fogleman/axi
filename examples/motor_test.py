import axi
import random
import time

def main():
    d = axi.Device()
    d.pen_up()
    d.enable_motors()
    time.sleep(0.2)
    points = []
    points.append((0, 0))
    for i in range(10):
        x = random.random() * 11
        y = random.random() * 8.5
        points.append((x, y))
    points.append((0, 0))
    d.run_path(points)
    d.wait()
    d.disable_motors()

if __name__ == '__main__':
    main()
