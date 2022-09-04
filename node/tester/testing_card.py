from game.card import card_base

class Hello_World(card_base.Card):
    name = 'Hello World'
    type = 'play'
    weight = 4
    tags = ['sky']
    
    def start(self, player):
        self.reset()
        for p1 in self.get_players():
            p1.gain(self, 5)
