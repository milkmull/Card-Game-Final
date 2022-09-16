import random

from . import exceptions
     
class Player_Base:
    type = 'player'
    tags = []
            
    def __init__(self, game, pid):
        self.game = game
        self.pid = pid

        self.score = 0
        self.done_turn = True

        self.decks = {
            'play': [],
            'extra': [],
            'treasure': []
        }

        self.log = []
        
    @property
    def name(self):
        return f'player {self.pid}'
        
    @property
    def id(self):
        return self.pid
        
    def __eq__(self, other):
        return getattr(other, 'id', None) == self.pid
            
    def __hash__(self):
        return self.pid
       
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def is_auto(self):
        return True
        
# starting stuff                

    def reset(self):
        self.done_turn = True
        
        for deck in self.decks.values():
            deck.clear()

        self.log.clear()
        
        self.update_score(0)

    def start(self):
        self.update_score(self.game.get_setting('ss'))
        self.draw_cards('play', self.game.get_setting('cards'))
        
    def copy(self, game):
        p = Player_Base(game, self.pid)
        p.score = self.score
        p.done_turn = self.done_turn
        
        for type, deck in self.decks.items():
            p.decks[type] = [c.copy(game=game) for c in deck]

        return p

# card stuff
                
    def new_deck(self, type, cards):
        self.decks[type] = cards
        
    def remove_card(self, c, type):
        deck = self.decks[type]
        found = False
        new_deck = []
        for o in deck:
            if o == c:
                found = True
            else:
                new_deck.append(o)
        if found:
            self.new_deck(type, new_deck)
            
        return found
        
    def draw_cards(self, type, num):
        cards = self.game.draw_cards(type, num=num)
        new_deck = self.decks[type] + cards
        self.new_deck(type, cards)
 
    def check_extra(self, spot):
        pass
        
    def play_card(self, card, spot):
        if not self.remove_card(card, 'play'):
            return
           
        self.check_extra(spot)
        
        self.add_log({
            't': 'play',
            'c': card,
            'p': spot.pos
        })
        
        card.player = self
        spot.set_card(card)
        card.play()

        self.done_turn = True

# log stuff

    def add_log(self, log):
        log['u'] = self.pid
        self.log.append(log)
        self.game.add_player_log(log)
        return log

# turn stuff

    def start_turn(self):
        self.done_turn = False  
        
    @property
    def done_game(self):
        return not self.decks['play']
        
    def select_card(self):
        if not self.decks['play']:
            print(self.log, self.game.done)
            
        card = random.choice(self.decks['play'])
        
        self.add_log({
            't': 'sc',
            'c': card
        })
        
        return card
        
    def select_spot(self):
        spots = [spot for spot in self.game.grid.spots if spot.is_open]
        spot = random.choice(spots) 

        self.add_log({
            't': 'ss',
            's': spot.pos
        })
        
        return spot
        
    def random_turn(self):
        card = self.select_card()
        spot = self.select_spot()
        self.play_card(card, spot)

    def update(self):
        if not self.done_turn:
            self.random_turn()

# point stuff

    def update_score(self, score):
        self.score = score
        
    def rob(self, points):
        if points > self.score:
            points = self.score
        if points:
            self.update_score(self.score - points)
        return points

    def gain(self, gp, card):
        if not gp:
            return

        self.update_score(self.score + gp)

        self.add_log({
            't': 'gp',
            'gp': gp,
            'c': card
        })
        
    def steal(self, sp, card, target):
        sp = target.rob(sp)
        if not sp:
            return

        self.update_score(self.score + sp)
        
        self.add_log({
            't': 'sp',
            'sp': sp,
            'c': card,
            'target': target
        })



