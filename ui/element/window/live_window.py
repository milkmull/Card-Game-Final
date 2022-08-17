from ..base.element import Element
from .window_base import Window_Base

class Live_Window(Window_Base, Element):
    def __init__(self, **kwargs):
        Element.__init__(self, **kwargs)
        Window_Base.__init__(self, **kwargs)
        
    def bind(self, element):
        element.set_parent(self.bounding_box, current_offset=True)
        
    def events(self, events):
        for e in self.elements:
            if e.enabled and self.rect.collidepoint(e.rect.center):
                e.events(events)
        super().events(events)
        
    def update(self):
        super().update()
        for e in self.elements:
            if e.refresh:
                e.update()
            
    def draw(self, surf):
        super().draw(surf)
        clip = surf.get_clip()
        r = self.clip_rect if self.clip_size else self.rect
        surf.set_clip(r)
        for e in sorted(self.elements, key=lambda e: e.layer):
            if e.visible and r.colliderect(e.rect):
                e.draw(surf)
        surf.set_clip(clip)
                