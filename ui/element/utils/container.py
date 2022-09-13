import pygame as pg

class Container:
    def __init__(self, rect=None, data=None):
        self._rect = rect
        self._pos = (0, 0)
        self.data = data if data is not None else []
        
    def __bool__(self):
        return bool(self.data)
        
    def __iter__(self):
        return iter(self.data)
        
    def __len__(self):
        return len(self.data)
        
    @property
    def rect(self):
        if self._rect:
            return self._rect
        if self.data:
            return self.data[0].rect.unionall([d.rect for d in self.data])
        return pg.Rect(self._pos, (0, 0))
        
    @property
    def pos(self):
        return self.rect.topleft
        
    @pos.setter
    def pos(self, pos):
        x1, y1 = pos
        x0, y0 = self.pos
        self.move(x1 - x0, y1 - y0)
        self._pos = pos
        
    def add(self, d):
        self.data.append(d)
        
    def clear(self):
        self.data.clear()

    def move(self, dx, dy):
        if self._rect:
            self._rect.move_ip(dx, dy)
        for d in self.data:
            d.move(dx, dy)
            
    def swap(self):
        if not all({isinstance(d, Container) for d in self.data}):
            return Container(rect=self._rect, data=self.data.copy())

        data = []
        for i in range(max({len(d.data) for d in self.data}, default=-1)):
            c = Container()
            for d in self.data:
                if i < len(d.data):
                    c.add(d.data[i])
            data.append(c)
        return Container(rect=self._rect, data=data)