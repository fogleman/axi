from .hershey_fonts import *

def text(string, font=FUTURAL, spacing=0):
    result = []
    x = 0
    for ch in string:
        i = ord(ch) - 32
        if i < 0 or i >= 96:
            x += spacing
            continue
        lt, rt, coords = font[i]
        for path in coords:
            path = [(x + i - lt, j) for i, j in path]
            if path:
                result.append(path)
        x += rt - lt + spacing
    return result
