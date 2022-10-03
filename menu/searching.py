from ui.scene.scene import Scene
from ui.element.base.style import Style
from ui.element.elements import Textbox, Image
from ui.icons.icons import icons

def searching(
    scene,
    text
):

    window = Style(
        size=(300, 150),
        fill_color=(100, 100, 100),
        outline_color=(255, 255, 255),
        outline_width=5,
        border_radius=10
    )
    window.rect.center = scene.rect.center

    tb = Textbox(
        text=text,
        size=(280, 100),
        center_aligned=True
    )
    tb.rect.center = window.rect.center
    window.add_child(tb, current_offset=True)
    
    icon = Image.from_element(
        Textbox(
            text=icons['spinner3'],
            font_name='icons.ttf',
            text_size=30,
            text_color=(128, 128, 255)
        ), 
        alpha=True
    )
    icon.rect.topright = (window.rect.right - 10, window.rect.top + 10)
    window.add_child(icon)
    
    icon.add_animation([{
        'attr': 'rotation',
        'end': -360,
        'frames': 20
    }], loop=True)

    return [window]

class Searching(Scene):
    def __init__(self, text):
        super().__init__(searching, init_args=(text,))





