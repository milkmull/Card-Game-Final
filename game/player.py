import random

from . import player_base

class Player(player_base.Player_Base):
    def __init__(self, game, pid, player_info):
        super().__init__(game, pid)
        
        self.player_info = player_info
        self.log_index = 0
        
    @property
    def username(self):
        return self.player_info['name']

    def is_auto(self):
        return isinstance(self, Auto_Player)

    def get_info(self):
        return self.player_info

# starting stuff                

    def reset(self):
        super().reset()
        self.log_index = 0
 
# card stuff 

    def new_deck(self, type, cards):
        self.decks[type] = cards
        self.add_log({'t': 'nd', 'deck': type, 'cards': cards.copy()})
        
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

# turn stuff

    def update(self, cmd='', data=[]):
        if cmd == 'play' and not self.done_turn:
            self.play_card(data)

# point stuff
 
    def update_score(self, score):
        self.score = score
        self.add_log({'t': 'score', 'score': self.score})
        
class Auto_Player(Player):
    def __init__(self, game, pid, player_info):
        super().__init__(game, pid, player_info)

        self.timer = 0

    def set_timer(self):
        self.timer = random.randrange(200, 400)
        
    def timer_up(self):
        return self.timer <= 0
        
    def start_turn(self):
        super().start_turn()
        self.set_timer()
        
    def get_decision(self):
        choices = self.game.tree.get_scores(self.pid)
        print(choices)
        if not isinstance(choices, dict):
            return
        choices = sorted(choices.items(), key=lambda c: c[1], reverse=True)
        cards = {c.sid: c for c in self.decks['play']}
        spots = self.game.grid.get_open_spots()

        for (pid, sid, x, y), score in choices:
            if (card := cards.get(sid)) and (spot := spots.get((x, y))):
                return (card, spot)

    def update(self):
        if not self.done_turn and self.timer_up():
            choice = self.get_decision()
            if choice:
                player_base.Player_Base.play_card(self, *choice)
        
        self.timer -= 1
