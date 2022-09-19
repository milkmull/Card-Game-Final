import random

from . import card_base

# play

class Fish(card_base.Card):
    sid = 0
    name = 'fish'
    type = 'play'
    weight = 2
    tags = ('water', 'animal')
    
    def play(self):
        for c in self.spot.get_group('row'):
            if c.name == self.name:
                self.player.gain(3, self, extra=c)
                    
        for c in self.spot.get_group('column'):
            if c.name == self.name:
                self.player.gain(3, self, extra=c)
                
class Michael(card_base.Card):
    sid = 1
    name = 'michael'
    type = 'play'
    weight = 1
    tags = ('human',)
    
    def play(self):
        for c in self.spot.get_group('border'):
            if c.player != self.player:
                self.player.steal(2, self, c.player, extra=c)

class Sunflower(card_base.Card):
    sid = 2
    name = 'sunflower'
    type = 'play'
    weight = 0.75
    tags = ('garden', 'plant')
    
    def update(self):
        for c in self.spot.get_group('border'):
            if self.check_new(c):
                if c.name == self.name:
                    self.player.gain(5, self, extra=c)
                else:
                    self.player.gain(2, self, extra=c)
                    
class Cow(card_base.Card):
    sid = 3
    name = 'cow'
    type = 'play'
    weight = 0.5
    tags = ('farm', 'animal')
    
    def remove(self):
        c = self.spot.get_at('left')
        if c:
            if 'plant' in c.tags:
                self.game.grid.clear_at(c.pos, kill=True)
                self.player.gain(5, self)
                self.can_move = True
    
    def move(self):
        s = self.spot.get_at('left', card=False)
        if s:
            if not s.card:
                self.move_to(s.pos)
        self.can_move = False
                
class Wind_Gust(card_base.Card):
    sid = 4
    name = 'wind gust'
    type = 'play'
    weight = 0.5
    tags = ('sky',)
    
    def play(self):
        self.spot.grid.condense_row(self.spot.pos, 1)
        self.spot.grid.condense_row(self.spot.pos, -1)
        
class Dom(card_base.Card):
    sid = 5
    name = 'dom'
    type = 'play'
    weight = 1
    tags = ('human',)
    
    def update(self):
        for c in self.spot.get_group('corner'):
            if self.check_new(c) and 'animal' in c.tags:
                self.player.gain(3 if c.player is self.player else 1, self, extra=c)
            
class Robber(card_base.Card):
    sid = 6
    name = 'robber'
    type = 'play'
    weight = 0.5
    tags = ('human',)
    
    def play(self):
        self.player.start_select(self, self.spot.get_group('border'))
        
    def select(self, card):
        card.spot.clear_card()
        self.player.add_card(card.copy())
        
class Ghost(card_base.Card):
    sid = 7
    name = 'ghost'
    type = 'play'
    weight = 0.5
    tags = ('monster',)
    
    def play(self):
        for c in self.spot.get_group('border'):
            if self.check_new(c) and 'human' in c.tags and c.player is not self.player:
                self.player.gain_ownership(c)
                self.player.gain(1, self, extra=c)
    
class Vines(card_base.Card):
    sid = 8
    name = 'vines'
    type = 'play'
    weight = 0.5
    tags = ('garden', 'plant')
    
    def move(self):
        s = self.spot.get_at('top', card=False)
        if s:
            if not s.card:
                s.set_card(self.player_copy())
                
    def update(self):
        self.can_move = True
                
class Fox(card_base.Card):
    sid = 9
    name = 'fox'
    type = 'play'
    weight = 1
    tags = ('city', 'animal')
    
    def play(self):
        self.player.start_select(self, self.spot.get_group('border'))
        
    def select(self, card):
        self.swap_with(card)
    
class OfficeFern(card_base.Card):
    sid = 10
    name = 'office fern'
    type = 'play'
    weight = 0.5
    tags = ('city', 'plant')
    
    def play(self):
        self.player.gain(-5, self)
        
    def kill(self):
        self.player.gain(15, self)
        
class Dragon(card_base.Card):
    sid = 11
    name = 'dragon'
    type = 'play'
    weight = 0.25
    tags = ('sky', 'monster')
    
    def play(self):
        self.player.start_select(self, self.spot.get_group('all'))
        
    def select(self, card):
        card.spot.clear_card()
        if 'monster' in card.tags:
            self.player.gain(3, self)
            
class BigSandWorm(card_base.Card):
    sid = 12
    name = 'big sand worm'
    type = 'play'
    weight = 0.5
    tags = ('desert', 'animal', 'bug')
    
    def play(self):
        self.player.start_select(self, self.spot.get_group('border'))
        
    def select(self, card):
        self.direction = self.spot.get_direction(card.spot)
        self.swap_with(card)
        
    def move(self):
        c = self.spot.get_at(self.direction)
        if c:
            self.swap_with(c)
            
    def update(self):
        self.can_move = True
            
            
            
            
            
            
                
                