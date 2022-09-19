
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
        self.multiplier = 1
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
            
    def set_owner(self, player):
        self.player = player
        
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
        c.multiplier = self.multiplier
        c.direction = self.direction
        
        c.can_move = self.can_move
        
        if self.player:
            c.player = game.get_player(self.player.pid)
        if self.spot:
            c.spot = game.grid.get_spot(self.spot.pos)
        
        return c

# checking stuff
   
    def check_new(self, card):
        if card.cid not in self.memory:
            self.memory.add(card.cid)
            return True
        
    def move_to(self, pos):
        self.spot.clear_card(kill=False)
        self.game.grid.set_at(pos, self)
        
    def clear(self):
        self.multiplier = 1
        
    def swap_with(self, card):
        s0 = card.spot
        s0.clear_card(kill=False)
        s1 = self.spot
        self.move_to(s0.pos)
        s1.set_card(card)

# overwrite stuff

    def play(self):
        pass
        
    def remove(self):
        pass
        
    def move(self):
        pass
        
    def update(self):
        pass

    def kill(self):
        pass
        
    def select(self, card):
        pass
        
        
        