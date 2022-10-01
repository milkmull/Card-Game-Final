import pygame as pg

from ..base.image_element import Image_Element

class Image(Image_Element): 
    @classmethod
    def from_path(cls, path, alpha=False, **kwargs):
        if alpha:
            image = pg.image.load(path).convert_alpha()
        else:
            image = pg.image.load(path).convert()
        return cls(image=image, **kwargs)
        
    @classmethod
    def from_element(cls, element, **kwargs):
        image = pg.Surface(element.total_rect.size).convert()
        element.draw_on(image, element.total_rect)
        return cls(image=image, **kwargs)
        

