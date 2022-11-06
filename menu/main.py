from ui.scene.scene import Scene
from ui.element.elements import Textbox, Button
from ui.icons.icons import icons

from .settings import run as run_settings
from .wireless_play import run as run_wireless_play
from .builder import run as run_builder
from .client import run_client_single, run_sandbox

def main_scene(scene):
    body = scene.body
    elements = []

    button_kwargs = {
        'size': (200, 40),
        'centerx_aligned': True,
        'centery_aligned': True,
        'outline_color': (255, 255, 255),
        'border_radius': 3,
        'text_size': 30
    }
    
    hover_animation = {
        'attr': 'outline_width',
        'end': 3,
        'frames': 5,
        'strict': True
    }

    b = Button.Text_Button(
        text='single player',
        func=run_client_single,
        **button_kwargs
    )
    elements.append(b)
    b.rect.centerx = body.centerx
    b.rect.y = 150
    
    b = Button.Text_Button(
        text='sandbox',
        func=run_sandbox,
        **button_kwargs
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + 10
    elements.append(b)
    
    b = Button.Text_Button(
        text='card builder',
        func=run_builder,
        **button_kwargs
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + 10
    elements.append(b)

    b = Button.Text_Button(
        text='wireless play',
        func=run_wireless_play,
        **button_kwargs
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + b.rect.height
    elements.append(b)
    
    b = Button.Text_Button(
        text='exit game',
        tag='exit',
        **button_kwargs
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + 5
    elements.append(b)

    for b in elements:
        b.add_animation([hover_animation.copy()], tag='hover')
    
    return elements
    
def run():
    m = Scene(main_scene)
    m.run()











