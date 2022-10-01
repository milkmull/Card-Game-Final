import random

from . import card_base

# play

class Fish(card_base.Card):
    sid = 0
    name = 'fish'
    type = 'play'
    weight = 1
    tags = ('water', 'animal')
    
    def special(self):
        cards = self.spot.get_card_group('border')
        if len(cards) == 4:
            if all({c.name == self.name for c in cards}):
                for c in cards:
                    c.spot.kill_card(self)
                    self.player.gain(3, self, extra=c)

    def update(self):
        for c in self.spot.get_card_group('row'):
            if self.register(c):
                if c.name == self.name:
                    self.player.gain(1, self, extra=c)
                    
        for c in self.spot.get_card_group('column'):
            if self.register(c):
                if c.name == self.name:
                    self.player.gain(1, self, extra=c)
                    
        self.special()
                
class Michael(card_base.Card):
    sid = 1
    name = 'michael'
    type = 'play'
    weight = 0.5
    tags = ('human',)
    
    def play(self):
        for c in self.spot.get_card_group('border'):
            if c.player != self.player:
                self.player.steal(2, self, c.player, extra=c)

class Sunflower(card_base.Card):
    sid = 2
    name = 'sunflower'
    type = 'play'
    weight = 0.75
    tags = ('garden', 'plant')
    
    def update(self):
        for c in self.spot.get_card_group('border'):
            if self.register(c):
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
    
    def play(self):
        cards = [c for c in self.spot.get_card_group('x') if 'plant' in c.tags]
        self.player.start_select(self, cards)
        
    def select(self, card):
        self.direction = self.spot.get_direction(card.spot)
    
    def remove(self):
        c = self.spot.get_card_at(self.direction)
        if c:
            if 'plant' in c.tags:
                c.spot.kill_card(self)
                self.player.gain(5, self)
                self.can_move = True
    
    def move(self):
        s = self.spot.get_spot_at(self.direction)
        if s:
            if not s.card:
                self.move_to(s)
        self.can_move = False
                
class Wind_Gust(card_base.Card):
    sid = 4
    name = 'wind gust'
    type = 'play'
    weight = 0.5
    tags = ('sky',)
    
    def play(self):
        self.spot.grid.condense_row(self.spot, 1)
        self.spot.grid.condense_row(self.spot, -1)
        
class Dom(card_base.Card):
    sid = 5
    name = 'dom'
    type = 'play'
    weight = 1
    tags = ('human',)
    
    def update(self):
        for c in self.spot.get_card_group('corner'):
            if self.register(c):
                if 'animal' in c.tags:
                    self.player.gain(3 if c.player is self.player else 1, self, extra=c)
            
class Robber(card_base.Card):
    sid = 6
    name = 'robber'
    type = 'play'
    weight = 0.5
    tags = ('human',)
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group('border'))
        
    def select(self, card):
        card.spot.kill_card(self)
        self.player.add_card('private', card.copy())
        
class Ghost(card_base.Card):
    sid = 7
    name = 'ghost'
    type = 'play'
    weight = 0.5
    tags = ('monster',)
    
    def play(self):
        for c in self.spot.get_card_group('border'):
            if self.register(c):
                if 'human' in c.tags and c.player is not self.player:
                    self.player.gain_ownership(c)
                    self.player.gain(1, self, extra=c)
                    
# make special vine goes from bottom to top condition
    
class Vines(card_base.Card):
    sid = 8
    name = 'vines'
    type = 'play'
    weight = 0.5
    tags = ('garden', 'plant')

    def move(self):
        s = self.spot.get_spot_at('top')
        if s:
            if not s.card:
                c = self.player_copy()
                c.can_move = True
                s.set_card(c, parent=self)
                
    def update(self):
        self.can_move = True
                
class Fox(card_base.Card):
    sid = 9
    name = 'fox'
    type = 'play'
    weight = 1
    tags = ('city', 'animal')
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group('border'))
        
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
        
    def kill(self, card):
        self.player.gain(15 if card.player is self.player else -5, self)
        
class Dragon(card_base.Card):
    sid = 11
    name = 'dragon'
    type = 'play'
    weight = 0.25
    tags = ('sky', 'monster')
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group('all'))
        
    def select(self, card):
        card.spot.kill_card(self)
        if 'monster' in card.tags:
            self.player.gain(3, self)
            
class BigSandWorm(card_base.Card):
    sid = 12
    name = 'big sand worm'
    type = 'play'
    weight = 0.5
    tags = ('desert', 'animal', 'bug')
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group('border'))
        
    def select(self, card):
        self.direction = self.spot.get_direction(card.spot)
        self.move()
        
    def move(self):
        c = self.spot.get_card_at(self.direction)
        if c:
            self.swap_with(c)
            
    def update(self):
        self.can_move = True
            
class NegativeZone(card_base.Card):
    sid = 13
    name = 'negative zone'
    type = 'play'
    weight = 0.125
    tags = ('multiplier',)
    
    def play(self):
        self.game.add_multiplier(self)
        
    def multiply(self, card):
        return -1
        
    def kill(self, card):
        self.game.remove_multiplier(self)
            
class GamblingMan(card_base.Card):
    sid = 14
    name = 'gambling man'
    type = 'play'
    weight = 1
    tags = ('city', 'human')

    def play(self):
        self.player.gain(4, self)
        
    def update(self):
        for c in self.spot.get_card_group('border'):
            if self.register(c):
                if 'human' in c.tags:
                    self.player.gain(-2, self, extra=c)
            
class Parade(card_base.Card):
    sid = 15
    name = 'parade'
    type = 'play'
    weight = 0.25
    tags = ('event',)

    def play(self):
        for c in self.spot.get_direction_chunk('left', check=lambda c: 'human' in c.tags):
            self.player.gain(1, self, extra=c)
        for c in self.spot.get_direction_chunk('right', check=lambda c: 'human' in c.tags):
            self.player.gain(1, self, extra=c)
            
class FishingPole(card_base.Card):
    sid = 16
    name = 'fishing pole'
    type = 'play'
    weight = 0.5
    tags = ('item',)

    def play(self):
        self.player.start_select(self, self.spot.get_all_name('fish'))
        
    def select(self, card):
        self.player.gain_ownership(card)
        self.swap_with(card)
                
                