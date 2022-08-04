import pygame as pg

from ..utils.timer import Timer

class Dragger:
    DRAGGERS = []
    LAST_LOG = {'type': 'carry', 'draggers': set()}
    
    @classmethod
    def select_all(cls):
        for d in cls.DRAGGERS:
            d.select()
    
    @classmethod
    def start_held_all(cls, all=all):
        for d in cls.DRAGGERS:
            if d.selected and not d.held:
                d.start_held(all=all)
                d.deselect_on_update = False
                
    @classmethod
    def get_selected(cls):
        return [d for d in cls.DRAGGERS if d.selected]
                
    @classmethod
    def reset(cls):
        cls.DRAGGERS.clear()
        
    @classmethod
    def get_logs(cls):
        logs = {'type': 'carry', 'draggers': cls.LAST_LOG['draggers'].copy()}
        cls.LAST_LOG['draggers'].clear()
        return [logs]
    
    def __init__(
        self,
        select_color=(255, 0, 0)
    ):
    
        self.held = False
        self.selected = False
        self.deselect_on_update = False
        self.hover = False
        self.stuck = False
        
        self.rel_pos = (0, 0)
        self.pickup_pos = None
        self.held_timer = Timer()  

        self.select_color = select_color        
        
        Dragger.DRAGGERS.append(self)
        
    @property
    def carry_dist(self):
        if not self.pickup_pos:
            return (0, 0)
        return (
            self.rect.x - self.pickup_pos[0],
            self.rect.y - self.pickup_pos[1]
        )

    def set_rel_pos(self):
        p = pg.mouse.get_pos()
        self.rel_pos = (
            p[0] - self.rect.x,
            p[1] - self.rect.y
        )
        
    def start_held(self, all=False):
        if not self.stuck:
            self.held = True
            
            if self.selected:
                if not all:
                    Dragger.start_held_all(all=True)
            else:
                self.selected = True

            self.set_rel_pos()
            self.pickup_pos = self.rect.topleft
   
    def drop(self):
        self.held = False
        self.held_timer.reset()
        
        if any(self.carry_dist):
            Dragger.LAST_LOG['draggers'].add(self)
        
    def select(self):
        self.selected = True
        
    def deselect(self):
        self.held = False
        self.selected = False
        self.held_timer.reset()
        
    def kill(self):
        super().kill()
        Dragger.DRAGGERS.remove(self)
        
    def update_drag(self):   
        if self.held:
            self.held_timer.step()
            
        dx = 0
        dy = 0

        if self.held and self.held_timer.time >= 4:
            x0, y0 = self.rect.topleft
            px, py = pg.mouse.get_pos()
            rx, ry = self.rel_pos
            self.rect.x = px - rx
            self.rect.y = py - ry
            x1, y1 = self.rect.topleft
            
            dx = x1 - x0
            dy = y1 - y0
            
        return (dx, dy)
        
    def left_click(self):
        super().left_click()
        self.start_held()
        
    def events(self, events):
        super().events(events)

        if not events['ctrl'] and not self.hit:
            mbd = events.get('mbd_a')
            if mbd:
                if mbd.button == 1:
                    self.deselect_on_update = True
                
        elif events['ctrl']:
            kd = events.get('kd')
            if kd:
                if kd.key == pg.K_a:
                    Dragger.select_all()
                    events.pop('kd')

        mbu = events.get('mbu')
        if mbu:
            self.drop()
        
    def update(self):
        if self.deselect_on_update:
            if not self.held:
                self.deselect()
            self.deselect_on_update = False
            
        self.update_drag()
        super().update()
        
    def draw_outline(self, surf):
        if self.selected:
            pg.draw.rect(
                surf,
                self.select_color,
                self.outline_rect.inflate(6, 6)
            )
        
        