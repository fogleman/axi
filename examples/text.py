from __future__ import division

import axi
import itertools
import string

TEXT = (
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor '
    'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis '
    'nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. '
    'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu '
    'fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in '
    'culpa qui officia deserunt mollit anim id est laborum. '
)

def word_wrap(text, width, measure_func):
    result = []
    for line in text.split('\n'):
        fields = itertools.groupby(line, lambda x: x.isspace())
        fields = [''.join(g) for _, g in fields]
        if len(fields) % 2 == 1:
            fields.append('')
        x = ''
        for a, b in zip(fields[::2], fields[1::2]):
            w, _ = measure_func(x + a)
            if w > width:
                if x == '':
                    result.append(a)
                    continue
                else:
                    result.append(x)
                    x = ''
            x += a + b
        if x != '':
            result.append(x)
    result = [x.strip() for x in result]
    return result

class Font(object):
    def __init__(self, font, point_size):
        self.font = font
        self.max_height = axi.Drawing(axi.text(string.printable, font)).height
        # self.cap_height = axi.Drawing(axi.text('H', font)).height
        height = point_size / 72
        self.scale = height / self.max_height
    def text(self, text):
        d = axi.Drawing(axi.text(text, self.font))
        d = d.scale(self.scale)
        return d
    def justify_text(self, text, width):
        d = self.text(text)
        w = d.width
        spaces = text.count(' ')
        if spaces == 0 or w >= width:
            return d
        e = ((width - w) / spaces) / self.scale
        d = axi.Drawing(axi.text(text, self.font, extra=e))
        d = d.scale(self.scale)
        return d
    def measure(self, text):
        return self.text(text).size
    def wrap(self, text, width, line_spacing=1, align=0, justify=False):
        lines = word_wrap(text, width, self.measure)
        ds = [self.text(line) for line in lines]
        max_width = max(d.width for d in ds)
        if justify:
            jds = [self.justify_text(line, max_width) for line in lines]
            ds = jds[:-1] + [ds[-1]]
        spacing = line_spacing * self.max_height * self.scale
        result = axi.Drawing()
        y = 0
        for d in ds:
            if align == 0:
                x = 0
            elif align == 1:
                x = max_width - d.width
            else:
                x = max_width / 2 - d.width / 2
            result.add(d.translate(x, y))
            y += spacing
        return result

def main():
    font = Font(axi.FUTURAL, 18)
    d = font.wrap(TEXT * 2, 12, 1.5, justify=True)
    d = d.center(12, 8.5)
    d.render(bounds=axi.V3_BOUNDS).write_to_png('out.png')

if __name__ == '__main__':
    main()
