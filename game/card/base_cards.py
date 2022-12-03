import random

from . import card_base

# play

class Fish(card_base.Card):
    sid = 0
    name = 'fish'
    type = 'play'
    weight = 1.25
    tags = ('water', 'animal')

    def update(self):
        for c in self.spot.cards_from_vector((1, 0), steps=-1, da=90, check=lambda c: c.name == 'fish'):
            if self.register(c):
                self.player.gain(1, self, extra=c)
                
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
        if c and 'plant' in c.tags:
            c.kill(self)
            self.player.gain(5, self)
            self.move_in(self.direction)
                
class Wind_Gust(card_base.Card):
    sid = 4
    name = 'wind gust'
    type = 'play'
    weight = 0.5
    tags = ('sky',)
    
    def play(self):
        for c in self.spot.cards_from_vector((-1, 0), steps=-1, reverse=True):
            self.spot.grid.slide(c, (-1, 0))
        for c in self.spot.cards_from_vector((1, 0), steps=-1, reverse=True):
            self.spot.grid.slide(c, (1, 0))
        
class Dom(card_base.Card):
    sid = 5
    name = 'dom'
    type = 'play'
    weight = 1
    tags = ('human',)
    
    def update(self):
        for c in self.spot.get_card_group('corner'):
            if self.register(c) and 'animal' in c.tags:
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
        card.kill(self)
        if 'item' in card.tags:
            self.player.gain(3, self)
        self.player.add_card('private', card.copy())
        
class Ghost(card_base.Card):
    sid = 7
    name = 'ghost'
    type = 'play'
    weight = 0.5
    tags = ('monster',)
    
    def play(self):
        for c in self.spot.get_card_group('border'):
            if self.register(c) and 'human' in c.tags and c.player is not self.player:
                c.swap_player(self.player)
                self.player.gain(1, self, extra=c)

class Vines(card_base.Card):
    sid = 8
    name = 'vines'
    type = 'play'
    weight = 0.5
    tags = ('garden', 'plant')
    
    def play(self):
        self.skip_move = True

    def move(self):
        s = self.spot.get_spot_at('top')
        if s and s.is_open:
            c = self.player_copy()
            s.set_card(c, parent=self)
            self.player.gain(1, self)
                
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
    
class Cactus(card_base.Card):
    sid = 10
    name = 'cactus'
    type = 'play'
    weight = 0.5
    tags = ('city', 'plant')

    def kill(self, card):
        card.player.gain(-5, self, extra=card)
        super().kill(card)
        
class Dragon(card_base.Card):
    sid = 11
    name = 'dragon'
    type = 'play'
    weight = 0.25
    tags = ('sky', 'monster')
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group('all'))
        
    def select(self, card):
        card.kill(self)
        if 'monster' in card.tags:
            self.player.gain(3, self)
            
class Big_Sand_Worm(card_base.Card):
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
        self.skip_move = True
        
    def move(self):
        c = self.spot.get_card_at(self.direction)
        if c:
            self.swap_with(c)
            
class Negative_Zone(card_base.Card):
    sid = 13
    name = 'negative zone'
    type = 'play'
    weight = 0.125
    tags = ('multiplier',)
    
    def play(self):
        self.game.add_multiplier(self)
        
    def multiply(self, card):
        return -1
            
class Gambling_Man(card_base.Card):
    sid = 14
    name = 'gambling man'
    type = 'play'
    weight = 1
    tags = ('city', 'human')

    def play(self):
        if self.spot.grid.any_open():
            self.player.start_select(self, list(self.player.decks['private'].values()))
            
    def select(self, card):
        spots = list(self.spot.grid.get_open_spots().values())
        if spots:
            spot = self.player.random_choice(spots, self)
            self.player.play_card('private', card.cid, spot)
            
            if spot.is_corner:
                self.player.gain(4, self)
            else:
                self.player.gain(-4, self)
            
class Parade(card_base.Card):
    sid = 15
    name = 'parade'
    type = 'play'
    weight = 0.25
    tags = ('event',)

    def play(self):
        count = 1
        for c in self.spot.cards_from_vector((1, 0), steps=-1, da=180, check=lambda c: 'human' in c.tags, stop_on_fail=True):
            self.player.gain(count, self, extra=c)
            count *= 2
            
class Fishing_Pole(card_base.Card):
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
                
class Pelican(card_base.Card):
    sid = 17
    name = 'pelican'
    type = 'play'
    weight = 0.15
    tags = ('sky', 'animal')
    
    def play(self):
        c = self.spot.get_card_at('bottom')
        if c and c.name == 'fish':
            s = self.spot.get_spot_at('top')
            if not s or (s and not s.is_open):
                c.kill(self)
                self.player.gain(5, self, extra=c)
        self.skip_move = True

    def move(self):
        if not self.move_in('down'):
            c = self.spot.get_card_at('bottom')
            if c and c.name == 'fish':
                if self.move_in('up'):
                    c.move_in('up')
                s = self.spot.get_spot_at('top')
                if not s or (s and not s.is_open):
                    c.kill(self)
                    self.player.gain(5, self, extra=c)
        
class Treasure_Chest(card_base.Card):
    sid = 18
    name = 'treasure chest'
    type = 'play'
    weight = 0.25
    tags = ('item',)
    
    def update(self):
        for c in self.spot.cards_from_vector((1, 0), da=90):
            if self.register(c):
                c.player.gain(3, self, extra=c)
    
class Zombie(card_base.Card):
    sid = 19
    name = 'zombie'
    type = 'play'
    weight = 0.25
    tags = ('monster',)
    
    def update(self):
        for c in self.spot.cards_from_vector((1, 0), da=90, check=lambda c: 'human' in c.tags):
            if self.register(c):
                self.game.transform(c, self.name)
                self.player.gain(1, self, extra=c)
                
class Future_Orb(card_base.Card):
    sid = 20
    name = 'future orb'
    type = 'play'
    weight = 0.5
    tags = ('item',)
    
    def play(self):
        self.start_wait('nt')
    
    def run_wait(self, player, card):
        if player == self.player:
            self.kill(self)
    
class Ninja(card_base.Card):
    sid = 21
    name = 'ninja'
    type = 'play'
    weight = 0.5
    tags = ('human',)
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group('all'))
        
    def select(self, card):
        self.swap_with(card)        