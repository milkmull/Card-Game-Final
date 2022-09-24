import pygame as pg

from data.constants import CONSTANTS

from ui.element.base.element import Element

class Spot(Element):
    def __init__(self, client, pos):
        self.client = client
        self._pos = pos
        self.card = None
        
        super().__init__(
            size=CONSTANTS['mini_card_size'],
            outline_color=(255, 255, 255),
            outline_width=1
        )
        
    def click_up(self, button):
        if button == 1:
            if self.client.held_card:
                self.client.send(f'play-{self.client.held_card.deck}-{self.client.held_card.cid}-{self._pos[0]}-{self._pos[1]}')
        
    def events(self, events):
        if self.children:
            self.child_events(events)
            return
            
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.fill_color = (100, 100, 100)
            if mbu := events.get('mbu'):
                self.click_up(mbu.button)
        else:
            self.fill_color = None
        
    def set_card(self, card):
        self.card = card
        self.card.rect.topleft = self.rect.topleft
        self.add_child(self.card, current_offset=True)
        
    def clear_card(self):
        if self.card:
            self.remove_child(self.card)
            self.card = None

class Grid(Element):
    SPACE = 2
    def __init__(
        self,
        client
    ):
        self.client = client
        self.grid_size = (0, 0)

        super().__init__(
            outline_color=(255, 255, 255),
            outline_width=1,
            layer=1
        )
        
        self.cards = {}
                
    def set_size(self, size):
        if size == self.grid_size:
            return
            
        self.clear_children()
        self.grid = {y: {x: Spot(self.client, (x, y)) for x in range(size[0])} for y in range(size[1])}
        c = self.rect.center
        self.size = (
            (size[0] * CONSTANTS['cw']) + ((size[0] + 1) * Grid.SPACE),
            (size[1] * CONSTANTS['ch']) + ((size[1] + 1) * Grid.SPACE)
        )
        
        self.spots = []
        for y, row in self.grid.items():
            for x, spot in row.items():
                self.spots.append(spot)
                spot.rect.topleft = (
                    self.rect.left + (x * spot.rect.width) + ((x + 1) * Grid.SPACE),
                    self.rect.top + (y * spot.rect.height) + ((y + 1) * Grid.SPACE)
                )
                self.add_child(spot, current_offset=True)
            
        self.grid_size = size
        self.rect.center = c
        
    def get_card(self, cid):
        return self.cards.get(cid)
                
    def set_card(self, card, pos):
        self.cards[card.cid] = card
        self.grid[pos[1]][pos[0]].set_card(card)
            
    def clear_card(self, pos):
        self.grid[pos[1]][pos[0]].clear_card()
            
                