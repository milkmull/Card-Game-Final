from ui.menu.menu import Menu
from ui.element.base.style import Style
from ui.element.elements import Textbox, Button, Live_Window, Static_Window
from ui.icons.icons import icons

def full_error(menu, err):
    body = menu.body

    tb = Textbox(
        text=err,
        font_name='JetBrainsMonoNL-Regular.ttf',
        text_size=17,
        text_color=(224, 226, 228),
        pad=5
    )
    tb.size = tb.text_surf.get_size()

    window = Static_Window(
        size=(tb.padded_rect.width, 430),
        fill_color=(41, 49, 52),
        outline_color=(255, 255, 255),
        outline_width=3
    )
    window.rect.center = body.center
    window.join_elements([tb], border=5)
    
    exit_button = Button.Text_Button(
        text=icons['x'],
        font_name='icons.ttf',
        text_color=(255, 0, 0),
        tag='exit'
    )
    exit_button.rect.bottomleft = (window.rect.right + 5, window.rect.top - 5)

    return [window, exit_button]
    
def run_full(err):
    m = Menu(full_error, init_args=[err])
    m.run()

def error_elements(menu, errors):
    body = menu.body
    elements = []
    
    buttons = []
    for err in errors:
        b = Button.Text_Button(
            text=err.splitlines()[-1].strip(),
            max_line_width=350,
            centerx_aligned=True,
            centery_aligned=True,
            pad=5,
            func=run_full,
            args=[err],
            hover_color=(100, 100, 100)
        )
        buttons.append(b)
    
    window = Live_Window(
        size=(400, 300),
        fill_color=(50, 50, 50),
        border_radius=5,
        inner_outline_color=(255, 0, 0),
        inner_outline_width=3,
        clip_size=(394, 294)
    )
    window.rect.center = body.center
    elements.append(window)
    
    window.join_elements(
        buttons,
        border=10,
        margin=15,
        centerx_aligned=True
    )
    
    error_text = Textbox(
        text=f"{len(errors)} Error{'' if len(errors) == 1 else 's'} Found:",
        text_size=30,
        text_color=(255, 0, 0),
        inf_width=False,
        max_line_width=window.rect.width,
        centery_aligned=True
    )
    window.add_child(error_text, centerx_anchor='centerx', bottom_anchor='top', bottom_offset=-10)
    
    ok_button = Button.Text_Button(
        text='Ok',
        size=(200, 25),
        centerx_aligned=True,
        centery_aligned=True,
        border_radius=5,
        hover_color=(0, 255, 0),
        tag='exit'
    )
    ok_button.rect.midtop = (window.rect.centerx, window.rect.bottom + 10)
    elements.append(ok_button)
    
    ok_button.add_animation(
        [{
            'attr': 'text_color',
            'end': (0, 0, 0)
        }],
        tag='hover'
    )

    return elements
    
def run(errors):
    m = Menu(error_elements, init_args=[errors])
    m.run()