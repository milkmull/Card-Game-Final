from .element import Element
from .image import Image

class Image_Element(Element, Image):
    def __init__(self, **kwargs):
        Element.__init__(self, **kwargs)
        Image.__init__(self, **kwargs)
        
    @property
    def size(self):
        return self.rect.size
        
    @size.setter
    def size(self, size):
        self.rect.size = size
        self.fit_image()

    def draw(self, surf):
        self.draw_rect(surf)
        if self.clip:
            clip = surf.get_clip()
            surf.set_clip(self.padded_rect)
            self.draw_image(surf)
            self.child_draw(surf)
            surf.set_clip(clip)
        else:
            self.draw_image(surf)
            self.child_draw(surf)
        
        