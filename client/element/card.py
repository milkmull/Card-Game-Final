import pygame as pg

from data.constants import CONSTANTS

from ui.element.base.position import Position

class Card(Position):
    def __init__(self, client, name, cid, player=None, deck=None):
        self.client = client
        self.name = name
        self.cid = cid
        self.player = player
        self.deck = deck
        
        super().__init__(size=CONSTANTS['mini_card_size'])
 
    def __eq__(self, other):
        return self.cid == other.cid and self.name == other.name
        
    def __repr__(self):
        return self.name
        
    def __hash__(self):
        return self.cid
        
    @property
    def is_select(self):
        return self.parent is self.client.selection.bounding_box

    def get_image(self, mini=True, scale=None):
        return self.client.sheet.get_image(self.name, mini=mini, scale=scale)
  
    def left_click(self):
        if not self.is_select:
            self.client.set_held_card(self)
        else:
            self.client.send(f'select-{self.cid}')
        
    def right_click(self):
        self.client.set_view_card(self)
                
    def events(self, events):
        if not events['hover']:
        
            if self.rect.collidepoint(pg.mouse.get_pos()):
                self.client.set_hover_card(self)
                
                if (mbd := events.pop('mbd', None)):
                    
                    match mbd.button:
                        case 1:
                            self.left_click()
                        case 3:
                            self.right_click()    

    def update(self):
        self.update_position()

    def draw(self, surf): 
        surf.blit(self.get_image(), self.rect)
        
        if self.player:
            pg.draw.rect(surf, self.player.color, self.rect, width=4)
