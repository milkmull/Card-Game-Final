import json

from data.constants import INFO_SHEET_FILE

from ..node.node_base import Node
from ..compiler import Compiler

from ui.scene.scene import Scene
from ui.element.elements import Textbox, Image, Button, Live_Window
from ui.element.utils.image import get_arrow
from ui.icons.icons import icons

def run_flow_scene(type, nodes):
    m = Scene(flow_scene, init_args=[type, nodes], overlay=True, opacity=220)
    m.run()
    
def flow_scene(scene, type, nodes):
    elements = []
    body = scene.body
    
    window = Live_Window(
        size=(0, 200),
        fill_color=(32, 32, 40),
        pad=25,
        outline_color=(255, 255, 255),
        outline_width=3,
        inf_height=False
    )
    elements.append(window)
    
    w = 0
    window_elements = []
    for i, name in enumerate(nodes):
        image = Image(
            image=Node.NODE_DATA[name](0).get_raw_image(scale=0.75)
        )
        window_elements.append(image)
        w += image.rect.width
        
        if i < len(nodes) - 1:
            arrow = Image(
                image=get_arrow('>', (15, 15))
            )
            window_elements.append(arrow)
            w += 10 + arrow.rect.width + 10
        
    window.rect.width = w
    window.rect.height = max({n.rect.height for n in window_elements})
    window.join_elements(
        window_elements,
        dir=0,
        margin=10,
        centerx_aligned=True,
        centery_aligned=True
    )
    window.rect.center = body.center
    
    style = {'fgcolor': (255, 255, 255), 'style': 4}
    text = f'Recommended {type.title()} Flow:'
    title = Textbox(
        text=text,
        text_size=40,
        text_style={i: style for i in range(len(text))}
    )
    title.rect.midbottom = (window.rect.centerx, window.rect.top - 50)
    elements.append(title)
    
    b = Button.Text_Button(
        size=body.size,
        tag='exit',
        layer=-1,
        cursor=0
    )
    elements.append(b)
    
    return elements

def run_key_scene(type, data):
    m = Scene(key_scene, init_args=[type, data], overlay=True, opacity=220)
    m.run()

def key_scene(scene, type, data):
    elements = []
    body = scene.body
    
    window = Live_Window(
        size=(450, 0),
        fill_color=(32, 32, 40),
        pad=5,
        outline_color=(255, 255, 255),
        outline_width=3
    )
    elements.append(window)
    
    y = 0
    texts = []
    for key, info in data.items():
        key_tb = Textbox(
            text=key,
            max_line_width=150,
        )
        key_tb.rect.width = 150
        info_tb = Textbox(
            text=info,
            max_line_width=300
        )
        info_tb.rect.width = 300
        texts.append(key_tb)
        texts.append(info_tb)
        
        y += max({key_tb.rect.height, info_tb.rect.height}) + 20
        
    window.rect.height = y - 20
    window.rect.center = body.center
    window.join_elements(texts, dir=0, marginy=20)
    
    key_text = Textbox(
        text='Data Key:'
    )
    key_text.rect.bottomleft = (window.rect.left, window.rect.top - 10)
    elements.append(key_text)
    
    value_text = Textbox(
        text='Extracted Value:'
    )
    value_text.rect.bottomleft = (window.rect.left + 150, window.rect.top - 10)
    elements.append(value_text)
    
    style = {'fgcolor': (255, 255, 255), 'style': 4}
    title = Textbox(
        text=type.title(),
        text_size=40,
        text_style={i: style for i in range(len(type))}
    )
    title.rect.midbottom = (window.rect.centerx, window.rect.top - 50)
    elements.append(title)

    b = Button.Text_Button(
        size=body.size,
        tag='exit',
        layer=-1,
        cursor=0
    )
    elements.append(b)
    
    return elements

def run(sheet='decks'):
    m = Scene(info_sheet, init_args=[sheet], fill_color=(32, 32, 40))
    m.run()

def info_sheet(scene, sheet):
    elements = []
    body = scene.body
    
    with open(INFO_SHEET_FILE, 'r') as f:
        data = json.load(f)

    window = Live_Window(
        size=(550, 400),
        pad=5,
        outline_color=(255, 255, 255),
        outline_width=3
    )
    window.rect.center = body.center
    elements.append(window)
    
    label = Textbox(
        text='Logs:',
        text_size=30
    )
    label.rect.bottomleft = (window.rect.left, window.rect.top - 10)
    window.add_child(label, current_offset=True)

    all_keys = (
        'decks',
        'requests',
        'logs'
    )
    current_key = [all_keys.index(sheet) - 1]

    def swap(dir, current_key=current_key, all_keys=all_keys):
        current_key[0] = (current_key[0] + dir) % len(all_keys)
        key = all_keys[current_key[0]]

        label.set_text(key.title() + ':')

        if key == 'decks' or key == 'requests':
            texts = []
            for type, info in data[label.text[:-1].lower()].items():
                info_tb = Textbox(
                    text=info,
                    max_line_width=window.rect.width * 3 // 4,
                )
                type_tb = Textbox(
                    text=type,
                    size=(window.rect.width // 4, info_tb.rect.height)
                )
                texts.append(type_tb)
                texts.append(info_tb)
            
        else:
            texts = []
            for type, d in data['logs'].items():
                info_tb = Textbox(
                    text=d['info'],
                    max_line_width=window.rect.width * 3 // 4,
                )
                type_tb = Button.Text_Button(
                    text=type,
                    size=(window.rect.width // 4, info_tb.rect.height),
                    hover_color=(100, 100, 100),
                    right_pad=window.rect.width * 3 // 4,
                    y_pad=5,
                    func=run_key_scene,
                    args=[type, d['data']]
                )
                texts.append(type_tb)
                texts.append(info_tb)
                
        window.join_elements(texts, dir=0, marginy=20)
    
    right_swap = Button.Image_Button(
        image=get_arrow('>', (20, 20), pad=(5, 5)),
        pad=5,
        func=swap,
        args=[1],
        hover_color=(100, 100, 100)
    )
    right_swap.rect.midleft = (window.rect.right + 40, window.rect.centery)
    window.add_child(right_swap, current_offset=True)
    
    left_swap = Button.Image_Button(
        image=get_arrow('<', (20, 20), pad=(5, 5)),
        pad=5,
        func=swap,
        args=[-1],
        hover_color=(100, 100, 100)
    )
    left_swap.rect.midright = (window.rect.left - 40, window.rect.centery)
    window.add_child(left_swap, current_offset=True)
    
    swap(1)
    
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
    back_button.rect.center = (body.centerx, (window.rect.bottom + body.height) // 2)
    elements.append(back_button)
    
    back_button.add_animation(
        [{
            'attr': 'text_color',
            'end': (0, 0, 0)
        }],
        tag='hover'
    )

    return elements