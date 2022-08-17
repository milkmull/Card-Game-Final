import pygame as pg

from ..base.text_element import Text_Element
from ...icons.icons import icons

class Check_Box(Text_Element):
    default_kwargs = {
        'size': (15, 15),
        'fill_color': (255, 255, 255),
        'text_color': (0, 0, 0),
        'text_size': 15,
        'pad': 2,
        'cursor': pg.SYSTEM_CURSOR_HAND
    }

    def __init__(
        self,
        value=True,
        **kwargs
    ):

        super().__init__(
            text=icons['check'] if value else '',
            font_name='icons.ttf',
            centerx_aligned=True,
            centery_aligned=True,
            **(Check_Box.default_kwargs | kwargs)
        )
        
        self.value = value
        
    def __bool__(self):
        return bool(self.value)
        
    def get_value(self):
        return self.value
        
    def get_state(self):
        return self.value
        
    def set_value(self, value):
        self.value = value
        if value:
            self.set_text(icons['check'])
        else:
            self.clear_text()
        
    def flip_value(self):
        self.set_value(not self.value)
        
    def left_click(self):
        self.flip_value()
        super().left_click()
        
            