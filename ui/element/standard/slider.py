import pygame as pg

from ..base.element import Element
from ..base.style import Style

class Slider(Element):
    default_handel_kwargs = {
        'fill_color': (255, 255, 255),
        'outline_color': (0, 0, 0),
        'outline_width': 1
    }

    def __init__(
        self,
        range=range(1),
        dir=0,
        flipped=False,
        handel_kwargs={},
        state=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.dir = dir
        self.range = range
        
        self.flipped = flipped
        self.held = False
        
        if 'size' not in handel_kwargs:
            if not self.dir:
                size = (10, self.rect.height * 2)
            else:
                size = (self.rect.width * 2, 10)
            handel_kwargs['size'] = size
        self.handel = Style(**(Slider.default_handel_kwargs | handel_kwargs))
        
        if not dir:
            self.add_child(
                self.handel,
                current_offset=True,
                left_limit=self.handel.rect.width // 2,
                right_limit=self.handel.rect.width // 2,
                centery_anchor='centery'
            )
            
        else:
            self.add_child(
                self.handel,
                current_offset=True,
                top_limit=self.handel.rect.height // 2,
                bottom_limit=self.handel.rect.height // 2,
                centerx_anchor='centerx'
            )
            
        if state is None:
            state = self.range[0]
        self.set_state(state)
        
    def flip(self):
        self.flipped = not self.flipped
        
    def get_state(self):
        ratio = self.get_state_as_ratio()
        full = len(self.range)
        shift = self.range[0]
        state = (full * ratio) + shift
        return round(state)
        
    def get_state_as_ratio(self):
        self.handel.update_position()
        
        if self.dir == 0:
            dx = self.handel.rect.centerx - self.rect.x
            ratio = dx / self.rect.width 
        elif self.dir == 1:
            dy = self.handel.rect.centery - self.rect.y
            ratio = dy / self.rect.height
            
        if self.flipped:
            ratio = 1 - ratio
            
        return ratio
            
    def set_state(self, value):
        state = round(value)
        full = len(self.range)
        shift = self.range[0]
        ratio = (state - shift) / full
        self.set_state_as_ratio(ratio)
        
    def set_state_as_ratio(self, ratio):
        if self.flipped:
            ratio = 1 - ratio
            
        if self.dir == 0:   
            dx = ratio * self.rect.width
            self.handel.rect.centerx = dx + self.rect.x
        elif self.dir == 1:
            dy = ratio * self.rect.height
            self.handel.rect.centery = dy + self.rect.y
            
        self.handel.set_stuck(False)
        self.handel.update_position()
        self.handel.set_stuck(True)

    def get_hit(self):
        p = pg.mouse.get_pos()
        return self.outline_rect.collidepoint(p) or self.handel.rect.collidepoint(p)
        
    def left_click(self):
        super().left_click()
        self.held = True
        self.handel.set_stuck(False)
        
    def click_up(self, button):
        if button == 1 and self.held:
            self.held = False
            self.handel.set_stuck(True)
                
    def update(self):
        if self.held:
            self.handel.rect.center = pg.mouse.get_pos()
        super().update()
