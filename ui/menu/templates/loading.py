import pygame as pg

from ..menu import Menu
from ...element.base.base import Base_Element
from ...element.base.style import Style
from ...element.elements import Textbox, Button, Progress_Bar
from ...element.utils.event import Event

def loading(
    menu,
    window_kwargs,
    lower_kwargs,
    text_kwargs,
    button_kwargs,
    bar_kwargs,
    func_kwargs,
):

    window = Style(**window_kwargs)
    
    s = Style(**lower_kwargs)
    window.add_child(s, left_anchor='left', bottom_anchor='bottom', right_anchor='right')
    
    tb = Textbox(**text_kwargs)
    window.add_child(tb, current_offset=True)
    
    ok_button = Button.Text_Button(
        text='ok',
        tag='exit',
        **button_kwargs
    )
    #s.add_child(ok_button, center=True)

    progress_bar = Progress_Bar(**bar_kwargs)
    progress_bar.set_enabled(False)
    progress_bar.rect.center = s.rect.center
    window.add_child(progress_bar, current_offset=True)

    e = Event(**func_kwargs)
    
    def update():
        r = e()
        progress_bar.set_state(r)
        if r >= 1:
            menu.set_return(1)
    
    progress_bar.add_event(
        tag='update',
        func=update
    )

    window.rect.center = menu.rect.center
    
    return [window]

class Loading(Menu):
    default_window_kwargs = {
        'size': (300, 150),
        'fill_color': (100, 100, 100),
        'outline_color': (255, 255, 255),
        'outline_width': 5,
        'border_radius': 10
    }
    
    default_lower_kwargs = {
        'size': (300, 50),
        'fill_color': (50, 50, 50),
        'border_bottom_left_radius': 10,
        'border_bottom_right_radius': 10
    }
    
    default_text_kwargs = {
        'size': (300, 100),
        'centerx_aligned': True,
        'centery_aligned': True
    }
    
    default_button_kwargs = {
        'size': (100, 30),
        'centerx_aligned': True,
        'centery_aligned': True,
        'key_color': (0, 0, 0),
        'hover_color': (0, 100, 0),
    }
    
    default_bar_kwargs = {
        'size': (200, 10),
        'fill_color': (255, 255, 255),
        'outline_color': (0, 0, 0),
        'outline_width': 3,
        'border_radius': 10,
        'bar_color': (0, 128, 0)
    }
    
    def __init__(
        self,
        
        window_kwargs={},
        lower_kwargs={},
        text_kwargs={},
        button_kwargs={},
        bar_kwargs={},
        func_kwargs={},
        
        **kwargs
):
        super().__init__(
            loading,
            init_kwargs={
                'window_kwargs': Loading.default_window_kwargs | window_kwargs,
                'lower_kwargs': Loading.default_lower_kwargs | lower_kwargs,
                'text_kwargs': Loading.default_text_kwargs | text_kwargs,
                'button_kwargs': Loading.default_button_kwargs | button_kwargs,
                'bar_kwargs': Loading.default_bar_kwargs | bar_kwargs,
                'func_kwargs': func_kwargs
            },
            **kwargs
        )
    








