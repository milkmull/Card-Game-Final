from game.card import card_base

class Player_0(card_base.Card):
    name = 'player 0'
    type = 'user'
    weight = 1
    tags = ['player']
    
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
    
    def ongoing(self, player, log):
        for i76 in range((player.played.index(self) - 1), len(player.string_to_deck('played'))):
            added71, c71 = self.check_index(player, i76)
            if added71:
                pass
    
    def start(self, player):
        self.reset()
        self.start_ongoing(player)
