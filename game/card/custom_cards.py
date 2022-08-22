from . import card_base

class Ducklinquent(card_base.Card):
    name = 'ducklinquent'
    type = 'treasure'
    weight = 3
    tags = ['monster', 'biome']
    
    def start(self, player):
        self.reset()
        player.add_request(self, 'flip')
    
    def flip(self, player, coin):
        self.t_coin = coin

class Duck_Man_Gang(card_base.Card):
    name = 'duck man gang'
    type = 'play'
    weight = 4
    tags = ['farm', 'animal', 'city']
    
    def start(self, player):
        self.reset()
        for i3 in range(0, 5):
            player.add_card(self.game.get_card('ducklinquent'), deck_string='unplayed', i=-1)

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
