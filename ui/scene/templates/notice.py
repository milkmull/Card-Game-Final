from ..scene import Scene
from ...element.base.style import Style
from ...element.elements import Textbox, Button

def notice(
    scene,
    window_kwargs,
    lower_kwargs,
    text_kwargs,
    button_kwargs
):
    window = Style(**window_kwargs)
    
    s = Style(**lower_kwargs)
    window.add_child(s, left_anchor="left", bottom_anchor="bottom", right_anchor="right")
    
    tb = Textbox(**text_kwargs)
    window.add_child(tb, current_offset=True)
    
    ok_button = Button.Text_Button(
        text="OK",
        tag="exit",
        **button_kwargs
    )
    s.add_child(ok_button, center=True)
    
    ok_button.add_animation(
        [{
            "attr": "text_color",
            "end": (0, 0, 0)
        }],
        tag="hover"
    )

    window.rect.center = scene.body.center
    
    return [window]

class Notice(Scene):
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
        "hover_color": (0, 255, 0),
        "border_radius": 5
    }
    
    def __init__(
        self,
        
        window_kwargs={},
        lower_kwargs={},
        text_kwargs={},
        button_kwargs={},
        
        **kwargs
):
        super().__init__(
            notice,
            init_kwargs={
                "window_kwargs": Notice.window_defaults | window_kwargs,
                "lower_kwargs": Notice.lower_defaults | lower_kwargs,
                "text_kwargs": Notice.text_defaults | text_kwargs,
                "button_kwargs": Notice.button_defaults | button_kwargs
            },
            **kwargs
        )
    








