import json
import re

import pygame as pg

from data.constants import NODE_DATA_FILE

from ..node.node_base import Node

from .info_sheet import run as run_info_sheet

from ui.scene.scene import Scene

from ui.element.base.base import Base_Element
from ui.element.base.text import Text
from ui.element.elements import Textbox, Button
from ui.element.utils.image import get_arrow

def set_text(scene, parent, text):
    node_refs = {}
    sheet_refs = {}
    
    style = {}
    s = {'fgcolor': (128, 128, 255), 'style': 4}

    for b in parent.children.copy():
        if isinstance(b, Button.Text_Button):
            parent.remove_child(b)

    for match in re.finditer(r"('[a-zA-Z]+')(?= node| function)", text):
        style.update({i: s for i in range(match.start(), match.end())})
        node_refs[(match.start(), match.end())] = match.group()

    for match in re.finditer(r"(Info Sheet >> )([a-zA-Z]+)", text):
        style.update({i: s for i in range(match.start(), match.end())})
        sheet_refs[(match.start(), match.end())] = match.group()
        
    parent.set_text(text, force=True, style=style)
    chars = parent.characters

    for (s, e), subtext in node_refs.items():

        def refresh(subtext=subtext):
            scene.args = [subtext.strip("'").replace(' ', '_')]
            scene.refresh()

        lines = []
        line = []
        for i in range(s, e):
            char = chars[i]
            if line:
                if not (line[-1].rect.top < char.rect.centery < line[-1].rect.bottom):
                    lines.append(line.copy())
                    line.clear()
                    continue
                line.append(char)
        if line:
            lines.append(line)
        
        for line in lines:
            b = Button.Text_Button(func=refresh)
            b.rect.size = (
                line[-1].rect.right - line[0].rect.left,
                max({char.rect.height for char in line})
            )
            b.rect.topleft = line[0].rect.topleft
            parent.add_child(b, current_offset=True)

    for (s, e), subtext in sheet_refs.items():
    
        lines = []
        line = []
        for i in range(s, e):
            char = chars[i]
            if line:
                if not (line[-1].rect.top < char.rect.centery < line[-1].rect.bottom):
                    lines.append(line.copy())
                    line.clear()
                    continue
            line.append(char)
        if line:
            lines.append(line)

        for line in lines:
            b = Button.Text_Button(
                func=run_info_sheet,
                kwargs={'sheet': subtext.split('>> ')[-1].lower()}
            )
            b.rect.size = (
                line[-1].rect.right - line[0].rect.left,
                max({char.rect.height for char in line})
            )
            b.rect.topleft = line[0].rect.topleft
            parent.add_child(b, current_offset=True)

def run(node):
    m = Scene(info_scene, init_args=[node], fill_color=(32, 32, 40))
    m.run()
    
def info_scene(scene, name):
    body = scene.body
    elements = []

    node = Node.from_name(name, id=0)
    node._stuck = True
    elements.append(node)
    
    with open(NODE_DATA_FILE, 'r') as f:
        data = json.load(f).get(name, {})   

    title = Textbox(
        pos=(30, 20),
        text=node.get_name(),
        text_size=40
    )
    elements.append(title)

    node_info = Textbox(
        pos=(30, 150),
        outline_color=(255, 255, 255),
        outline_width=3,
        border_radius=10,
        max_line_width=400,
        line_spacing=1.2,
        inf_width=False,
        inf_height=True,
        pad=5
    )
    set_text(scene, node_info, data.get('info') or '')
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
                text = data.get('tips')
            else:
                label.set_text('Info:')
                text = data.get('info')
            set_text(scene, node_info, text or '')
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
            size=(400, 150),
            outline_color=color,
            outline_width=pad,
            inf_width=False,
            inf_height=False,
            pad=pad
        )
        set_text(scene, port_text, port_data[port])
        port_text.rect.topleft = (550, 50)
        elements.append(port_text)
        
        port_label = Textbox(
            text=f'Port {port}:',
            size=(port_text.rect.width, 20),
            centery_aligned=True,
            x_pad=2 * pad,
            top_pad=pad,
            fill_color=color,
            text_color=Text.color_text(color)
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
            set_text(scene, port_text, port_data[port])
            port_label.text_color = Text.color_text(color)
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
        
    else:
        node.rect.center = (
            (node_info.rect.right + scene.body.right) // 2,
            scene.body.centery
        )
        
    back_button = Button.Text_Button(
        text='Back',
        size=(200, 25),
        centerx_aligned=True,
        centery_aligned=True,
        outline_color=(255, 255, 255),
        outline_width=3,
        border_radius=5,
        hover_color=(255, 0, 0),
        tag='exit'
    )
    back_button.rect.midbottom = (body.centerx, body.height - 20)
    elements.append(back_button)
    
    back_button.add_animation(
        [{
            'attr': 'text_color',
            'end': (0, 0, 0)
        }],
        tag='hover'
    )
    
    return elements
 