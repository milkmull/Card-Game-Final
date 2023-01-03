import pygame as pg

from ..base.text_element import Text_Element
from ..standard.button import Button

from ..utils.image import get_arrow

class Flipper(Text_Element):
    defaults = {
        "center_aligned": True
    }
    
    @classmethod
    def Counter(cls, range, *args, **kwargs):
        return cls([str(i) for i in range], *args, **kwargs)
    
    def __init__(
        self,
        
        selection,
        index=0,
        
        arrow_kwargs={},
        button_kwargs={},
        
        **kwargs
    ):
        
        self.selection = selection
        self.index = index
        
        super().__init__(text=self.selection[self.index], **(Flipper.defaults | kwargs))

        if self.auto_fit:
            self.auto_fit = False
            self.size = self.get_max_size(self.selection)
        
        if "size" not in arrow_kwargs:
            arrow_kwargs = {"size": (self.rect.height - 5, self.rect.height - 5)} | arrow_kwargs
            
        left_arrow = get_arrow(
            "<",
            **arrow_kwargs
        )

        left_button = Button.Image_Button(
            image=left_arrow,
            **button_kwargs
        )
        left_button.add_event(
            self.flip,
            args=[1],
            tag="left_click"
        )

        right_button = Button.Image_Button(
            image=pg.transform.flip(left_arrow, True, False),
            **button_kwargs
        )
        right_button.add_event(
            self.flip,
            args=[-1],
            tag="left_click"
        )
        
        self.add_child(left_button, right_anchor="left", right_offset=-10, centery_anchor="centery")
        self.add_child(right_button, left_anchor="right", left_offset=10, centery_anchor="centery")
        
    @property
    def current_value(self):
        return self.selection[self.index]
        
    def flip(self, dir):
        self.index = (self.index + dir) % len(self.selection)
        self.set_text(self.current_value)
        
    def events(self, events):
        super().events(events)
        
        if self.hit and (mw := events.get("mw")):
            self.flip(mw.y)
