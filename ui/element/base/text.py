import pygame as pg
import pygame.freetype

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
    pg.freetype.init()
    VALID_CHARS = (set(range(32, 384)) | {9, 10})
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
    def render_to(cls, *args, font=None, **kwargs):
        if font is None:
            font = Textbox.FONTS[Textbox.DEFAULT_FONT]
        return font.render_to(*args, **kwargs)

    def __init__(
        self,
        
        text='',
        font_name=pg.freetype.get_default_font(),
        text_size=20,
        line_spacing=1,
  
        text_color=(255, 255, 255),
        text_background_color=None,

        right_aligned=False,
        bottom_aligned=False,
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

        self.text_color = text_color
        self.last_text_color = text_color
        self.text_background_color = text_background_color
        self.text_style = {}

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
    def default_style(self):
        return {
            'fgcolor': self.text_color,
            'bgcolor': self.text_background_color
        }
            
    def get_text(self):
        return self.text
  
    def set_text(self, text, force=False):
        if self.text != text or force:
            self.text = text
            self.fit_text()
            
    def set_value(self, text):
        self.set_text(text)

    def clear_text(self):
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

            surf = pg.Surface(block.rect.size).convert_alpha()
            if self.text_background_color:
                surf.fill(self.text_background_color)
            else:
                surf.fill((0, 0, 0, 0))
            
            block.pos = (0, 0)
            i = 0
            default_style = self.default_style
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

    def render(self):
        self.text_surf.fill((0, 0, 0, 0))
        self.block.pos = (0, 0)
        i = 0
        default_style = self.default_style
        for line in self.block:
            for word in line:
                for character in word:
                    if self.can_render(character.character):
                        self.font.render_to(
                            self.text_surf, 
                            character.rect, 
                            character.character,  
                            size=character.size, 
                            **self.text_style.get(i, default_style)
                        )
                    i += 1
                    
    def draw_text(self, surf):
        if self.text_color != self.last_text_color:
            self.last_text_color = self.text_color
            self.render()
        if self.text:
            surf.blit(self.text_surf, self.text_rect)
