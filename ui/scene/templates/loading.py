import pygame as pg

from ..scene import Scene
from ...element.base.base import Base_Element
from ...element.base.style import Style
from ...element.elements import Textbox, Progress_Bar
from ...element.utils.event import Event

def loading(
    scene,
    window_kwargs,
    lower_kwargs,
    text_kwargs,
    bar_kwargs,
    func_kwargs,
):

    window = Style(**window_kwargs)
    
    s = Style(**lower_kwargs)
    window.add_child(s, left_anchor='left', bottom_anchor='bottom', right_anchor='right')
    
    tb = Textbox(**text_kwargs)
    window.add_child(tb, current_offset=True)

    progress_bar = Progress_Bar(**bar_kwargs)
    progress_bar.set_enabled(False)
    progress_bar.rect.center = s.rect.center
    window.add_child(progress_bar, current_offset=True)

    e = Event(**func_kwargs)
    
    def update():
        r = e()
        progress_bar.set_state(r)
        if r >= 1:
            scene.set_return(1)
    
    progress_bar.add_event(
        tag='update',
        func=update
    )

    window.rect.center = scene.rect.center
    
    return [window]

class Loading(Scene):
    window_defaults = {
        'size': (300, 150),
        'fill_color': (100, 100, 100),
        'outline_color': (255, 255, 255),
        'outline_width': 5,
        'border_radius': 10
    }
    
    lower_defaults = {
        'size': (300, 50),
        'fill_color': (50, 50, 50),
        'border_bottom_left_radius': 10,
        'border_bottom_right_radius': 10
    }
    
    text_defaults = {
        'size': (300, 100),
        'centerx_aligned': True,
        'centery_aligned': True
    }
    
    bar_defaults = {
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
        bar_kwargs={},
        func_kwargs={},
        
        **kwargs
):
        super().__init__(
            loading,
            init_kwargs={
                'window_kwargs': Loading.window_defaults | window_kwargs,
                'lower_kwargs': Loading.lower_defaults | lower_kwargs,
                'text_kwargs': Loading.text_defaults | text_kwargs,
                'bar_kwargs': Loading.bar_defaults | bar_kwargs,
                'func_kwargs': func_kwargs
            },
            **kwargs
        )
    








