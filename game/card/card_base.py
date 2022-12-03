
class Card:
    sid = -1
    name = 'base'
    type = 'base'
    weight = 0
    tags = []
    
    @classmethod
    def get_subclasses(cls):
        return cls.__subclasses__()
    
    def __init__(self, game, cid):
        self.game = game
        self.spot = None
        self.player = None

        self.cid = cid
        self.priority = 0
        self.memory = set()
        self.direction = None
        self.wait = None
        
        self.skip_remove = False
        self.skip_move = False
        self.skip_update = False

    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return getattr(other, 'id', None) == self.cid
            
    def __hash__(self):
        return self.cid
        
    @property
    def id(self):
        return self.cid
        
    @property
    def pos(self):
        if self.spot:
            return self.spot.pos
            
    def set_player(self, player):
        self.player = player
        self.wipe_memory()
        
    def swap_player(self, player):
        if self.player:
            player.gain_ownership(self)
            
    def set_priority(self, p):
        self.priority = p
        
    @property
    def multiplier(self):
        multiplier = 1
        for c in self.game.multipliers.values():
            multiplier *= c.multiply(self)
        return multiplier
        
# copy stuff

    def copy(self):
        return type(self)(self.game, self.game.get_new_cid())
        
    def game_copy(self, game):
        return type(self)(game, self.cid)
        
    def player_copy(self):
        c = self.copy()
        c.player = self.player
        return c
        
    def deepcopy(self, game):
        c = type(self)(game, self.cid)
        
        c.memory = self.memory.copy()
        c.priority = self.priority
        c.direction = self.direction
        c.wait = self.wait
        
        c.skip_remove = self.skip_remove
        c.skip_move = self.skip_move
        c.skip_update = self.skip_update
        
        if self.player:
            c.player = game.get_player(self.player.pid)
        if self.spot:
            c.spot = game.grid.grid[self.pos[1]][self.pos[0]]
        
        return c
        
# setup stuff

    def clear(self):
        self.spot = None
        
    def total_clear(self):
        self.end_multiplier()
        self.end_wait()
        self.priority = 0
        self.wipe_memory()
        self.spot = None
        
        self.skip_remove = False
        self.skip_move = False
        self.skip_update = False

    def register(self, card):
        if card:
            if card.cid not in self.memory:
                self.memory.add(card.cid)
                return True
                
    def wipe_memory(self):
        self.memory.clear()

# overwrite stuff

    def multiply(self, card):
        return 1
        
    def run_wait(self, player, card):
        pass

    def play(self):
        pass
        
    def remove(self):
        pass
        
    def move(self):
        pass
        
    def update(self):
        pass

    def kill(self, card):
        if self.spot:
            self.spot.clear_card(kill=True)
        self.total_clear()
        
    def select(self, card):
        pass
        
# other stuff
        
    def move_to(self, spot):
        self.spot.clear_card()
        if spot.is_open:
            spot.set_card(self)
            
    def move_in(self, dir):
        result = False
        
        spot = self.spot.get_spot_at(dir)
        if spot and spot.is_open:
            self.spot.clear_card()
            spot.set_card(self)
            result = True
        
        return result
   
    def swap_with(self, card):
        if card is self:
            return
        
        new_spot = card.spot
        last_spot = self.spot
        
        new_spot.clear_card()
        self.move_to(new_spot)
        last_spot.set_card(card)
        
    def start_multiplier(self):
        self.game.add_multiplier(self)
        
    def end_multiplier(self):
        self.game.remove_multiplier(self)
        
    def start_wait(self, wait):
        self.wait = wait
        self.game.add_wait(self)
        
    def end_wait(self):
        self.game.remove_wait(self)
        self.wait = None
        