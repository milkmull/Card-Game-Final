from .moving_text import Moving_Text
from .moving_card import Moving_Card
from .points import Points

class Pack:
    def __init__(self, manager):
        self.manager = manager
        
        self.queue = {}
        self.points = {}
        
    @property
    def finished(self):
        return not self.queue

    def add_card(self, *args, **kwargs):
        card = Moving_Card(self, *args, **kwargs)
        
        phase = card.phase
        for _phase, cards in self.queue.items():
            for cid, c in cards.items():
                if c.card == card.card or c.target_rect.center == card.target_rect.center:
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
        if self.queue:
        
            phase, cards = min(self.queue.items(), key=lambda item: item[0])
            for cid, c in list(cards.items()):
                if c.update():
                    cards.pop(cid)   
                    if not c.child:
                        self.manager.cards.pop(cid)
                    if (points := self.points.get(cid)):
                        points.rect.center = c.rect.center
                    
            if not phase0:
                if not cards:
                    self.queue.pop(phase)
                    
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
        self.text = []
        
    @property
    def finished(self):
        return not self.queue and not self.points
        
    def reset(self):
        self.cards.clear()
        self.queue.clear()
        self.points.clear()
        self.text.clear()
        
    def add_text(self, *args, **kwargs):
        t = Moving_Text(*args, **kwargs)
        t.rect.top = self.text[-1].rect.bottom + 10 if self.text else 10
        t.start()
        self.text.append(t)
        
        return t
        
    def shift_text(self, y):
        for t in self.text:
            t.shift(y + 10)

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
        
    def merge_points(self, points):
        for p in points:
            p.start()
            self.points.append(p)
        
    def update(self):  
        i = 0
        while i < len(self.text):
            t = self.text[i]
            if t.update():
                self.text.pop(i)
                self.shift_text(t.rect.height)
            else:
                i += 1
                
        if self.queue and not self.points:
            turn, pack = min(self.queue.items(), key=lambda item: item[0])
            if turn <= self.client.turn:
                pack.update(turn == self.client.turn)
                if turn < self.client.turn and pack.finished:
                    self.queue.pop(turn)
                    self.merge_points(pack.points.values())
                   
        i = 0
        while i < len(self.points):
            p = self.points[i]
            if p.update():
                self.points.pop(i)
            else:
                i += 1
    
    def draw(self, surf):
        for t in self.text:
            t.draw(surf)
            
        for pack in reversed(self.queue.values()):
            pack.draw(surf)
            
        for p in self.points:
            p.draw(surf)
        
        