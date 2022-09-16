from data import save

from .card import cards as card_manager
from .player import Player, Auto_Player
from .tree import Tree

from . import game_base
 
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
                    
                elif hasattr(val, 'cid'):
                    log[key] = (val.name, val.cid)
                    
                elif isinstance(val, list):
                    new_list = []
                    for i in val:  
                        if hasattr(i, 'id'):
                            new_list.append((i.name, i.id))   
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
            cards = card_manager.get_base_card_data()
   
        super().__init__(mode, settings, cards)
        
        self.tree = Tree(self)

        self.new_status('waiting')

        if self.mode == 'single':
            self.add_player(0, Game.get_user_player_info())
            self.add_cpus()#num=2)
        
# new game stuff

    def new_game(self):
        self.tree.reset()
        super().new_game()
        
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
        data = data.split('-')
        cmd = data.pop(0)
        
        match cmd:
            
            case 'pid':
                reply = 0
                
            case 'info':
                self.main()
                reply = self.get_info(0)
                
            case 'start':
                self.start(0)
                reply = 1
                
            case 'continue':
                match self.status:
                    case 'next round':
                        self.new_round()  
                    case 'new game':
                        self.new_game()
                reply = 1
                
            case 'play':
                if self.status == 'playing':
                    self.get_player(0).update(cmd='play', data=data)    
                reply = 1

        return reply

# log stuff
    
    def add_player_log(self, log):
        self.log.append(log)
        if log['t'] == 'play':
            self.tree.trim(log)

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
   
# main game logic
 
    def new_status(self, stat):
        super().new_status(stat)
        self.add_log({'t': 'ns', 'stat': stat})
        
    def new_turn(self):
        super().new_turn()
        self.add_log({'t': 'nt', 'p': self.players[self.current_turn].pid})
        
    def main(self):
        if self.status != 'waiting':
            self.tree.simulate()
            super().main()
            
    def end_game(self):
        super().end_game()
        self.add_log({'t': 'fin', 'w': self.get_winners()})
