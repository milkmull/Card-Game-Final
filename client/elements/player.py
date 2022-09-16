import random

from ui.element.elements import Textbox

class Player:
    def __init__(self, client, name, pid, color):
        self.client = client
        self.name = name
        self.pid = pid
        self.color = color

        self.score = 0
        self.done_turn = True

        self.decks = {
            'play': [],
            'extra': [],
            'treasure': []
        }

        self.score_card = Textbox(
            text=f'{self.name}: {self.score}',
            size=(client.scores.rect.width, 25),
            inf_width=False,
            text_color=self.color
        )
        client.scores.add_element(self.score_card)
        
    def __repr__(self):
        return self.name
        
    def __str__(self):
        return self.name
        
    @property
    def is_main(self):
        return self.pid == self.client.pid

    def update_score(self, score):
        self.score = score
        self.score_card.set_text(f'{self.name}: {self.score}')
        
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
                c = self.client.get_card(name, cid)
            new_deck.append(c)
        
        self.decks[deck_name] = new_deck
        
        if self.is_main:
            
            if deck_name == 'play':
                self.client.sequence.join_elements(new_deck)
                
    def new_turn(self):
        self.done_turn = False

    def play(self, cid, d):
        self.done_turn = True

    def update(self):
        pass
            