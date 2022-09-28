import json

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
  
    def __init__(self, mode, *args, settings=None, cards=None, **kwargs):
        if settings is None:
            settings = save.SAVE.get_data('settings')
        if cards is None:
            cards = card_manager.get_base_card_data()
   
        super().__init__(mode, settings, cards)
        print(self.seed)
        
        self.tree = Tree(self)

        self.new_status('waiting')

        if self.mode == 'single':
            self.add_player(0, Game.get_user_player_info())
            self.add_cpus()
        
# new game stuff

    def reset(self):
        super().reset()
        self.tree.reset()
        self.log.insert(0, {'t': 'res'})
        
    def start(self, pid):
        if pid == 0:
            if len(self.players) > 1:
                self.new_game()

# networking
 
    def get_pid(self):
        return 0
         
    def update_game(self, data, pid=0):
        data = data.split('-')
        cmd = data.pop(0)
        
        match cmd:
            
            case 'ppid':
                reply = pid
                
            case 'info':
                self.main()
                reply = self.get_info(pid)
                
            case 'settings':
                if pid == 0:
                    self.set_settings(data)
                reply = 1
                
            case 'start':
                if pid == 0:
                    self.start(0)
                reply = 1
                
            case 'continue':
                if pid == 0:
                    self.reset()
                reply = 1
                
            case 'play' | 'select':
                if self.status == 'playing':
                    self.get_player(pid).update(cmd=cmd, data=data)    
                reply = 1

        return reply
        
# settings stuff

    def set_settings(self, settings):
        settings = json.loads(settings[0])
        self.settings = settings
        
        self.add_log({
            't': 'set',
            'settings': settings
        })
        
        self.grid.resize(settings['size'])
        self.balance_cpus(settings['cpus'])

# log stuff
    
    def add_log(self, log):
        self.log.append(log)
        if log['t'] == 'p' or log['t'] == 's':
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

        return logs
        
    def get_startup_log(self, pid):
        logs = []
        logs.append({
            't': 'ns',
            'stat': 'waiting'
        })
        logs.append({
            't': 'set',
            'settings': self.get_settings()
        })
        
        for p in self.players:
            logs.append({
                't': 'ap',
                'p': p.pid,
                'name': p.username,
            })

        for log in logs:
            log['exc'] = pid

        self.log += logs

# player stuff

    def balance_cpus(self, count):
        cpus = [p for p in sorted(self.players, key=lambda p: p.pid) if isinstance(p, Auto_Player)]
        diff = count - len(cpus)

        if diff > 0:
            self.add_cpus(num=diff)
        elif diff < 0:
            for p in cpus[diff:]:  
                self.remove_player(p.pid)

    def add_cpus(self, num=0):
        self.pid = len(self.players)
        for _ in range(num or self.get_setting('cpus')):  
            player_info = Game.blank_player_info(self.pid)
            p = Auto_Player(self, self.pid, player_info)
            self.players.append(p)   
            
            self.add_log({
                't': 'ap',
                'p': p.pid,
                'name': p.username
            })
                
            self.pid += 1
        self.new_status('waiting')
            
    def add_player(self, pid, player_info):
        if self.status == 'waiting':
            p = Player(self, pid, player_info)
            self.players.append(p)  
            p.log_index = len(self.log)
            
            self.add_log({
                't': 'ap',
                'p': pid,
                'name': p.username
            })
            
            self.pid += 1
            self.get_startup_log(p.pid)
            self.new_status('waiting')
            return p 
            
    def remove_player(self, pid):
        for p in self.players:
            if p.pid == pid:
                self.players.remove(p)
            
                self.add_log({
                    't': 'rp',
                    'p': pid
                })
                
                break
            
# card stuff

    def add_community(self, card):
        self.community_deck[card.cid] = card
        
        self.add_log({
            't': 'ac',
            'c': (card.cid, card.name),
            'd': 'community'
        })
        
    def remove_community(self, card):
        self.community_deck.pop(card.cid)
        
        self.add_log({
            't': 'rc',
            'c': card.cid,
            'd': 'community'
        })
            
    def pop_community(self, cid):
        card = self.community_deck.pop(cid, None)
        
        if card:
        
            self.add_log({
                't': 'rc',
                'c': card.cid,
                'd': 'community'
            })
            
            self.add_community(self.draw_cards()[0])
        
        return card
   
# main game logic
 
    def new_status(self, stat):
        super().new_status(stat)
        
        self.add_log({
            't': 'ns',
            'stat': stat
        })
        
    def new_turn(self):
        super().new_turn()
        
        self.add_log({
            't': 'nt',
            'p': self.players[self.current_turn].pid
        })
        
    def main(self):
        if self.status != 'waiting':
            self.tree.simulate()
            super().main()
            
    def end_game(self):
        super().end_game()
        
        self.add_log({
            't': 'fin',
            'w': self.get_winners()
        })
