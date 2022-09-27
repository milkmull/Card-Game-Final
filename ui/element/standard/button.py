import pygame as pg

from ..base.text_element import Text_Element
from ..base.image_element import Image_Element

from .textbox import Textbox

class Button_Base:
    def __init__(
        self,

        func=None,
        include_self=False,
        args=None,
        kwargs=None,
        
        **kw
    ):
 
        if func is not None:
            self.add_event(
                tag='left_click',
                func=func,
                include_self=include_self,
                args=args,
                kwargs=kwargs
            )
   
class Button:

    class Text_Button(Text_Element, Button_Base):
        defaults = {
            'inf_width': True,
            'inf_height': True,
            'cursor': pg.SYSTEM_CURSOR_HAND,
            'key_color': (0, 0, 0)
        }
        
        def __init__(self, **kwargs):
            Text_Element.__init__(self, **(Button.Text_Button.defaults | kwargs))
            Button_Base.__init__(self, **kwargs)
    
    class Image_Button(Image_Element, Button_Base):
        defaults = {
            'const_size': False,
            'cursor': pg.SYSTEM_CURSOR_HAND,
            'key_color': (0, 0, 0)
        }
        
        def __init__(self, **kwargs):
            Image_Element.__init__(self, **(Button.Image_Button.defaults | kwargs))
            Button_Base.__init__(self, **kwargs)