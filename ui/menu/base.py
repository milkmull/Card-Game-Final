import sys

import pygame as pg

class Base_Loop:
    FPS = 30
    TIME_STEP = 1
    LAST_EVENT_BATCH = []
    CTRL = False
    
    @classmethod
    def set_framerate(cls, fps):
        cls.FPS = fps
        cls.TIME_STEP = 30 / fps
    
    @classmethod
    def get_event_batch(cls):
        event_batch = pg.event.get()

        events = {}
        events['all'] = event_batch
        events['p'] = pg.mouse.get_pos()
        for e in event_batch:
            if e.type == pg.QUIT:
                events['q'] = e
            elif e.type == pg.MOUSEBUTTONDOWN:
                events['mbd'] = e
                events['mbd_a'] = e
            elif e.type == pg.MOUSEBUTTONUP:
                events['mbu'] = e
            elif e.type == pg.MOUSEWHEEL:
                events['mw'] = e
            elif e.type == pg.KEYDOWN:
                events['kd'] = e
                if e.key == pg.K_ESCAPE:
                    events['e'] = e
                elif e.key == pg.K_RCTRL or e.key == pg.K_LCTRL:
                    cls.CTRL = True
            elif e.type == pg.KEYUP:
                events['ku'] = e
                if e.key == pg.K_RCTRL or e.key == pg.K_LCTRL:
                    cls.CTRL = False

        events['ctrl'] = cls.CTRL
        cls.LAST_EVENT_BATCH = events.copy()

        return events
    
    def __init__(
        self,
        elements=None,
        fill_color=(0, 0, 0)
    ):
    
        self.running = False
        self.status = 0
        self.window = pg.display.get_surface()
        self.clock = pg.time.Clock()

        self.elements = elements if elements is not None else []
        self.fill_color = fill_color
   
    def set_status(self, status):
        self.status = status
        
    def add_element(self, element):
        self.elements.append(element)
        element.set_scene(self)
        
    def remove_element(self, element):
        while element in self.elements:
            self.elements.remove(element)
            
    def get_events(self):
        return Base_Loop.get_event_batch()
        
    def exit(self, status=0):
        self.running = False
        self.status = status
        
    def quit(self):
        pg.quit()
        sys.exit()
        
    def sub_events(self, events):
        for e in sorted(self.elements, key=lambda e: e.layer, reverse=True):
            if e.enabled:
                e.events(events)
                
    def events(self):
        events = self.get_events()

        if events.get('q'):
            self.quit()
        elif events.get('e'):
            self.exit()
            return

        self.sub_events(events)
        
        if 'cursor_set' not in events:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
            
        return events
        
    def update(self):
        for e in self.elements:
            if e.refresh:
                e.update()
                
    def lite_draw(self):
        for e in sorted(self.elements, key=lambda e: e.layer):
            if e.visible:
                e.draw(self.window)

    def draw(self):
        self.window.fill(self.fill_color)
        for e in sorted(self.elements, key=lambda e: e.layer):
            if e.visible:
                e.draw(self.window)
        pg.display.flip()

    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(Base_Loop.FPS)
            self.events()
            if not self.running:
                break
            self.update()
            self.draw()
        return self.status
