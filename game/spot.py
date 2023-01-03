import math

class Spot:
    BORDER_STRINGS = (
        "left",
        "top",
        "right",
        "bottom"
    )
    CORNER_STRINGS = (
        "topleft",
        "topright",
        "bottomright",
        "bottomleft"
    )
    AROUND_STRINGS = (
        "topleft",
        "top",
        "topright",
        "right",
        "bottomright",
        "bottom",
        "bottomleft",
        "left"
    )
    X_STRINGS = (
        "left",
        "right"
    )
    Y_STRINGS = (
        "top",
        "bottom"
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
        
    @property
    def is_corner(self):
        x, y = self.pos
        w, h = self.grid.size
        
        return (y == 0 or y + 1 == h) and (x == 0 or x + 1 == w)
        
    @property
    def is_edge(self):
        x, y = self.pos
        w, h = self.grid.size
        
        return (y == 0 or y + 1 == h or x == 0 or x + 1 == w)
        
# setting card stuff

    def set_card(self, card, parent=None):
        self.card = card
        card.spot = self

        self.grid.game.add_log({
            "t": "sc",
            "c": (card.cid, card.name),
            "p": card.player.pid,
            "pos": self.pos,
            "parent": parent.cid if parent else None
        })
        
    def clear_card(self, kill=False):
        card = self.card
        self.card = None

        self.grid.game.add_log({
            "t": "cc",
            "c": card.cid,
            "pos": self.pos,
            "k": kill
        })  
        
# getting group stuff
        
    def get_spot_at(self, dir):
        if dir is None:
            return
            
        x, y = self.pos
        
        match dir:
            case "left":
                return self.grid.grid.get(y, {}).get(x - 1)
            case "right":
                return self.grid.grid.get(y, {}).get(x + 1)
            case "top" | "up":
                return self.grid.grid.get(y - 1, {}).get(x)
            case "bottom" |"down":
                return self.grid.grid.get(y + 1, {}).get(x)
            case "topleft":
                return self.grid.grid.get(y - 1, {}).get(x - 1)
            case "topright":
                return self.grid.grid.get(y - 1, {}).get(x + 1)
            case "bottomleft":
                return self.grid.grid.get(y + 1, {}).get(x - 1)
            case "bottomright":
                return self.grid.grid.get(y + 1, {}).get(x + 1)
                
        raise Exception(f"Invalid direction: {dir}")
        
    def get_card_at(self, dir, check=lambda c: True):
        spot = self.get_spot_at(dir)
        if spot and spot.card and check(spot.card):
            return spot.card

    def get_spot_group(self, group):
        match group:
            case "border":
                return [spot for dir in Spot.BORDER_STRINGS if (spot := self.get_spot_at(dir))]
            case "corner":
                return [spot for dir in Spot.CORNER_STRINGS if (spot := self.get_spot_at(dir))]
            case "around":
                return [spot for dir in Spot.AROUND_STRINGS if (spot := self.get_spot_at(dir))]
            
            case "row":
                return [spot for spot in self.grid.grid[self.pos[1]].values() if spot is not self]
            case "column":
                return [row[self.pos[0]] for y, row in self.grid.grid.items() if self.pos[1] != y]
                
            case "x":
                return [spot for dir in Spot.X_STRINGS if (spot := self.get_spot_at(dir))]
            case "y":
                return [spot for dir in Spot.Y_STRINGS if (spot := self.get_spot_at(dir))]
                
        raise Exception(f"Invalid group: {group}")
                
    def get_card_group(self, group, check=lambda c: True):
        return [spot.card for spot in self.get_spot_group(group) if spot.card and check(spot.card)]
        
    def get_global_spot_group(self, group, include_self=False):
        spots = self.grid.get_spot_group(group)
        if not include_self and self in spots:
            spots.remove(self)
        return spots
        
    def get_global_card_group(self, group, include_self=False, check=lambda c: True):
        return [spot.card for spot in self.get_global_spot_group(group, include_self=include_self) if spot.card and check(spot.card)]
                
    def get_direction(self, spot):
        sx, sy = self.pos
        ox, oy = spot.pos
        
        if ox == sx + 1:
            if oy == sy:
                return "right"
            elif oy == sy + 1:
                return "bottomright"
            elif oy == sy - 1:
                return "topright"
        
        elif ox == sx:
            if oy == sy + 1:
                return "bottom"
            elif oy == sy - 1:
                return "top"
                
        elif ox == sx - 1:
            if oy == sy:
                return "left"
            elif oy == sy + 1:
                return "bottomleft"
            elif oy == sy - 1:
                return "topleft"
    
    def cards_from_vector(self, dir, steps=1, da=360, check=lambda c: True, stop_on_empty=False, stop_on_fail=False, reverse=False):    
        cards = []
            
        sx, sy = self.pos
        dx, dy = dir
        if dx == dy == 0:
            return cards

        angle =  round(math.degrees(math.atan2(dy, dx)))
        if angle < 0:
            angle += 360
        assert not angle % 45
        dr = math.radians(da)
        rcos = math.cos(dr)
        rsin = math.sin(dr)
        
        if steps == -1:
            steps = math.inf

        for angle in range(angle, angle + 360, da):
            
            step = 0
            x = sx + dx
            y = sy + dy
        
            while step < steps:
                
                spot = self.grid.grid.get(y, {}).get(x)
                if spot is None:
                    break
                    
                if (card := spot.card):
                    if check(card):
                        cards.append(card)
                    elif stop_on_fail:
                        break
                elif stop_on_fail or stop_on_empty:
                    break
                        
                x += dx
                y += dy
                step += 1
    
            ndx = round((dx * rcos) - (dy * rsin))
            ndy = round((dx * rsin) + (dy * rcos))
            dx, dy = ndx, ndy
            
        if reverse:
            cards.reverse()

        return cards