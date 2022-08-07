from data.save import SAVE
from data.constants import CONSTANTS
from spritesheet.customsheet import CUSTOMSHEET
from builder.builder import run as run_builder

from ui.menu.menu import Menu
from ui.menu.templates.yes_no import Yes_No
from ui.element.elements import Textbox, Image, Button, Live_Window, Label
from ui.math.position import center_elements_y

CARD_WIDTH, CARD_HEIGHT = CONSTANTS['card_size']

def card_edit_menu(menu, card):
    body = menu.body
    elements = []

    t = Textbox(
        text=f"{card['name']}:"
    )
    t.rect.centerx = body.centerx
    elements.append(t)
    
    i = Image(image=CUSTOMSHEET.get_image(card['name'], size=(CARD_WIDTH // 3, CARD_HEIGHT // 3)))
    i.rect.midtop = elements[-1].rect.midbottom
    i.rect.y += 5
    elements.append(i)
    
    b = Button.Text_Button(
        text='edit card',
        tag='exit',
        func=run_builder,
        args=[card]
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + b.rect.height
    elements.append(b)
    
    def del_card(data):
        m = Yes_No(text_kwargs={'text': 'Are you sure you want to delete this card?'})
        if m.run():
            SAVE.del_card(data)
            menu.exit()
    
    if card['id'] != 0:
        b = Button.Text_Button(
            text='delete card',
            func=del_card,
            args=[card]
        )
        b.rect.centerx = body.centerx
        b.rect.y = elements[-1].rect.bottom + 5
        elements.append(b)
    
    b = Button.Text_Button(
        text='back',
        tag='exit'
    )
    b.rect.centerx = body.centerx
    b.rect.y = elements[-1].rect.bottom + b.rect.height
    elements.append(b)
    
    center_elements_y(elements, marginy=10)
    
    return elements
    
def run_card_edit(card):
    m = Menu(card_edit_menu, init_args=[card])
    m.run()

def builder_menu(menu):
    body = menu.body
    elements = []
    
    w = Live_Window(
        size=(300, 300),
        fill_color=(100, 0, 0)
    )
    w.rect.centerx = body.centerx
    w.rect.y = 70
    elements.append(w)
    elements.append(Label(w, text='custom cards:', height=30, fill_color=(0, 0, 100)))
    
    button_kwargs = {
        'centerx_aligned': True,
        'centery_aligned': True
    }

    cards = SAVE.get_data('cards').copy()
    
    buttons = []
    for c in cards:
        name = c['name']
        b = Button.Text_Button(
            text=name,
            size=(200, 22),
            func=run_card_edit,
            args=[c],
            tag='refresh',
            **button_kwargs
        )
        buttons.append(b)    
    w.join_elements(buttons, centerx_aligned=True, marginy=20)

    b = Button.Text_Button(
        text='new',
        func=run_builder,
        args=[SAVE.get_new_card_data()],
        tag='refresh',
        **button_kwargs
    )
    b.rect.midbottom = (body.centerx, body.height)
    b.rect.y -= b.rect.height * 2
    elements.append(b)
    
    b = Button.Text_Button(
        text='back',
        tag='exit'
    )
    b.rect.midtop = elements[-1].rect.midbottom
    b.rect.y += 5
    elements.append(b)
    
    return elements
    
def run():
    m = Menu(builder_menu)
    m.run()













