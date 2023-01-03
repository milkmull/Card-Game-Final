import pygame as pg

from .static_window import Static_Window
from .live_window import Live_Window
from ..standard.button import Button
from ..utils.image import get_arrow

class Popup_Base:
    animation_defaults = {
        "frames": 15
    }
    
    arrow_defaults = {
        "size": (20, 20)
    }

    button_defaults = {
        "hover_color": (100, 100, 100)
    }

    def __init__(
        self,
        
        dir="^",
        animation_kwargs={},
        arrow_kwargs={},
        button_kwargs={},
        
        **kwargs
    ):
    
        self.dir = dir
        self.animation_kwargs = (Popup_Base.animation_defaults | animation_kwargs)

        arrow = get_arrow(dir, **(Popup_Base.arrow_defaults | arrow_kwargs))
        self.button = Button.Image_Button(
            image=arrow,
            func=self.open_close,
            **(Popup_Base.button_defaults | button_kwargs)
        )
        
        match dir:
            case "^":
                self.button.rect.bottomright = (self.rect.right, self.rect.top - 15)
            case "v":
                self.button.rect.topright = (self.rect.right, self.rect.bottom + 15)
            case ">":
                self.button.rect.topleft = (self.rect.right + 15, self.rect.bottom - self.button.size[1])
            case "<":
                self.button.rect.topright = (self.rect.left - 15, self.rect.bottom - self.button.size[1])  
            
        self.open_animation = self.add_animation(
            [{
                "attr": "y' if dir in 'v^' else 'x",
                "end": 0
            } | self.animation_kwargs],
            tag="open"
        ).sequence[0]
            
        self.add_child(self.button, current_offset=True)
        
    @property
    def is_closed(self):
        return not self.moving and not self.is_open
        
    def open_close(self):
        if self.is_closed:
            self.open()
        else:
            self.close()
        
    def open(self):
        match self.dir:
            case "^":
                end = self.rect.top - self.rect.height
            case "v":
                end = self.rect.bottom
            case ">":
                end = self.rect.right
            case "<":
                end = self.rect.left - self.rect.width
                
        self.open_animation.start_value = [self.rect.y]
        self.open_animation.end_value = [end]

        super().open()
        self.button.image = pg.transform.flip(self.button.image, False, True)
        
    def close(self):
        super().close()
        self.button.image = pg.transform.flip(self.button.image, False, True)

    def events(self, events):
        if self.is_closed:
            self.button.events(events)
        else:
            super().events(events)
            
    def update(self):
        if self.is_closed:
            self.button.update()
        else:
            super().update()
        
    def draw(self, surf):
        if self.is_closed:
            self.button.draw(surf)
        else:
            super().draw(surf)
        
class Popup:
    
    class Static_Popup(Popup_Base, Static_Window):
        def __init__(self, **kwargs):
            Static_Window.__init__(self, **kwargs)
            Popup_Base.__init__(self, **kwargs)
            
    class Live_Popup(Popup_Base, Live_Window):
        def __init__(self, **kwargs):
            Live_Window.__init__(self, **kwargs)
            Popup_Base.__init__(self, **kwargs)
            
            
            
            
            