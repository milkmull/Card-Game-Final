import random

from ui.element.elements import Textbox

class Player:
    def __init__(self, client, name, pid, color, spot):
        self.client = client
        self.name = name
        self.pid = pid
        self.color = color
        self.spot = spot
        self.spot.set_player(self)

        self.score = 0

        self.decks = {
            'play': [],
            'selection': []
        }
        
    def __repr__(self):
        return self.name
        
    def __str__(self):
        return self.name
        
    @property
    def is_main(self):
        return self.pid == self.client.pid

    def update_score(self, score):
        self.score = score
        self.spot.points_spot.set_score(self.score)
        
    def new_deck(self, deck_name, cards):
        deck = self.decks.get(deck_name)
        if deck is None:
            return
            
        new_deck = []
        
        for name, cid in cards:
            for c in deck:
                if c.cid == cid:
                    break
            else:
                c = self.client.get_card(name, cid, add=False)
            new_deck.append(c)
        
        self.decks[deck_name] = new_deck
        
        if self.is_main:
            
            match deck_name:
                case 'play':
                    self.client.sequence.join_elements(new_deck)
                case 'selection':
                    self.client.selection.join_elements(new_deck)
            
    def start_turn(self):
        self.spot.start_turn()

    def end_turn(self):
        self.spot.end_turn()

    def update(self):
        pass
            