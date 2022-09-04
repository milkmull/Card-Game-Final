from game.card import card_base

class Fish2(card_base.Card):
    name = '---fish2'
    type = 'play'
    weight = 1
    tags = []
    
    def start(self, player):
        self.reset()
        if player.string_to_deck('r'):
            pass
