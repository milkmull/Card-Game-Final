import random
from datetime import datetime

from data import save

from .card import cards as card_manager
from .player import Player, Auto_Player
from simulator.tree import Tree

from . import game_base
    
def sort_logs(log):
    u = log.get('u')
    if u == 'g':
        return -1
    return u
 
class Game(game_base.Game_Base):
    @staticmethod
    def blank_player_info(pid):
        return {
            'name': f'player {pid}',
            'tags': ['player']
        }
        
    @staticmethod
    def get_user_player_info():
        return {
            'name': save.SAVE.get_data('cards')[0]['name'],
            'tags': ['player']
        }

    @staticmethod
    def pack_log(logs):
        new_log = []
    
        for log in logs:
            log = log.copy()
            for key, val in log.items():

                if isinstance(val, Player):
                    log[key] = val.pid
                    
                elif hasattr(val, 'uid'):
                    log[key] = (val.name, val.uid)
                    
                elif isinstance(val, list):
                    new_list = []
                    for i in val:  
                        if hasattr(i, 'get_id'):
                            new_list.append((i.name, i.get_id()))   
                        else:   
                            new_list.append(i)       
                    log[key] = new_list

                else:
                    log[key] = val
                    
            new_log.append(log)
                    
        return new_log
  
    def __init__(self, mode, *args, settings=None, cards=None, **kwargs):
        if settings is None:
            settings = save.SAVE.get_data('settings')
        if cards is None:
            cards = card_manager.get_playable_card_data()
   
        super().__init__(mode, settings, cards)
        
        self.tree = Tree(self)

        self.new_status('waiting')
        
        self.seed = datetime.now().timestamp()
        print(self.seed)
        random.seed(self.seed)

        if self.mode == 'single':
            #self.add_player(0, Game.get_user_player_info())
            self.add_cpus(num=2)
            
            #random.seed(3)
            
# copy stuff

    def copy(self):
        return game_base.Game_Base.copy(self)
        
# new game stuff

    def new_game(self):
        self.clear_logs()
        self.tree.reset()
        self.add_log({'t': 'res'})

        super().new_game()
        
        self.update_round()

    def new_round(self):
        self.clear_logs()
        self.tree.reset()
        self.add_log({'t': 'nr'})
        
        super().new_round()
        
        self.update_round()

    def reset(self):
        self.new_status('waiting')
        for p in self.players: 
            p.reset()    
        self.add_log({'t': 'res'})
        
    def start(self, pid):
        if pid == 0:
            if len(self.players) > 1:
                self.new_game()

# networking
 
    def get_pid(self):
        return 0
         
    def send_and_recv(self, data):
        if not data:        
            return
            
        reply = ''

        if data == 'disconnect':
            return
        
        if data == 'pid':            
            reply = 0

        elif data == 'info':
            self.main()
            reply = self.get_info(0)
            
        elif data.startswith('name'):
            reply = self.get_player(0).set_name(data[5:])
        
        elif data == 'start':
            self.start(0)
            reply = 1
            
        elif data == 'reset':
            self.reset()
            reply = 1
            
        elif data == 'continue':
            status = self.status
            if status == 'next round':
                self.new_round()  
            elif status == 'new game': 
                self.new_game()
            reply = 1
            
        elif data == 'play':
            if self.status == 'playing':
                self.update_player(0, cmd='play')    
            reply = 1
            
        elif data == 'cancel':
            if self.status == 'playing':
                self.update_player(0, cmd='cancel')    
            reply = 1
            
        elif data.lstrip('-').isdigit():
            self.update_player(0, cmd=f'select {data}')
            reply = 1

        elif data == 'flip':
            if self.status == 'playing':
                self.update_player(0, cmd='flip')        
            reply = 1
            
        elif data == 'roll':
            if self.status == 'playing':
                self.update_player(0, cmd='roll')   
            reply = 1

        elif data == 'settings':
            reply = self.get_settings()
                
        elif data == 'us':
            self.update_settings()
            reply = 1

        return reply
        
    def recieve_player_info(self, pid):
        p = self.get_player(pid)
        return p.get_info()

    def close(self):
        pass

    def get_active_names(self): #will need to update if custom cards can be toggled
        card_names = [name for deck in self.cards for name in self.cards[deck]]
        player_names = [p.name for p in self.players]
        return card_names + player_names

    def update_settings(self):
        self.settings = save.SAVE.get_data('settings')  
        if self.mode == 'single':
            self.balance_cpus()
        self.add_log({'t': 'set', 'settings': self.get_settings()})

