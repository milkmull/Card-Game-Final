import pygame as pg

from ui.element.standard.slider import Slider
from ui.element.standard.textbox import Textbox

class RGB_Slider(Slider):
    CHANNELS = ("r', 'g', 'b")
    
    def __init__(
        self,
        channel,
        **kwargs
    ):
        super().__init__(
            range=range(255),
            handel_kwargs={
                "outline_color": (255, 255, 255)
            },
            **kwargs
        )
        
        self.channel = RGB_Slider.CHANNELS.index(channel)
        
        surf = pg.Surface((255, 1)).convert()
        color = [0, 0, 0]
        for x in self.range:
            color[self.channel] = x
            surf.set_at((x, 0), color)
        if self.dir:
            surf = pg.transform.rotate(surf, -90)
        self.image = pg.transform.scale(surf, self.rect.size)
        
        color = self.get_color()
        self.textbox = Textbox(pad=1)
        self.handel.add_child(self.textbox, centerx_anchor="centerx', bottom_anchor='top", bottom_offset=-5)
        
        self.textbox.add_event(
            tag="update",
            func=self.update_textbox
        )
 
    def flip(self):
        super().flip()
        if not self.dir:
            self.image = pg.transform.flip(self.image, True, False) 
        else:
            self.image = pg.transform.flip(self.image, False, True)
            
    def get_color(self):
        color = [0, 0, 0]
        color[self.channel] = self.get_state()
        return color
        
    def update_textbox(self):
        p = pg.mouse.get_pos()
        self.textbox.set_visible(self.held or self.handel.rect.collidepoint(p))
        if self.textbox.visible:
            color = self.get_color()
            self.textbox.text_color = color
            self.textbox.fill_color = Textbox.color_text(color)
            self.textbox.set_text(str(self.get_state()))
        
    def update(self):
        super().update()
        self.handel.fill_color = self.get_color()

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        super().draw(surf)