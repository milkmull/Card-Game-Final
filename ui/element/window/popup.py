from .static_window import Static_Window
from .live_window import Live_Window
from ..standard.button import Button
from ..utils.image import transform, get_arrow

class Popup_Base:
    
    default_animation_kwargs = {
        'frames': 15
    }
    
    default_arrow_kwargs = {
        'size': (16, 16)
    }

    default_button_kwargs = {
        'hover_color': (100, 100, 100),
        'pad': 4
    }

    def __init__(
        self,
        
        dir='^',
        animation_kwargs={},
        arrow_kwargs={},
        button_kwargs={},
        
        **kwargs
    ):
    
        self.dir = dir
        self.animation_kwargs = (Popup_Base.default_animation_kwargs | animation_kwargs)
            
        arrow = get_arrow(dir, **(Popup_Base.default_arrow_kwargs | arrow_kwargs))
        self.button = Button.Image_Button(
            image=arrow,
            func=self.open_close,
            **(Popup_Base.default_button_kwargs | button_kwargs)
        )
        
        if dir == '^':
            self.button.rect.bottomright = (self.rect.right, self.rect.top - 15)
        elif dir == 'v':
            self.button.rect.topright = (self.rect.right, self.rect.bottom + 15)
        elif dir == '>':
            self.button.rect.topleft = (self.rect.right + 15, self.rect.bottom - self.button.size[1])
        elif dir == '<':
            self.button.rect.topright = (self.rect.left - 15, self.rect.bottom - self.button.size[1])  
            
        self.open_animation = self.add_animation(
            [{
                'attr': 'y' if dir in 'v^' else 'x',
                'end': 0
            } | self.animation_kwargs],
            tag='open'
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
        if self.dir == '^':
            end = self.rect.top - self.rect.height
        elif self.dir == 'v':
            end = self.rect.bottom
        elif self.dir == '>':
            end = self.rect.right
        elif self.dir == '<':
            end = self.rect.left - self.rect.width
        self.open_animation.start_value = [self.rect.y]
        self.open_animation.end_value = [end]

        super().open()
        self.button.image = transform('rotate', self.button.image, 180)
        
    def close(self):
        super().close()
        self.button.image = transform('rotate', self.button.image, 180)

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
            
            
            
            
            