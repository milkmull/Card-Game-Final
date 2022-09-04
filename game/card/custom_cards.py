from . import card_base

class Fish2(card_base.Card):
    name = '---fish2'
    type = 'landscape'
    weight = 1
    tags = []
    
    def ongoing(self, player, log):
        pass
    
    def start_ongoing(self, player):
        pass

class Hello_World(card_base.Card):
    name = 'Hello World'
    type = 'play'
    weight = 4
    tags = ['sky']
    
    def start(self, player):
        self.reset()
        for p1 in self.get_players():
            p1.gain(self, 5)
