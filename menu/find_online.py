from ui.scene.scene import Scene
from ui.element.base.style import Style
from ui.element.elements import Textbox, Button, Input
from ui.element.utils.image import get_arrow

def join_game(scene):
    elements = []

    s = Style(
        size=(350, 250),
        fill_color=(100, 100, 100),
        outline_color=(0, 0, 128),
        outline_width=5,
        border_radius=10,
        layer=-10
    )
    s.rect.center = scene.rect.center
    elements.append(s)
    
    host_label = Textbox(
        text='Host:'
    )
    host_label.rect.topleft = (s.rect.left + 15, s.rect.top + 10)
    elements.append(host_label)
    
    host = Input(
        size=(s.rect.width - 30, 25),
        outline_color=(0, 0, 0),
        outline_width=3
    )
    host.open()
    host.rect.topleft = (host_label.rect.left, host_label.rect.bottom + 5)
    elements.append(host)
    
    port_label = Textbox(
        text='Port:'
    )
    port_label.rect.topleft = (host.rect.left, host.rect.bottom + 10)
    elements.append(port_label)
    
    port = Input(
        size=(75, 25),
        text='5555',
        max_length=5,
        text_check=lambda t: t.isnumeric(),
        outline_color=(0, 0, 0),
        outline_width=3
    )
    port.rect.topleft = (port_label.rect.left, port_label.rect.bottom + 5)
    elements.append(port)
        
    def return_host():
        _host = host.text
        _port = int(port.text)
        scene.set_return((_host, _port))

    b = Button.Text_Button(
        text='Join Game!',
        text_size=35,
        inf_width=False,
        inf_height=False,
        center_aligned=True,
        size=(200, 80),
        fill_color=(0, 200, 0),
        text_color=(0, 0, 0),
        border_radius=10,
        func=return_host,
        outline_color=(0, 0, 0),
        outline_width=3
    )
    b.rect.top = host.rect.bottom + 15
    b.set_parent(
        s,
        left_anchor='left',
        left_offset=15,
        right_anchor='right',
        right_offset=-15,
        bottom_anchor='bottom',
        bottom_offset=-15,
        top_anchor='top',
        top_offset=140
    )
    elements.append(b)
    
    cancel_button = Button.Text_Button(
        text='Cancel',
        size=(100, 30),
        center_aligned=True,
        hover_color=(255, 0, 0),
        text_hover_color=(0, 0, 0),
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=5,
        tag='exit'
    )
    cancel_button.rect.midtop = (s.rect.centerx, s.rect.bottom + 20)
    elements.append(cancel_button)
    
    return elements
    
def run_find_online():
    s = Scene(join_game)
    host = s.run()
    return host
    