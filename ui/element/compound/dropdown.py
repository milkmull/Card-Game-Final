import pygame as pg

from ..standard.button import Button
from ..standard.image import Image
from ..window.live_window import Live_Window

from ..utils.image import get_arrow, transform, swap_colors
from ...ui import get_size

class Dropdown(Button.Text_Button):
    defaults = {
        'centery_aligned': True
    }
    
    button_defaults = {
        'centery_aligned': True,
        'hover_color': (100, 100, 100)
    }
    
    @staticmethod
    def to_dict(selection):
        return {k: None for k in selection}
        
    @staticmethod
    def find_default(selection, data=None):
        if data is None:
            data = selection
        key = list(selection)[0]
        value = data[key]
        if not value:
            return key
        return Dropdown.find_default(value)
        
    @staticmethod
    def find_all_text(data):
        all = []
        for k, v in data.items():
            all.append(k)
            if v is not None:
                all += Dropdown.find_all_text(v)
        return all

    def __init__(
        self,
        
        selection,
        selected=None,
        
        max_buttons=10,
        
        arrow_kwargs={},
        button_kwargs={},
        window_kwargs={},
        
        **kwargs
        
    ):
    
        if not isinstance(selection, dict):
            selection = Dropdown.to_dict(selection)
        if selected is None:
            selected = Dropdown.find_default(selection)
            
        super().__init__(text=selected, func=self.flip, **(Dropdown.defaults | kwargs))
        
        if self.auto_fit:
            self.auto_fit = False
            self.size = self.get_max_size(self.find_all_text(selection))
            self.width += self.pad['left']
                    
        self.button_kwargs = Dropdown.button_defaults | button_kwargs
        self.window_kwargs = window_kwargs.copy()
        arrow_kwargs = arrow_kwargs.copy()
        
        self.selection = selection
        self.max_buttons = max_buttons
        self.windows = {}
        
        if 'size' not in arrow_kwargs:
            arrow_kwargs['size'] = (self.height - 5, self.height - 5)
        down_arrow = get_arrow(
            'v',
            color=self.text_color,
            **arrow_kwargs
        )
        self.right_arrow = get_arrow(
            '>',
            color=self.button_kwargs.get('text_color', (255, 255, 255)),
            **arrow_kwargs
        )

        self.arrow = Image(
            image=down_arrow,
            cursor=pg.SYSTEM_CURSOR_HAND,
            pad=5,
            enabled=False
        )
        self.add_child(self.arrow, left_anchor='right', centery_anchor='centery')
        self.right_pad = self.arrow.rect.width + 3
        
        self.original_width = self.rect.width
        
    @property
    def text_color(self):
        return self._text_color
        
    @text_color.setter
    def text_color(self, text_color):
        self.arrow.swap_colors(self.text_color, text_color)
        self._text_color = text_color
        self._render()
    
    @property
    def click_close(self):
        return not (self.hit or self.hit_any()) and self.is_open
        
    @property
    def is_open(self):
        return bool(self.windows)
        
    @is_open.setter
    def is_open(self, is_open):
        pass
        
    def set_value(self, val):
        self.set_text(val)
        if self.is_open:
            self.close()

    def flip(self):
        if self.is_open:
            self.close()
        else:
            self.open()
        
    def open(self):
        super().open()
        self.arrow.image = pg.transform.flip(self.arrow.image, False, True)
        self.new_window(self.selection)
        
    def close(self):
        super().close()
        self.arrow.image = pg.transform.flip(self.arrow.image, False, True)
        for w in self.windows:
            self.remove_child(w)
        self.windows.clear()
        
    def new_window(self, data, last=None, level=0):  
        if not data:
            return
            
        found = False
        
        for w, info in self.windows.copy().items():
            if info['level'] >= level:
                self.remove_child(w)
                self.windows.pop(w)
                if (p := info['parent']):
                    p.unfreeze_animations('hover')
                    if not p.hit:
                        p.run_animations('hover', reverse=True)
                    if p is last:
                        found = True
        
        if found:
            return
                   
        buttons = []
        w = max({self.get_max_size(data)[0], self.original_width})
        for k, v in data.items():
            b = Button.Text_Button(
                size=(w, self.rect.height),
                text=k,
                **self.button_kwargs
            )
            b.padding = self.padding
                
            if v is None:
                b.add_event(
                    tag='left_click',
                    func=self.set_value, 
                    args=[k]
                )
            else:
                b.add_event(
                    tag='left_click',
                    func=self.new_window,
                    args=[v],
                    kwargs={'last': b, 'level': level + 1}
                )
                
                i = Image(image=self.right_arrow)
                i.set_enabled(False)
                i.rect.midleft = b.rect.midright
                b.add_child(i, current_offset=True)
                
            buttons.append(b)
            
        h = sum([b.padded_rect.height for b in buttons[:self.max_buttons]])
        window = Live_Window(
            size=(max({b.padded_rect.width for b in buttons}), h),
            **self.window_kwargs
        )

        self.windows[window] = {
            'parent': last,
            'level': level,
        }

        if last is not None:
            window.rect.topleft = (
                last.outline_rect.right + self.pad['left'] + window.outline_width + 2,
                last.outline_rect.top - self.pad['top'] - window.outline_width
            )
            last.freeze_animations('hover')
        else:
            window.rect.midtop = (
                self.padded_rect.centerx,
                self.padded_rect.bottom + self.pad['top'] + window.outline_width + 2
            )
            
        w, h = get_size()
        dy = window.rect.bottom - h
        if dy > 0:
            window.move(0, -dy - 5)
            
        self.add_child(window, current_offset=True)
        window.join_elements(
            buttons,
            borderx=self.pad['left'],
            bordery=self.pad['top'],
            marginx=self.pad['left'],
            marginy=self.pad['top'] + self.pad['bottom']
        )
        
    def events(self, events):
        super().events(events)

        mbd = events.get('mbd')
        if mbd and self.click_close:
            if mbd.button == 1 or mbd.button == 3:
                if self.is_open:
                    self.close()   
        
