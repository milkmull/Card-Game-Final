import pygame as pg

from .scene.base import Base_Loop

BASE_SIZE = (0, 0)

def init(size=(0, 0), caption=None, icon_path=None, **kwargs):
    global BASE_SIZE
    
    pg.init()
    if caption:
        pg.display.set_caption(caption)
    pg.display.set_mode(size=size, **kwargs)
    if icon_path:
        pg.display.set_icon(pg.image.load(icon_path).convert())
    BASE_SIZE = get_size()
    
def quit():
    pg.quit()

def get_constants():
    w, h = pg.display.get_surface().get_size()
    constants = {
        'WIDTH': w,
        'HEIGHT': h,
        'SIZE': (w, h),
        'CENTER': (w // 2, h // 2),
        'CENTERX': w // 2,
        'CENTERY': h // 2
    }
    
    return constants
    
def get_size():
    return pg.display.get_surface().get_size()
    
def get_base_size():
    return BASE_SIZE
    
