import math

import pygame as pg

from .math.bezier import bezier_points

def aaline(surf, color, start_pos, end_pos, width=1):
    x0, y0 = start_pos
    x1, y1 = end_pos
    
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2

    length = math.hypot(x1 - x0, y1 - y0)
    angle = math.atan2(y0 - y1, x0 - x1)
    
    length2 = length / 2
    width2 = width / 2
    
    sin_angle = math.sin(angle)
    cos_angle = math.cos(angle)
    
    width2_sin_angle = width2 * sin_angle
    width2_cos_angle = width2 * cos_angle
    
    length2_sin_angle = length2 * sin_angle
    length2_cos_angle = length2 * cos_angle

    tl = (
        cx + length2_cos_angle - width2_sin_angle,
        cy + width2_cos_angle + length2_sin_angle
    )
    tr = (
        cx - length2_cos_angle - width2_sin_angle,
        cy + width2_cos_angle - length2_sin_angle
    )
    bl = (
        cx + length2_cos_angle + width2_sin_angle,
        cy - width2_cos_angle + length2_sin_angle
    )
    br = (
        cx - length2_cos_angle + width2_sin_angle,
        cy - width2_cos_angle - length2_sin_angle
    )
    
    pg.gfxdraw.aapolygon(surf, (tl, tr, br, bl), color)
    pg.gfxdraw.filled_polygon(surf, (tl, tr, br, bl), color)
    
def aalines(surf, color, closed, points, width=1):
    for i in range(-closed, len(points) - 1):
        aaline(surf, color, points[i], points[i + 1], width=width)

def bezier(surf, color, points, width=1, samples=20):
    new_points = bezier_points(points, samples)
    aalines(surf, color, False, new_points, width=width)
    
def dashed_bezier(surf, color, points, width=1, samples=20):
    new_points = bezier_points(points, samples)
    for i in range(0, len(new_points) - 1, 2):
        p0 = new_points[i]
        p1 = new_points[i + 1]
        aaline(surf, color, p0, p1, width=width)
    
def aacircle(surf, color, center, radius):
    x, y = center
    pg.gfxdraw.aacircle(surf, x, y, radius, color)
    pg.gfxdraw.filled_circle(surf, x, y, radius, color)