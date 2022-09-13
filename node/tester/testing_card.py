from game.card import card_base

class New_Card(card_base.Card):
    name = 'New Card'
    type = 'play'
    weight = 1
    tags = []
    
    def start(self, player):
        self.reset()
