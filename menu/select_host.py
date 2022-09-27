from data.save import SAVE
from network.net_base import get_public_ip, get_local_ip

from ui.scene.scene import Scene
from ui.scene.templates.yes_no import Yes_No
from ui.element.base.style import Style
from ui.element.elements import Textbox, Label, Button, Input, Live_Window
from ui.math.position import center_elements_y
from ui.icons.icons import icons

def new_entry(scene):
    body = scene.body
    elements = []
    
    input_kwargs = {
        'size': (200, 25),
        'fill_color': None,
        'text_color': (255, 255, 255),
        'outline_color': (255, 255, 255),
        'outline_width': 3,
        'cursor_color': (255, 255, 255),
        'centery_aligned': True
    }

    i = Input(text='name', **input_kwargs)
    elements.append(i)

    tb = Textbox(text='name:', size=(200, 25), centery_aligned=True)
    tb.rect.topleft = i.rect.topleft
    tb.set_enabled(False)
    tb.rect.bottomleft = (i.rect.left, i.rect.top - 5)
    tb.set_parent(i, current_offset=True)
    elements.append(tb)
    
    i = Input(
        text='255.255.255.255',
        text_check=lambda text: all({char.isnumeric() or char == '.' for char in text}),
        **input_kwargs
    )
    i.rect.topleft = (elements[0].rect.x, elements[0].rect.bottom + 60)
    elements.append(i)
    
    tb = Textbox(text='ip:', size=(200, 25), centery_aligned=True)
    tb.rect.topleft = i.rect.topleft
    tb.set_enabled(False)
    tb.rect.bottomleft = (i.rect.left, i.rect.top - 5)
    tb.set_parent(i, current_offset=True)
    elements.append(tb)
    
    center_elements_y(elements[::2], marginy=50)
    
    s = Style(
        size=(250, 150),
        fill_color=(100, 100, 100),
        outline_color=(0, 0, 128),
        outline_width=5,
        border_radius=10,
        layer=-10
    )
    s.rect.center = body.center
    s.rect.y -= 10
    elements.append(s)
    
    button_kwargs = {
        'pad': 5,
        'tag': 'exit'
    }

    b = Button.Text_Button(
        text='save', 
        hover_color=(0, 100, 0), 
        func=add_new_entry, 
        args=[elements[0], elements[2]], 
        **button_kwargs
    )
    b.rect.left = s.rect.left + 20
    b.rect.y = s.rect.bottom + b.rect.height + 5
    elements.append(b)
    
    b = Button.Text_Button(text='cancel', hover_color=(100, 0, 0), **button_kwargs)
    b.rect.right = s.rect.right - 20
    b.rect.y = s.rect.bottom + b.rect.height + 5
    elements.append(b)
    
    return elements
    
def run_new_entry():
    m = Scene(new_entry, overlay=True)
    m.run()

def select_host(scene):
    body = scene.body
    elements = []
    
    w = Live_Window(size=(300, 400), fill_color=(100, 0, 0))
    w.rect.centerx = body.centerx
    w.rect.y = 70
    elements.append(w)
    l = Label(w, text='saved ips:', height=30, fill_color=(0, 0, 255))
    elements.append(l)
    
    button_kwargs = {
        'pad': 5,
    }
    
    buttons = []
    for entry in SAVE.get_data('ips'):
        b = Button.Text_Button(
            text=f"{entry['name']}: {entry['ip']}",
            func=run_join_game,
            args=[entry['name'], entry['ip']],
            tag='refresh',
            **button_kwargs
        )    
        buttons.append(b)
    w.join_elements(buttons, centerx_aligned=True, marginy=10)

    b = Button.Text_Button(text='new entry', pad=5, func=run_new_entry, tag='refresh')
    b.rect.left = elements[0].rect.left + 30   
    b.rect.y = elements[0].rect.bottom + 20
    elements.append(b)
    
    b = Button.Text_Button(text='view my ip', pad=5, func=run_view_ip)
    b.rect.right = elements[0].rect.right - 30
    b.rect.y = elements[0].rect.bottom + 20
    elements.append(b)
        
    b = Button.Text_Button(text='back', size=(200, 25), tag='exit')
    b.rect.midtop = elements[-1].rect.midbottom
    b.rect.y += b.rect.height
    elements.append(b)

    return elements
    
def run():
    m = Scene(select_host)
    m.run()

