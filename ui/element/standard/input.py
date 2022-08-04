import pygame as pg

import pyperclip

from ...math.line import distance

from ..utils.timer import Timer
from ..base.text import Text
from ..base.text_element import Text_Element

class Input(Text_Element):
    VALID_CHARS = set(range(32, 127)) | {9, 10}

    BLINK_TIMER_MAX = 20
    
    default_kwargs = {
        'size': (200, 20),
        'left_pad': 2,
        'right_pad': 2,
        'top_pad': 2,
        'bottom_pad': 2,
        'inf_width': True,
        'fill_color': (255, 255, 255),
        'text_color': (0, 0, 0),
        'cursor': pg.SYSTEM_CURSOR_IBEAM,
        'clip': True
    }

    @classmethod
    def copy(cls, text):
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
        cursor_color=(0, 0, 0),
        cursor_width=2,

        text_check=lambda text: True,
        max_length=None,
        max_lines=100,

        **kwargs
    ):

        if not kwargs.get('text'):
            kwargs['text'] = default
        super().__init__(**(Input.default_kwargs | kwargs))

        self.default = default if default else self.text

        self.selecting = False
        self.held_key = None
        
        self.index = len(self.text)
        self.end_index = self.index
        
        self.highlight_color = highlight_color
        self.highlight_text_color = highlight_text_color
        self.cursor_color = cursor_color
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
                self.block.pos = r.topleft
                c = self._characters[self.index]
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
        super().open()
        self.blink_timer.reset()
        
    def close(self):
        if not self.text:
            self.set_text(self.default)
        super().close()
        self.selecting = False
        self.scroll_offset = [0, 0]
        self.index = 0
        self.end_index = 0
        self.held_key = None
                        
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
        p = (c.rect.x, c.rect.y - (dir * c.size))
        self.set_index(self.get_closest_index(p))

    def get_closest_index(self, p):
        i = min(
            range(len(self.characters) - 1),
            key=lambda i: distance(self.characters[i].rect.midtop, p),
            default=0
        )
        r = self.characters[i].rect
        if p[0] - r.centerx >= 0 and self.characters[i].character.strip():
            i += 1
        return i
        
    def set_text(self, text):
        check = self.text_check(text) and all({ord(c) in Input.VALID_CHARS for c in text})
        length = self.max_length is None or len(text) <= self.max_length
        lines = self.max_lines is None or len(text.splitlines()) <= self.max_lines
        if not text or (check and length and lines):
            super().set_text(text)

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
                self.highlight_section(' \n')
            elif self.clicks == 3:
                self.highlight_section('\n')
                
    def click_up(self, button):
        if button == 1:
            self.selecting = False
                
    def events(self, events):  
        super().events(events)
        
        if events.get('mbd_a') and self.click_close:
            self.close()

        if self.is_open:

            kd = events.get('kd', self.held_key if self.key_timer.time > 15 else None)
            if kd:
                
                if kd.key != getattr(self.held_key, 'key', None):
                    self.held_key = kd
                    self.key_timer.reset()

                if events['ctrl']:
                    if kd.key == pg.K_a:
                        self.highlight_section('')
                    elif kd.key == pg.K_c:
                        Input.copy(self.selected_text)
                    elif kd.key == pg.K_x:
                        self.cut()
                    elif kd.key == pg.K_v:
                        self.remove_selected()
                        self.add_text(Input.paste())
                    events.pop('kd', None)
                                
                elif kd.key == pg.K_RIGHT:
                    self.shift_index_x(1)
                elif kd.key == pg.K_LEFT:
                    self.shift_index_x(-1)
                elif kd.key == pg.K_UP:
                    self.shift_index_y(1)
                elif kd.key == pg.K_DOWN:
                    self.shift_index_y(-1)
                    
                elif kd.key == pg.K_HOME:
                    self.set_index(0)
                elif kd.key == pg.K_END:
                    self.set_index(len(self.text))
            
                elif kd.key == pg.K_BACKSPACE:
                    self.backspace()
                elif kd.key == pg.K_DELETE:
                    self.delete()

                elif kd.key == pg.K_RETURN:
                    if self.max_lines > 1:
                        self.add_text('\n')
                    else:
                        self.run_events('enter')
                        self.close()
                elif kd.key == pg.K_TAB:
                    self.add_text('    ')

                elif kd.unicode:
                    self.add_text(kd.unicode)

            if events.get('ku') and self.held_key:
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
            if self.clip:
                surf.set_clip(self.rect)

            for c in self.selected_characters:
                pg.draw.rect(surf, self.highlight_color, c.rect)
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
        
        
        
        
        
        
        
        