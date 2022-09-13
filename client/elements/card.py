import pygame as pg

from data.constants import CONSTANTS

from ui.element.base.element import Element

from ui.particals.get_particals import bubble

class Card(Element):
    def __init__(self, client, name, uid):
        self.client = client
        self.name = name
        self.uid = uid
        
        self.active = False
        self.bubbles = []
        
        super().__init__(
            size=CONSTANTS['mini_card_size']
        )
 
    def __eq__(self, other):
        return self.uid == other.uid and self.name == other.name
        
    def __repr__(self):
        return self.name
        
    def __hash__(self):
        return self.uid
        
    def copy(self):
        return Card(self.client, self.name, self.uid)
 
    def get_image(self, mini=True, scale=None):
        return self.client.sheet.get_image(self.name, mini=mini, scale=scale)
        
    def left_click(self):
        self.client.send(str(self.uid))
        
    def update_info(self, name, uid):
        self.name = name
        self.uid = uid
        
    def right_click(self):
        self.client.set_view_card(self)
        
    def click_up(self, button):
        if button == 3:
            if self.client.view_card is self:
                self.client.clear_view_card()
                
    def events(self, events):
        super().events(events)
        
        if self.hit:
            self.client.set_hover_card(self)
        elif self.client.hover_card is self:
            self.client.clear_hover_card()
            
    def update(self):
        super().update()
        
        if self.active:
            self.bubbles += bubble((5 if not self.bubbles else 1), self.rect, (5, 10))
            
            for b in self.bubbles.copy():
                b[0][1] -= 1
                b[1] -= 1
                if b[1] <= 0:
                    self.bubbles.remove(b)

    def draw(self, surf): 
        surf.blit(self.get_image(), self.rect)
        
        if self.active:
            for p, r in self.bubbles:
                pg.draw.circle(surf, (255, 0, 0), p, r)
