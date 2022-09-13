from ui.element.standard.button import Button
from .element.input import INPUTS
from .element.check_box import Logged_Check_Box as Check_Box
from .element.dropdown import Logged_Dropdown as Dropdown
from ui.element.utils.image import get_arrow
from ui.icons.icons import icons

def set_input_element(port, type, value=''):
    i = INPUTS[type](
        port,
        text=value
    )
    port.set_element(i)
    
def set_check_element(port):
    cb = Check_Box(
        port,
        value=port.node._get_default(port.port) == 'True'
    )
    port.set_element(cb)
    
def set_dropdown_element(port, options, value=None):
    dd = Dropdown(
        port,
        options,
        value=value
    )
    port.set_element(dd)

def get_transform_button(node):
    h = node.label_rect.height - 10
    i = get_arrow('>', (h, h))
    
    b = Button.Image_Button(
        image=i,
        pad=5,
        border_radius=2,
        func=node.transform,
        hover_color=(100, 100, 100)
    )
    
    b.rect.midright = (node.label_rect.right - 5, node.label_rect.centery)
    node.add_child(b, current_offset=True)
    
def get_ar_buttons(node, io):
    h = node.label_rect.height - 5
    a = Button.Text_Button(
        text=icons['+'],
        font_name='icons.ttf',
        size=(h, h),
        pad=2,
        centerx_aligned=True,
        centery_aligmed=True,
        inf_width=False,
        inf_height=False,
        func=node.add_port,
        hover_color=(100, 100, 100)
    )
    r = Button.Text_Button(
        text=icons['-'],
        font_name='icons.ttf',
        size=(h, h),
        pad=2,
        centerx_aligned=True,
        centery_aligmed=True,
        inf_width=False,
        inf_height=False,
        func=node.remove_port,
        hover_color=(100, 100, 100)
    )
    if io == 1:
        a.rect.midleft = (node.label_rect.left + 5, node.label_rect.top + 10)
        r.rect.midleft = (a.padded_rect.right + r.pad['left'] + 5, a.rect.centery)
    elif io == -1:
        r.rect.midright = (node.label_rect.right - 5, node.label_rect.top + 10)
        a.rect.midright = (r.padded_rect.left - a.pad['right'] - 5, r.rect.centery)
    node.add_child(a, current_offset=True)
    node.add_child(r, current_offset=True)
 