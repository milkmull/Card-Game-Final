from ui.menu.menu import Menu
from ui.element.elements import Textbox, Button
from ui.icons.icons import icons

from .settings import run as run_settings
from .wireless_play import run as run_wireless_play
from .builder import run as run_builder

def main_menu(menu):
    body = menu.body
    elements = []

    button_kwargs = {
        'size': (200, 40),
        'centerx_aligned': True,
        'centery_aligned': True,
        'outline_color': (255, 255, 255),
        'border_radius': 3,
        'text_size': 30
    }
    
    hover_animation = {
        'attr': 'outline_width',
        'end': 3,
        'frames': 5,
        'strict': True
    }

    b = Button.Text_Button(
        text='single player',
        **button_kwargs
    )
    elements.append(b)
    b.rect.centerx = body.centerx
    b.rect.y = 150
    
    b = Button.Text_Button(
        text='card builder',
        func=run_builder,
        **button_kwargs
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + 10
    elements.append(b)

    b = Button.Text_Button(
        text='wireless play',
        func=run_wireless_play,
        **button_kwargs
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + b.rect.height
    elements.append(b)
    
    b = Button.Text_Button(
        text='settings',
        func=run_settings,
        clip=True,
        **button_kwargs
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + b.rect.height
    elements.append(b)
    
    tb = Textbox(text=icons['cog'], font_name='icons.ttf', text_size=30)
    tb = tb.to_image(size=tb.rect.size, auto_fit=True)
    tb.set_enabled(False)
    tb.rect.midright = b.rect.midright
    tb.rect.x -= 15
    b.add_child(tb)
    
    b.add_animation(
        [{
            'attr': 'alpha',
            'start': 0,
            'end': 255,
            'frames': 5,
            'element': tb
        }],
        tag='hover'
    )
    
    b.add_animation(
        [{
            'attr': 'rotation',
            'start': 0,
            'end': 360,
            'frames': 5,
            'element': tb
        }],
        tag='hover'
    )
    
    b.add_animation(
        [{
            'attr': 'x',
            'end': b.rect.x - 20,
            'frames': 5
        }],
        tag='hover'
    )
    
    b.add_animation(
        [{
            'attr': 'padding',
            'end': (-20, 20, 0, 0),
            'frames': 5
        }],
        tag='hover'
    )
    
    b = Button.Text_Button(
        text='exit game',
        tag='exit',
        **button_kwargs
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + 5
    elements.append(b)

    for b in elements:
        b.add_animation([hover_animation.copy()], tag='hover')
    
    return elements
    
def run():
    m = Menu(main_menu)
    m.run()











