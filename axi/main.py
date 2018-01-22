import axi
import sys

'''
TODO:
axi draw FILE
axi (repl)
'''

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        return
    command, args = args[0], args[1:]
    command = command.lower()
    device = axi.Device()
    if command == 'zero':
        device.zero_position()
    elif command == 'home':
        device.home()
    elif command == 'up':
        device.pen_up()
    elif command == 'down':
        device.pen_down()
    elif command == 'on':
        device.enable_motors()
    elif command == 'off':
        device.disable_motors()
    elif command == 'move':
        dx, dy = map(float, args)
        device.move(dx, dy)
    elif command == 'goto':
        x, y = map(float, args)
        device.goto(x, y)
    elif command == 'draw':
        axi.draw(args[0])
    else:
        pass

if __name__ == '__main__':
    main()
