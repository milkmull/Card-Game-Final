import pygame as pg

from .style import Style
from .event import Event
from .animation import Animation

from ..utils.timer import Timer

class Element(Style, Event, Animation):
    CLICK_TIMER_MAX = 8
    HOVER_TIMER_MAX = 15
    
    def __init__(
        self,
        
        clip=False,

        hover_color=None,
        cursor=pg.SYSTEM_CURSOR_ARROW,

        **kwargs
    ):
        Style.__init__(self, **kwargs)
        Event.__init__(self)
        Animation.__init__(self)
        
        self.hit = False
        self.is_open = False
        
        self.clip = clip

        self.cursor = cursor

        self.clicks = 1
        self.click_timer = Timer()
        
        if hover_color:
            self.hover_color = hover_color
        
    @property
    def total_rect(self):
        self.update_position()
        return self.outline_rect.unionall([c.total_rect for c in self.children if c.visible])
        
    @property
    def clip_rect(self):
        return self.rect
        
    @property
    def hover_color(self):
        a = self.get_animation_by_name('hover_color')
        if a:
            return a.sequence[0].end
            
    @hover_color.setter
    def hover_color(self, hover_color):
        if hover_color:
            a = self.get_animation_by_name('hover_color')
            if a:
                a.sequence[0].end_value = hover_color
                if self.hit:
                    a.sequence[0].update(1)
            else:
                self.add_animation(
                    [{
                        'attr': 'fill_color',
                        'end': hover_color
                    }],
                    tag='hover',
                    name='hover_color'
                )
        else:
            self.remove_animation('hover_color')

    def open(self):
        self.is_open = True
        self.run_animations('open')
        
    def close(self):
        self.is_open = False
        self.run_animations('open', reverse=True)

    def left_click(self):
        if self.click_timer.time < Element.CLICK_TIMER_MAX:
            self.clicks += 1
        else:
            self.clicks = 1
        self.click_timer.reset()

    def right_click(self):
        pass

    def click_up(self, button):
        pass
        
    def get_hit(self):
        return self.padded_rect.collidepoint(pg.mouse.get_pos())
        
    def events(self, events):
        super().events(events)
        
        last_hit = self.hit
        self.hit = self.get_hit()
        if self.hit:
            if not last_hit:
                self.run_animations('hover')
            if not events['hover']:
                events['hover'] = self
                    
            if not events['cursor_set']:
                pg.mouse.set_cursor(self.cursor)
                events['cursor_set'] = True
                
        elif last_hit:
            self.run_animations('hover', reverse=True)
                
        if not events['clicked']:    
            if self.hit and (mbd := events.get('mbd')):
                events['clicked'] = self
                match mbd.button:
                    case 1:
                        self.left_click()
                        self.run_events('left_click')
                    case 3:
                        self.right_click()
                        self.run_events('right_click')
                        
        if (mbu := events.get('mbu')):
            self.click_up(mbu.button)
            self.run_events('click_up')

    def update(self):
        self.update_animations()
        self.run_events('update')
        super().update()
        self.click_timer.step()

    def draw(self, surf):
        self.draw_rect(surf)
        if self.clip:
            clip = surf.get_clip()
            surf.set_clip(self.clip_rect)
            super().draw(surf)
            surf.set_clip(clip)
        else:
            super().draw(surf)
        