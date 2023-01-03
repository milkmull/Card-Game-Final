from ui.scene.scene import Scene
from ui.element.base.style import Style
from ui.element.elements import Textbox, Button, Input
from ui.scene.templates.notice import Notice

def host_game(scene):
    elements = []

    s = Style(
        size=(350, 180),
        fill_color=(100, 100, 100),
        outline_color=(0, 0, 128),
        outline_width=5,
        border_radius=10,
        layer=-10
    )
    s.rect.center = scene.rect.center
    elements.append(s)

    port_label = Textbox(
        text="Port:"
    )
    port_label.rect.topleft = (s.rect.left + 15, s.rect.top + 10)
    elements.append(port_label)
    
    port = Input(
        size=(75, 25),
        text="5555",
        max_length=5,
        text_check=lambda t: t.isnumeric(),
        outline_color=(0, 0, 0),
        outline_width=3
    )
    port.rect.topleft = (port_label.rect.left, port_label.rect.bottom + 5)
    elements.append(port)
        
    def return_port():
        _port = int(port.text)
        if not 1024 < _port <= 65536:
            m = Notice(text_kwargs={"text": "Please choose a port between 1025 and 65536."})
            m.run()
            return
            
        scene.set_return(_port)

    b = Button.Text_Button(
        text="Start Game!",
        text_size=35,
        inf_width=False,
        inf_height=False,
        center_aligned=True,
        size=(200, 80),
        fill_color=(0, 200, 0),
        text_color=(0, 0, 0),
        border_radius=10,
        func=return_port,
        outline_color=(0, 0, 0),
        outline_width=3
    )
    b.rect.top = port.rect.bottom + 15
    b.set_parent(
        s,
        left_anchor="left",
        left_offset=15,
        right_anchor="right",
        right_offset=-15,
        bottom_anchor="bottom",
        bottom_offset=-15,
        top_anchor="top",
        top_offset=80
    )
    elements.append(b)
    
    cancel_button = Button.Text_Button(
        text="Cancel",
        size=(100, 30),
        center_aligned=True,
        hover_color=(255, 0, 0),
        hover_text_color=(0, 0, 0),
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=5,
        tag="exit"
    )
    cancel_button.rect.midtop = (s.rect.centerx, s.rect.bottom + 20)
    elements.append(cancel_button)
    
    return elements
    
def run_host_game():
    s = Scene(host_game)
    port = s.run()
    return port
    