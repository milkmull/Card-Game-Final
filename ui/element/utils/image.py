import pygame as pg

from ...icons.icons import icons
from ..base.text import Text

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
    pad=None,
    color=(255, 255, 255),
    background_color=None
):
    w, h = size
    
    image = Text.render(
        icons['play'],
        font_name='icons.ttf',
        fgcolor=color,
        bgcolor=background_color,
        size=h
    )
    image = pg.transform.scale(image, size)

    a = 0
    match dir:
        case 'v':
            a = -90
        case '<':
            a = 180
        case '^':
            a = 90
    if a:
        image = pg.transform.rotate(image, a)

    if pad:
        surf = pg.Surface((w + (2 * pad[0]), h + (2 * pad[1]))).convert_alpha()
        if background_color:
            surf.fill(background_color)
        else:
            surf.fill((0, 0, 0, 0))
        surf.blit(image, image.get_rect().move(*pad))
        image = surf
    
    return image
    
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
            
    return pg.transform.rotozoom(surf, 0, 100)









