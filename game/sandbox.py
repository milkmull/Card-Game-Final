from .player import Player
from . import game_base, game
 
class Sandbox(game.Game):
    def __init__(self, *args, **kwargs):
        self.cpus_enabled = False
        self.current_view = 0
        
        super().__init__(*args, **kwargs)

    def set_cpu_enabled(self, on):
        self.cpus_enabled = on
        
    def skip_turn(self):
        self.players[self.current_turn].end_turn()
        
        if self.status == 'playing':
            p = self.players[self.current_turn]
            if not p.active_card:
                p.played = True
                self.card_update()
                self.advance_turn()
                
    def set_turn(self, pid):
        self.players[self.current_turn].end_turn()
        
        for i, p in enumerate(self.players):
            if p.pid == pid:
                self.current_turn = i
                self.players[self.current_turn].start_turn()
                
                self.add_log({
                    't': 'nt',
                    'p': self.players[self.current_turn].pid
                })
                
                break
                
    def switch_view(self, pid):
        logs = []
        current_player = self.get_player(self.current_view)
        
        for c in current_player.decks['private'].values():
            logs.append({
                't': 'rc',
                'c': c.cid,
                'd': 'private',
                'exc': pid
            })
            
        for c in current_player.decks['selection'].values():
            logs.append({
                't': 'rc',
                'c': c.cid,
                'd': 'selection',
                'exc': pid
            })

        self.current_view = pid
        p = self.get_player(pid)
        
        for c in p.decks['private'].values():
            logs.append({
                't': 'ac',
                'c': (c.cid, c.name),
                'd': 'private',
                'exc': pid
            })
            
        for c in p.decks['selection'].values():
            logs.append({
                't': 'ac',
                'c': (c.cid, c.name),
                'd': 'selection',
                'exc': pid
            })
            
        for log in logs:
            self.add_log(log)
            
    def add_log(self, log):
        self.log.append(log)

        for p in self.players.copy():
            if p.pid == self.current_view and log.get('exc', p.pid) == p.pid:
                p.log_queue.append(log)
                break
                
    def handel_requests(self):
        while self.request_queue:
            pid, cmd, data = self.request_queue.pop(0)
            
            match cmd:
        
                case 'settings':
                    self.set_settings(data)
                    
                case 'start':
                    self.start(0)
                    
                case 'reset':
                    self.reset()
                    
                case 'play' | 'select':
                    if self.status == 'playing':
                        p = self.get_player(pid)
                        Player.update(p, cmd=cmd, data=data) 
        
    def add_message(self, pid, data):
        text = '-'.join(data)

        if self.status == 'playing' and len(data) == 2 and not data[0]:

            match data[1]:
            
                case 'hint':
                    if self.players[self.current_turn].pid == pid:
                        text = self.get_hint(pid)

        self.add_log({
            't': 'msg',
            'p': pid,
            'text': text
        })
        
    def get_hint(self, pid):
        p = self.get_player(pid)
        choices = self.tree.get_scores(pid)
        choice = max(choices.items(), key=lambda c: c[1])
        
        if not p.played:
            pid, deck, cid, x, y = choice[0]
            deck = 'private' if deck else 'public'
            return f'Play {p.decks[deck][cid].name} at ({x}, {y})'
            
        elif p.active_card:
            pid, cid = choice[0]
            return f"Select {p.decks['selection'][cid].name}"
        
    def main(self):
        self.running_main = True
        self.handel_requests()
        if self.status == 'playing':
            game_base.Game_Base.main(self)
        self.running_main = False
        
