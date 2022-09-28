import pygame as pg

from .base import Base_Loop

class Scene(Base_Loop):
    @classmethod
    def build_and_run(cls, *args, **kwargs):
        m = cls(*args, **kwargs)
        return m.run()

    def __init__(
        self,
        
        init,
        init_args=None,
        init_kwargs=None,
        
        overlay=False,
        opacity=180,

        **kwargs
    ):
        
        super().__init__(**kwargs)
        
        self.init = init
        self.args = init_args or []
        self.kwargs = init_kwargs or {}
        self.return_value = None
        
        self.background = None
        if overlay:
            self.background = self.get_background(opacity)

        self.rect = self.body
        
    @property
    def body(self):
        return self.window.get_rect()
        
    @property
    def all_elements(self):
        elements = set()
        for e in self.elements:
            elements.add(e)
            if hasattr(e, 'all_children'):
                elements |= e.all_children
        return elements
        
    def get_background(self, opacity):
        surf = self.window.copy()
        over = pg.Surface(surf.get_size()).convert_alpha()
        over.fill((0, 0, 0, opacity))
        surf.blit(over, (0, 0))
        return surf
        
    def refresh(self):
        self.elements = self.init(self, *self.args, **self.kwargs)
        self.set_funcs()
        for e in self.elements:
            e.set_scene(self)
        
    def set_funcs(self):
        for e in self.all_elements:
            match e.tag:
                case 'exit':
                    e.add_event(tag='left_click', func=self.exit)
                case 'return':
                    e.add_event(
                        tag='left_click',
                        func=lambda e=e: self.set_return(e.get_return('left_click'))
                    )
                case 'refresh':
                    e.add_event(tag='left_click', func=self.refresh)

    def set_return(self, value):
        self.return_value = value
        
    def get_return(self):
        r = self.return_value
        self.return_value = None
        return r
        
    def quit(self):
        self.close()
        super().quit()
        
    def close(self):
        for e in self.all_elements:
            e.kill()
            
    def __del__(self):
        self.close()
        
    def start_draw(self):
        self.window.fill(self.fill_color)
        if self.background:
            self.window.blit(self.background, (0, 0))
        for e in sorted(self.elements, key=lambda e: e.layer):
            if e.visible:
                e.draw(self.window)
        
    def draw(self):
        self.window.fill(self.fill_color)
        if self.background:
            self.window.blit(self.background, (0, 0))
        for e in sorted(self.elements, key=lambda e: e.layer):
            if e.visible:
                e.draw(self.window)
        pg.display.flip()
        
    def run(self):
        self.refresh()
        self.running = True

        while self.running:
            self.clock.tick(self.fps)
            self.events()
            if not self.running or self.return_value is not None:
                break
            self.update()
            self.draw()
            
        self.close()
        return self.return_value
        
        
        
        
        
        
        
        