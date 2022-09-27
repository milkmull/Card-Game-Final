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
        if tuple(self.size) != tuple(size):
            self.rect.size = size
            self.fit_text()

    def set_hover_text_color(self, hover_text_color):
        self.add_animation(
            [{
                'attr': 'text_color',
                'end': hover_text_color
            }],
            tag='hover'
        )

    def set_text(self, text, force=False, style=None):
        super().set_text(text, force=force, style=style)
        self.run_events('set_text')
        
    def draw(self, surf):
        self.draw_rect(surf)
        if self.clip:
            clip = surf.get_clip()
            surf.set_clip(self.clip_rect)
            self.draw_text(surf)
            surf.set_clip(clip)
            self.child_draw(surf)
        else:
            self.draw_text(surf)
            self.child_draw(surf)
        
        