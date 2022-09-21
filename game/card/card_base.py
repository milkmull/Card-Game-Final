
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
        self.memory = set()
        self.direction = None
        self.can_move = False

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
        c.direction = self.direction
        c.can_move = self.can_move
        
        if self.player:
            c.player = game.get_player(self.player.pid)
        if self.spot:
            c.spot = game.grid.grid[self.pos[1]][self.pos[0]]
        
        return c
        
# setup stuff

    def clear(self):
        self.spot = None

    def register(self, card):
        if card:
            if card.cid not in self.memory:
                self.memory.add(card.cid)
                return True

# overwrite stuff

    def multiply(self, card):
        return 1

    def play(self):
        pass
        
    def remove(self):
        pass
        
    def move(self):
        pass
        
    def update(self):
        pass

    def kill(self, card):
        pass
        
    def select(self, card):
        pass
        
# other stuff
        
    def move_to(self, spot):
        self.spot.clear_card()
        if spot.is_open:
            spot.set_card(self)
   
    def swap_with(self, card):
        new_spot = card.spot
        last_spot = self.spot
        
        new_spot.clear_card()
        self.move_to(new_spot)
        last_spot.set_card(card)
        
        
        