def join_game(scene, name, ip):
    body = scene.body
    elements = []
    
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
    
    textbox_kwargs = {
        'centery_aligned': True
    }
    
    tb = Textbox(text=name, **textbox_kwargs)
    tb.rect.topleft = (s.rect.left + 10, s.rect.top + 10)
    elements.append(tb)
    
    tb = Textbox(text=ip, **textbox_kwargs)
    tb.rect.topleft = elements[-1].rect.bottomleft
    tb.rect.y += 5
    elements.append(tb)

    tb = Textbox(text='port: ', centery_aligned=True)
    tb.set_enabled(False)
    tb.rect.topleft = (s.rect.left + 10, s.rect.bottom + 20)
    elements.append(tb)
    
    input_kwargs = {
        'size': (100, 25),
        'fill_color': None,
        'text_color': (255, 255, 255),
        'outline_color': (255, 255, 255),
        'outline_width': 3,
        'cursor_color': (255, 255, 255),
        'centery_aligned': True
    }

    i = Input.num_input(text=str(SAVE.get_data('port')), max_length=5, **input_kwargs)
    i.rect.midleft = tb.rect.midright
    elements.append(i)
    
    b = Button.Text_Button(
        text='Join Game!',
        text_size=35,
        inf_width=False,
        inf_height=False,
        centerx_aligned=True,
        centery_aligned=True,
        size=(200, 80),
        fill_color=(0, 200, 0),
        border_radius=10,
    )
    b.rect.top = elements[2].rect.bottom + 15
    b.set_parent(
        s,
        left_anchor='left',
        left_offset=15,
        right_anchor='right',
        right_offset=-15,
        bottom_anchor='bottom',
        bottom_offset=-15,
        top_anchor='top',
        top_offset=b.rect.top - s.rect.top
    )
    elements.append(b)
    
    b = Button.Text_Button(
        text=icons['trash'],
        font_name='icons.ttf',
        pad=5,
        hover_color=(128, 0, 0),
        centerx_aligned=True,
        centery_aligned=True,
        tag='exit',
        func=del_entry,
        args=[{'name': name, 'ip': ip}]
    )
    b.rect.topright = (s.rect.right - 10, s.rect.top + 10)
    elements.append(b)
    
    b = Button.Text_Button(
        text=icons['x'],
        font_name='icons.ttf',
        pad=5,
        hover_color=(128, 0, 0),
        centerx_aligned=True,
        centery_aligned=True,
        tag='exit'
    )
    b.rect.bottomleft = (s.rect.right + 10, s.rect.top - 10)
    elements.append(b)
    
    return elements
    
def run_join_game(name, ip):
    m = Scene(join_game, init_args=[name, ip])
    m.run()
    
def view_ip(scene):
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
            text=icons['copy'],
            font_name='icons.ttf',
            hover_color=(255, 255, 0),
            centerx_aligned=True,
            centery_aligned=True,
            func=Input.copy,
            args=[public_ip]
        )
        b.rect.midleft = elements[-2].rect.midright
        b.rect.right = s.rect.right - 10
        elements.append(b)
    
    t = Textbox(text=local_ip)
    t.rect.topleft = (s.rect.left + 10, s.rect.top + 105)
    elements.append(t)
    t = Textbox(text='local ip:', text_size=15)
    t.set_parent(elements[-1], bottom_anchor='top', bottom_offset=-5, left_anchor='left')
    elements.append(t)
    
    b = Button.Text_Button(
        text=icons['copy'],
        font_name='icons.ttf',
        hover_color=(255, 255, 0),
        centerx_aligned=True,
        centery_aligned=True,
        func=Input.copy,
        args=[local_ip]
    )
    b.rect.midleft = elements[-2].rect.midright
    b.rect.right = s.rect.right - 10
    elements.append(b)

    b = Button.Text_Button(
        text=icons['x'],
        font_name='icons.ttf',
        pad=5,
        hover_color=(128, 0, 0),
        centerx_aligned=True,
        centery_aligned=True,
        tag='exit'
    )
    b.rect.bottomleft = (s.rect.right + 10, s.rect.top - 10)
    elements.append(b)
    
    return elements
    
def run_view_ip():
    m = Scene(view_ip)
    m.run()
    
def add_new_entry(name_input, ip_input):
    SAVE.update_ips({
        'name': name_input.text,
        'ip': ip_input.text
    })
    
def del_entry(entry):
    scene = Yes_No(text_kwargs={'text': 'Delete this entry?'}, overlay=True)
    if scene.run():
        SAVE.del_ips(entry)












