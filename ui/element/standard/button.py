import pygame as pg

from ..base.text_element import Text_Element
from ..base.image_element import Image_Element

from .textbox import Textbox

class Button_Base:
    def __init__(
        self,
        hover_color=None,
        description='',
        
        func=None,
        include_self=False,
        args=None,
        kwargs=None,
        
        **kw
    ):
        if hover_color:
            self.add_animation([{
                'attr': 'fill_color',
                'end': hover_color
            }], tag='hover')
            
        self._description = description
        if description:
            self.add_event(
                tag='hover',
                func=self.hover_description
            )
            self.add_event(
                tag='no_hover',
                func=self.end_hover
            )
 
        if func:
            self.add_event(
                tag='left_click',
                func=func,
                include_self=include_self,
                args=args,
                kwargs=kwargs
            )
            
    @property
    def description_box(self):
        for c in self.children:
            if c.tag == 'desc':
                return c
                
    @property
    def description(self):
        return self._description
        
    @description.setter
    def description(self, description):
        self._description = description
        if box := self.description_box:
            box.set_text(description)
            
    def hover_description(self):
        if not self.description_box:
            tb = Textbox(
                text=self._description,
                text_size=15,
                text_color=(0, 0, 0),
                fill_color=(255, 255, 255),
                pad=2,
                tag='desc'
            )
            x, y = pg.mouse.get_pos()
            tb.rect.topleft = (x, self.outline_rect.bottom + 5)
            self.add_child(tb, current_offset=True)
            
    def end_hover(self):
        for c in self.children:
            if c.tag == 'desc':
                self.remove_child(c)
                break
   
class Button:

    class Text_Button(Text_Element, Button_Base):
        default_kwargs = {
            'inf_width': True,
            'inf_height': True,
            'cursor': pg.SYSTEM_CURSOR_HAND,
            'key_color': (0, 0, 0)
        }
        
        def __init__(self, **kwargs):
            Text_Element.__init__(self, **(Button.Text_Button.default_kwargs | kwargs))
            Button_Base.__init__(self, **kwargs)
    
    class Image_Button(Image_Element, Button_Base):
        default_kwargs = {
            'const_size': False,
            'cursor': pg.SYSTEM_CURSOR_HAND,
            'key_color': (0, 0, 0)
        }
        
        def __init__(self, **kwargs):
            Image_Element.__init__(self, **(Button.Image_Button.default_kwargs | kwargs))
            Button_Base.__init__(self, **kwargs)