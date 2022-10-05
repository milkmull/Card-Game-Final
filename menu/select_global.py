from ui.scene.scene import Scene
from ui.element.base.style import Style
from ui.element.elements import Textbox, Button, Input
from ui.element.utils.image import get_arrow

def join_game(scene):
    elements = []

    s = Style(
        size=(350, 200),
        fill_color=(100, 100, 100),
        outline_color=(0, 0, 128),
        outline_width=5,
        border_radius=10,
        layer=-10
    )
    s.rect.center = scene.rect.center
    elements.append(s)
    
    ip = Input(size=(250, 25))
    ip.rect.topleft = (s.rect.left + 10, s.rect.top + 10)
    elements.append(ip)
    
    port = Input(size=(100, 25), text='5555')
    port.rect.topleft = ip.rect.bottomleft
    port.rect.y += 5
    elements.append(port)
        
    def return_host():
        host = ip.get_text()
        scene.set_return(host)

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
        func=return_host
    )
    b.rect.top = ip.rect.bottom + 15
    b.set_parent(
        s,
        left_anchor='left',
        left_offset=15,
        right_anchor='right',
        right_offset=-15,
        bottom_anchor='bottom',
        bottom_offset=-15,
        top_anchor='top',
        top_offset=100
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
    
def run_select_global():
    s = Scene(join_game)
    host = s.run()
    return host
    