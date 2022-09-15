import random

RAND = random.Random(0)

def bubble(num, rect, radii):
    x0, y0 = rect.topleft
    x1, y1 = rect.bottomright
    r0, r1 = radii
    dx = x1 - x0
    dy = y1 - y0
    dr = r1 - r0
    return [[[x0 + (RAND.random() * dx), y0 + (RAND.random() * dy)], r0 + (RAND.random() * dr)] for _ in range(num)]