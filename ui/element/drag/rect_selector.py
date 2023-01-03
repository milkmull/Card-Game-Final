import pygame as pg

from ..base.base import Base_Element
from .dragger import Dragger

class Rect_Selector(Base_Element):
    def __init__(
        self,
        
        selection=None,
        
        color=(255, 0, 0),
        line_width=3,
        
        layer=-20,
        
        **kwargs
    ):
        super().__init__(layer=layer, **kwargs)
        
        self.selection = selection or Dragger.DRAGGERS
        self.anchor = None
        self.rect = pg.Rect(0, 0, 0, 0)
        
        self.color = color
        self.line_width = line_width
        
    @property
    def open(self):
        return self.anchor is not None
        
    @property
    def selected(self):
        return [d for d in self.selection if d.selected]
        
    def select(self):
        for d in self.selection:
            if self.rect.colliderect(d.rect):
                d.select()
        
    def events(self, events):
        if events["ctrl"]:
            if (kd := events.get("kd")):
                if kd.key == pg.K_a:
                    Dragger.select_all()
                    events.pop("kd")
                    
        else:
            if not events["clicked"] and (mbd := events.get("mbd")):
                if mbd.button == 1:
                    self.anchor = mbd.pos
                    events["clicked"] = self

        if (mbu := events.get("mbu")):
            if mbu.button == 1:
                self.select()
                self.anchor = None
        
    def update(self):
        if self.anchor:
            mx, my = pg.mouse.get_pos()
            ax, ay = self.anchor
            
            w = mx - ax
            h = my - ay
            
            self.rect.size = (abs(w), abs(h))
            self.rect.topleft = self.anchor
            
            if w < 0:
                self.rect.right = ax
            if h < 0:
                self.rect.bottom = ay
                
    def draw(self, surf):
        if self.anchor:
            points = (
                self.rect.topleft,
                self.rect.bottomleft,
                self.rect.bottomright,
                self.rect.topright
            )
            pg.draw.lines(surf, self.color, True, points, self.line_width)
        