import pygame as pg

from data.constants import CONSTANTS

from ui.element.base.element import Element

class Card(Element):
    def __init__(self, client, name, cid, player=None):
        self.client = client
        self.name = name
        self.cid = cid
        self.player = player

        super().__init__(
            size=CONSTANTS['mini_card_size']
        )
 
    def __eq__(self, other):
        return self.cid == other.cid and self.name == other.name
        
    def __repr__(self):
        return self.name
        
    def __hash__(self):
        return self.cid
        
    def copy(self):
        return Card(self.client, self.name, self.cid)
 
    def get_image(self, mini=True, scale=None):
        return self.client.sheet.get_image(self.name, mini=mini, scale=scale)
        
    @property
    def is_select(self):
        return self.parent is self.client.selection.bounding_box
        
    def left_click(self):
        if not self.is_select:
            self.client.set_held_card(self)
        else:
            self.client.send(f'select-{self.cid}')
        
    def update_info(self, name, cid):
        self.name = name
        self.cid = cid
        
    def right_click(self):
        self.client.set_view_card(self)
        
    def click_up(self, button):
        match button:
            
            case 1:
                if self.client.held_card is self:
                    self.client.clear_held_card()
  
            case 3:
                if self.client.view_card is self:
                    self.client.clear_view_card()
                
    def events(self, events):
        super().events(events)
        
        if self.hit:
            self.client.set_hover_card(self)
        elif self.client.hover_card is self:
            self.client.clear_hover_card()

    def draw(self, surf): 
        surf.blit(self.get_image(), self.rect)
        
        if self.player:
            pg.draw.rect(surf, self.player.color, self.rect, width=2)
