import random
import time

from . import player_base

class Player(player_base.Player_Base):
    def __init__(self, game, pid, player_info):
        super().__init__(game, pid)
        
        self.player_info = player_info
        self.log_index = 0
        self.max = 60
        self.ft = 0
        self.rt = 0
        
    @property
    def username(self):
        return self.player_info['name']

    def is_auto(self):
        return isinstance(self, Auto_Player)

    def get_info(self):
        return self.player_info
        
    def copy(self, g):
        return Player_Copy(g, self)

# starting stuff                

    def reset(self):
        super().reset()
        self.log_index = 0
        self.ft = 0
        self.rt = 0

    def start(self):
        super().start()
        self.max = 60 * (len([p for p in self.game.players if not p.is_auto()]) or 1)
 
# card stuff 
                
    def new_deck(self, deck, cards):
        setattr(self, deck, cards)
        self.add_log({'t': 'nd', 'deck': deck, 'cards': cards.copy()})
        
    def discard_card(self, c, add_to_discard=True): 
        super().discard_card(c, add_to_discard=add_to_discard)
        #if add_to_discard:
        #    self.add_log({'t': 'disc', 'c': c, 'tags': c.tags}) #maybe change in the future
    
# vote stuff

    def set_vote(self, vote):
        self.vote = vote
        self.add_log({'t': 'v', 'v': vote})

# request stuff

    def ready_coin(self):
        self.coin = -1
        self.ft = self.max
        
    def ready_dice(self):
        self.dice = -1
        self.rt = self.max

    def set_active_card(self, c):
        self.active_card = c
        self.add_log({'t': 'aac', 'c': c, 'w': c.wait, 'cancel': self.can_cancel()})
        
    def remove_active_card(self):
        self.active_card = None
        self.add_log({'t': 'rac'})
        
    def process_request(self):
        self.requests.sort(key=Player.sort_request_cards)
        c = self.requests[0]
        if c is not self.active_card:
            self.cancel_request()
            self.start_request(c)
            self.set_active_card(c)
  
        confirm = False
        last_wait = c.wait

        if c.wait == 'flip' and not self.ft:
            if self.coin is not None:
                c.wait = None
                c.flip(self, self.coin)
                confirm = True
                
        elif c.wait == 'roll' and not self.rt:
            if self.dice is not None:  
                c.wait = None
                c.roll(self, self.dice)
                confirm = True

        elif c.wait == 'select':
            if self.selected:   
                c.wait = None
                c.select(self, len(self.selected))                
                confirm = True
            
        elif c.wait == 'cast': 
            if self.selected:
                c.wait = None
                target = self.selected.pop(0)
                self.cast(target, c)
                confirm = True

        if c.wait is None:
            self.requests.pop(0)
            self.cancel_request()
            
        elif confirm:
            self.soft_cancel_request()
            self.start_request(c)
            if c.wait != last_wait:
                self.set_active_card(c)

    def select(self, uid):
        if self.selection:
            for c in self.selection:  
                if c.id == uid:
                    self.selected.append(c)
                    return

        if not (self.gone or self.requests):
            for c in self.unplayed:
                if c.id == uid:   
                    self.play_card(c)
                    return
                    
        for c in self.requests:
            if c.id == uid:
                return
        
        if not self.game_over:

            for c in self.items: 
                if c.id == uid:
                    if c.can_use(self):
                        c.start(self)
                    return
                    
            for c in self.spells:    
                if c.id == uid:
                    c.wait = 'cast'
                    self.requests.append(c)
                    return
                    
            for c in self.treasure:
                if c.id == uid:  
                    if hasattr(c, 'start'):
                        c.start(self)     
                    return
                    
            for c in self.equipped:                   
                if c.id == uid:  
                    self.unequip(c)
                    return

    def flip(self):
        if self.ft == self.max / 2:
            self.coin = random.choice((1, 0))
            self.add_log({'t': 'cfe', 'coin': self.coin, 'd': False})
        self.ft = max(self.ft - 1, 0)

    def roll(self): 
        if self.rt == self.max / 2:
            self.dice = random.randrange(0, 6) + 1
            self.add_log({'t': 'dre', 'dice': self.dice, 'd': False})  
        self.rt = max(self.rt - 1, 0)
       
# log stuff

    def add_log(self, log):
        log['u'] = self.pid
        self.log.append(log)
        self.game.add_player_log(log)
        if not log.get('d'):
            self.og(log=log)

