from ui.menu.menu import Menu
from ui.element.elements import Textbox, Button
from ui.math.position import center_elements_y

from .select_host import run as run_select_host

def wireless_play_menu(menu):
    body = menu.body
    elements = []
    
    button_kwargs = {
        'size': (300, 40),
        'centerx_aligned': True,
        'outline_color': (255, 255, 255),
        'border_radius': 3,
        'text_size': 30
    }
    
    b = Button.Text_Button(
        text='host game',
        **button_kwargs
    )
    elements.append(b)
    
    b = Button.Text_Button(
        text='find local game',
        **button_kwargs
    )
    elements.append(b)
    
    b = Button.Text_Button(
        text='join online game',
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
    m = Menu(wireless_play_menu)
    m.run()













