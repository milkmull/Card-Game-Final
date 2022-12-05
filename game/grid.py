from .spot import Spot

class Grid:
    def __init__(self, game, size):
        self.game = game
        self.size = size
        self.grid = {y: {x: Spot(self, (x, y)) for x in range(size[0])} for y in range(size[1])}
        self.spots = [spot for y, row in self.grid.items() for x, spot in row.items()]
        self.priority = 0
        
    @property
    def width(self):
        return self.size[0]
        
    @property
    def height(self):
        return self.size[1]
        
    @property
    def full(self):
        return all({all({spot.card for spot in row.values()}) for row in self.grid.values()})
        
    @property
    def cards(self):
        return [spot.card for spot in self.spots if spot.card]
        
    def resize(self, size):
        self.size = size
        self.grid = {y: {x: Spot(self, (x, y)) for x in range(size[0])} for y in range(size[1])}
        self.spots = [spot for y, row in self.grid.items() for x, spot in row.items()]
        
    def reset(self):
        for spot in self.spots:
            spot.card = None
        self.priority = 0
    
    def copy_to(self, game):
        for y, row in self.grid.items():
            for x, spot in row.items():
                if spot.card:
                    game.grid.grid[y][x].card = spot.card.deepcopy(game)
        game.grid.priority = self.priority
        
    def in_bounds(self, pos):
        x, y = pos
        w, h = self.size
        return 0 <= x < w and 0 <= y < h
        
    def get_spot(self, pos):
        x, y = pos
        return self.grid[y][x]
        
    def get_open_spots(self):
        return {spot.pos: spot for spot in self.spots if spot.is_open}
        
    def any_open(self):
        for s in self.spots:
            if not s.card:
                return True
        return False
        
    def get_priority(self):
        p = self.priority
        self.priority += 1
        return p
    
# transforming operations
      
    def shift(self, cards, dir=1):
        for i in range(0, len(cards) - 1, dir):
            c0 = cards[i]
            c1 = cards[(i + 1) % len(cards)]
            c0.swap_with(c1)
            
    def slide(self, card, dir, max_dist=99):
        dx, dy = dir
        assert dx or dy
        x, y = card.spot.pos
        dist = 0
        last_spot = None
 
        while True:
            x += dx
            y += dy
            
            if dist < max_dist and self.in_bounds((x, y)):
                spot = self.get_spot((x, y))
                if not spot.card:
                    last_spot = spot
                    dist += 1
                    continue
                    
            break

        if last_spot:
            card.move_to(last_spot)
            
        return dist
        
# getting group stuff

    def get_spot_group(self, group):
        match group:
            
            case 'all':
                return self.spots.copy()
            case 'corner':
                w, h = self.grid.size
                return [
                    self.grid.grid[0][0], 
                    self.grid.grid[0][w - 1],
                    self.grid.grid[h - 1][0],
                    self.grid.grid[h - 1][w - 1]
                ]
            case 'edge':
                return [s for s in self.spots if s.is_edge]
            case 'open':
                return [s for s in self.spots if s.is_open]
            case 'closed':
                return [s for s in self.spots if not s.is_open]
                
    def get_card_group(self, group, check=lambda c: True):
        return [spot.card for spot in self.get_spot_group(group) if spot.card is not None and check(spot.card)]
                
    def get_row(self, row):
        if 0 <= row < self.height:
            return list(self.grid[row].values())
        raise Exception(f'Row out of bounds: {row}')
        
    def get_column(self, col):
        if 0 <= col < self.width:
            return [row[col] for row in self.grid.values()]
        raise Exception(f'Row out of bounds: {col}')
        