# log stuff

    def get_scores(self):
        return {p.pid: p.score for p in self.players}

    def add_log(self, log):
        log['u'] = 'g'
        self.log.append(log)
        
    def add_player_log(self, log):
        self.log.append(log)
        if log['t'] == 'select':
            self.tree.trim(log)

    def clear_logs(self):     
        self.log.clear()

    def get_info(self, pid):
        p = self.get_player(pid)
        logs = []
        count = 0
        
        for log in self.log[p.log_index:]:
            p.log_index += 1
            if log.get('exc', pid) == pid:
                logs.append(log)
                count += 1
                if count == 5:
                    break

        return Game.pack_log(logs)
        
    def get_startup_log(self, pid):
        logs = []
        logs.append({'t': 'ns', 'stat': 'waiting', 'u': 'g'})
        logs.append({'t': 'set', 'settings': self.get_settings(), 'u': 'g'})
        
        for p in self.players:
            logs.append({'t': 'add', 'pid': p.pid, 'name': p.username, 'u': p.pid})

        for log in logs:
            log['exc'] = pid

        self.log += logs

# player stuff

    def add_cpus(self, num=0):
        self.pid = len(self.players)
        for _ in range(num or self.get_setting('cpus')):  
            player_info = Game.blank_player_info(self.pid)
            p = Auto_Player(self, self.pid, player_info)
            self.players.append(p)      
            self.add_log({'t': 'add', 'pid': p.pid, 'name': p.username})
            self.pid += 1
        self.new_status('waiting')
            
    def add_player(self, pid, player_info):
        if self.status == 'waiting':
            p = Player(self, pid, player_info)
            self.players.append(p)  
            p.log_index = len(self.log)
            self.pid += 1
            self.add_log({'t': 'add', 'pid': pid, 'name': p.username})
            self.get_startup_log(p.pid)
            self.new_status('waiting')
            return p 
            
    def remove_player(self, pid):
        p = self.get_player(pid)
        if p:
            self.players.remove(p)
            self.add_log({'t': 'del', 'pid': p.pid})
            if self.mode == 'online':
                if self.status == 'playing':
                    self.reset()
                else:
                    self.new_status('waiting')

    def balance_cpus(self):
        players = sorted(self.players, key=lambda p: p.pid, reverse=True)
        dif = (len(self.players) - 1) - self.get_setting('cpus')
        
        if dif > 0:
            for i in range(dif): 
                p = players[i]
                self.remove_player(p.pid)
                
        elif dif < 0: 
            for p in self.players.copy():   
                if p.is_auto():    
                    self.remove_player(p.pid)        
            self.add_cpus()
   
# main game logic

    def update_round(self):
        text = f"round {self.round}/{self.get_setting('rounds')}"
        self.add_log({'t': 'ur', 's': text})
            
    def new_status(self, stat):
        self.status = stat
        self.add_log({'t': 'ns', 'stat': stat})

    def update_player(self, pid, cmd=''):
        p = self.get_player(pid)
        p.update(cmd)
        self.advance_turn()
        
    def main(self):
        if self.status != 'waiting':
            for p in self.players:
                p.update()
                self.advance_turn()  
                
            if self.mode == 'single':
                self.tree.simulate()

    def count_votes(self):
        v = 'keep'
        rotate = 0
        keep = 0
        
        for p in self.players:
            if p.vote == 'rotate':
                rotate += 1
            elif p.vote == 'keep':
                keep += 1
            p.set_vote(None)
        
        if rotate > keep:
            self.rotate_cards()
            v = 'rotate'
        elif rotate == keep:
            self.shuffle_cards()
            v = 'shuffle'
            
        self.add_log({'t': 'v', 'v': v})

    def new_turn(self):
        super().new_turn()
        self.add_log({'t': 'nt'})
    
    def advance_turn(self):
        if self.status != 'playing':
            return 
            
        finished_round = set()
        finished_playing = set()
        finished_turn = set()
        voting = False
        voted = set()
        
        for p in self.players:
            finished_round.add(p.finished_game())
            finished_playing.add(p.done_with_round())
            finished_turn.add(p.done_with_turn())
            if p.active_card == self.vote_card or p.vote:
                voting = True
            voted.add(p.vote)

        if all(finished_round):
            if not self.done():
                if self.round <= self.get_setting('rounds') - 1: 
                    self.new_status('next round')   
                else:
                    self.new_status('new game')
                self.add_log({'t': 'fin', 'w': self.get_winners()})
                return
                
        elif all(finished_playing): 
            for p in self.players:
                p.end_round(not (self.round % self.get_setting('rounds')))
      
        elif voting and all(voted):
            self.count_votes()
            self.new_turn()

        elif all(finished_turn):
            if not voting:
                self.vote_card.start()

# in game operations

    def set_event(self):
        super().set_event()
        self.add_log({'t': 'se', 'c': self.event.copy()})

    def fill_shop(self, m=3):
        super().fill_shop(m=m)
        self.add_log({'t': 'fill', 'cards': self.shop.copy()})
                  
    def add_discard(self, c):
        super().add_discard(c)
        self.add_log({'t': 'disc', 'c': self.discard[-1] if self.discard else None})
        
    def restore(self, c):
        if super().restore(c):
            self.add_log({'t': 'disc', 'c': self.discard[-1] if self.discard else None})
            return True
