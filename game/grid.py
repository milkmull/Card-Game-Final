
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
    def __init__(self, grid, pos):
        self.grid = grid
        self.pos = pos
        
        self.card = None
        
    def __str__(self):
        return str(self.card)
        
    def __repr__(self):
        return str(self.card)
        
    @property
    def is_open(self):
        return self.card is None
    
    def set_card(self, card):
        self.card = card
        card.spot = self

        self.grid.game.add_log({
            't': 'sc',
            'c': card,
            'o': card.player,
            'p': self.pos
        })
        
    def clear_card(self, remove=True):
        if self.card:
        
            if remove:
                self.card.remove()
                
            self.card.spot = None
            self.card = None

            self.grid.game.add_log({
                't': 'sc',
                'c': None,
                'p': self.pos
            }) 
        
    def get_at(self, spot_string, card=True):
        spot = None
        x, y = self.pos
        
        match spot_string:
            case 'left':
                spot = self.grid.grid.get(y, {}).get(x - 1)
            case 'right':
                spot = self.grid.grid.get(y, {}).get(x + 1)
            case 'top':
                spot = self.grid.grid.get(y - 1, {}).get(x)
            case 'bottom':
                spot = self.grid.grid.get(y + 1, {}).get(x)
            case 'topleft':
                spot = self.grid.grid.get(y - 1, {}).get(x - 1)
            case 'topright':
                spot = self.grid.grid.get(y - 1, {}).get(x + 1)
            case 'bottomleft':
                spot = self.grid.grid.get(y + 1, {}).get(x - 1)
            case 'bottomright':
                spot = self.grid.grid.get(y + 1, {}).get(x + 1)
                
        if not card:
            return spot
        if spot:
            return spot.card

    def get_group(self, group_string, card=True):
        match group_string:
            case 'border':
                return [result for spot_string in Spot.BORDER_STRINGS if (result := self.get_at(spot_string, card=card))]
            case 'corner':
                return [result for spot_string in Spot.CORNER_STRINGS if (result := self.get_at(spot_string, card=card))]
            case 'around':
                return [result for spot_string in Spot.AROUND_STRINGS if (result := self.get_at(spot_string, card=card))]
            
            case 'row':
                if not card:
                    return [spot for spot in self.grid.grid[self.pos[1]].values() if spot is not self]
                return [card for spot in self.grid.grid[self.pos[1]].values() if spot is not self and (card := spot.card)]

            case 'column':
                if not card:
                    spots = []
                    return [row[self.pos[0]] for y, row in self.grid.grid.items() if self.pos[1] != y]
                return [card for y, row in self.grid.grid.items() if self.pos[1] != y and (card := row[self.pos[0]].card)]

class Grid:
    def __init__(self, game, size):
        self.game = game
        self.size = size
        self.grid = {y: {x: Spot(self, (x, y)) for x in range(size[0])} for y in range(size[1])}
        self.spots = [spot for y, row in self.grid.items() for x, spot in row.items()]
        
    @property
    def width(self):
        return self.size[0]
        
    @property
    def height(self):
        return self.size[1]
        
    @property
    def full(self):
        return all({all({spot.card for spot in row.values()}) for row in self.grid.values()})
    
    def copy(self, game):
        g = Grid(game, self.size)
        for y, row in self.grid.items():
            for x, spot in row.items():
                if spot.card:
                    g.grid[y][x].card = spot.card.copy(game=game)
        return g
        
    def in_bounds(self, pos):
        x, y = pos
        w, h = self.size
        return 0 <= x < w and 0 <= y < h
        
    def get_spot(self, pos):
        x, y = pos
        return self.grid[y][x]
        
    def get_open_spots(self):
        return {spot.pos: spot for spot in self.spots if spot.is_open}
        
    def set_at(self, pos, card):
        x, y = pos
        self.grid[y][x].set_card(card)
        
    def clear_at(self, pos):
        x, y = pos
        self.grid[y][x].clear_card(pos)
                
                
                
                