import re
import keyword

import pygame as pg
import pygame.freetype

from ...color.ops import is_light
from ..utils.container import Container
from ...icons.icons import icons

class TextFitError(Exception):
    def __init__(self, text_size, rect_size):
        super().__init__(f'Could not fit text of size {text_size} to rect of size {rect_size}')
            
class Character:
    def __init__(
        self,
        character,
        size,
        font
    ):
        self.character = character
        self.size = size
        self.rect = font.get_rect(character, size=size)
        self.bearing_x, self.bearing_y = self.rect.topleft
        self.font = font
        
    @property
    def metrics(self):
        return self.font.get_metrics(self.character, size=self.size)

    @property
    def horizontal_advance_x(self):
        m = self.font.get_metrics(self.character, size=self.size)[0]
        if m:
            return m[4]
        return self.rect.width
   
    @property
    def pos(self):
        return self.rect.topleft
        
    @pos.setter
    def pos(self, pos):
        self.rect.topleft = pos
        
    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)
        
class Text:
    OUTLINE_CACHE = {}
    pg.freetype.init()
    STYLE_DICT = {
        'normal': 0,
        'strong': 1,
        'oblique': 2,
        'underline': 4,
        'wide': 8,
        'default': 255
    }
    DEFAULT_FONT = pg.freetype.get_default_font()
    FONTS = {
        DEFAULT_FONT: pg.freetype.Font(None),
        'icons.ttf': pg.freetype.Font('ui/icons/icons.ttf')
    }
    for font in FONTS.values():
        font.pad = True

    @classmethod
    def load_font(cls, path):
        name = path.split('/')[-1]
        font = pg.freetype.Font(path)
        font.pad = True
        cls.FONTS[name] = font

    @classmethod
    def get_font(cls, name):
        return cls.FONTS.get(name)
        
    @classmethod
    def render(cls, *args, font_name=None, **kwargs):
        if not (font := cls.FONTS.get(font_name)):
            font = cls.FONTS[cls.DEFAULT_FONT]
        return font.render(*args, **kwargs)[0]
        
    @classmethod
    def render_to(cls, *args, font_name=None, **kwargs):
        if not (font := cls.FONTS.get(font_name)):
            font = cls.FONTS[cls.DEFAULT_FONT]
        return font.render_to(*args, **kwargs)
        
    @classmethod
    def get_outline_points(cls, r):
        points = cls.OUTLINE_CACHE.get(r)
        
        if not points:
            x, y, e = r, 0, 1 - r
            points = []

            while x >= y:
            
                points.append((x, y))
                y += 1
                if e < 0:
                    e += 2 * y - 1 
                else:
                    x -= 1
                    e += 2 * (y - x) - 1
                    
            points += [(y, x) for x, y in points if x > y]
            points += [(-x, y) for x, y in points if x]
            points += [(x, -y) for x, y in points if y]
            points.sort() 
            cls.OUTLINE_CACHE[r] = points
            
        return points
        
    @staticmethod
    def color_text(c):
        return (0, 0, 0) if not is_light(c) else (255, 255, 255)
        
    @staticmethod
    def style_text(text):
        style = {}
        
        number_style = {'fgcolor': (255, 205, 34)}
        for match in re.finditer(r'(?<![a-zA-Z0-9^_])([0-9]+)', text):
            style.update({i: number_style for i in range(match.start(), match.end())})
            
        keyword_style = {'fgcolor': (147, 199, 99), 'style': 1}
        for word in keyword.kwlist:
            for match in re.finditer(fr'(?<![a-zA-Z0-9^_])({word})(?![a-zA-Z0-9^_])', text):
                style.update({i: keyword_style for i in range(match.start(), match.end())})
       
        string_style = {'fgcolor': (236, 118, 0)}
        for match in re.finditer(r'(["\'])(.*?)\1', text):
            style.update({i: string_style for i in range(match.start(), match.end())})
            
        class_style = {'fgcolor': (160, 130, 189), 'style': 1}
        for match in re.finditer(r'(?<=class )([a-zA-Z0-9_]+)', text):
            style.update({i: class_style for i in range(match.start(), match.end())})
            
        def_style = {'fgcolor': (103, 140, 177), 'style': 1}
        for match in re.finditer(r'(?<=def )([a-zA-Z0-9_]+)', text):
            style.update({i: def_style for i in range(match.start(), match.end())})
            
        return style

    def __init__(
        self,
        
        text='',
        font_name=pg.freetype.get_default_font(),
        text_size=20,
        line_spacing=1,
  
        text_color=(255, 255, 255),
        text_background_color=None,
        text_style=None,
        
        text_outline_color=None,
        text_outline_width=0,

        right_aligned=False,
        bottom_aligned=False,
        center_aligned=False,
        centerx_aligned=False,
        centery_aligned=False,

        inf_width=False,
        inf_height=False,
        max_line_width=None,
        wrap=True,
        
        const_size=False,
        auto_fit=False,

        **kwargs
    ):

        self.text = text
        self.original_text = text
        self.font = Text.get_font(font_name)
        self.text_size = text_size
        self.line_spacing = line_spacing

        self._text_color = text_color
        self.text_background_color = text_background_color
        self.text_style = text_style or {}
        
        self.text_outline_color = text_outline_color
        self.text_outline_width = text_outline_width

        self.alignment = {
            'right': False,
            'bottom': False,
            'centerx': False,
            'centery': False
        }
        
        if self.size == (0, 0):
            auto_fit = True
            inf_width = inf_height = True
            
        self.inf_width = inf_width
        self.inf_height = inf_height
        self.max_line_width = max_line_width
        self.wrap = wrap
        
        self.const_size = const_size
        self.auto_fit = auto_fit

        self.block = None
        self._characters = []
        
        if center_aligned:
            centerx_aligned = centery_aligned = True

        self.set_text_alignment(
            left=not (right_aligned or centerx_aligned),
            right=right_aligned,
            top=not (bottom_aligned or centery_aligned),
            bottom=bottom_aligned,
            centerx=centerx_aligned,
            centery=centery_aligned
        )
        
        self.text_surf = None
        self.fit_text()
        
    @property
    def text_rect(self):
        r = self.text_surf.get_rect()
        if self.alignment['right']:
            r.right = self.rect.right
        elif self.alignment['centerx']:
            r.centerx = self.rect.centerx
        else:
            r.left = self.rect.left
        if self.alignment['bottom']:
            r.bottom = self.rect.bottom
        elif self.alignment['centery']:
            r.centery = self.rect.centery
        else:
            r.top = self.rect.top
        return r
        
    @property
    def characters(self):
        self.block.pos = self.text_rect.topleft
        return self._characters
        
    @property
    def lines(self):
        characters = self.characters
        if not characters:
            return []
        
        lines = []
        current_line = []
        top = characters[0].rect.top
        
        for c in characters:
            if c.rect.top == top:
                current_line.append(c)
            else:
                lines.append(current_line)
                current_line = [c]
                top = c.rect.top
        lines.append(current_line)
        
        return lines
  
    @property
    def default_style(self):
        return {
            'fgcolor': self._text_color,
            'bgcolor': self.text_background_color
        }
        
    @property
    def text_color(self):
        return self._text_color
        
    @text_color.setter
    def text_color(self, text_color):
        self._text_color = text_color
        self._render()
            
    def get_text(self):
        return self.text
  
    def set_text(self, text, force=False, style=None):
        if self.text != text or force:
            if style is not None:
                self.text_style = style
            self.text = text
            self.fit_text()
            
    def set_value(self, text):
        self.set_text(text)

    def clear(self):
        self.set_text('')

    def set_text_alignment(
        self,
        left=False,
        right=False,
        top=False,
        bottom=False,
        centerx=False,
        centery=False,
        center=False
    ):
        if center:
            centerx = centery = True
        self.alignment['right'] = right
        self.alignment['bottom'] = bottom
        self.alignment['centerx'] = centerx
        self.alignment['centery'] = centery
        
    def set_text_limits(
        self,
        inf_width=False,
        inf_height=False
    ):
        self.inf_width = inf_width
        self.inf_height = inf_height
        
    def fit_to_text(self, width=True, height=True):
        w, h = self.text_rect.size
        if not width:
            w = self.rect.width
        if not height:
            h = self.rect.height
        self.size = (w, h)
        
    def get_text_rect(self, text=None):
        if text is None:
            text = self.text
        return self.font.get_rect(text, size=self.text_size)

    def get_max_size(self, texts):
        mw = 0
        mh = 0
        for text in texts:
            w, h = self.font.get_rect(text, size=self.text_size).size
            if w > mw:
                mw = w
            if h > mh:
                mh = h
        return (mw, mh)

    def can_render(self, text):
        return all({self.font.get_metrics(c, size=1)[0] or c == '\n' for c in text})
        
    def wrap_to_width(self, text=None, width=0, end='-'):
        text = text or self.text
        width = width or self.max_line_width
        
        new_text = ''
        words = text.split(' ')
        for word in words:
            r = self.get_text_rect(word)
            if r.width <= width:
                new_text += ' ' + word
                continue
                
            current_word = ''
            for char in word:
                r = self.get_text_rect(current_word + char + end)
                if r.width > width:
                    new_text += ' ' + current_word + end
                    current_word = ''
                current_word += char
                
            new_text += ' ' + current_word

        self.set_text(new_text[1:])
        
    def chop_to_width(self, text=None, width=0, end='...'):
        text = text or self.text
        width = width or self.max_line_width
        
        w = self.get_text_rect(text).width
        if w < width:
            return

        while True:
            w = self.get_text_rect(text + end).width
            if w >= width:
                text = text[:-1]
                if not text:
                    break
            else:
                break

        self.set_text(text + end if text else '')

    def fit_text(self):
        lines = [line.split(' ') for line in self.text.splitlines()]
        if not self.text or self.text.endswith('\n'):
            lines.append([''])
            
        if not self.const_size and not self.inf_height:
            size = min({self.rect.height, self.text_size})
        else:
            size = self.text_size
        
        max_width = self.max_line_width or self.rect.width
        max_height = self.rect.height
        block = Container()
        characters = []
        
        while size > 0:
            x = y = 0
            status = 0
            current_line = Container()
            space_width = self.font.get_rect(' ', size=size).width

            for line in lines:
                for word in line:

                    word_rect = self.font.get_rect(word, size=size)

                    if not self.inf_height:
                        if y + word_rect.height > max_height:
                            status = 1
                            break
                            
                    if not self.inf_width or (self.inf_width and self.max_line_width):
                        if x + word_rect.width >= max_width:
                            if not current_line or not self.wrap:
                                status = 2
                                break
                            
                            x = 0
                            y += round(word_rect.height * self.line_spacing)
                            
                            if not self.inf_height:
                                if y + word_rect.height >= max_height:
                                    status = 3
                                    break
                                if x + word_rect.width >= max_width:
                                    status = 4
                                    break

                            block.add(current_line)
                            current_line = Container()
                            
                    word_rect.topleft = (x, y)
                    current_word = Container(rect=word_rect)
                    cx, cy = x, y
                    for character in word + ' ':
                        character = Character(
                            character,
                            size,
                            self.font
                        )
                        character.rect.topleft = (cx, cy)
                        character.rect.x += character.bearing_x
                        current_word.add(character)
                        cx += character.horizontal_advance_x

                    current_line.add(current_word)
                    x += (cx - x)

                if status:
                    break
                    
                x = 0
                y += round(current_word.rect.height * self.line_spacing)
                if current_line:
                    block.add(current_line)
                    current_line = Container()
                    
            if status:
                if self.const_size:
                    raise TextFitError(size, self.rect.size)
                size -= 1
                block.clear()
                continue
            break
            
        if not size or not block:
            surf = pg.Surface((0, 0)).convert()

        else:

            if self.alignment['centerx']:
                for line in block:
                    dx = (self.rect.width - line.rect.width) // 2
                    line.move(dx, 0)
                        
            elif self.alignment['right']:
                for line in block:
                    dx = self.rect.width - line.rect.right
                    line.move(dx, 0)
                        
            if self.alignment['centery']:
                h = sum([line.rect.height for line in block])
                dy = (self.rect.height - h) // 2
                for line in block:
                    line.move(0, dy)
          
            elif self.alignment['bottom']:
                dy = self.rect.height - block.rect.bottom
                for line in block:
                    line.move(0, dy)

            block._rect = block.rect.inflate(2 * self.text_outline_width, 2 * self.text_outline_width)
            surf = pg.Surface(block.rect.size).convert_alpha()
            if self.text_background_color:
                surf.fill(self.text_background_color)
            else:
                surf.fill((0, 0, 0, 0))
            
            block.pos = (0, 0)
            i = 0
            default_style = self.default_style
            
            if self.text_outline_color and self.text_outline_width:
                self.render_outline(surf, block)
            
            for line in block:
                for word in line:
                    for character in word:
                        if self.can_render(character.character):
                            self.font.render_to(
                                surf, 
                                character.rect, 
                                character.character,  
                                size=size, 
                                **self.text_style.get(i, default_style)
                            )
                        characters.append(character)
                        i += 1

        self.block = block
        self._characters = characters
        self.text_surf = surf
        
        if self.auto_fit:
            tl = self.rect.topleft
            self.rect = surf.get_rect()
            self.rect.topleft = tl

    def _render(self):
        self.text_surf.fill((0, 0, 0, 0))
        self.block.pos = (0, 0)
        i = 0
        default_style = self.default_style
        
        if self.text_outline_color and self.text_outline_width:
            self.render_outline(self.text_surf, self.block)

        for line in self.block:
            for word in line:
                for character in word:
                    if self.can_render(character.character):
                        print(default_style)
                        self.font.render_to(
                            self.text_surf, 
                            character.rect, 
                            character.character,  
                            size=character.size, 
                            **self.text_style.get(i, default_style)
                        )
                    i += 1
                    
    def render_outline(self, surf, block):
        points = Text.get_outline_points(self.text_outline_width)
        
        for line in block:
            for word in line:
                for character in word:
                    if self.can_render(character.character):
                        for dx, dy in points:
                            self.font.render_to(
                                surf, 
                                character.rect.move(dx, dy), 
                                character.character,  
                                size=character.size, 
                                fgcolor=self.text_outline_color
                            )  
                    
    def draw_text(self, surf):
        if self.text:
            surf.blit(self.text_surf, self.text_rect)
