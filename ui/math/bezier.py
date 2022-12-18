import math
import random

def _point_on_bezier(points, t):
    q = list(points)
    for k in range(1, len(points)):
        for i in range(len(points) - k):
            q[i] = (1 - t) * q[i][0] + t * q[i + 1][0], (1 - t) * q[i][1] + t * q[i + 1][1]
    return (round(q[0][0]), round(q[0][1]))
    
def bezier_points(points, samples=20):
    return [_point_on_bezier(points, i / samples) for i in range(0, samples + 1)]
    
def bezier_structure(start, end, max_pad=50):
    ox, oy = start
    ix, iy = end
    
    cx = (ox + ix) // 2
    cy = (oy + iy) // 2 
        
    dx = max(ix - ox, -max_pad)
    if dx > 0:
        return (start, (cx, oy), (cx, iy), end)
        
    xmin = ix + dx
    xmax = ox - dx
    return (start, (xmax, oy), (xmax, cy), (xmin, cy), (xmin, iy), end)

class Bezier:
    
    RAND = random.Random()
    
    def linear(x):
        return x
    
    def ease_in_sine(x):
        return 1 - math.cos((x * math.pi) / 2)
        
    def ease_out_sine(x):
        return math.sin((x * math.pi) / 2)
        
    def ease_in_out_sine(x):
        return -(math.cos(math.pi * x) - 1) / 2
        
        
    def ease_in_quad(x):
        return x * x
        
    def ease_out_quad(x):
        return 1 - (1 - x) * (1 - x)
        
    def ease_in_out_quad(x):
        if x < 0.5:
            return 2 * x * x
        return 1 - pow(-2 * x + 2, 2) / 2
        
        
    def ease_in_cubic(x):
        return x * x * x
        
    def ease_out_cubic(x):
        return 1 - pow(1 - x, 3)
        
    def ease_in_out_cubic(x):
        if x < 0.5:
            return 4 * x * x * x
        return 1 - pow(-2 * x + 2, 3) / 2
        
    
    def ease_in_quart(x):
        return x * x * x * x
        
    def ease_out_quart(x):
        return 1 - pow(1 - x, 4)
        
    def ease_in_out_quart(x):
        if x < 0.5:
            return 8 * x * x * x * x
        return 1 - pow(-2 * x + 2, 4) / 2
        
    
    def ease_in_quint(x):
        return x * x * x * x * x
        
    def ease_out_quint(x):
        return 1 - pow(1 - x, 5)
        
    def ease_in_out_quint(x):
        if x < 0.5:
            return 16 * x * x * x * x * x
        return 1 - pow(-2 * x + 2, 5) / 2
        
    
    def ease_in_expo(x):
        if x == 0:
            return 0
        return pow(2, 10 * x - 10)
        
    def ease_out_expo(x):
        if x == 1:
            return 1
        return 1 - pow(2, -10 * x)
        
    def ease_in_out_expo(x):
        if x == 0:
            return 0
        if x == 1:
            return 1
        if x < 0.5:
            return pow(2, 20 * x - 10) / 2
        return (2 - pow(2, -20 * x + 10)) / 2
        
    
    def ease_in_circ(x):
        return 1 - sqrt(1 - pow(x, 2))
        
    def ease_out_circ(x):
        return sqrt(1 - pow(x - 1, 2))
        
    def ease_in_out_circ(x):
        if x < 0.5:
            return (1 - sqrt(1 - pow(2 * x, 2))) / 2
        return sqrt(1 - pow(-2, * x + 2, 2)) + 1
        
    
    def ease_in_back(x):
        c1 = 1.70158
        c3 = c1 + 1
        
        return c3 * x * x * x - c1 * x * x
    
    def ease_out_back(x):
        c1 = 1.70158
        c3 = c1 + 1
        
        return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)
        
    def ease_in_out_back(x):
        c1 = 1.70158
        c2 = c1 * 1.525
        
        if x < 0.5:
            return (pow(2 * x, 2) * ((c2 + 1) * 2 * x - c2)) / 2
        return (pow(2 * x - 2, 2) * ((c2 + 1) * (x * 2 - 2) + c2) + 2) / 2
        
    
    def ease_in_elastic(x):
        c4 = (2 * math.pi) / 3
        
        if x == 0:
            return 0
        if x == 1:
            return 1
        return -pow(2, 10 * x - 10) * math.sin((x * 10 - 10.75) * c4)
        
    def ease_out_elastic(x):
        c4 = (2 * math.pi) / 3
        
        if x == 0:
            return 0
        if x == 1:
            return 1
        return pow(2, -10 * x) * math.sin((x * 10 - 0.75) * c4) + 1
        
    def ease_in_out_elastic(x):
        c5 = (2 * math.pi) / 4.5
        
        if x == 0:
            return 0
        if x == 1:
            return 1
        if x < 0.5:
            return -(pow(2, 20 * x - 10) * math.sin((20 * x - 11.125) * c5)) / 2
        return (pow(2, -20 * x + 10) * math.sin((20 * x - 11.125) * c5)) / 2 + 1
        
    
    def ease_in_bounce(x):
        return 1 - Bezier.ease_out_bounce(1 - x)
        
    def ease_out_bounce(x):
        n1 = 7.5625
        d1 = 2.75
        
        if x < 1 / d1:
            return n1 * x * x
        if x < 2 / d1:
            return n1 * (x - 1.5 / d1) * x + 0.75
        if  x < 2.5 / d1:
            return n1 * (x - 2.25 / d1) * x + 0.9375
        return n1 * (x - 2.625 / d1) * x + 0.984375
        
    def ease_in_out_bounce(x):
        if x < 0.5:
            return (1 - Bezier.ease_out_bounce(1 - 2 * x)) / 2
        return (1 + Bezier.ease_out_bounce(2 * x - 1)) / 2
        
        
    def random_shake(x):
        if Bezier.RAND.getrandbits(1):
            return -Bezier.RAND.random()
        return Bezier.RAND.random()
        
        