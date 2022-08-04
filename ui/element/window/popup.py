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
        self.button = Button.Image_Button(image=arrow, **(Popup_Base.default_button_kwargs | button_kwargs))
        
        if dir == '^':
            self.button.rect.bottomright = (self.rect.right, self.rect.top - 15)
        elif dir == 'v':
            self.button.rect.topright = (self.rect.right, self.rect.bottom + 15)
        elif dir == '>':
            self.button.rect.topleft = (self.rect.right + 15, self.rect.bottom - self.button.size[1])
        elif dir == '<':
            self.button.rect.topright = (self.rect.left - 15, self.rect.bottom - self.button.size[1])  
        self.add_child(self.button, current_offset=True)

        self.button.add_event(self.popup, tag='left_click')
        
    @property
    def is_closed(self):
        return not self.moving and not self.is_open
        
    def popup(self):
        if not self.moving:
            if not self.is_open:

                self.open()
                if self.dir == '^':
                    self.add_animation([{'attr': 'y', 'end': self.rect.top - self.rect.height} | self.animation_kwargs])
                elif self.dir == 'v':
                    self.add_animation([{'attr': 'y', 'end': self.rect.bottom} | self.animation_kwargs])
                elif self.dir == '>':
                    self.add_animation([{'attr': 'x', 'end': self.rect.right} | self.animation_kwargs])
                elif self.dir == '<':
                    self.add_animation([{'attr': 'x', 'end': self.rect.left - self.rect.width} | self.animation_kwargs])
                    
            else:
            
                self.close()
                if self.dir == '^':
                    self.add_animation([{'attr': 'y', 'end': self.rect.bottom} | self.animation_kwargs])
                elif self.dir == 'v':
                    self.add_animation([{'attr': 'y', 'end': self.rect.top - self.rect.height} | self.animation_kwargs])
                elif self.dir == '>':
                    self.add_animation([{'attr': 'x', 'end': self.rect.left - self.rect.width} | self.animation_kwargs])
                elif self.dir == '<':
                    self.add_animation([{'attr': 'x', 'end': self.rect.right} | self.animation_kwargs])
                    
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
            
            
            
            
            