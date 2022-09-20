import random

from . import player_base

class Player(player_base.Player_Base):
    def __init__(self, game, pid, player_info):
        super().__init__(game, pid)
        
        self.player_info = player_info
        self.log_index = 0
        
    @property
    def is_auto(self):
        return False
        
    @property
    def username(self):
        return self.player_info['name']

    def get_info(self):
        return self.player_info

# starting stuff                

    def reset(self):
        super().reset()
        self.log_index = 0
 
# card stuff 

    def new_deck(self, type, cards):
        self.decks[type] = cards
        self.add_log({
            't': 'nd',
            'deck': type,
            'cards': cards.copy(),
            'exc': self.pid
        })
        
    def play_card(self, data):
        cid, x, y = data
        
        cid = int(cid)
        for card in self.decks['play']:
            if card.cid == cid:
                break
        else:
            return

        x = int(x)
        y = int(y)
        spot = self.game.grid.get_spot((x, y))
        
        super().play_card(card, spot)
        
    def select_card(self, data):
        cid = int(data[0])
        for card in self.decks['selection']:
            if card.cid == cid:
                break
        else:
            return
            
        super().select_card(card)
        
    def gain_ownership(self, card):
        card.set_player(self)
        
        self.add_log({
            't': 'own',
            'c': card,
            'p': self
        })

# turn stuff

    def update(self, cmd='', data=[]):
        if cmd == 'play' and not self.played:
            self.play_card(data)
        
        elif cmd == 'select' and self.active_card:
            self.select_card(data)

# point stuff
 
    def update_score(self, score):
        self.score = score
        self.add_log({
            't': 'score',
            'score': self.score
        })
        
class Auto_Player(Player):
    def __init__(self, game, pid, player_info):
        super().__init__(game, pid, player_info)

        self.timer = 0

    def set_timer(self):
        self.timer = random.randrange(200, 250)
        
    def timer_up(self):
        return self.timer <= 0
        
    def start_turn(self):
        super().start_turn()
        self.set_timer()
        
    def get_decision(self):
        choices = self.game.tree.get_scores(self.pid)
        if not isinstance(choices, dict):
            return
        choices = sorted(choices.items(), key=lambda c: c[1], reverse=True)
        
        if not self.played:
            cards = {c.sid: c for c in self.decks['play']}
            spots = self.game.grid.get_open_spots()

            for (pid, sid, x, y), score in choices:
                if (card := cards.get(sid)) and (spot := spots.get((x, y))):
                    return (card, spot)
                    
        elif self.active_card:
            cards = {c.cid: c for c in self.decks['selection']}

            for (pid, cid), score in choices:
                if (card := cards.get(cid)):
                    return card

    def update(self):
        if self.timer_up():
        
            choice = self.get_decision()
            if choice:
            
                if not self.played:
                    player_base.Player_Base.play_card(self, *choice)
                elif self.active_card:
                    player_base.Player_Base.select_card(self, choice)
                    
                self.set_timer()
        
        self.timer -= 1
