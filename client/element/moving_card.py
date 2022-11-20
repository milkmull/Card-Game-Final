import pygame as pg

from ui.element.base.base import Base_Element
from ui.element.utils.animation.animation import Animation
from ui.element.utils.animation.sequence import Sequence

class Moving_Card(Base_Element):
    def __init__(self, pack, card, type, **kwargs):   
        self.pack = pack
        
        self.card = card
        self.card.turn_off()
        self.base_image = self.card.get_image(mini=False)
        self.rect = self.card.rect.copy()
        self.target_rect = self.rect.copy()

        self.child = None
        self.type = type
        
        super().__init__(
            enabled=False,
            layer=1
        )

        self.animations = []
        self.set_animations(**kwargs)
        
    def __str__(self):
        return self.card.name
        
    def __repr__(self):
        return self.card.name
    
    @property
    def size(self):
        return self.rect.size
        
    @size.setter
    def size(self, size):
        c = self.rect.center
        self.rect.size = size
        self.rect.center = c
                
    @property
    def center(self):
        return self.rect.center
        
    @center.setter
    def center(self, center):
        self.rect.center = center
        
    @property
    def x(self):
        return self.rect.x
        
    @x.setter
    def x(self, x):
        self.rect.x = x
        
    @property
    def y(self):
        return self.rect.y
        
    @y.setter
    def y(self, y):
        self.rect.y = y
        
    @property
    def w(self):
        return self.rect.width
        
    @w.setter
    def w(self, w):
        c = self.rect.center
        self.rect.width = w
        self.rect.center = c

    @property
    def phase(self):
        match self.type:
            case 'play':
                return 0
            case 'kill':
                return 1
            case _:
                return 2
                
    def set_child(self, child):
        self.child = child
        self.child.visible = False
        
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
        
    def end(self):
        if self.child:
            self.child.visible = True
        else:
            self.card.turn_on()
            
            if self.type == 'kill':
                self.pack.manager.client.get_kill_particles(self.card.rect, self.card.player.color)
            
    def update(self):
        for a in self.animations.copy():
            a.step()
            if a.finished:
                self.animations.remove(a)
                if not self.animations:
                    self.end()
                    return True

    def draw(self, surf):
        if self.rect.size == self.card.rect.size:
            surf.blit(self.card.get_image(), self.rect)
            if self.card.player:
                pg.draw.rect(surf, self.card.player.color, self.rect, width=4)
        else:
            surf.blit(pg.transform.smoothscale(self.base_image, self.rect.size), self.rect)
        
    def set_animations(self, start=None, **kwargs):
        if start:
            self.rect.center = start
        else:
            self.rect.center = self.card.rect.center
            
        match self.type:

            case 'play':

                self.add_animation([{
                    'attr': 'center',
                    'start': start,
                    'end': self.card.rect.center,
                    'frames': 10,
                    'method': 'ease_out_expo'
                }])

                self.add_animation([
                    {
                        'attr': 'size',
                        'start': (0, 0),
                        'end': self.card.rect.inflate(self.card.rect.width * 3, self.card.rect.height * 3).size,
                        'frames': 10,
                        'method': 'ease_out_expo'
                    },
                    {
                        'attr': 'size',
                        'end': self.card.rect.size,
                        'frames': 10,
                        'delay': 5,
                        'method': 'ease_in_expo'
                    }
                ])
                
            case 'shift':
                
                self.add_animation([{
                    'attr': 'center',
                    'start': start,
                    'end': self.card.rect.center,
                    'frames': 10,
                    'method': 'ease_in_out_expo'
                }])
                
            case 'kill':
                
                self.add_animation([{
                    'attr': 'x',
                    'end': self.card.rect.x - 5,
                    'frames': 20,
                    'method': 'random_shake'
                }])
                
                self.add_animation([{
                    'attr': 'y',
                    'end': self.card.rect.y - 5,
                    'frames': 20,
                    'method': 'random_shake'
                }])
                
            case 'own' | 'tf':
                
                self.add_animation([
                    {
                        'attr': 'w',
                        'end': 0,
                        'frames': 10,
                        'method': 'ease_in_expo'
                    },
                    {
                        'attr': 'w',
                        'end': self.card.rect.width,
                        'frames': 10,
                        'method': 'ease_out_expo'
                    }
                ])
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        