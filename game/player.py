import random
import time

from . import player_base

class Player(player_base.Player_Base):
    def __init__(self, game, pid, player_info):
        super().__init__(game, pid)
        
        self.player_info = player_info
        self.log_queue = []

        self.timer = 0
        self.start_time = 0
        
    @property
    def is_auto(self):
        return False
        
    @property
    def is_cpu(self):
        return isinstance(self, Auto_Player)
        
    @property
    def username(self):
        return self.player_info["name"].replace(" ", "_")

    def get_info(self):
        return self.player_info
        
# timer stuff

    @property
    def max_time(self):
        return self.game.get_setting("tt")
        
    @property
    def current_time(self):
        return self.max_time - (time.time() - self.start_time)
        
    @property
    def timer_up(self):
        return self.current_time <= 0
        
    def set_timer(self):
        self.start_time = time.time()
 
# card stuff 

    def add_card(self, deck, card):
        self.decks[deck][card.cid] = card
        
        self.add_log({
            "t": "ac",
            "c": (card.cid, card.name),
            "d": deck
        }, exc=True)
        
    def remove_card(self, deck, card):
        self.decks[deck].pop(card.cid)
        
        self.add_log({
            "t": "rc",
            "c": card.cid,
            "d": deck
        }, exc=True)
        
    def pop_card(self, deck, cid):
        card = self.decks[deck].pop(cid)
        
        self.add_log({
            "t": "rc",
            "c": card.cid,
            "d": deck
        }, exc=True)
        
        if deck == "private":
            if len(self.decks["private"]) < 3:
                self.draw_cards("private", 1)

        return card
        
    def play_card_from_data(self, data):
        deck, cid, x, y = data
        
        cid = int(cid)
        x = int(x)
        y = int(y)
        spot = self.game.grid.get_spot((x, y))
        
        self.play_card(deck, cid, spot)
        
    def select_card_from_data(self, data):
        cid = int(data[0])
        self.select_card(cid)
        
    def gain_ownership(self, card):
        card.set_player(self)
        
        self.add_log({
            "t": "own",
            "c": card.cid
        })

# turn stuff
    
    def start_turn(self):
        super().start_turn()
        self.set_timer()

    def update(self, cmd="", data=[]):
        if cmd == "play" and not self.played:
            self.play_card_from_data(data)
        
        elif cmd == "select" and self.active_card:
            self.select_card_from_data(data)
            
        if (not self.played or self.active_card) and self.timer_up:
            super().update()

# point stuff
 
    def update_score(self, score):
        self.score = score
        
        self.add_log({
            "t": "score",
            "score": self.score
        })
        
class Auto_Player(Player):   
    def set_timer(self):
        self.start_time = time.time()
        tmin = 4
        tmax = min(self.current_time // 2, 15)
        self.timer = random.randrange(tmin, tmax)
        
    def get_decision(self):
        choices = self.game.tree.get_scores(self.pid)
        if not isinstance(choices, dict):
            return
        choices = sorted(choices.items(), key=lambda c: c[1], reverse=True)
        decks = {
            0: "public",
            1: "private"
        }
        
        match self.game.get_setting("diff"):
            case 1:
                choices = choices[:15]
                random.shuffle(choices)
            case 2:
                choices = choices[:10]
                random.shuffle(choices)
            case 3:
                choices = choices[:5]
                random.shuffle(choices)

        if not self.played:

            spots = self.game.grid.get_open_spots()
            
            #for (pid, deck, cid, x, y), score in choices:
            #    print(pid, deck, cid, x, y)
            #    deck = decks[deck]
            #    if self.decks[deck].get(cid) and (spot := spots.get((x, y))):
            #        print(self.decks[deck].get(cid), score)

            for node, score in choices:
                pid, deck, cid, x, y = node.data
                deck = decks[deck]
                if self.decks[deck].get(cid) and (spot := spots.get((x, y))):
                    return (deck, cid, spot)
                    
        elif self.active_card:
        
            cards = {cid: c for cid, c in self.decks["selection"].items()}

            for node, score in choices:
                pid, cid = node.data
                if cards.get(cid):
                    return cid

    def update(self):
        if not getattr(self.game, "cpus_enabled", True):
            return
            
        ct = self.timer - (time.time() - self.start_time)
        
        if ct <= 0:

            if not self.played:
                choice = self.get_decision()
                if choice:
                    self.play_card(*choice)
                    
            elif self.active_card:
                choice = self.get_decision()
                if choice:
                    self.select_card(choice)
                    
            self.set_timer()
