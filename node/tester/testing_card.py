from game.card import card_base

class Cow2(card_base.Card):
    name = 'Cow2'
    weight = 1
    tags = ['farm', 'animal']
    
    def start(self, player):
        self.reset()