# turn stuff

    def end_round(self, end_all):
        if hasattr(self.game.event, 'end'):
            self.game.event.end(self)
        if end_all:
            for c in self.played + self.active_spells + self.treasure:
                if hasattr(c, 'end'):
                    c.end(self)
        self.game_over = True

    def update(self, cmd=''):
        if 'select' in cmd and (self.dice is self.coin is None):
            uid = int(cmd.split()[1])
            self.select(uid)
 
        elif cmd == 'cancel':
            self.cancel()

        elif cmd == 'play' and not self.gone:
            if self.unplayed:
                card = self.unplayed[0]
                self.play_card(card)
            
        elif cmd == 'flip' and self.coin == -1:  
            self.add_log({'t': 'cfs'})
            self.flipping = True   

        elif cmd == 'roll' and self.dice == -1:
            self.add_log({'t': 'drs'})
            self.rolling = True
            
        if self.flipping:
            self.flip()
        elif self.rolling:
            self.roll()

        if self.requests:
            self.process_request()
        self.og()

# point stuff
 
    def update_score(self, score):
        self.score = score
        self.add_log({'t': 'score', 'score': self.score})
        
class Auto_Player(Player):
    def __init__(self, game, pid, player_info):
        super().__init__(game, pid, player_info)

        self.timer = 0

    def set_timer(self):
        self.timer = random.randrange(60, 120)
        
    def start_turn(self):
        super().start_turn()
        self.set_timer()
        
    def get_decision(self):
        choices = self.game.tree.get_scores(self.pid)
        if not isinstance(choices, dict):
            print('tree', self.game.tree.tree)
            return
        if not self.selection and self.gone:
            choices['w'] = 0
        choices = sorted(choices.items(), key=lambda c: c[1], reverse=True)
        selection = {c.id: c for c in self.get_selection()}
        
        #print(self.pid, [(getattr(selection.get(uid), 'name', None), score) for uid, score in choices])

        for uid, _ in choices:
            if uid == 'w':
                break
            if c := selection.get(uid):
                return c

    def timer_up(self):
        return self.timer <= 0

    def start_request(self, c):
        sel = self.selection.copy()
        super().start_request(c)
        if not self.selecting or (self.selecting and self.selection != sel):
            self.set_timer()
        
    def get_selection(self):
        if self.selection:
            return self.selection.copy()
        return super().get_selection()

    def auto_select(self):
        s = None
        
        if self.game.done():
            return

        if self.timer_up() and not (self.flipping or self.rolling):
            s = self.get_decision()
            self.set_timer()
            
        if s:
            self.add_log({'t': 'select', 's': s})

        return s

    def update(self):
        s = self.auto_select()
        if s:
            self.select(s.id)
            
        if self.timer < 30:
            if self.coin == -1:
                if not self.flipping:
                    self.add_log({'t': 'cfs'})
                self.flipping = True
            elif self.dice == -1:
                if not self.rolling:
                    self.add_log({'t': 'drs'})   
                self.rolling = True

        if self.flipping:
            self.flip()
        elif self.rolling:
            self.roll()

        if self.requests:
            self.process_request()   
        self.og()
        
        self.timer -= 1
        
class Player_Copy(player_base.Player_Base):
    def __init__(self, game, p):
        super().__init__(game, p.pid)
        
        self.player = p

        self.score = p.score
        self.vote = p.vote
        
        self.selecting = p.selecting
        self.gone = p.gone
        self.flipping = p.flipping
        self.rolling = p.rolling      
        self.game_over = p.game_over
        self.invincible = p.invincible

        self.coin = p.coin
        self.dice = p.dice
        
        self.log = p.log.copy()

        self.first_choice = None
        
    def set_cards(self):
        self.played = [c.sim_copy(self.game) for c in self.player.played]
        self.unplayed = [c.light_sim_copy(self.game) for c in self.player.unplayed]
        
        self.items = [c.light_sim_copy(self.game) for c in self.player.items]
        self.equipped = [c.sim_copy(self.game) for c in self.player.equipped]

        self.spells = [c.light_sim_copy(self.game) for c in self.player.spells]
        self.active_spells = [c.sim_copy(self.game) for c in self.player.active_spells]
        
        self.treasure = [c.light_sim_copy(self.game) for c in self.player.treasure]
        self.landscapes = [c.sim_copy(self.game) for c in self.player.landscapes]
        
        self.selection = [c.sim_copy(self.game) for c in self.player.selection]
        self.selected = [c.sim_copy(self.game) for c in self.player.selected]
        
        self.ongoing = [c.sim_copy(self.game) for c in self.player.ongoing]
        self.active_og = [c.sim_copy(self.game) for c in self.player.active_og]
        
        self.requests = [c.sim_copy(self.game) for c in self.player.requests]
        self.active_card = None
        for c in self.requests:
            if c == self.player.active_card:
                self.active_card = c
                break 

# auto stuff

    def auto_select(self):
        s = None
        
        if self.game.done():
            return
            
        if self.selection:
            s = random.choice(self.selection)
            
        elif not self.requests:
            cards = self.get_selection()

            if cards:
                cards.append(None)
                s = random.choice(cards) 
                    
        if s:
            if not self.first_choice:
                self.first_choice = s
            self.add_log({'t': 'select', 's': s})
        
        return s
        