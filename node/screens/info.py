import json

import pygame as pg

from ui.menu.menu import Menu
from ui.element.base.base import Base_Element
from ui.element.elements import Textbox, Button, Flipper, Live_Window, Label
from ui.element.utils.image import get_arrow
from ui.color.ops import is_light

def run(node):
    m = Menu(info_menu, init_args=[node])
    m.run()
    
def info_menu(menu, node):
    body = menu.body
    elements = []

    node = node.copy()
    node._stuck = True
    elements.append(node)
    
    with open('data/node/node_info.json', 'r') as f:
        data = json.load(f)    
    data = data.get(node.name, {})

    title = Textbox(
        pos=(30, 20),
        text=node.get_name(),
        text_size=40
    )
    elements.append(title)

    node_info = Textbox(
        text=data.get('info') or '',
        pos=(30, 150),
        fill_color=(0, 0, 0),
        outline_color=(255, 255, 255),
        outline_width=3,
        border_radius=10,
        max_line_width=400,
        line_spacing=1.2,
        inf_width=False,
        inf_height=True,
        pad=5
    )
    node_info.rect.width = 400
    elements.append(node_info)
    
    label = Textbox(
        text='Info:'
    )
    label.rect.bottomleft = (
        node_info.rect.left + 10,
        node_info.rect.top - 10
    )
    elements.append(label)
        
    if data.get('tips'):

        def swap():
            if label.text == 'Info:':
                label.set_text('Tips:')
                node_info.set_text(data.get('tips') or '')
            else:
                label.set_text('Info:')
                node_info.set_text(data.get('info') or '') 
            node_info.rect.width = 400
        
        swap_button = Button.Image_Button(
            image=get_arrow('>', (20, 20), padding=(5, 5)),
            pad=5,
            func=swap,
            hover_color=(100, 100, 100)
        )
        node_info.add_child(
            swap_button,
            left_anchor='right',
            left_offset=20,
            top_anchor='top',
            top_offset=20
        )
        
    port_data = data.get('ports', {})
    for p, d in port_data.copy().items():
        if not d:
            port_data.pop(p)

    if port_data:   

        port = list(port_data)[0]
        color = node.get_port(int(port)).color
        pad = 5

        port_text = Textbox(
            text=port_data[port],
            size=(400, 150),
            fill_color=(0, 0, 0),
            outline_color=color,
            outline_width=pad,
            inf_width=False,
            inf_height=False,
            pad=pad
        )
        port_text.rect.topleft = (550, 50)
        elements.append(port_text)
        
        port_label = Textbox(
            text=f'Port {port}:',
            size=(port_text.rect.width, 20),
            centery_aligned=True,
            x_pad=2 * pad,
            top_pad=pad,
            fill_color=color,
            text_color=(255, 255, 255) if is_light(color) else (0, 0, 0)
        )
        port_label.rect.bottomleft = (port_text.rect.left, port_text.rect.top - (2 * pad))
        port_text.add_child(
            port_label,
            current_offset=True
        )
        
        def draw(self, surf):
            start = self.port.rect.center
            end = port_text.padded_rect.midbottom
            
            xs, ys = start
            xe, ye = end
            
            midy = (port_text.outline_rect.bottom + node.background_rect.top) // 2
            
            dir = -1 if self.port.port > 0 else 1
            
            points = (
                start,
                (xs + (dir * 20), ys),
                (xs + (dir * 20), midy),
                (port_text.rect.centerx, midy),
                end
            )
            
            pg.draw.lines(surf, self.port.color, False, points, width=3)
        
        wire = Base_Element(draw=draw)
        setattr(wire, 'port', node.get_port(int(port)))
        elements.append(wire)
        
        def set_port(port):
            wire.port = node.get_port(int(port))
            color = node.get_port(int(port)).color
            
            port_text.outline_color = color
            port_text.set_text(port_data[port])
            port_label.text_color = (255, 255, 255) if is_light(color) else (0, 0, 0)
            port_label.fill_color = color
            port_label.set_text(f'Port {port}:')
            
        for p in port_data:
            port = node.get_port(int(p))
            b = Button.Text_Button(
                size=port.rect.inflate(5, 5).size,
                func=set_port,
                args=[p]
            )
            b.rect.center = port.rect.center
            port.add_child(b, current_offset=True)
        
        if len(port_data) > 1:
            
            def swap(dir):
                port = port_label.text.split()[-1][:-1]
                ports = list(port_data)
                
                port = ports[(ports.index(port) + dir) % len(ports)]
                while not port_data[port]:
                    port = ports[(ports.index(port) + dir) % len(ports)]

                set_port(port)
            
            swap_button = Button.Image_Button(
                image=get_arrow('>', (15, 15), padding=(5, 5)),
                pad=5,
                func=swap,
                args=[1],
                hover_color=(100, 100, 100)
            )
            port_text.add_child(
                swap_button,
                left_anchor='right',
                left_offset=20,
                top_anchor='top',
                top_offset=20
            )
            
            swap_button = Button.Image_Button(
                image=get_arrow('<', (15, 15), padding=(5, 5)),
                pad=5,
                func=swap,
                args=[-1],
                hover_color=(100, 100, 100)
            )
            port_text.add_child(
                swap_button,
                right_anchor='left',
                right_offset=-20,
                top_anchor='top',
                top_offset=20
            )
            
        node.rect.center = (
            port_text.rect.centerx,
            ((port_text.rect.bottom + body.height) // 2) + 30
        )
        
    back_button = Button.Text_Button(
        text='Back',
        size=(200, 25),
        centerx_aligned=True,
        centery_aligned=True,
        border_radius=5,
        hover_color=(255, 0, 0),
        tag='exit'
    )
    back_button.rect.midbottom = (body.centerx, body.height - 10)
    elements.append(back_button)

    return elements
 