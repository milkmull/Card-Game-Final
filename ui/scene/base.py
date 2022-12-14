import sys

import pygame as pg

from .. import ui

cursors = (
    "SYSTEM_CURSOR_ARROW",
    "SYSTEM_CURSOR_IBEAM",
    "SYSTEM_CURSOR_WAIT",
    "SYSTEM_CURSOR_CROSSHAIR",
    "SYSTEM_CURSOR_WAITARROW",
    "SYSTEM_CURSOR_SIZENWSE",
    "SYSTEM_CURSOR_SIZENESW",
    "SYSTEM_CURSOR_SIZEWE",
    "SYSTEM_CURSOR_SIZENS",
    "SYSTEM_CURSOR_SIZEALL",
    "SYSTEM_CURSOR_NO",
    "SYSTEM_CURSOR_HAND"
)

class Base_Loop:
    FPS = 30
    TIME_STEP = 1
    CTRL = False

    @classmethod
    def set_framerate(cls, fps):
        cls.FPS = fps
        cls.TIME_STEP = 30 / fps
    
    @classmethod
    def get_event_batch(cls):
        event_batch = pg.event.get()

        events = {}
        events["all"] = event_batch
        events["p"] = pg.mouse.get_pos()
        
        mbd = False
        mbu = False
        kd = False
        ku = False
        
        for e in event_batch:
        
            match e.type:

                case pg.QUIT:
                    events["q"] = e

                case pg.MOUSEBUTTONDOWN:
                    if not mbd:
                        events["mbd"] = e
                        mbd = True
                    else:
                        pg.event.post(e)
                case pg.MOUSEBUTTONUP:
                    if not mbu:
                        events["mbu"] = e
                        mbu = True
                    else:
                        pg.event.post(e)
                    
                case pg.MOUSEWHEEL:
                    events["mw"] = e
                
                case pg.KEYDOWN:
                    if not kd:
                        events["kd"] = e
                        kd = True
                    else:
                        pg.event.post(e)
                    if e.key == pg.K_ESCAPE:
                        events["e"] = e
                    elif e.key == pg.K_RCTRL or e.key == pg.K_LCTRL:
                        cls.CTRL = True
                case pg.KEYUP:
                    if not ku:
                        events["ku"] = e
                        ku = True
                    else:
                        pg.event.post(e)
                    if e.key == pg.K_RCTRL or e.key == pg.K_LCTRL:
                        cls.CTRL = False
                        
                case pg.TEXTINPUT:
                    events["text"] = e

        events["ctrl"] = cls.CTRL
        events["cursor_set"] = False
        events["clicked"] = None
        events["hover"] = None

        return events
    
    def __init__(
        self,
        fps=None,
        can_quit=True,
        elements=None,
        fill_color=(0, 0, 0)
    ):
    
        self.running = False
        self.status = 0
        self.window = pg.display.get_surface()
        self._scale = (1, 1)
        self.clock = pg.time.Clock()

        self.fps = fps or Base_Loop.FPS
        self.can_quit = can_quit
        self.elements = elements or []
        self.fill_color = fill_color
        
        self.current_events = {}
        
    @property
    def framerate(self):
        return self.clock.get_fps()
            
    def get_scale(self):
        return self._scale

    def set_status(self, status):
        self.status = status
        
    def add_element(self, element):
        self.elements.append(element)
        element.set_scene(self)
        
    def remove_element(self, element):
        while element in self.elements:
            self.elements.remove(element)
        element.set_scene(None)
            
    def get_events(self):
        self.current_events = Base_Loop.get_event_batch()
        return self.current_events
        
    def post_event(self, key, value):
        self.current_events[key] = value
        
    def exit(self):
        self.running = False
        self.status = 1
        
    def quit(self):
        pg.quit()
        sys.exit()
        
    def sub_events(self, events):
        for e in sorted(self.elements, key=lambda e: e.layer, reverse=True):
            if e.enabled:
                e.events(events)
                
    def events(self):
        events = self.get_events()

        if self.can_quit and "q" in events:
            self.quit()

        self.sub_events(events)
        
        if self.can_quit and "e" in events:
            self.exit()
            return {}
        
        if not events["cursor_set"]:
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
            self.clock.tick(self.fps)
            self.events()
            if not self.running:
                break
            self.update()
            self.draw()
        return self.status
