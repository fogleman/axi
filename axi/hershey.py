from .hershey_fonts import *

def text(string, font=FUTURAL, spacing=0, extra=0):
    result = []
    x = 0
    for ch in string:
        index = ord(ch) - 32
        if index < 0 or index >= 96:
            x += spacing
            continue
        lt, rt, coords = font[index]
        for path in coords:
            path = [(x + i - lt, j) for i, j in path]
            if path:
                result.append(path)
        x += rt - lt + spacing
        if index == 0:
            x += extra
    return result

def text_width(string, font=FUTURAL, spacing=0):
    x = 0
    for ch in string:
        index = ord(ch) - 32
        if index < 0 or index >= 96:
            x += spacing
            continue
        lt, rt, coords = font[index]
        x += rt - lt + spacing
    return x

def justify_text(lines, font=FUTURAL, spacing=0):
    widths = [text_width(x, font, spacing) for x in lines]
    max_width = max(widths)
    extras = []
    for i, (line, width) in enumerate(zip(lines, widths)):
        spaces = line.count(' ')
        if spaces == 0:
            e = 0
        else:
            e = float(max_width - width) / spaces
        if i == len(lines) - 1:
            e = 0
        extras.append(e)
        print width, max_width, spaces, e
    return [text(line, font, spacing, extra) for line, extra in zip(lines, extras)]
