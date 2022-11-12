import pygame as pg

import pyperclip

from ..base.text import Text
from ..base.text_element import Text_Element

from ...math.line import distance
from ..utils.timer import Timer

class Input(Text_Element):
    BLINK_TIMER_MAX = 20
    
    defaults = {
        'size': (200, 20),
        'left_pad': 2,
        'right_pad': 2,
        'top_pad': 2,
        'bottom_pad': 2,
        'inf_width': True,
        'centery_aligned': True,
        'fill_color': (255, 255, 255),
        'text_color': (0, 0, 0),
        'cursor': pg.SYSTEM_CURSOR_IBEAM,
        'clip': True,
        'max_lines': 1
    }

    @classmethod
    def copy(cls, text):
        if text:
            pyperclip.copy(text)
    
    @classmethod
    def paste(cls): 
        return pyperclip.paste()
        
    @classmethod
    def num_input(cls, **kwargs):
        return cls(text_check=lambda text: text.isnumeric(), **kwargs)
        
    @classmethod
    def signed_num_input(cls, **kwargs):
        return cls(text_check=lambda text: f"{text.lstrip('-+')}0".isnumeric(), **kwargs)

    def __init__(
        self,
        default='',
        
        highlight_color=(0, 100, 255),
        highlight_text_color=(0, 0, 0),
        cursor_color=None,
        cursor_width=2,

        text_check=lambda text: True,
        max_length=None,
        max_lines=100,

        **kwargs
    ):

        if not kwargs.get('text'):
            kwargs['text'] = default
        super().__init__(**(Input.defaults | kwargs))

        self.default = default or self.text

        self.selecting = False
        self.held_key = None
        
        self.index = len(self.text)
        self.end_index = self.index
        
        self.highlight_color = highlight_color
        self.highlight_text_color = highlight_text_color
        self.cursor_color = cursor_color or self.text_color
        self.cursor_width = cursor_width
        
        self.text_check = text_check
        self.max_length = max_length
        self.max_lines = max_lines
        
        self.key_timer = Timer()
        self.blink_timer = Timer(
            start_time=-Input.BLINK_TIMER_MAX,
            stop_time=Input.BLINK_TIMER_MAX
        )
        
        self.scroll_offset = [0, 0]
        
    @property
    def click_close(self):
        return not self.hit and self.is_open
        
    @property
    def can_scroll_x(self):
        return self.inf_width and not (self.alignment['right'] or self.alignment['centerx'])
        
    @property
    def can_scroll_y(self):
        return self.inf_height and not (self.alignment['bottom'] or self.alignment['centery'])
        
    @property
    def text_rect(self):
        r = super().text_rect
        if self.is_open:
            
            if self.can_scroll_x:
                r.left = self.rect.left - self.scroll_offset[0]
            if self.can_scroll_y:
                r.top = self.rect.top - self.scroll_offset[1]
            self.block.pos = r.topleft
            c = self._characters[self.index]

            if self.can_scroll_x:
                if not self.rect.collidepoint(c.rect.midleft):
                    if c.rect.left < self.rect.left:
                        r.x += self.rect.left - c.rect.left
                    else:
                        r.x += self.rect.right - c.rect.left - self.cursor_width
                if r.right <= self.rect.right and r.left < self.rect.left:
                    r.right = self.rect.right - self.cursor_width
                if r.left > self.rect.left:
                    r.left = self.rect.left
                self.scroll_offset[0] = self.rect.left - r.left
                
            if self.can_scroll_y:
                if not self.rect.collidepoint(c.rect.midtop):
                    if c.rect.top < self.rect.top:
                        r.y += self.rect.top - c.rect.top
                    else:
                        r.y += self.rect.bottom - c.rect.top - c.rect.height
                if r.bottom <= self.rect.bottom and r.top < self.rect.top:
                    r.bottom = self.rect.bottom
                if r.top > self.rect.top:
                    r.top = self.rect.top
                self.scroll_offset[1] = self.rect.top - r.top

        return r
                
    @property
    def selected(self):
        return self.index != self.end_index
        
    @property
    def selected_characters(self):
        i = self.index
        j = self.end_index
        if i > j:
            i, j = j, i
        return self.characters[i:j]
        
    @property
    def selected_text(self):
        return ''.join([c.character for c in self.selected_characters])
        
    def open(self):
        self.is_open = True
        self.blink_timer.reset()
        self.index = len(self.text)
        
    def close(self):
        if not self.text:
            self.set_text(self.default)
        self.is_open = False
        self.selecting = False
        self.scroll_offset = [0, 0]
        self.index = 0
        self.end_index = 0
        self.held_key = None
        self.run_events('close')
                        
    def set_index(self, index):
        if index < 0:
            index = 0 
        elif index > len(self.text):
            index = len(self.text)
        self.index = index
        if not self.selecting:
            self.end_index = index
        self.blink_timer.reset()
            
    def shift_index_x(self, dir):
        if self.index == self.end_index:
            self.set_index(self.index + dir)
        elif dir == 1:
            self.set_index(max({self.index, self.end_index}))
        elif dir == -1:
            self.set_index(min({self.index, self.end_index}))
            
    def shift_index_y(self, dir):
        c = self.characters[self.index]
        
        lines = self.lines
        if not lines:
            return
        
        for i, line in enumerate(lines):
            if c in line:
                break

        i += dir
        if not -1 < i < len(lines):
            return
        
        line = lines[i]
        r = line[0].rect.unionall([o.rect for o in line])
        p = [c.rect.x, c.rect.centery + (dir * c.rect.height)]
        if p[0] < r.left:
            p[0] = r.left
        elif p[0] > r.right:
            p[0] = r.right

        self.set_index(self.get_closest_index(p))

    def get_closest_index(self, p):
        i = min(
            range(len(self.characters) - 1),
            key=lambda i: distance(self.characters[i].rect.center, p),
            default=0
        )
        r = self.characters[i].rect
        if p[0] - r.centerx >= 0 and self.characters[i].character.strip():
            i += 1
        return i
        
    def set_text(self, text):
        check = self.text_check(text) and self.can_render(text)
        length = self.max_length is None or len(text) <= self.max_length
        lines = self.max_lines is None or len(text.splitlines()) <= self.max_lines
        if not text or (check and length and lines):
            super().set_text(text)
            
    def clear(self):
        self.set_text('')
        self.set_index(0)

    def add_text(self, text):
        if self.selected:
            self.remove_selected()
        self.set_text(self.text[:self.index] + text + self.text[self.index:])
        self.set_index(self.index + len(text))
        
    def backspace(self):
        if self.selected:
            self.remove_selected()
        elif self.index > 0:
            self.set_text(self.text[:self.index - 1] + self.text[self.index:])
            self.set_index(self.index - 1)
        
    def delete(self):
        if self.selected:
            self.remove_selected()
        else:
            self.set_text(self.text[:self.index] + self.text[self.index + 1:])
        
    def remove_selected(self):
        i = self.index
        j = self.end_index
        if i > j:
            i, j = j, i
        self.set_text(self.text[:i] + self.text[j:])
        if self.index > self.end_index:
            self.set_index(self.end_index)
        else:
            self.end_index = self.index
            
        self.selecting = False
        
    def cut(self):
        Input.copy(self.selected_text)
        self.remove_selected()
        
    def highlight_section(self, dividers):
        start = end = self.index
        while start > 0 and self.text[start - 1] not in dividers:
            start -= 1
        while end < len(self.text) and self.text[end] not in dividers:
            end += 1
        self.set_index(end)
        self.end_index = start

    def left_click(self):
        super().left_click()

        if self.clicks == 1:
            if not self.is_open:
                self.open()
            self.set_index(self.get_closest_index(pg.mouse.get_pos()))
            self.selecting = True
        elif self.is_open:
            if self.clicks == 2:
                self.highlight_section(',;:.?!(){}[] \n')
            elif self.clicks == 3:
                self.highlight_section('\n')
                
    def click_up(self, button):
        if button == 1:
            self.selecting = False
                
    def events(self, events):  
        super().events(events)
        
        if 'mbd' in events and self.click_close:
            self.close()

        if self.is_open:

            if events.get('text'):
                self.add_text(events['text'].text)
                self.held_key = None

            kd = events.get('kd', self.held_key if self.key_timer.time > 15 else None)
            if kd:
                
                if kd.key != getattr(self.held_key, 'key', None):
                    self.held_key = kd
                    self.key_timer.reset()

                if events['ctrl']:
                    match kd.key:
                        case pg.K_a:
                            self.highlight_section('')
                        case pg.K_c:
                            Input.copy(self.selected_text)
                        case pg.K_x:
                            self.cut()
                        case pg.K_v:
                            self.remove_selected()
                            self.add_text(Input.paste())
                    
                else:
                    
                    match kd.key:
                                
                        case pg.K_RIGHT:
                            self.shift_index_x(1)
                        case pg.K_LEFT:
                            self.shift_index_x(-1)
                        case pg.K_UP:
                            self.shift_index_y(-1)
                        case pg.K_DOWN:
                            self.shift_index_y(1)
                            
                        case pg.K_HOME:
                            self.set_index(0)
                        case pg.K_END:
                            self.set_index(len(self.text))
                    
                        case pg.K_BACKSPACE:
                            self.backspace()
                        case pg.K_DELETE:
                            self.delete()

                        case pg.K_RETURN:
                            if self.max_lines > 1:
                                self.add_text('\n')
                            else:
                                self.run_events('enter')
                        case pg.K_TAB:
                            self.add_text('    ')
                    
                events.pop('kd', None)

            if 'ku' in events and self.held_key:
                self.held_key = None
                    
            if self.selecting:
                self.set_index(self.get_closest_index(pg.mouse.get_pos()))

        super().events(events)
        
    def update(self):
        super().update()
        self.key_timer.step()
        if self.is_open:
            self.blink_timer.step()
        
    def draw(self, surf):
        super().draw(surf)

        if self.is_open:
            
            clip = surf.get_clip()
            surf.set_clip(self.rect)

            for c in self.selected_characters:
                pg.draw.rect(
                    surf,
                    self.highlight_color,
                    c.rect.inflate(2 * self.text_outline_width, 2 * self.text_outline_width)
                )
            for c in self.selected_characters:
                s = self.font.render(
                    c.character,
                    size=c.size,
                    fgcolor=self.highlight_text_color
                )[0]
                surf.blit(s, c.rect)


            if self.blink_timer.time < 0:
                r = self.characters[self.index].rect
                pg.draw.line(
                    surf,
                    self.cursor_color,
                    r.topleft,
                    r.bottomleft,
                    width=self.cursor_width
                )
            
            surf.set_clip(clip)
        
     