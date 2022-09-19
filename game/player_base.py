import random

from . import exceptions
     
class Player_Base:
    type = 'player'
    tags = []
            
    def __init__(self, game, pid):
        self.game = game
        self.pid = pid

        self.score = 0
        self.played = True

        self.decks = {
            'play': [],
            'selection': []
        }
        self.active_card = None

        self.log = []
        
    @property
    def name(self):
        return f'player {self.pid}'
        
    @property
    def id(self):
        return self.pid
        
    @property
    def is_auto(self):
        return True
        
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
        self.played = True
        
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
        p.played = self.played

        return p
        
    def copy_cards(self, game):
        p = game.get_player(self.pid)
        
        p.decks['play'] = [c.game_copy(game) for c in self.decks['play']]
        
        selection = p.decks['selection']
        for c in self.decks['selection']:
            if not c.spot:
                selection.append(c.game_copy(game))
            else:
                spot = game.grid.get_spot(c.spot.pos)
                card = spot.card
                if card:
                    selection.append(card)
                else:
                    raise Exception

        if self.active_card:
            spot = game.grid.get_spot(self.active_card.spot.pos)
            active_card = spot.card
            if active_card:
                p.active_card = active_card
            else:
                raise Exception

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

        
    def play_card(self, card, spot):
        if not self.remove_card(card, 'play'):
            return

        card.set_owner(self)
        spot.set_card(card)
        card.play()
        
        self.played = True
        
        self.add_log({
            't': 'play',
            'c': card,
            'p': spot.pos
        })
        
    def add_card(self, card):
        self.new_deck('play', self.decks['play'] + [card])
        
    def gain_ownership(self, card):
        card.set_owner(self)
        
        self.add_log({
            't': 'own',
            'c': card,
            'p': self
        })
        
# selection stuff

    def start_select(self, card, selection):
        if selection:
            if len(selection) == 1:
                card.select(selection[0])
            else:
                self.new_deck('selection', selection)
                self.active_card = card
            
    def end_select(self):
        self.new_deck('selection', [])
        self.active_card = None
        
    def select_card(self, card):
        self.active_card.select(card)
        self.end_select()
        
        self.add_log({
            't': 's',
            'c': card,
            'exc': self.pid
        })

# log stuff

    def add_log(self, log):
        log['u'] = self.pid
        self.log.append(log)
        self.game.add_player_log(log)
        return log

# turn stuff
    
    @property
    def done_turn(self):
        return self.played and not self.active_card

    def start_turn(self):
        self.played = False  
        
    @property
    def done_game(self):
        return not self.decks['play'] and not self.active_card
        
    def _select_card(self, deck):
        card = random.choice(self.decks[deck])
        return card
        
    def select_spot(self):
        spots = [spot for spot in self.game.grid.spots if spot.is_open]
        spot = random.choice(spots) 
        return spot
        
    def random_turn(self):
        card = self._select_card('play')
        spot = self.select_spot()
        self.play_card(card, spot)
        
    def random_selection(self):
        card = self._select_card('selection')
        self.select_card(card)

    def update(self):
        if not self.played:
            self.random_turn()
                
        elif self.active_card:
            self.random_selection()

# point stuff

    def update_score(self, score):
        self.score = score
        
    def rob(self, points):
        if points > self.score:
            points = self.score
        if points:
            self.update_score(self.score - points)
        return points

    def gain(self, gp, card, extra=None):
        gp *= card.multiplier
        if not gp:
            return

        self.update_score(self.score + gp)

        self.add_log({
            't': 'gp',
            'points': gp,
            'c': card,
            'e': extra
        })
        
    def steal(self, sp, card, target, extra=None):
        sp *= card.multiplier
        sp = target.rob(sp)
        if not sp:
            return

        self.update_score(self.score + sp)
        
        self.add_log({
            't': 'sp',
            'points': sp,
            'c': card,
            'target': target,
            'e': extra
        })



