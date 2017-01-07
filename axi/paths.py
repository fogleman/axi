from spatial import Index

def sort_paths(paths, reversable=True):
    first = paths[0]
    paths.remove(first)
    result = [first]
    points = []
    for path in paths:
        x1, y1 = path[0]
        x2, y2 = path[-1]
        points.append((x1, y1, path, False))
        if reversable:
            points.append((x2, y2, path, True))
    index = Index(points)
    while index.size > 0:
        x, y, path, reverse = index.search(result[-1][-1])
        x1, y1 = path[0]
        x2, y2 = path[-1]
        index.remove((x1, y1, path, False))
        if reversable:
            index.remove((x2, y2, path, True))
        if reverse:
            result.append(list(reversed(path)))
        else:
            result.append(path)
    return result
