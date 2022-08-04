import pygame as pg

from ..base.text_element import Text_Element
from ..base.image_element import Image_Element
from ..standard.button import Button

from ..utils.image import get_arrow

class Flipper_Base:
    default_arrow_kwargs = {
    
    }

    default_button_kwargs = {
        'hover_color': (100, 100, 100),
        'border_radius': 10
    }
    
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
        
        if 'size' not in arrow_kwargs:
            arrow_kwargs['size'] = (self.height - 11, self.height - 11)
        left_arrow = get_arrow(
            '<',
            **(Flipper_Base.default_arrow_kwargs | arrow_kwargs)
        )
        
        if 'pad' not in button_kwargs:
            button_kwargs['pad'] = 11
        left_button = Button.Image_Button(
            image=left_arrow,
            **(Flipper_Base.default_button_kwargs | button_kwargs)
        )
        left_button.add_event(
            self.flip,
            args=[-1],
            tag='left_click'
        )

        right_button = Button.Image_Button(
            image=pg.transform.flip(left_arrow, True, False),
            **(Flipper_Base.default_button_kwargs | button_kwargs)
        )
        right_button.add_event(
            self.flip,
            args=[1],
            tag='left_click'
        )
        
        self.add_child(left_button, left_anchor='left', left_offset=-20, centery_anchor='centery')
        self.add_child(right_button, right_anchor='right', right_offset=20, centery_anchor='centery')
        
    @property
    def current_value(self):
        return self.selection[self.index]
        
    def flip(self, dir):
        self.index = (self.index + dir) % len(self.selection)
        
class Flipper:

    class Text_Flipper(Text_Element, Flipper_Base):
        default_kwargs = {
            'centerx_aligned': True,
            'centery_aligned': True
        }
        
        @classmethod
        def Counter(cls, range, *args, **kwargs):
            return cls([str(i) for i in range], *args, **kwargs)
        
        def __init__(
            self,
            *args,
            **kwargs
        ):
            Text_Element.__init__(self, **(kwargs | Flipper.Text_Flipper.default_kwargs))
            Flipper_Base.__init__(self, *args, **kwargs)
            
            if self.auto_fit:
                self.auto_fit = False
                self.size = self.get_max_size(self.selection)
            
            self.set_text(self.current_value)
            
        def flip(self, dir):
            super().flip(dir)
            self.set_text(self.current_value)

    class Image_Flipper(Image_Element, Flipper_Base):
        default_kwargs = {
            'const_size': False
        }
        
        def __init__(
            self,
            *args,
            **kwargs
        ):
            Image_Element.__init__(self, **(kwargs | Flipper.Image_Flipper.default_kwargs))
            Flipper_Base.__init__(self, *args, **kwargs)
            
            if self.auto_fit:
                self.auto_fit = False
                self.size = self.get_max_aspect(self.selection)
            
            self.set_image(self.current_value)
            
        def flip(self, dir):
            super().flip(dir)
            self.set_image(self.current_value)
