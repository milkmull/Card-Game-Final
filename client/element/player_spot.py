import pygame as pg

from ui.element.elements import Textbox, Image, Input
from ui.element.utils.image import get_arrow
from ui.icons.icons import icons

class Player_Spot(Textbox):
    SEP = 3
    def __init__(self):
        super().__init__(
            text_outline_color=(0, 0, 0),
            text_outline_width=2,
            layer=5
        )

        self.player = None
        self._display_full = 0
        
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
        
        self.set_points_spot()
        
        self.add_animation(
            [{
                'attr': 'display_full',
                'end': 1
            }],
            tag='hover'
        )

    def __str__(self):
        return f'{self.player.name} spot'
        
    def __repr__(self):
        return f'{self.player.name} spot'
        
    def set_points_spot(self):
        self.points_spot = Textbox(
            text='0',
            text_outline_color=(0, 0, 0),
            text_outline_width=2
        )
        self.add_child(
            self.points_spot,
            left_anchor='right',
            left_offset=10,
            centery_anchor='centery'
        )
        
    @property
    def display_full(self):
        return self._display_full
        
    @display_full.setter
    def display_full(self, display_full):
        self._display_full = display_full
        self.update_name()
    
    @property
    def display_name(self):
        if not self.player:
            return ''
            
        if self._display_full:
            return self.player.name
            
        tr = self.rect.topright
        name = self.player.name
        add = False
        while True:
            r = self.get_text_rect(text=name + ('...' if add else ''))
            r.width += self.turn_indicator.rect.width + 10
            r.topright = tr
            if not r.colliderect(self.scene.grid.rect):
                break
            name = name[:-1]
            add = True
            if not name:
                break
        
        if self.player.name == name:
            return self.player.name
            
        return f'{name}...'
        
    def update_name(self):
        name = self.text
        new_name = self.display_name
        if name != new_name:
            tr = self.rect.topright
            self.set_text(new_name)
            self.rect.topright = tr
   
    def set_player(self, player):
        self.player = player
        self.text_color = player.color
        self.outline_color = player.color
        self.set_text(self.display_name)
        self.turn_indicator.text_color = player.color
        self.points_spot.text_color = player.color
        
    def set_score(self, score):
        self.points_spot.set_text(str(score))
        
    def start_turn(self):
        self.turn_indicator.turn_on()
        
    def end_turn(self):
        self.turn_indicator.turn_off()
        
class Sandbox_Player_Spot(Player_Spot):
    def __init__(self):
        super().__init__()
        
        self.cursor = pg.SYSTEM_CURSOR_HAND
        self.add_animation(
            [{
                'attr': 'outline_width',
                'end': 2
            }],
            tag='hover'
        )
        
    def set_points_spot(self):
        self.points_spot = Input(
            text='0',
            fill_color=None,
            text_outline_color=(0, 0, 0),
            text_outline_width=2,
            text_check=lambda t: t.lstrip('-').isnumeric(),
            max_length=3,
            max_lines=1
        )
        self.add_child(
            self.points_spot,
            left_anchor='right',
            left_offset=10,
            centery_anchor='centery'
        )

    def set_player(self, player):
        super().set_player(player)
        self.outline_color = player.color
        