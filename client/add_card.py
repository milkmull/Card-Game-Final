import json

import pygame as pg

from data.constants import get_sorted_names_dict
from ui.scene.scene import Scene

from ui.element.base.element import Element
from ui.element.elements import Textbox, Button, Image, Dropdown
from .element.player_dropdown import Player_Dropdown

LAST_CHOICE = None
        
def run_add_card(client, spot=None, deck=None):
    m = Scene(add_card_scene, init_args=[client, spot, deck], overlay=True)
    m.run()
    
def add_card_scene(scene, client, spot, deck):
    global LAST_CHOICE
    
    elements = []
    settings = client.get_settings()
    
    s = Element(
        size=(420, 350),
        fill_color=(80, 80, 100),
        outline_color=(255, 255, 255),
        outline_width=5,
        border_radius=10,
        layer=-1
    )
    s.rect.center = scene.rect.center
    elements.append(s)
    
    top_text = Textbox(
        text=f"Add to {'grid' if spot is not None else deck}:",
        text_size=30
    )
    top_text.rect.bottomleft = (s.rect.left + 5, s.rect.top - 10)
    s.add_child(top_text, current_offset=True)
    
    tb = Textbox(
        text='Card:'
    )
    tb.rect.topleft = (s.rect.left + 20, s.rect.top + 20)
    s.add_child(tb, current_offset=True)
    
    card_selection = Dropdown(
        get_sorted_names_dict(),
        max_buttons=6,
        centery_aligned=True,
        pad=5,
        text_color=(255, 255, 255),
        fill_color=(32, 32, 40),
        outline_color=(0, 0, 0),
        outline_width=3,
        border_radius=5,
        window_kwargs={
            'fill_color': (32, 32, 40),
            'outline_color': (200, 200, 200),
            'outline_width': 3
        },
        layer=2
    )
    card_selection.rect.topleft = (tb.rect.left, tb.rect.bottom + 10)
    s.add_child(card_selection, current_offset=True)

    if deck != 'public':
    
        tb = Textbox(
            text='Player:'
        )
        tb.rect.topleft = (card_selection.rect.left, card_selection.rect.bottom + 30)
        s.add_child(tb, current_offset=True)
    
        player_selection = Player_Dropdown(
            client,
            max_buttons=5,
            centery_aligned=True,
            pad=5,
            fill_color=(32, 32, 40),
            outline_color=(0, 0, 0),
            outline_width=3,
            border_radius=5,
            window_kwargs={
                'fill_color': (32, 32, 40),
                'outline_color': (200, 200, 200),
                'outline_width': 3
            },
            layer=1
        )
        player_selection.rect.topleft = (tb.rect.left, tb.rect.bottom + 10)
        s.add_child(player_selection, current_offset=True)
    
    card_image = Image(
        image=client.sheet.get_image(card_selection.text.lower(), scale=0.5)
    )
    card_image.rect.topright = (s.rect.right - 20, s.rect.top + 15)
    s.add_child(card_image, current_offset=True)
    
    def update_image():
        global LAST_CHOICE
        text = card_selection.text
        card_image.set_image(client.sheet.get_image(text.lower(), scale=0.5))
        LAST_CHOICE = text
        
    card_selection.add_event(
        tag='set_text',
        func=update_image
    )
    
    if not LAST_CHOICE:
        LAST_CHOICE = card_selection.text
    else:
        card_selection.set_value(LAST_CHOICE)

    def set_card():
        name = card_selection.text.lower()
        match deck:
            case 'public':
                client.add_public_card(name)
            case 'private':
                player_name = player_selection.text
                client.add_private_card(name, player_name)
            case _:
                player_name = player_selection.text
                client.manual_set_card(spot, name, player_name)

    play_button = Button.Text_Button(
        text='Add' if spot is None else 'Play',
        size=(150, 30),
        center_aligned=True,
        hover_color=(0, 255, 0),
        hover_text_color=(0, 0, 0),
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=5,
        tag='exit',
        func=set_card
    )
    play_button.rect.bottomleft = (s.rect.left + 40, s.rect.bottom - 20)
    s.add_child(play_button, current_offset=True)
    
    back_button = Button.Text_Button(
        text='Back',
        size=(150, 30),
        center_aligned=True,
        hover_color=(255, 0, 0),
        hover_text_color=(0, 0, 0),
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=5,
        tag='exit'
    )
    back_button.rect.bottomright = (s.rect.right - 40, s.rect.bottom - 20)
    s.add_child(back_button, current_offset=True)

    return elements
    