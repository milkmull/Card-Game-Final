from game.card import card_base

class Player_0(card_base.Card):
    name = 'player 0'
    type = 'landscape'
    weight = 3
    tags = ['player', 'human']
    
    def start(self, player):
        self.reset()
        for p2 in self.get_players():
            if (not p2.score):
                p2.gain(self, 10)
