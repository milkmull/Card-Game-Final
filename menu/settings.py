from data.save import SAVE

from ui.scene.scene import Scene
from ui.scene.templates.yes_no import Yes_No
from ui.scene.templates.notice import Notice
from ui.element.elements import Textbox, Button, Input
from ui.element.base.style import Style
from ui.math.position import center_elements_y

def save_changes(username_input, port_input):
    username = username_input.text
    SAVE.set_data("username", username)
    
    port = int(port_input.text)
    if port < 1023:
        message = "Port value too small. Please enter a value between 1023 and 65535."
    elif port > 65535:
        message = "Port value too large. Please enter a value between 1023 and 65535."
    else:
        SAVE.set_data("port", port)
        message = "Changes saved."
        
    m = Notice(text_kwargs={"text": message})
    m.run()
    
def reset_save_data():
    m = Yes_No(overlay=True, text_kwargs={"text": "Are you sure you want to reset your save data?"})
    if m.run():
        SAVE.reset_save()

def settings(scene):
    body = scene.body
    elements = []
    
    input_kwargs = {
        "size": (200, 25),
        "fill_color": None,
        "text_color": (255, 255, 255),
        "outline_color": (255, 255, 255),
        "outline_width": 3,
        "cursor_color": (255, 255, 255),
        "centery_aligned": True,
        "max_lines": 1
    }

    i = Input(text=SAVE.get_data("username"), **input_kwargs)
    elements.append(i)

    tb = Textbox(text="username:", size=(200, 25), centery_aligned=True)
    tb.rect.topleft = i.rect.topleft
    tb.set_enabled(False)
    tb.rect.bottomleft = (i.rect.left, i.rect.top - 5)
    tb.set_parent(i, current_offset=True)
    elements.append(tb)
    
    i = Input.num_input(text=str(SAVE.get_data("port")), max_length=5, **input_kwargs)
    i.rect.topleft = (elements[0].rect.x, elements[0].rect.bottom + 60)
    elements.append(i)
    
    tb = Textbox(text="default port:", size=(200, 25), centery_aligned=True)
    tb.rect.topleft = i.rect.topleft
    tb.set_enabled(False)
    tb.rect.bottomleft = (i.rect.left, i.rect.top - 5)
    tb.set_parent(i, current_offset=True)
    elements.append(tb)
    
    center_elements_y(elements[::2], marginy=50)
    
    button_kwargs = {
        "size": (200, 25),
        "centerx_aligned": True,
        "centery_aligned": True,
        "outline_color": (255, 255, 255),
        "border_radius": 3
    }
    
    b = Button.Text_Button(text="reset save data", **button_kwargs)
    b.add_event(tag="left_click", func=reset_save_data)
    b.rect.center = (body.centerx, body.height - 150)
    elements.append(b)
    
    b = Button.Text_Button(text="save changes", **button_kwargs)
    b.add_event(tag="left_click", func=save_changes, args=[elements[0], elements[2]])
    b.rect.center = elements[-1].rect.midbottom
    b.rect.y += 10
    elements.append(b)
    
    b = Button.Text_Button(text="back', tag='exit", **button_kwargs)
    b.rect.midtop = elements[-1].rect.midbottom
    b.rect.y += 10
    elements.append(b)
    
    return elements
    
def run():
    m = Scene(settings)
    m.run()













