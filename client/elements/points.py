import pygame as pg

from ui.element.standard.textbox import Textbox

class Points(Textbox):
    def __init__(
        self, 
        client, 
        player, 
        points, 
        card, 
        target=None, 
        parent=None
    ):

        super().__init__(
            text=str(points) if points < 0 else f'+{points}',
            text_size=30,
            text_color=player.color,
            text_outline_color=(0, 0, 0),
            text_outline_width=2,
            layer=1,
            enabled=False
        )
        
        self.client = client
        self.player = player
        self.points = points
        self.card = card

        self.rect.center = card.rect.center
        
        delay = 60 if not parent else 10
        end = player.spot.points_spot.rect.center if not parent else parent.rect.center

        self.animation = self.add_animation([{
            'attr': 'center',
            'end': end,
            'delay': delay,
            'frames': 20,
            'method': 'ease_in_quad'
        }])
        
        self.client.elements.append(self)
        
    @property
    def center(self):
        return self.rect.center
        
    @center.setter
    def center(self, center):
        self.rect.center = center
        
    def add(self, points):
        self.points += points
        self.text_size += (2 * points)
        c = self.rect.center
        self.set_text(str(self.points) if self.points < 0 else f'+{self.points}')
        self.rect.center = c

    def merge(self, child):
        self.add(child.points)
        self.remove_child(child)
        
    def add_child_points(self, points, card, target=None):
        self.add_child(Points(self.client, self.player, points, card, target=target, parent=self))
   
    def end(self):
        self.client.elements.remove(self)
        if self.parent:
            self.parent.merge(self)
        else:
            self.client.points.pop(self.card.cid, None)
        
    def update(self):
        super().update()

        if self.animation.finished:
            self.end()
            return
            
    def draw(self, surf):
        if not self.points:
            self.child_draw(surf)
        else:
            super().draw(surf)
            
    
        