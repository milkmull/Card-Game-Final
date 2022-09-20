
class Spot:
    BORDER_STRINGS = (
        'left',
        'top',
        'right',
        'bottom'
    )
    CORNER_STRINGS = (
        'topleft',
        'topright',
        'bottomright',
        'bottomleft'
    )
    AROUND_STRINGS = (
        'topleft',
        'top',
        'topright',
        'right',
        'bottomright',
        'bottom',
        'bottomleft',
        'left'
    )
    X_STRINGS = (
        'left',
        'right'
    )
    Y_STRINGS = (
        'top',
        'bottom'
    )
    
    def __init__(self, grid, pos):
        self.grid = grid
        self.pos = pos
        
        self.card = None
        
    def __str__(self):
        return str(self.pos)
        
    def __repr__(self):
        return str(self.pos)
        
    @property
    def x(self):
        return self.pos[0]
        
    @property
    def y(self):
        return self.pos[1]
        
    @property
    def is_open(self):
        return self.card is None
        
# setting card stuff

    def set_card(self, card):
        self.card = card
        card.spot = self

        self.grid.game.add_log({
            't': 'sc',
            'c': card,
            'o': card.player,
            'p': self.pos
        })
        
    def kill_card(self, other):
        if self.card:
            self.card.kill(other)
            self.clear_card(kill=True)
        
    def clear_card(self, kill=False):
        card = self.card
        card.clear()
        self.card = None

        self.grid.game.add_log({
            't': 'cc',
            'c': card,
            'p': self.pos,
            'k': kill
        })  
        
# getting group stuff
        
    def get_spot_at(self, dir):
        x, y = self.pos
        
        match dir:
            case 'left':
                return self.grid.grid.get(y, {}).get(x - 1)
            case 'right':
                return self.grid.grid.get(y, {}).get(x + 1)
            case 'top':
                return self.grid.grid.get(y - 1, {}).get(x)
            case 'bottom':
                return self.grid.grid.get(y + 1, {}).get(x)
            case 'topleft':
                return self.grid.grid.get(y - 1, {}).get(x - 1)
            case 'topright':
                return self.grid.grid.get(y - 1, {}).get(x + 1)
            case 'bottomleft':
                return self.grid.grid.get(y + 1, {}).get(x - 1)
            case 'bottomright':
                return self.grid.grid.get(y + 1, {}).get(x + 1)
        
    def get_card_at(self, dir):
        spot = self.get_spot_at(dir)
        if spot:
            return spot.card

    def get_spot_group(self, group):
        match group:
            case 'all':
                return [spot for spot in self.grid.spots if spot is not self]
            
            case 'border':
                return [spot for dir in Spot.BORDER_STRINGS if (spot := self.get_spot_at(dir))]
            case 'corner':
                return [spot for dir in Spot.CORNER_STRINGS if (spot := self.get_spot_at(dir))]
            case 'around':
                return [spot for dir in Spot.AROUND_STRINGS if (spot := self.get_spot_at(dir))]
            
            case 'row':
                return [spot for spot in self.grid.grid[self.pos[1]].values() if spot is not self]
            case 'column':
                return [row[self.pos[0]] for y, row in self.grid.grid.items() if self.pos[1] != y]
                
            case 'x':
                return [spot for dir in Spot.X_STRINGS if (spot := self.get_spot_at(dir))]
            case 'y':
                return [spot for dir in Spot.Y_STRINGS if (spot := self.get_spot_at(dir))]
                
    def get_card_group(self, group):
        return [spot.card for spot in self.get_spot_group(group) if spot.card is not None]
                
    def get_direction(self, spot):
        sx, sy = self.pos
        ox, oy = spot.pos
        
        if ox == sx + 1:
            if oy == sy:
                return 'right'
            elif oy == sy + 1:
                return 'bottomright'
            elif oy == sy - 1:
                return 'topright'
        
        elif ox == sx:
            if oy == sy + 1:
                return 'bottom'
            elif oy == sy - 1:
                return 'top'
                
        elif ox == sx - 1:
            if oy == sy:
                return 'left'
            elif oy == sy + 1:
                return 'bottomleft'
            elif oy == sy - 1:
                return 'topleft'
