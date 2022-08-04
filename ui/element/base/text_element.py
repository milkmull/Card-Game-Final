from .element import Element
from .text import Text

class Text_Element(Element, Text):
    def __init__(self, **kwargs):
        Element.__init__(self, **kwargs)
        Text.__init__(self, **kwargs)
        
    @property
    def size(self):
        return self.rect.size
        
    @size.setter
    def size(self, size):
        self.rect.size = size
        self.fit_text()
        
    def set_text(self, text):
        super().set_text(text)
        self.run_events('set')
        
    def draw(self, surf):
        self.draw_rect(surf)
        if self.clip:
            clip = surf.get_clip()
            surf.set_clip(self.padded_rect)
            self.draw_text(surf)
            self.child_draw(surf)
            surf.set_clip(clip)
        else:
            self.draw_text(surf)
            self.child_draw(surf)
        
        