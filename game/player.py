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

    def add_card(self, deck, card):
        self.decks[deck][card.cid] = card
        
        self.add_log({
            't': 'ac',
            'c': (card.cid, card.name),
            'd': deck
        }, exc=True)
        
    def remove_card(self, deck, card):
        self.decks[deck].pop(card.cid)
        
        self.add_log({
            't': 'rc',
            'c': card.cid,
            'd': deck
        }, exc=True)
        
    def pop_card(self, deck, cid):
        card = self.decks[deck].pop(cid)
        
        self.add_log({
            't': 'rc',
            'c': card.cid,
            'd': deck
        }, exc=True)
        
        if deck == 'play':
            if len(self.decks['play']) < 3:
                self.draw_cards('play', 1)

        return card
        
    def play_card(self, data):
        deck, cid, x, y = data
        
        cid = int(cid)
        x = int(x)
        y = int(y)
        spot = self.game.grid.get_spot((x, y))
        
        super().play_card(deck, cid, spot)
        
    def select_card(self, data):
        cid = int(data[0])
        super().select_card(cid)
        
    def gain_ownership(self, card):
        card.set_player(self)
        
        self.add_log({
            't': 'own',
            'c': card.cid
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
        self.timer = random.randrange(200, 300)
        
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
        decks = {
            0: 'community',
            1: 'play'
        }

        if not self.played:

            spots = self.game.grid.get_open_spots()

            for (pid, deck, cid, x, y), score in choices:
                deck = decks[deck]
                if self.decks[deck].get(cid) and (spot := spots.get((x, y))):
                    return (deck, cid, spot)
                    
        elif self.active_card:
            cards = {cid: c for cid, c in self.decks['selection'].items()}

            for (pid, cid), score in choices:
                if cards.get(cid):
                    return cid

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
