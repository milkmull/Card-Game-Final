from . import card_base

class Player_0(card_base.Card):
    name = 'player 0'
    type = 'item'
    weight = 1
    tags = ['player']
    
    def start(self, player):
        self.reset()
        seq0 = player.draw_cards('treasure', num=1)
