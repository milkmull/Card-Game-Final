from . import card_base

class This_Is_My_Demo_Card(card_base.Card):
    name = 'This is my demo card'
    type = 'play'
    weight = 4
    tags = ['human']
    
    def start(self, player):
        self.reset()
        for p2 in self.get_players():
            p2.gain(self, 10)
