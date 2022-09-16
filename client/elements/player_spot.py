import pygame as pg

from data.constants import CONSTANTS

from ui.element.elements import Textbox, Static_Window
from ui.element.utils.timer import Timer
from ui.color.ops import color_text

from ..elements.card_window import Card_Window
from .visuals import COIN, DICE, SELECT, VOTE

class Player_Spot(Card_Window):
    SEP = 3
    def __init__(self):
        super().__init__(
            dir=-1,
            size=(CONSTANTS['cw'], CONSTANTS['ch'] * 6),
            outline_width=Player_Spot.SEP
        )

        self.player = None

        self.ongoing = Card_Window(
            dir=-1,
            size=self.size,
            outline_width=Player_Spot.SEP
        )
        self.ongoing.rect.topright = (self.rect.left - Player_Spot.SEP, self.rect.top)
        self.add_child(self.ongoing, current_offset=True)
        
        self.played = self
        
        self.active_card = Card_Window(
            dir=-1,
            size=CONSTANTS['mini_card_size'],
            outline_width=Player_Spot.SEP
        )
        self.active_card.rect.topleft = (self.rect.right + Player_Spot.SEP, self.rect.top)
        self.add_child(self.active_card, current_offset=True)

        self.sub_windows = {
            'ongoing': self.ongoing,
            'played': self.played,
            'active_card': self.active_card
        }
        
        self.label = Textbox(
            size=(self.active_card.rect.right - self.ongoing.rect.left, 30),
            centerx_aligned=True,
            centery_aligned=True,
            border_top_left_radius=10,
            border_top_right_radius=10,
            outline_width=Player_Spot.SEP
        )
        self.label.rect.midbottom = (self.rect.centerx, self.rect.top - Player_Spot.SEP)
        self.add_child(self.label, current_offset=True)
        
        self._points = 0
        self.points = Textbox(
            text_size=30,
            text_outline_color=(0, 0, 0),
            text_outline_width=2,
            enabled=False
        )
        self.label.add_child(self.points, left_anchor='right', centery_anchor='centery')
        self.points_timer = Timer(stop_time=120)
        
    def __str__(self):
        return f'{self.player.name} spot'
        
    def __repr__(self):
        return f'{self.player.name} spot'
   
    def set_player(self, player):
        self.player = player
        self.label.text_color = color_text(player.color)
        self.label.set_text(player.name)
        
        self.outline_color = player.color
        self.ongoing.outline_color = player.color
        self.active_card.outline_color = player.color
        self.label.outline_color = player.color
        self.label.fill_color = player.color
        
    def add_cards(self, win, cards):
        win = self.sub_windows[win]
        win.join_objects(cards)
        return win.get_visible()
        
    def find_card(self, cid):
        for c in self.elements:
            if c.cid == cid:
                return c
                
        for c in self.ongoing.elements:
            if c.cid == cid:
                return c
                
        for c in self.active_card.elements:
            if c.cid == cid:
                return c
                
    def reset_points(self):
        self._points = 0
        self.points.set_refresh(False)
        self.points.set_visible(False)
                
    def add_points(self, points):
        self._points += points
        if not self._points:
            self.reset_points()
            return
            
        self.points.set_refresh(True)
        self.points.set_visible(True)
        self.points.text_color = (255, 0, 0) if self._points < 0 else (0, 255, 0)
        self.points.set_text(str(self._points) if self._points < 0 else f'+{self._points}')
        self.points_timer.reset()
                
    def update(self):
        super().update()

        self.points_timer.step()
        if not self.points_timer:
            self.reset_points()
   
    def draw(self, surf):
        super().draw(surf)
        
        if self.player.coin is not None:
            c = COIN[self.player.coin]
            c.rect.center = self.active_card.rect.center
            c.draw(surf)
            
        elif self.player.dice is not None:
            d = DICE[self.player.dice]
            d.rect.center = self.active_card.rect.center
            d.draw(surf)
            
        elif self.player.selecting:
            s = SELECT
            s.rect.center = self.active_card.rect.center
            s.draw(surf)
        
        
        
        