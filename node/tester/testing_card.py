from game.card import card_base

class New_Card(card_base.Card):
    name = 'New Card'
    weight = 1
    tags = []
    
    def update(self):
        for c3 in self.spot.cards_from_vector((-1, 0), steps=-1, da=360, check=lambda c: True, stop_on_empty=False, stop_on_fail=False, reverse=True):
            c5 = self.game.grid.slide(c3, (-1, 0), max_dist=99)
        for c0 in self.spot.cards_from_vector((1, 0), steps=-1, da=360, check=lambda c: True, stop_on_empty=False, stop_on_fail=False, reverse=True):
            c6 = self.game.grid.slide(c0, (1, 0), max_dist=99)
