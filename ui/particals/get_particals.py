import random

def bubble(num, rect, radii):
    x0, y0 = rect.topleft
    x1, y1 = rect.bottomright
    r0, r1 = radii
    dx = x1 - x0
    dy = y1 - y0
    dr = r1 - r0
    return [[[x0 + (random.random() * dx), y0 + (random.random() * dy)], r0 + (random.random() * dr)] for _ in range(num)]