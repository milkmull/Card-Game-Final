import random

RAND = random.Random(0)

def bubble(num, rect, radii):
    x0, y0 = rect.topleft
    x1, y1 = rect.bottomright
    r0, r1 = radii
    dx = x1 - x0
    dy = y1 - y0
    dr = r1 - r0
    
    particles = []
    for _ in range(num):
        particles.append([
            [x0 + (RAND.random() * dx), y0 + (RAND.random() * dy)], 
            r0 + (RAND.random() * dr)
        ])
    return particles
    
def explode_no_grav(num, rect, vel, radii, time):
    x0, y0 = rect.topleft
    x1, y1 = rect.bottomright
    v0, v1 = vel
    r0, r1 = radii
    t0, t1 = time
    
    dx = x1 - x0
    dy = y1 - y0
    dr = r1 - r0
    dv = v1 - v0
    dt = t1 - t0
    
    
    particles = []
    for _ in range(num):
        particles.append([
            [x0 + (RAND.random() * dx), y0 + (RAND.random() * dy)],
            [v0 + (RAND.random() * dv), v0 + (RAND.random() * dv)],
            r0 + (RAND.random() * dr),
            t0 + (RAND.random() * dt)
        ])
    return particles