import pygame as pg

from ui.element.elements import Textbox, Image
from ui.element.utils.image import get_arrow
from ui.icons.icons import icons

from .points_spot import Points_Spot

class Player_Spot(Textbox):
    SEP = 3
    def __init__(self):
        super().__init__(
            text_outline_color=(0, 0, 0),
            text_outline_width=2
        )

        self.player = None
        
        self.turn_indicator = Textbox(
            text=icons['play'],
            font_name='icons.ttf',
            text_outline_color=(0, 0, 0),
            text_outline_width=2
        )
        self.turn_indicator.turn_off()
        self.add_child(
            self.turn_indicator,
            right_anchor='left',
            right_offset=-10,
            centery_anchor='centery'
        )
        
        self.turn_indicator.add_animation([
            {
                'attr': 'right_offset',
                'start': -10,
                'end': -15,
                'frames': 10,
                'method': 'ease_in_out_quart'
            },
            {
                'attr': 'right_offset',
                'end': -10,
                'frames': 10,
                'method': 'ease_in_out_quart'
            },
        ], loop=True)
        
        self.points_spot = Points_Spot(self)
        self.add_child(
            self.points_spot,
            left_anchor='right',
            left_offset=10,
            centery_anchor='centery'
        )
        
    def __str__(self):
        return f'{self.player.name} spot'
        
    def __repr__(self):
        return f'{self.player.name} spot'
   
    def set_player(self, player):
        self.player = player
        self.text_color = player.color
        self.outline_color = player.color
        self.set_text(player.name)
        self.turn_indicator.text_color = player.color
        self.points_spot.text_color = player.color
        
    def start_turn(self):
        self.turn_indicator.turn_on()
        
    def end_turn(self):
        self.turn_indicator.turn_off()
        
        
        
        