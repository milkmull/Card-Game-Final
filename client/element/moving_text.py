import pygame as pg

from ui.element.base.text import Text
from ui.element.base.position import Position
from ui.element.utils.animation.animation import Animation
from ui.element.utils.animation.sequence import Sequence

from .moving_card import Moving_Card

class Moving_Text(Position, Text):
    def __init__(
        self, 
        **kwargs
    ):
    
        Position.__init__(
            self,
            layer=1,
            enabled=False
        )

        Text.__init__(
            self,
            **kwargs
        )

        self.animations = []

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
        
    def start(self):
        self.set_animation()
        
    def update(self):
        super().update()

        for a in self.animations.copy():
            a.step()
            if a.finished:
                self.animations.remove(a)
                if not self.animations:
                    return True

    def draw(self, surf):
        self.draw_text(surf)
            
    def set_animation(self):
        w, h = pg.display.get_window_size()
        self.rect.left = w
        end = w - (20 + self.rect.width)
        
        self.add_animation([
            {
                'attr': 'x',
                'end': end,
                'frames': 10,
                'method': 'ease_out_quad'
            },
            {
                'attr': '_id',
                'end': self.id,
                'delay': 60
            }
        ])
        
    def shift(self, y):
        self.add_animation([
            {
                'attr': 'y',
                'end': self.rect.y - y,
                'frames': 5,
                'method': 'ease_out_expo'
            },
            {
                'attr': '_id',
                'end': self.id,
                'delay': 40
            }
        ])
        