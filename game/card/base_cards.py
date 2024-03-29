import random

from . import card_base

class Fish(card_base.Card):
    sid = 0
    name = "fish"
    weight = 1.25
    tags = ("water", "animal")

    def update(self):
        for c in self.spot.cards_from_vector((1, 0), steps=-1, da=90, check=lambda c: c.has_name("fish")):
            if self.register(c):
                self.player.gain(1, self, extra=c)
                
class Michael(card_base.Card):
    sid = 1
    name = "michael"
    weight = 0.5
    tags = ("human",)
    
    def play(self):
        for c in self.spot.get_card_group("border"):
            if c.player != self.player:
                self.player.steal(2, self, c.player, extra=c)

class Sunflower(card_base.Card):
    sid = 2
    name = "sunflower"
    weight = 0.75
    tags = ("garden", "plant")
    
    def update(self):
        for c in self.spot.get_card_group("border"):
            if self.register(c):
                if c.has_name(self.name):
                    self.player.gain(5, self, extra=c)
                else:
                    self.player.gain(2, self, extra=c)
                    
class Cow(card_base.Card):
    sid = 3
    name = "cow"
    weight = 0.5
    tags = ("farm", "animal")
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group("x", check=lambda c: c.has_tag("plant")))
        
    def select(self, card):
        self.set_direction(self.spot.get_direction(card.spot))
    
    def remove(self):
        c = self.spot.get_card_at(self.direction, check=lambda c: c.has_tag("plant"))
        if c:
            c.kill(self)
            self.player.gain(3, self)
            self.move_in(self.direction)
                
class Wind_Gust(card_base.Card):
    sid = 4
    name = "wind gust"
    weight = 0.5
    tags = ("sky",)
    
    def play(self):
        for c in self.spot.cards_from_vector((-1, 0), steps=-1, reverse=True):
            self.spot.grid.slide(c, (-1, 0))
        for c in self.spot.cards_from_vector((1, 0), steps=-1, reverse=True):
            self.spot.grid.slide(c, (1, 0))
        
class Dom(card_base.Card):
    sid = 5
    name = "dom"
    weight = 1
    tags = ("human",)
    
    def update(self):
        for c in self.spot.get_card_group("corner", check=lambda c: c.has_tag("animal")):
            if self.register(c):
                self.player.gain(3 if c.player is self.player else 1, self, extra=c)
            
class Robber(card_base.Card):
    sid = 6
    name = "robber"
    weight = 0.5
    tags = ("human",)
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group("border"))
        
    def select(self, card):
        card.kill(self)
        if card.has_tag("item"):
            self.player.gain(3, self)
        self.player.add_card("private", card.copy())
        
class Ghost(card_base.Card):
    sid = 7
    name = "ghost"
    weight = 0.5
    tags = ("monster",)
    
    def play(self):
        for c in self.spot.get_card_group("border", check=lambda c: c.has_tag("human")):
            if self.register(c) and c.change_player(self.player):
                self.player.gain(1, self, extra=c)

class Vines(card_base.Card):
    sid = 8
    name = "vines"
    weight = 0.5
    tags = ("garden", "plant")
    
    def play(self):
        self.skip_move = True

    def move(self):
        if self.copy_to(self.spot.get_spot_at("top")):
            self.player.gain(1, self)
                
class Fox(card_base.Card):
    sid = 9
    name = "fox"
    weight = 1
    tags = ("city", "animal")
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group("border"))
        
    def select(self, card):
        self.swap_with(card)
    
class Cactus(card_base.Card):
    sid = 10
    name = "cactus"
    weight = 0.5
    tags = ("city", "plant")

    def kill(self, card):
        card.player.gain(-5, self, extra=card)
        super().kill(card)
        
class Dragon(card_base.Card):
    sid = 11
    name = "dragon"
    weight = 0.25
    tags = ("sky", "monster")
    
    def play(self):
        self.player.start_select(self, self.spot.get_global_card_group("all"))
        
    def select(self, card):
        card.kill(self)
        if card.has_tag("monster"):
            self.player.gain(3, self)
            
