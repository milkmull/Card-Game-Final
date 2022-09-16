import random

from . import card_base

# play

class Fish(card_base.Card):
    sid = 0
    name = 'fish'
    type = 'play'
    weight = 1
    tags = ('water', 'animal')
    
    def play(self):
        for c in self.spot.get_group('row'):
            if c.name == self.name:
                self.player.gain(3, self)
                    
        for c in self.spot.get_group('column'):
            if c.name == self.name:
                self.player.gain(3, self)
                
class Michael(card_base.Card):
    sid = 1
    name = 'michael'
    type = 'play'
    weight = 1
    tags = ('human',)
    
    def play(self):
        for c in self.spot.get_group('border'):
            if c.player != self.player:
                self.player.steal(2, self, c.player)

class Sunflower(card_base.Card):
    sid = 2
    name = 'sunflower'
    type = 'play'
    weight = 1
    tags = ('garden', 'plant')
    
    def update(self):
        for c in self.spot.get_group('border'):
            if self.check_new(c):
                if c.name == self.name:
                    self.player.gain(5, self)
                else:
                    self.player.gain(2, self)
                    
class Cow(card_base.Card):
    sid = 3
    name = 'cow'
    type = 'play'
    weight = 1
    tags = ('farm', 'animal')
    
    def update(self):
        c = self.spot.get_at('left')
        if c:
            if 'plant' in c.tags:
                pos = c.pos
                self.game.grid.clear_at(pos)
                self.move_to(pos)
                self.player.gain(5, self)
                
class NegativeZone():
    name = 'negative zone'
    type = 'play'
    weight = 0
    tags = ('boost',)
    def update(self):
        for c in self.get_around():
            if self.check_new(c):
                c.multiplier *= -1
            
                
    
                
                