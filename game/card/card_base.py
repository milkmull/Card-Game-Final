
class Card:
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
        self.skip = True

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
        
# copy stuff

    def copy(self, game=None):
        c = type(self)(
            game or self.game,
            self.cid
        )
        c.memory = self.memory.copy()
        c.skip = self.skip
        if self.player:
            c.player = c.game.get_player(self.player.pid)
        if self.spot:
            c.spot = c.game.grid.get_spot(self.spot.pos)
        
        return c

# checking stuff
   
    def check_new(self, card):
        if card.cid not in self.memory:
            self.memory.add(card.cid)
            return True
        
    def move_to(self, pos):
        self.spot.clear_card(remove=False)
        self.game.grid.set_at(pos, self)
        
# overwrite stuff

    def play(self):
        pass
        
    def update(self):
        pass
        
    def uncover(self):
        pass
        
    def remove(self):
        pass
        
        
        