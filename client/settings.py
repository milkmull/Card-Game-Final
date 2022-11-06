import json

import pygame as pg

from data.save import SAVE

from ui.scene.scene import Scene
from ui.scene.templates.notice import Notice
from ui.scene.templates.yes_no import Yes_No

from ui.element.base.element import Element
from ui.element.elements import Textbox, Button, Flipper

def confirm_exit():
    m = Yes_No(text_kwargs={'text': 'Are you sure you want to exit the game?'}, overlay=True)
    return m.run()
        
def run_settings(client):
    m = Scene(settings_scene, init_args=[client], overlay=True)
    quit = m.run()
    if quit:
        client.running = False

def settings_scene(scene, client):
    elements = []
    settings = client.get_settings()
    
    s = Element(
        size=(420, 300),
        fill_color=(50, 50, 50),
        outline_color=(255, 255, 255),
        outline_width=5,
        border_radius=10,
        layer=-1
    )
    s.rect.center = scene.rect.center
    elements.append(s)
    
    x0 = s.rect.left + 10
    x1 = s.rect.left + 300
    y = 25
    
# grid size section

    tb = Textbox(text='Grid Size:')
    tb.set_parent(
        s,
        left_anchor='left',
        left_offset=10,
        top_anchor='top',
        top_offset=y
    )
    elements.append(tb)
    
    x = Textbox(text='x')
    x.rect.center = (x1, tb.rect.centery)
    x.set_parent(tb, centery_anchor='centery')
    elements.append(x)

    w = Flipper.Counter(range(1, 13), index=settings['size'][0] - 1, text_size=30)
    w.rect.midright = (x.rect.left - 40, x.rect.centery)
    w.set_parent(tb, centery_anchor='centery')
    elements.append(w)

    h = Flipper.Counter(range(1, 9), index=settings['size'][1] - 1, text_size=30)
    h.rect.midleft = (x.rect.right + 40, x.rect.centery)
    h.set_parent(tb, centery_anchor='centery')
    elements.append(h)
    
    y += 50
    
# turn timer section

    tb = Textbox(text='Seconds Per Turn:')
    tb.set_parent(
        s,
        left_anchor='left',
        left_offset=10,
        top_anchor='top',
        top_offset=y
    )
    elements.append(tb)

    r = range(10, 300, 10)
    tt = Flipper.Counter(r, index=r.index(settings['tt']), text_size=30)
    tt.rect.center = (x1, tb.rect.centery)
    tt.set_parent(tb, centery_anchor='centery')
    elements.append(tt)
    
    y += 50
    
# cpu section

    tb = Textbox(text='CPU Players:')
    tb.set_parent(
        s,
        left_anchor='left',
        left_offset=10,
        top_anchor='top',
        top_offset=y
    )
    elements.append(tb)
    
    cpu_count = len([p for p in client.players if p.is_cpu])
    non_cpu_count = len(client.players) - cpu_count
    min_cpu = 1 if client.is_single else 0
    max_cpu = 11 - non_cpu_count
    r = range(min_cpu, max_cpu)

    cpus = Flipper.Counter(r, index=r.index(cpu_count), text_size=30, size=tt.rect.size)
    cpus.rect.center = (x1, tb.rect.centery)
    cpus.set_parent(tb, centery_anchor='centery')
    elements.append(cpus)
    
    y += 50
    
# difficulty section

    tb = Textbox(text='CPU Difficulty:')
    tb.set_parent(
        s,
        left_anchor='left',
        left_offset=10,
        top_anchor='top',
        top_offset=y
    )
    elements.append(tb)

    diff = Flipper.Counter(range(1, 5), index=settings['diff'] - 1, text_size=30, size=tt.rect.size)
    diff.rect.center = (x1, tb.rect.centery)
    diff.set_parent(tb, centery_anchor='centery')
    elements.append(diff)
    
# turn off all elements if player is not host

    if not client.is_host:
        for e in elements[1:]:
            e.set_enabled(False)
    
# bottom section

    back_button = Button.Text_Button(
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
    if client.is_host:
        back_button.set_parent(
            s,
            right_anchor='right',
            right_offset=-20,
            bottom_anchor='bottom',
            bottom_offset=-20
        )
    else:
        back_button.set_parent(
            s,
            centerx_anchor='centerx',
            bottom_anchor='bottom',
            bottom_offset=-20
        )
    elements.append(back_button)
    
    if client.is_host:
    
        def set_defaults():
            settings = SAVE.get_base_settings()
            
            w.set_text(str(settings['size'][0]))
            h.set_text(str(settings['size'][1]))
            tt.set_text(str(settings['tt']))
            cpus.set_text(str(settings['cpus']))
            diff.set_text(str(settings['diff']))
        
        defaults_button = Button.Text_Button(
            text='Defaults',
            size=(100, 30),
            center_aligned=True,
            hover_color=(255, 255, 0),
            hover_text_color=(0, 0, 0),
            outline_color=(255, 255, 255),
            outline_width=2,
            border_radius=5,
            func=set_defaults
        )
        defaults_button.set_parent(
            s,
            centerx_anchor='centerx',
            bottom_anchor='bottom',
            bottom_offset=-20
        )
        elements.append(defaults_button)
        
        def apply_settings():
            new_settings = {
                'size': [int(w.text), int(h.text)],
                'tt': int(tt.text),
                'cpus': int(cpus.text),
                'diff': int(diff.text)
            }
            client.send(f'settings-{json.dumps(new_settings)}')

            n = Notice(text_kwargs={'text': 'Settings have been applied successfully!'}, overlay=True)
            n.run()
        
        apply_button = Button.Text_Button(
            text='Apply',
            size=(100, 30),
            center_aligned=True,
            hover_color=(0, 255, 0),
            hover_text_color=(0, 0, 0),
            outline_color=(255, 255, 255),
            outline_width=2,
            border_radius=5,
            func=apply_settings
        )
        apply_button.set_parent(
            s,
            left_anchor='left',
            left_offset=20,
            bottom_anchor='bottom',
            bottom_offset=-20
        )
        elements.append(apply_button)
    
    exit_button = Button.Text_Button(
        text='Exit Game',
        size=(150, 30),
        center_aligned=True,
        fill_color=(0, 0, 1),
        hover_color=(255, 0, 0),
        hover_text_color=(0, 0, 0),
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=5,
        func=confirm_exit,
        tag='return'
    )
    exit_button.set_parent(
        s,
        centerx_anchor='centerx',
        top_anchor='bottom',
        top_offset=20
    )
    elements.append(exit_button)
    
    b = Button.Text_Button(
        size=scene.rect.size,
        cursor=0,
        layer=-2,
        tag='exit'
    )
    elements.append(b)
    
    return elements
    