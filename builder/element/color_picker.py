import pygame as pg

from ui.element.elements import Textbox
from ui.icons.icons import icons

class Color_Picker(Textbox):
    def __init__(self):
        super().__init__(
            font_name='icons.ttf',
            text=icons['eyedropper'],
            center_aligned=True,
            text_outline_color=(0, 0, 0),
            text_outline_width=1,
            layer=10
        ) 

        self.home = None
        self.last_color = (0, 0, 0)
        
    @property
    def is_held(self):
        return self.home is not None
        
    @property
    def display_rect(self):
        mx, my = pg.mouse.get_pos()
        r = pg.Rect(0, 0, 10, 10)
        r.center = (mx - 5, my - 20)
        return r
  
    def left_click(self):
        super().left_click()
        self.home = self.pos
        
    def click_up(self, button):
        if self.is_held:
            self.pos = self.home
            self.home = None
            self.run_events('set_color')
            
    def events(self, events):
        if self.is_held:
            mx, my = pg.mouse.get_pos()
            self.rect.bottomleft = (mx - 2, my + 3)
        super().events(events)
        
    def update(self):
        self.set_visible(self.parent.visible)
        if not self.is_held:
            super().update()
            
    def draw(self, surf):
        if self.is_held:
            r = self.display_rect
            c = pg.display.get_surface().get_at(pg.mouse.get_pos())
            pg.draw.rect(surf, self.color_text(c), r.inflate(4, 4))
            pg.draw.rect(surf, c, r)
            self.last_color = c
            
        super().draw(surf)
        
        