class Big_Sand_Worm(card_base.Card):
    sid = 12
    name = "big sand worm"
    weight = 0.5
    tags = ("desert", "animal", "bug")
    
    def play(self):
        self.player.start_select(self, self.spot.get_card_group("border"))
        
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
    name = "negative zone"
    weight = 0.125
    tags = ("multiplier",)
    
    def spawn(self):
        self.game.add_multiplier(self)
        
    def multiply(self, card):
        return -1
            
class Gambling_Man(card_base.Card):
    sid = 14
    name = "gambling man"
    weight = 0.15
    tags = ("city", "human")

    def play(self):
        if self.spot.grid.any_open():
            self.player.start_select(self, self.player.get_deck("private"))
            
    def select(self, card):
        spots = self.spot.get_global_card_group("open")
        if spots:
            spot = self.player.random_choice(spots, self)
            self.player.play_card("private", card.cid, spot)
            self.player.gain(4 if self.is_corner else -4, self)
            
class Parade(card_base.Card):
    sid = 15
    name = "parade"
    weight = 0.25
    tags = ("event",)

    def play(self):
        count = 1
        for c in self.spot.cards_from_vector((1, 0), steps=-1, da=180, check=lambda c: c.has_tag("human"), stop_on_fail=True):
            self.player.gain(count, self, extra=c)
            count *= 2
            
class Fishing_Pole(card_base.Card):
    sid = 16
    name = "fishing pole"
    weight = 0.5
    tags = ("item",)

    def play(self):
        self.player.start_select(self, self.spot.get_global_card_group("all", check=lambda c: c.has_name("fish")))
        
    def select(self, card):
        card.change_player(self.player)
        self.swap_with(card)
                
class Pelican(card_base.Card):
    sid = 17
    name = "pelican"
    weight = 0.15
    tags = ("sky", "animal")
    
    def play(self):
        c = self.spot.get_card_at("bottom")
        if c and c.has_name("fish"):
            s = self.spot.get_spot_at("top")
            if not s or (s and not s.is_open):
                c.kill(self)
                self.player.gain(5, self, extra=c)
        self.skip_move = True

    def move(self):
        if not self.move_in("down"):
            c = self.spot.get_card_at("bottom")
            if c and c.has_name("fish"):
                if self.move_in("up"):
                    c.move_in("up")
                s = self.spot.get_spot_at("top")
                if not s or (s and not s.is_open):
                    c.kill(self)
                    self.player.gain(5, self, extra=c)
        
class Treasure_Chest(card_base.Card):
    sid = 18
    name = "treasure chest"
    weight = 0.25
    tags = ("item",)
    
    def update(self):
        for c in self.spot.cards_from_vector((1, 0), da=90):
            if self.register(c):
                c.player.gain(3, self, extra=c)
    
class Zombie(card_base.Card):
    sid = 19
    name = "zombie"
    weight = 0.25
    tags = ("monster",)
    
    def update(self):
        for c in self.spot.cards_from_vector((1, 0), da=90, check=lambda c: c.has_tag("human")):
            if self.register(c):
                self.game.transform(c, self.game.get_card(self.name))
                self.player.gain(1, self, extra=c)
                
class Future_Orb(card_base.Card):
    sid = 20
    name = "future orb"
    weight = 0.5
    tags = ("item",)
    
    def play(self):
        self.start_wait("nt")
    
    def run_wait(self, data):
        if data["player"] == self.player:
            self.kill(self)
    
class Ninja(card_base.Card):
    sid = 21
    name = "ninja"
    weight = 0.5
    tags = ("human",)
    
    def play(self):
        self.player.start_select(self, self.spot.get_global_card_group("all"))
        
    def select(self, card):
        self.swap_with(card)        
        
class Mystery_Seed(card_base.Card):
    sid = 22
    name = "mystery seed"
    weight = 0.1
    tags = ("garden", "plant")
    
    def spawn(self):
        self.start_wait("nt")

    def run_wait(self, data):
        if data["player"] == self.player:
            self.game.transform(self, self.game.draw_card_from_tag("plant", self))