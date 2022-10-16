from network.net_base import get_public_ip, get_local_ip

from ui.scene.scene import Scene
from ui.element.base.style import Style
from ui.element.elements import Textbox, Label, Button, Input, Live_Window
from ui.icons.icons import icons

def view_ips(scene):
    body = scene.body
    elements = []
    
    public_ip = get_public_ip()
    local_ip = get_local_ip()
    
    s = Style(
        size=(250, 150),
        fill_color=(100, 100, 100),
        outline_color=(0, 0, 128),
        outline_width=5,
        border_radius=10,
        layer=-10
    )
    s.rect.center = body.center
    elements.append(s)

    t = Textbox(text=public_ip if public_ip is not None else 'No connection found.')
    t.rect.topleft = (s.rect.left + 10, s.rect.top + 45)
    elements.append(t)
    t = Textbox(text='public ip:', text_size=15)
    t.set_parent(elements[-1], bottom_anchor='top', bottom_offset=-5, left_anchor='left')
    elements.append(t)
    
    if public_ip is not None:
        b = Button.Text_Button(
            text=icons['files-empty'],
            font_name='icons.ttf',
            text_size=30,
            center_aligned=True,
            pad=5,
            border_radius=5,
            hover_color=(255, 255, 0),
            hover_text_color=(0, 0, 0),
            func=Input.copy,
            args=[public_ip]
        )
        b.rect.midleft = elements[-2].rect.midright
        b.rect.right = s.rect.right - 20
        elements.append(b)
    
    t = Textbox(text=local_ip)
    t.rect.topleft = (s.rect.left + 10, s.rect.top + 105)
    elements.append(t)
    t = Textbox(text='local ip:', text_size=15)
    t.set_parent(elements[-1], bottom_anchor='top', bottom_offset=-5, left_anchor='left')
    elements.append(t)
    
    b = Button.Text_Button(
        text=icons['files-empty'],
        font_name='icons.ttf',
        text_size=30,
        center_aligned=True,
        pad=5,
        border_radius=5,
        hover_color=(255, 255, 0),
        hover_text_color=(0, 0, 0),
        func=Input.copy,
        args=[local_ip]
    )
    b.rect.midleft = elements[-2].rect.midright
    b.rect.right = s.rect.right - 20
    elements.append(b)
    
    cancel_button = Button.Text_Button(
        text='Back',
        size=(100, 30),
        center_aligned=True,
        hover_color=(255, 0, 0),
        hover_text_color=(0, 0, 0),
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=5,
        tag='exit'
    )
    cancel_button.rect.midtop = (s.rect.centerx, s.rect.bottom + 20)
    elements.append(cancel_button)

    return elements
    
def run_view_ips():
    m = Scene(view_ips, overlay=True)
    m.run()