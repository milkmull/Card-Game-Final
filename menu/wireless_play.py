from ui.scene.scene import Scene
from ui.element.elements import Textbox, Button
from ui.math.position import center_elements_y

from .select_host import run as run_select_host
from .client import run_client_online, find_local_game

def wireless_play_scene(scene):
    body = scene.body
    elements = []
    
    button_kwargs = {
        'size': (300, 40),
        'centerx_aligned': True,
        'outline_color': (255, 255, 255),
        'border_radius': 3,
        'text_size': 30
    }
    
    b = Button.Text_Button(
        text='Host Game',
        func=run_client_online,
        **button_kwargs
    )
    elements.append(b)
    
    b = Button.Text_Button(
        text='Local Game',
        func=find_local_game,
        **button_kwargs
    )
    elements.append(b)
    
    b = Button.Text_Button(
        text='Online Game',
        func=run_select_host,
        **button_kwargs
    )
    elements.append(b)
    
    center_elements_y(elements, marginy=10)
    
    b = Button.Text_Button(
        text='back',
        tag='exit',
        **button_kwargs
    )
    b.rect.bottomleft = (10, body.height - 10)
    elements.append(b)
    
    return elements
    
def run():
    m = Scene(wireless_play_scene)
    m.run()













