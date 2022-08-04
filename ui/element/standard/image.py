import pygame as pg

from ..base.image_element import Image_Element

class Image(Image_Element): 
    @classmethod
    def from_path(cls, path, alpha=False, **kwargs):
        if alpha:
            image = pg.image.load(path).convert_alpha()
        else:
            image = pg.image.load(path).convert()
        return cls(image, **kwargs)
        
    def __init__(
        self,
        image,
        **kwargs
    ):
        super().__init__(image=image, **kwargs)

        self.fit_to_image()
        

