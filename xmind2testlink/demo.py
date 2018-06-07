f = {}
f['count'] = 4


def loop(c, parent=None):
    if c > 0:
        return c, parent

    if parent:
        parent.append(c)
    else:
        parent = [c]

    c = c + 1

    return loop(c, parent)


for x in loop(-5):
    print(x)
