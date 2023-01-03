from ..scene import Scene
from ...element.base.style import Style
from ...element.elements import Textbox, Button

from ...ui import get_constants

def yes_no(
    scene,
    window_kwargs,
    lower_kwargs,
    text_kwargs,
    yes_kwargs,
    no_kwargs
):
    constants = get_constants()

    window = Style(**window_kwargs)
    
    s = Style(**lower_kwargs)
    window.add_child(s, left_anchor="left", bottom_anchor="bottom", right_anchor="right")
    
    tb = Textbox(**text_kwargs)
    window.add_child(tb, current_offset=True)

    yes_button = Button.Text_Button(
        text="yes",
        func=lambda: 1,
        tag="return",
        hover_color=(0, 255, 0),
        **yes_kwargs
    )
    s.add_child(yes_button, left_anchor="left", left_offset=20, centery_anchor="centery")
    
    yes_button.add_animation(
        [{
            "attr": "text_color",
            "end": (0, 0, 0)
        }],
        tag="hover"
    )

    no_button = Button.Text_Button(
        text="no",
        func=lambda: 0,
        tag="return",
        hover_color=(255, 0, 0),
        **no_kwargs
    )
    s.add_child(no_button, right_anchor="right", right_offset=-20, centery_anchor="centery")
    
    no_button.add_animation(
        [{
            "attr": "text_color",
            "end": (0, 0, 0)
        }],
        tag="hover"
    )
    
    window.rect.center = constants["CENTER"]
    
    return [window]

class Yes_No(Scene):
    window_defaults = {
        "size": (300, 150),
        "fill_color": (100, 100, 100),
        "outline_color": (255, 255, 255),
        "outline_width": 5,
        "border_radius": 10
    }
    
    lower_defaults = {
        "size": (300, 50),
        "fill_color": (50, 50, 50),
        "border_bottom_left_radius": 10,
        "border_bottom_right_radius": 10
    }
    
    text_defaults = {
        "size": (300, 100),
        "centerx_aligned": True,
        "centery_aligned": True
    }
    
    button_defaults = {
        "size": (100, 30),
        "centerx_aligned": True,
        "centery_aligned": True,
        "border_radius": 5
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
                "window_kwargs": Yes_No.window_defaults | window_kwargs,
                "lower_kwargs": Yes_No.lower_defaults | lower_kwargs,
                "text_kwargs": Yes_No.text_defaults | text_kwargs,
                "yes_kwargs": Yes_No.button_defaults | yes_kwargs,
                "no_kwargs": Yes_No.button_defaults | no_kwargs
            },
            **kwargs
        )