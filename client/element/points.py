import pygame as pg

from ui.element.base.text import Text
from ui.element.base.position import Position
from ui.element.utils.animation.animation import Animation
from ui.element.utils.animation.sequence import Sequence

from .moving_card import Moving_Card

class Points(Position, Text):
    def __init__(
        self, 
        card,
        player, 
        points,
        target=None
    ):
    
        Position.__init__(
            self,
            layer=1,
            enabled=False
        )

        Text.__init__(
            self,
            text=str(points) if points < 0 else f'+{points}',
            text_size=30,
            text_color=player.color,
            text_outline_color=(0, 0, 0),
            text_outline_width=2
        )

        self.player = player
        self.points = points
        self.card = card
        self.rect.center = self.card.rect.center

        self.animations = []

    @property
    def center(self):
        return self.rect.center
        
    @center.setter
    def center(self, center):
        self.rect.center = center
        
    def add_animation(self, animations, loop=False):
        for kwargs in animations:
            kwargs['element'] = self
        s = Sequence(
            [Animation(**kwargs) for kwargs in animations], 
            tag='temp',
            loop=loop
        )
        self.animations.append(s)
        return s
        
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
        self.add_child(Points(card, self.player, points, target=target))
        
    def start(self):
        self.set_animation()
        for c in self.children:
            c.start()
   
    def end(self):
        if self.parent:
            self.parent.merge(self)
        
    def update(self):
        super().update()

        for a in self.animations.copy():
            a.step()
            if a.finished:
                self.animations.remove(a)
                if not self.animations:
                    self.end()
                    return True

    def draw(self, surf):
        if not self.points:
            self.child_draw(surf)
        else:
            self.child_draw(surf)
            self.draw_text(surf)
            
    def set_animation(self):
        if self.parent:
            delay = 10
            end = self.parent.rect.center
        else:
            delay = 60
            end = self.player.spot.points_spot.rect.center

        self.add_animation([{
            'attr': 'center',
            'end': end,
            'delay': delay,
            'frames': 10,
            'method': 'ease_in_quad'
        }])
        