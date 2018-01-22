import axi
import sys

def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print 'Usage: python axifile.py drawing.axi'
        return
    d = axi.Drawing.load(args[0])
    axi.draw(d)

if __name__ == '__main__':
    main()
