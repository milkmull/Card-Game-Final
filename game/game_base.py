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
        self.status = ""
        self.turn = 0
        self.current_turn = 0
        
        self.log = []
        self.public_deck = {}
        self.multipliers = {}
        self.wait = {}
        self.players = [] 
        self.grid = Grid(self, self.get_setting("size"))
        
        if seed is None:
            seed = datetime.now().timestamp()
        self.seed = seed
        random.seed(self.seed)
        
    @property
    def done(self):
        return self.status == "new game"
        
    def copy(self, seed=None):
        g = Game_Base(self.mode, self.settings, self.cards, seed=seed)
        g.pid = self.pid
        g.cid = self.cid
        g.status = self.status
        g.turn = self.turn
        g.current_turn = self.current_turn
        
        g.public_deck = {cid: c.game_copy(g) for cid, c in self.public_deck.items()}
        g.players = [p.copy(g) for p in self.players]
        self.grid.copy_to(g)
        
        g.multipliers = {cid: g.grid.get_spot(c.spot.pos).card for cid, c in self.multipliers.items()}
        g.wait = {cid: g.grid.get_spot(c.spot.pos).card for cid, c in self.wait.items()}

        for p in self.players:
            p.copy_cards_to(g)

        return g

# new game stuff
    
    def reset(self):
        self.log.clear()
        self.public_deck.clear()
        self.multipliers.clear()
        self.wait.clear()
        self.grid.reset()
        
        for p in self.players: 
            p.reset()
        self.cid = len(self.players)
        
        self.turn = 0
        self.current_turn = 0
        
        self.new_status("waiting")  

    def new_game(self):
        self.reset()
        self.new_status("playing") 
        
        for p in self.players:
            p.start()

        self.current_turn = random.choice([p.pid for p in self.players])
        self.new_turn()

        for c in self.draw_cards(num=9):
            self.add_public(c)
                
    def add_cpus(self, num=0):
        self.pid = 0
        for _ in range(num or self.get_setting("cpus")):  
            p = player_base.Player_Base(self, self.pid)
            self.players.append(p)      
            self.pid += 1
            
# log stuff

    def add_log(self, log):     
        self.log.append(log)
        
    def get_last_log(self, types):
        for log in reverse(self.log):
            if log["t"] in types:
                return log

# player stuff 
   
    def get_player(self, pid):
        for p in self.players:
            if p.pid == pid:
                return p
                
    def get_players(self):
        return self.players.copy()

# card stuff
     
    def add_card_data(self, cls):
        self.cards[cls.name] = cls
     
    def set_card_data(self, data):
        self.cards = data
     
    def get_new_cid(self):
        cid = self.cid
        self.cid += 1
        return cid
        
    def draw_card_from_tag(self, tag, caller):
        deck = {name: cls for name, cls in self.cards.items() if tag in cls.tags}
        weights = [cls.weight for cls in deck.values()]
        name = random.choices(list(deck.keys()), weights=weights, k=1)[0]
        
        self.add_log({
            "u": caller.player.pid,
            "t": "rand",
            "len": len(deck)
        })
        self.add_log({
            "u": caller.player.pid,
            "t": "randres",
            "res": deck[name].sid,
            "w": deck[name].weight
        })
        
        return self.get_card(name)
     
    def draw_cards(self, num=1):
        weights = [cls.weight for cls in self.cards.values()]
        cards = random.choices(list(self.cards), weights=weights, k=num)
        for i, name in enumerate(cards):
            cards[i] = self.get_card(name)
        return cards
 
    def get_card(self, name, cid=None):
        if cid is None:
            cid = self.get_new_cid()
        cls = self.cards.get(name)
        if cls:
            return cls(self, cid)
        raise exceptions.CardNotFound(name)

    def add_public(self, card):
        if len(self.public_deck) < 15:
            self.public_deck[card.cid] = card
        
    def remove_public(self, card):
        self.public_deck.pop(card.cid)
            
    def pop_public(self, cid):
        card = self.public_deck.pop(cid)
        if self.mode == "test" and len(self.public_deck) < 9:
            self.add_public(self.draw_cards()[0])
        return card
        
    def add_multiplier(self, card):
        self.multipliers[card.cid] = card
        
    def remove_multiplier(self, card):
        self.multipliers.pop(card.cid, None)
        
    def add_wait(self, card):
        self.wait[card.cid] = card
        
    def remove_wait(self, card):
        self.wait.pop(card.cid, None)
        
    def transform(self, card, new_card):
        if card.name is new_card:
            return card
            
        spot = card.spot
        card.spot.clear_card()
        card.total_clear()
        new_card.setup(card.player)
        new_card.spawn_to(spot)
        return new_card

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
        self.current_turn = (self.current_turn + 1) % len(self.players)
        self.players[self.current_turn].start_turn()
        self.run_wait("nt", player=self.players[self.current_turn])
        
    def card_update(self):
        cards = sorted(self.grid.cards, key=lambda c: c.priority, reverse=True)
        
        for card in cards:
            if not card.skip_remove and card.spot:
                card.remove()
            card.skip_remove = False
            
        for card in cards:
            if not card.skip_move and card.spot:
                card.move()
            card.skip_move = False
            
        for card in cards:
            if not card.skip_update and card.spot:
                card.update()
            card.skip_update = False
                
    def run_wait(self, wait, **data):
        for c in list(self.wait.values()):
            if c.wait == wait:
                c.run_wait(data)

    def main(self):
        if self.status == "playing":
            p = self.players[self.current_turn]
            p.update()
            if p.done_turn:
                self.card_update()
                self.advance_turn() 
    
    def advance_turn(self):
        if self.status != "playing":
            return 

        if self.grid.full or (not self.public_deck and all({not p.decks["private"] for p in self.players})):
            self.end_game()
            
        else:
            self.new_turn()
            
    def end_game(self):
        self.new_status("new game") 
            
# ending stuff

    def get_winners(self):
        hs = max({p.score for p in self.players})
        return [p.pid for p in self.players if p.score == hs]
  