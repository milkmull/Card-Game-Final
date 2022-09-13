import random

from ui.element.elements import Textbox

class Player:
    def __init__(self, client, name, pid, color, spot):
        self.client = client
        self.name = name
        self.pid = pid
        self.color = color
        
        self.spot = spot
        spot.set_player(self)

        self.score = 0
        self.gone = False
        
        self.active_card = None
        self.decks = {
            'played': [],
            'unplayed': [],
            'items': [],
            'spells': [],
            'selection': [],
            'equipped': [],
            'active_spells': [],
            'treasure': [],
            'landscapes': []
        }
        
        self.selecting = False
        self.can_cancel = False
        
        self.flipping = False
        self.coin = None

        self.rolling = False
        self.dice = None
        
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

    def set_spot(self, spot):
        self.spot = spot

    def start_turn(self):
        self.gone = False
        
    def update_score(self, score):
        self.score = score
        self.score_card.set_text(f'{self.name}: {self.score}')
        
    def new_deck(self, deck_name, cards):
        deck = self.decks.get(deck_name)
        if deck is None:
            return
            
        new_deck = []
        
        for name, uid in cards:
            for c in deck:
                if c.uid == uid:
                    break
            else:
                c = self.client.get_card(name, uid)
            new_deck.append(c)
        
        self.decks[deck_name] = new_deck
        
        if deck_name == 'played':
            self.spot.join_elements(new_deck)
        elif deck_name == 'landscapes':
            self.spot.ongoing.join_elements(new_deck + self.decks['active_spells'])
        elif deck_name == 'active_spells':
            self.spot.ongoing.join_elements(self.decks['landscapes'] + new_deck)
        
        if self.is_main:
            
            if deck_name == 'unplayed':
                self.client.sequence.join_elements(new_deck)
            elif deck_name == 'selection':
                self.client.selection.join_elements(new_deck)
                
            elif deck_name == 'items':
                self.client.items.join_elements(self.decks['equipped'] + new_deck)
            elif deck_name == 'equipped':
                self.client.items.join_elements(new_deck + self.decks['items'])
                for c in new_deck:
                    c.active = True
            elif deck_name == 'spells':
                self.client.spells.join_elements(new_deck)
            elif deck_name == 'treasure':
                self.client.treasure.join_elements(new_deck)
                
    def new_turn(self):
        self.gone = False
          
    def cancel_active_text(self):
        self.coin = self.dice = None
        self.flipping = self.rolling = self.selecting = False
        self.can_cancel = False
            
    def set_active_card(self, card, wait=None, can_cancel=False):
        self.active_card = card
        
        new_deck = [card] if card else []
        
        self.spot.active_card.join_elements(new_deck)
        if self.is_main:
            if card:
                new_deck = [card.copy()]
            self.client.active_card.join_elements(new_deck)

        self.cancel_active_text()

        if wait == 'flip':
            self.coin = -1 
        elif wait == 'roll':
            self.dice = -1
        elif wait == 'select' or wait == 'cast' or wait == 'vote':
            self.selecting = True
            
        self.can_cancel = can_cancel
            
    def start_flip(self):
        self.flipping = True
        
    def end_flip(self, result):
        self.flipping = False
        self.coin = result
        
    def start_roll(self):
        self.rolling = True
        
    def end_roll(self, result):
        self.rolling = False
        self.dice = result
        
    def play(self, uid, d):
        self.gone = True
        self.client.get_moving_card(self, 'play', self.client.cards[uid][-1 if not d else -2])
        
    def buy(self, uid):
        self.client.get_moving_card(self, 'buy', self.client.cards[uid][-1])
        
    def cast(self, uid):
        self.client.get_moving_card(self, 'cast', self.client.cards[uid][-1])
        
    def discard(self, uid):
        self.client.get_moving_card(self, 'discard', self.client.cards[uid][-1])
 
    def update(self):
        if self.flipping:
            self.coin = random.choice((0, 1))
        elif self.rolling:
            self.dice = random.randrange(0, 6)
            