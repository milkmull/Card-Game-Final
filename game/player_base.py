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
            'play': {},
            'community': game.community_deck,
            'selection': {}
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
        
# starting stuff                

    def reset(self):
        self.played = True
        self.decks['play'].clear()
        self.decks['selection'].clear()
        self.log.clear()
        self.update_score(0)

    def start(self):
        self.update_score(20)
        self.draw_cards('play', 3)
        
    def copy(self, game):
        p = Player_Base(game, self.pid)
        p.score = self.score
        p.played = self.played
        return p
        
    def copy_cards_to(self, game):
        p = game.get_player(self.pid)
        
        p.decks['play'] = {cid: c.game_copy(game) for cid, c in self.decks['play'].items()}
        
        selection = p.decks['selection']
        for cid, c in self.decks['selection'].items():
            spot = game.grid.get_spot(c.spot.pos)
            card = spot.card
            if card:
                selection[cid] = card
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
        
    def add_card(self, deck, card):
        self.decks[deck][card.cid] = card
        
    def remove_card(self, deck, card):
        self.decks[deck].pop(card.cid)
        
    def pop_card(self, deck, cid):
        card = self.decks[deck].pop(cid)
        self.draw_cards('play', 1)
        return card
        
    def clear_deck(self, deck):
        for cid in list(self.decks[deck]):
            self.pop_card(deck, cid)
        
    def draw_cards(self, deck, num):
        cards = self.game.draw_cards(deck, num=num)
        for card in cards:
           self.add_card(deck, card) 
        
    def play_card(self, deck, cid, spot):
        match deck:
            case 'play':
                card = self.pop_card(deck, cid)
                deck = 1
            case 'community':
                card = self.game.pop_community(cid)
                deck = 0
                
        if not card:
            return
        
        card.set_player(self)
        spot.set_card(card)
        card.play()
        
        self.played = True
        
        self.add_log({
            't': 'p',
            'd': deck,
            'c': card.cid,
            'pos': spot.pos
        })

    def gain_ownership(self, card):
        card.set_player(self)
        
# selection stuff

    def start_select(self, card, selection):
        if selection:
            if len(selection) == 1:
                card.select(selection[0])
            else:
                for c in selection:
                    self.add_card('selection', c)
                self.active_card = card
            
    def end_select(self):
        self.clear_deck('selection')
        self.active_card = None
        
    def select_card(self, cid):
        card = self.decks['selection'][cid]
        self.active_card.select(card)
        self.end_select()
        
        self.add_log({
            't': 's',
            'c': card.cid
        }, exc=True)

# log stuff

    def add_log(self, log, exc=False):
        log['u'] = self.pid
        if exc:
            log['exc'] = self.pid
        self.log.append(log)
        self.game.add_log(log)
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
        
    def choose_random_play(self):
        choices = (
            [('play', cid) for cid in self.decks['play']] +
            [('community', cid) for cid in self.decks['community']]
        )
        return random.choice(choices)

    def choose_random_spot(self):
        spots = [spot for spot in self.game.grid.spots if spot.is_open]
        return random.choice(spots) 
        
    def random_turn(self):
        deck, cid = self.choose_random_play()
        spot = self.choose_random_spot()
        self.play_card(deck, cid, spot)
        
    def random_selection(self):
        cid = random.choice(list(self.decks['selection']))
        self.select_card(cid)

    def update(self):
        if not self.played:
            self.random_turn()
                
        if self.active_card:
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
            'c': card.cid,
            'e': extra.cid if extra else None
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
            'c': card.cid,
            'target': target.pid,
            'e': extra.cid if extra else None
        })



