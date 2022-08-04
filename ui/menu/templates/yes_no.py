from ui.menu.menu import Menu
from ui.element.base.style import Style
from ui.element.elements import Textbox, Button

from ui.ui import get_constants

def yes_no(
    menu,
    window_kwargs,
    lower_kwargs,
    text_kwargs,
    yes_kwargs,
    no_kwargs
):
    constants = get_constants()

    window = Style(**window_kwargs)
    
    s = Style(**lower_kwargs)
    window.add_child(s, left_anchor='left', bottom_anchor='bottom', right_anchor='right')
    
    tb = Textbox(**text_kwargs)
    window.add_child(tb, current_offset=True)

    yes_button = Button.Text_Button(
        text='yes',
        func=lambda: 1,
        tag='return',
        **yes_kwargs
    )
    s.add_child(yes_button, left_anchor='left', left_offset=20, centery_anchor='centery')
    
    no_button = Button.Text_Button(
        text='no',
        func=lambda: 0,
        tag='return',
        **no_kwargs
    )
    s.add_child(no_button, right_anchor='right', right_offset=-20, centery_anchor='centery')
    
    window.rect.center = constants['CENTER']
    
    return [window]

class Yes_No(Menu):
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
        'centery_aligned': True
    }
    
    def __init__(
        self,
        
        window_kwargs={},
        lower_kwargs={},
        text_kwargs={},
        yes_kwargs={},
        no_kwargs={},
        
        **kwargs
):
        super().__init__(
            yes_no,
            init_kwargs={
                'window_kwargs': Yes_No.default_window_kwargs | window_kwargs,
                'lower_kwargs': Yes_No.default_lower_kwargs | lower_kwargs,
                'text_kwargs': Yes_No.default_text_kwargs | text_kwargs,
                'yes_kwargs': Yes_No.default_button_kwargs | {'hover_color': (0, 100, 0)} | yes_kwargs,
                'no_kwargs': Yes_No.default_button_kwargs | {'hover_color': (100, 0, 0)} | no_kwargs
            },
            **kwargs
        )
    








