import pygame as pg

from ..base.image_element import Image_Element

class Image(Image_Element): 
    @classmethod
    def from_file(cls, file, alpha=False, **kwargs):
        if alpha:
            image = pg.image.load(file).convert_alpha()
        else:
            image = pg.image.load(file).convert()
        return cls(image=image, **kwargs)
        
    @classmethod
    def from_element(cls, element, alpha=False, **kwargs):
        if alpha:
            image = pg.Surface(element.total_rect.size).convert_alpha()
            image.fill((0, 0, 0, 0))
        else:
            image = pg.Surface(element.total_rect.size).convert()
        element.draw_on(image, element.total_rect)
        return cls(image=image, **kwargs)
        

