import pygame as pg

from data.constants import CONSTANTS

from ui.element.base.element import Element
from ui.element.base.position import Position

class Spot(Position):
    def __init__(self, client, grid, pos):
        self.client = client
        self.grid = grid
        self._pos = pos
        self.card = None
        self.last_state = 0
        self.hover = False
        
        super().__init__(
            size=CONSTANTS['mini_card_size']
        )
        
    @property
    def state(self):
        if self.card:
            return 2 if self.card.visible else 0
        return 1 if self.hover else 0
        
    def click_up(self, button):
        if button == 1:
            if self.client.held_card and not self.client.held_card.player:
                self.client.send(f'play-{self.client.held_card.deck}-{self.client.held_card.cid}-{self._pos[0]}-{self._pos[1]}')
        
    def events(self, events):
        if self.children:
            self.child_events(events)
            return
            
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.hover = True
            if (mbu := events.get('mbu')):
                self.click_up(mbu.button)
        else:
            self.hover = False
        
    def set_card(self, card):
        self.card = card
        self.card.rect.topleft = self.rect.topleft
        self.add_child(self.card, current_offset=True)
        
    def clear_card(self):
        if self.card:
            self.remove_child(self.card)
            self.card = None
            
    def _draw(self, surf):
        match self.last_state:
            case 0:
                pg.draw.rect(surf, self.client.fill_color, self.rect)
            case 1:
                pg.draw.rect(surf, (100, 100, 100), self.rect)
            case 2:
                super().draw(surf)

        pg.draw.rect(surf, (255, 255, 255), self.rect, width=1)
        
    def draw(self, surf):
        state = self.state
        if state != self.last_state:
            self.last_state = state
            self.draw_on(surf, self.grid.rect, method=self._draw)

class Grid(Position):
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
        
        self.image = None
        
        self.cards = {}
        self.spots = []
        
    def reset(self):
        self.cards.clear()
        
        for spot in self.spots:
            spot.clear_card()
   
    def set_size(self, size):
        if size == self.grid_size:
            return
            
        self.clear_children()
        self.grid = {y: {x: Spot(self.client, self, (x, y)) for x in range(size[0])} for y in range(size[1])}
        c = self.rect.center
        self.size = (
            (size[0] * CONSTANTS['cw']) + ((size[0] + 1) * Grid.SPACE),
            (size[1] * CONSTANTS['ch']) + ((size[1] + 1) * Grid.SPACE)
        )
        
        self.spots.clear()
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
        
        self.image = pg.Surface(self.size).convert()
        self.image.fill(self.client.fill_color)
        for c in self.children:
            c.draw_on(self.image, self.rect, method=c._draw)
        
    def get_card(self, cid):
        return self.cards.get(cid)
                
    def set_card(self, card, pos):
        self.cards[card.cid] = card
        self.grid[pos[1]][pos[0]].set_card(card)
            
    def clear_card(self, pos):
        self.grid[pos[1]][pos[0]].clear_card()
        
    def draw(self, surf):
        if self.image:
            self.child_draw(self.image)
            surf.blit(self.image, self.rect)
            
        pg.draw.rect(surf, (255, 255, 255), self.rect, width=1)
            
            
                