from .moving_card import Moving_Card
from .points import Points

class Pack:
    def __init__(self, manager):
        self.manager = manager
        
        self.queue = {}
        self.phase = 0
        self.points = {}
        
    @property
    def finished(self):
        return not self.queue

    def add_card(self, *args, **kwargs):
        card = Moving_Card(self, *args, **kwargs)
        
        phase = card.phase
        for _phase, cards in self.queue.items():
            for cid, c in cards.items():
                if c.card.rect.center == card.card.rect.center:
                    if phase <= _phase:
                        phase = _phase + 1   

        if phase not in self.queue:
            self.queue[phase] = {}
        self.queue[phase][card.card.cid] = card
  
        return card
        
    def add_points(self, type, p, card, points, extra=None, target=None):    
        if not (parent_points := self.points.get(card.cid)):
            parent_points = Points(card, p, 0 if extra else points)
            self.points[card.cid] = parent_points
            
        if extra:
            parent_points.add_child_points(points, extra)
            
            if target:
                self.add_points(type, target, extra, -points)
                
        return parent_points
  
    def update(self, phase0):
        for cid, c in list(self.queue[self.phase].items()):
            if c.update():
                self.queue[self.phase].pop(cid)   
                if not c.child:
                    self.manager.cards.pop(cid)
                
        if not phase0:
            if not self.queue[self.phase]:
                self.queue.pop(self.phase)
                if self.queue:
                    self.phase = min(self.queue, default=0)
                    
    def draw(self, surf):   
        for phase, queue in sorted(self.queue.items(), key=lambda item: item[0], reverse=True):
            for cid, c in queue.items():
                if c.visible:
                    c.draw(surf)

class Animation_Manager:
    def __init__(self, client):
        self.client = client
        
        self.cards = {}
        self.queue = {}
        self.points = []
        self.turn = 0

    def add_card(self, *args, **kwargs):
        if not (pack := self.queue.get(self.client.turn)):
            pack = Pack(self)
            self.queue[self.client.turn] = pack
            
        card = pack.add_card(*args, **kwargs)
        
        if (c := self.cards.get(card.card.cid)):
            c.set_child(card)
        self.cards[card.card.cid] = card

        return card
        
    def add_points(self, *args, **kwargs):
        if not (pack := self.queue.get(self.client.turn)):
            pack = Pack(self)
            self.queue[self.client.turn] = pack
            
        return pack.add_points(*args, **kwargs)
        
    def update(self):
        if self.queue:
            turn, pack = min(self.queue.items(), key=lambda item: item[0])
            if turn <= self.client.turn:
                pack.update(turn == self.client.turn)
                if turn < self.client.turn and pack.finished:
                    self.queue.pop(turn)
                    self.points.extend(pack.points.values())
                   
        i = 0
        while i < len(self.points):
            p = self.points[i]
            if p.update():
                self.points.pop(i)
            else:
                i += 1
    
    def draw(self, surf):
        for pack in reversed(self.queue.values()):
            pack.draw(surf)
            
        for p in self.points:
            p.draw(surf)
        
        