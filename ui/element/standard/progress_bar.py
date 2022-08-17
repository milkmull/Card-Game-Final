import pygame as pg

from ..base.element import Element

class Progress_Bar(Element):
    def __init__(
        self,
        bar_color=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.bar_color = bar_color
        self.state = 0
        
    @property
    def bar_rect(self):
        return pg.Rect(
            self.rect.x,
            self.rect.y,
            int(self.rect.width * self.state),
            self.rect.height
        )
        
    def set_state(self, state):
        self.state = state
        
    def draw(self, surf):
        super().draw(surf)
        
        pg.draw.rect(
            surf,
            self.bar_color,
            self.bar_rect,
            **self.border_kwargs
        )