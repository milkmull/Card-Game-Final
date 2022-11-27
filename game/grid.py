from .spot import Spot

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
    
    def copy_to(self, game):
        for y, row in self.grid.items():
            for x, spot in row.items():
                if spot.card:
                    game.grid.grid[y][x].card = spot.card.deepcopy(game)
        
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
    
# transforming operations
        
    def condense_row(self, spot, side):
        sx, y = spot.pos
        row = self.grid[y]
        open_spots = []
        
        for x, spot in list(row.items())[::side]:
            if x == sx:
                break
                
            if not spot.card:
                open_spots.append(spot)
                
            elif open_spots and spot.card:
                card = spot.card
                spot.clear_card()
                open_spots.pop(0).set_card(card)
                open_spots.append(spot)
                    
    def condense_column(self, spot, side):
        x, sy = spot.pos
        column = {y: self.grid[y][x] for y in range(self.size[1])}
        open_spots = []
        
        for y, spot in list(column.items())[::side]:
            if y == sy:
                break
                
            if not spot.card:
                open_spots.append(spot)
                
            elif open_spots and spot.card:
                card = spot.card
                spot.clear_card()
                open_spots.pop(0).set_card(card)
                open_spots.append(spot)
      
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