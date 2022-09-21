import random
from datetime import datetime

from . import exceptions

from . import player_base
from .grid import Grid

class Game_Base:
    def __init__(self, mode, settings, cards, seed=None):    
        self.mode = mode
        self.settings = settings
        self.cards = cards

        self.pid = 0
        self.cid = 0
        self.status = ''
        self.turn = 0
        self.current_turn = 0
        
        self.log = []
        self.community_deck = {}
        self.players = [] 
        self.grid = Grid(self, self.get_setting('size'))
        
        if seed is None:
            seed = datetime.now().timestamp()
        self.seed = seed
        random.seed(self.seed)
        
    @property
    def done(self):
        return self.status == 'new game'
        
    def copy(self, seed=None):
        g = Game_Base(self.mode, self.settings, self.cards, seed=seed)
        g.pid = self.pid
        g.cid = self.cid
        g.status = self.status
        g.turn = self.turn
        g.current_turn = self.current_turn
        
        g.community_deck = {cid: c.game_copy(g) for cid, c in self.community_deck.items()}
        g.players = [p.copy(g) for p in self.players]
        self.grid.copy_to(g)

        for p in self.players:
            p.copy_cards_to(g)

        return g

# new game stuff

    def new_game(self):
        self.log.clear()
        for p in self.players: 
            p.reset()
        self.cid = len(self.players)
        self.community_deck.clear()
        
        for p in self.players:
            p.start()

        self.turn = 0
        self.current_turn = random.choice([p.pid for p in self.players])

        self.new_turn()
        self.new_status('playing')  
        
        for c in self.draw_cards(num=9):
            self.add_community(c)
                
    def add_cpus(self, num=0):
        self.pid = 0
        for _ in range(num or self.get_setting('cpus')):  
            p = player_base.Player_Base(self, self.pid)
            self.players.append(p)      
            self.pid += 1
            
# log stuff

    def add_log(self, log):
        self.log.append(log)

# player stuff 
   
    def get_player(self, pid):
        for p in self.players:
            if p.pid == pid:
                return p

# card stuff
     
    def add_card_data(self, cls):
        self.cards[cls.type][cls.name] = cls
     
    def set_card_data(self, data):
        self.cards = data
     
    def get_new_cid(self):
        cid = self.cid
        self.cid += 1
        return cid
     
    def draw_cards(self, type='play', num=1):
        deck = self.cards[type]
        weights = [cls.weight for cls in deck.values()]
        cards = random.choices(list(deck.keys()), weights=weights, k=num)
        for i, name in enumerate(cards):
            cards[i] = self.get_card(name)
        return cards
 
    def get_card(self, name, cid=None):
        if cid is None:
            cid = self.get_new_cid()
        for type, deck in self.cards.items():
            cls = deck.get(name)
            if cls:
                return cls(self, cid)
        raise exceptions.CardNotFound(name)

    def add_community(self, card):
        self.community_deck[card.cid] = card
        
    def remove_community(self, card):
        self.community_deck.pop(card.cid)
            
    def pop_community(self, cid):
        card = self.community_deck.pop(cid)
        self.add_community(self.draw_cards()[0])
        return card

# update info stuff
            
    def new_status(self, stat):
        self.status = stat
                     
# settings stuff

    def get_setting(self, setting):
        return self.settings[setting]
        
    def get_settings(self):
        return self.settings.copy()

# turn stuff

    def new_status(self, stat):
        self.status = stat
            
    def new_turn(self):
        if self.community_deck:
            self.current_turn = (self.current_turn + 1) % len(self.players)
            
        else:
            current_turn = (self.current_turn + 1) % len(self.players)
            for p in (self.players[current_turn:] + self.players[:current_turn]):
                if p.decks['play']:
                    self.current_turn = self.players.index(p)
                    break
            
        self.players[self.current_turn].start_turn()
        
    def card_update(self):
        cards = self.grid.cards
        
        for card in cards:
            if card.spot:
                card.remove()
            
        for card in cards:
            if card.spot:
                if card.can_move:
                    card.move()
            
        for card in cards:
            if card.spot:
                card.update()
   
    def main(self):
        if self.status == 'playing':
            p = self.players[self.current_turn]
            p.update()
            if p.done_turn:
                self.card_update()
                self.advance_turn() 
    
    def advance_turn(self):
        if self.status != 'playing':
            return 

        if self.grid.full or (not self.community_deck and all({not p.decks['play'] for p in self.players})):
            self.end_game()
            
        else:
            self.new_turn()
            
    def end_game(self):
        self.new_status('new game') 
            
# ending stuff

    def get_winners(self):
        hs = max({p.score for p in self.players})
        return [p.pid for p in self.players if p.score == hs]
  