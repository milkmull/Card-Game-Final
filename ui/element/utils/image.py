import pygame as pg

def get_surface(size, color=None, alpha=False):
    if not alpha:
        surf = pg.Surface(size).convert()
    else:
        surf = pg.Surface(size).convert_alpha()
    if color is not None:
        surf.fill(color)
    return surf

def get_arrow(
    dir,
    size,
    padding=(0, 0),
    color=(255, 255, 255),
    background_color=(0, 0, 0, 0)
):
    surf = pg.Surface(size).convert_alpha()
    surf.fill(background_color)
    w, h = size
    top = (w // 2, padding[1] // 2)
    bottomleft = (padding[0] // 2, h - (padding[1] // 2))
    bottomright = (w - (padding[0] // 2), h - (padding[1] // 2))
    pg.draw.polygon(surf, color, (top, bottomleft, bottomright))
    
    a = 0
    if dir == 'v':
        a = 180
    elif dir == '<':
        a = 90
    elif dir == '>':
        a = -90
    if a:
        surf = pg.transform.rotate(surf, a)
        
    return surf
    
def crop(img, x, y, w, h):
    surf = pg.Surface((w, h))
    surf.blit(img, (0, 0), (x, y, w, h))
    return surf
    
def transform(mode, *args, **kwargs):
    return getattr(pg.transform, mode)(*args, **kwargs)
    
def gradient(colors, dir, size, angle=0):
    if dir:
        surf = pg.Surface((1, len(colors))).convert()
        for y, color in enumerate(colors):
            surf.set_at((0, y), color)
            
    else:
        surf = pg.Surface((len(colors), 1)).convert()
        for x, color in enumerate(colors):
            surf.set_at((x, 0), color)
            
    return pg.transform.roto_zoom(surf, angle, size)









