from data.save import SAVE

from ui.scene.scene import Scene
from ui.element.elements import Textbox, Button, Input
from ui.math.position import center_elements_y
from ui.icons.icons import icons

from .select_host import run as run_select_host
from .client import host_game, find_local_game, find_global_game

def change_port(scene):
    elements = []
    
    port = Input(
        text=str(SAVE.get_data('port')),
        size=(75, 25),
        outline_color=(0, 0, 0),
        outline_width=3,
        max_length=5,
        text_check=lambda t: t.isnumeric()
    )
    port.rect.center = scene.rect.center
    elements.append(port)
    
    return elements
    
def run_change_port():
    m = Scene(change_port, overlay=True)
    m.run()

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
        func=host_game,
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
        func=find_global_game,
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
    
    b = Button.Text_Button(
        text=icons['cog'],
        font_name='icons.ttf',
        text_size=30,
        center_aligned=True,
        hover_color=(100, 100, 100),
        border_radius=5,
        pad=5,
        func=run_change_port
    )
    b.rect.topright = (scene.rect.right - 20, scene.rect.top + 20)
    elements.append(b)
    
    return elements
    
def run():
    m = Scene(wireless_play_scene)
    m.run()













