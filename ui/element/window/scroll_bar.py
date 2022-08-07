import pygame as pg

from ..standard.slider import Slider
from ..standard.button import Button

from ..utils.image import get_arrow

class Scroll_Bar(Slider):
    default_kwargs = {
        'fill_color': (255, 255, 255)
    }
    
    default_handel_kwargs = {
        'fill_color': (100, 100, 100),
        'outline_color': None
    }
    
    default_arrow_kwargs = {
        'size': (16, 16),
        'padding': (6, 6),
        'color': (100, 100, 100),
        'background_color': (255, 255, 255)
    }

    default_button_kwargs = {
        'fill_color': (255, 255, 255),
        'hover_color': (100, 100, 100),
        'layer': -1
    }
    
    def __init__(
        self,
        
        size=(0, 0),
        dir=1,
        scroll_parent=None,
        
        handel_kwargs={},
        arrow_kwargs={},
        button_kwargs={},
        
        **kwargs
    ):

        width, height = size
        if dir and not width:
            width = 16
        elif not height:
            height = 16

        if 'size' not in handel_kwargs:
            if dir:
                handel_kwargs['size'] = (width - 4, 10)
            else:
                handel_kwargs['size'] = (10, height - 4)

        super().__init__(
            size=(width, height),
            dir=dir,
            handel_kwargs=(Scroll_Bar.default_handel_kwargs | handel_kwargs),
            **(kwargs | Scroll_Bar.default_kwargs)
        )
        
        self.scroll_parent = scroll_parent
        
        if dir:
            self.handel.set_limits(top=0, bottom=0)
            
            arrow = get_arrow(
                '^',
                **(Scroll_Bar.default_arrow_kwargs | arrow_kwargs)
            )

            self.up_button = Button.Image_Button(
                image=arrow,
                **(Scroll_Bar.default_button_kwargs | button_kwargs)
            )
            self.up_button.add_event(self.scroll, args=[-1], tag='left_click')

            self.down_button = Button.Image_Button(
                image=pg.transform.flip(arrow, False, True),
                **(Scroll_Bar.default_button_kwargs | button_kwargs)
            )
            self.down_button.add_event(self.scroll, args=[1], tag='left_click')

            self.add_child(
                self.up_button, 
                bottom_anchor='top',
                centerx_anchor='centerx'
            )

            self.add_child(
                self.down_button, 
                top_anchor='bottom',
                centerx_anchor='centerx'
            )
            
        else:
            self.handel.set_limits(left=0, right=0)
            
            arrow = get_arrow(
                '<',
                **(Scroll_Bar.default_arrow_kwargs | arrow_kwargs)
            )
            
            self.left_button = Button.Image_Button(
                image=arrow,
                **(Scroll_Bar.default_button_kwargs | button_kwargs)
            )
            self.left_button.add_event(self.scroll, args=[-1], tag='left_click')
            
            self.right_button = Button.Image_Button(
                image=pg.transform.flip(arrow, True, False),
                **(Scroll_Bar.default_button_kwargs | button_kwargs)
            )
            self.right_button.add_event(self.scroll, args=[1], tag='left_click')
            
            self.add_child(
                self.left_button, 
                right_anchor='left',
                centery_anchor='centery'
            )
            
            self.add_child(
                self.right_button, 
                left_anchor='right',
                centery_anchor='centery'
            )
            
        self.turn_off()
        
    @property
    def size_ratio(self):
        if self.dir:
            return self.handel.rect.height / self.rect.height
        return self.handel.rect.width / self.rect.width
        
    @property
    def scroll_ratio(self):
        if self.dir:
            return round((self.handel.rect.top - self.rect.top) / self.rect.height, 3)
        return round((self.handel.rect.left - self.rect.left) / self.rect.width, 3)
        
    @property
    def full(self):
        return self.size_ratio == 1
        
    def set_size_ratio(self, r):
        if self.dir:
            self.handel.rect.height = min({round(self.rect.height * r), self.rect.height})
        else:
            self.handel.rect.width = min({round(self.rect.width * r), self.rect.width})
        self.handel.set_stuck(False)
        self.handel.update_position()
        self.handel.set_stuck(True)
        
    def set_size(self, size):
        r = self.size_ratio
        if self.dir:
            self.rect.height = size - self.up_button.rect.height - self.down_button.rect.height
        else:
            self.rect.width = size - self.left_button.rect.width - self.right_button.rect.width
        self.set_size_ratio(r)

    def can_scroll_down(self):
        return self.handel.rect.bottom < self.rect.bottom
        
    def can_scroll_up(self):
        return self.handel.rect.top > self.rect.top
        
    def can_scroll_right(self):
        return self.handel.rect.right < self.rect.right
        
    def can_scroll_left(self):
        return self.handel.rect.left > self.rect.left
        
    def scroll(self, dist):
        if self.dir:
            self.handel.move(0, dist * max({self.handel.rect.height / 5, 1}))
        else:
            self.handel.move(dist * max({self.handel.rect.width / 5, 1}), 0)
        self.handel.update_limits()
        self.handel.set_stuck(True)
        
    def go_to_bottom(self):
        self.handel.rect.bottom = self.rect.bottom
        self.handel.set_stuck(True)
            
    def go_to_top(self):
        self.handel.rect.top = self.rect.top
        self.handel.set_stuck(True)
        
    def go_to_right(self):
        self.handel.rect.right = self.rect.right
        self.handel.set_stuck(True)
            
    def go_to_left(self):
        self.handel.rect.left = self.rect.left
        self.handel.set_stuck(True)
        
    def can_scroll(self):
        if self.scroll_parent:
            if self.scroll_parent.rect.collidepoint(pg.mouse.get_pos()):
                return True
        return self.total_rect.collidepoint(pg.mouse.get_pos())

    def update_full(self):
        if self.full:
            self.turn_off()
        else:
            self.turn_on()
        
    def events(self, events):                
        super().events(events)

        mw = events.get('mw')
        if mw:
            if self.can_scroll():
                self.scroll(-mw.y)
        
        
        
        
        
        
        
        
        
        
        
        