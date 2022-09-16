import os
import shutil
import ast

import pygame as pg

from data.constants import CONSTANTS, CUSTOM_IMG_PATH, CUSTOM_SND_PATH, TEMP_SND_PATH

from node.node.node_base import pack
from node.compiler import Compiler
from node.tester import tester

from ui.menu.templates.notice import Notice

from ui.element.base.image_element import Image_Element
from ui.element.base.style import Style
from ui.element.elements import Textbox, Image, Button, Input

from .elements.fitted_image import Fitted_Image

CARD_SIZE = CONSTANTS['card_size']
CARD_WIDTH, CARD_HEIGHT = CARD_SIZE
IMAGE_SIZE = (CARD_WIDTH - 75, 210)

def is_valid_code(code):
    try:
        ast.parse(code)
    except SyntaxError:
        return False
    return True
    
class Card(Image_Element):
    @classmethod
    def build_card(cls, info):
        return cls(**info).get_card_image()
   
    def __init__(
        self,
        
        name='name',
        type='play',
        description='description',
        tags=None,
        color=[161, 195, 161],
        id=None, 
        
        image='',
        keep_aspect=False,
        rotation=0,
        outline=True,

        sound=None,
        
        node_data={},
        weight=1,
        code='',
        lines=(0, 0),
        published=False,
        
        **kwargs
    ):

        self.sound = sound
        self.cid = id
        self.node_data = node_data
        self.weight = weight
        self.code = code
        self.lines = lines
        self.published = published
        
        if tags is None:
            tags = []

        card_image = pg.Surface(CARD_SIZE).convert_alpha()
        card_image.fill((50, 50, 50))
        super().__init__(image=card_image)

        self.elements_dict = {}

        bg = Style(
            size=self.rect.inflate(-30, -30).size,
            fill_color=color,
        )
        bg.rect.center = self.rect.center
        self.add_child(bg, current_offset=True)
        self.elements_dict['bg'] = bg
        
        style_kwargs = {
            'outline_width': 2,
            'outline_color': (0, 0, 0),
        }
        
        text_kwargs = {
            'fill_color': (255, 255, 255),
            'text_color': (0, 0, 0),
            'pad': 5,
            'inf_width': False,
            'inf_height': False,
            'centerx_aligned': True,
            'centery_aligned': True
        }

        name = Input(
            size=(245, 30), 
            text=name,
            text_size=30,
            max_length=30,
            max_lines=1,
            **text_kwargs,
            **style_kwargs
        )
        name.rect.centerx = bg.rect.centerx
        name.rect.y = 35
        self.add_child(name, current_offset=True)
        self.elements_dict['name'] = name

        pic = Fitted_Image(
            image=(pg.image.load(image) if image else pg.Surface(IMAGE_SIZE)).convert_alpha(),
            size=IMAGE_SIZE,
            keep_aspect=keep_aspect,
            rotation=rotation,
            outline_color=(0, 0, 0) if outline else None,
            outline_width=2
        )
        pic.rect.centerx = bg.rect.centerx
        pic.rect.y = name.rect.bottom + 15
        self.elements_dict['pic'] = pic
        self.add_child(pic, current_offset=True)

        desc = Input(
            size=(245, 160),
            text=description,
            text_size=25,
            max_length=300,
            max_lines=5,
            **text_kwargs,
            **style_kwargs
        )
        desc.rect.centerx = bg.rect.centerx
        desc.rect.y += 305
        self.add_child(desc, current_offset=True)
        self.elements_dict['desc'] = desc
        
        text_kwargs['pad'] = 1

        type = Textbox(
            size=((pic.rect.width // 3) - 20, 20),
            text=type,
            text_size=45,
            **text_kwargs,
            **style_kwargs
        )
        type.rect.x = pic.rect.x + 5
        type.rect.y += 480
        self.add_child(type, current_offset=True)
        self.elements_dict['type'] = type

        tags = Textbox(
            size=(pic.rect.width - type.rect.width - 20, 20),
            text=str(tags).replace("'", '') if tags else '', 
            text_size=45,
            **text_kwargs,
            **style_kwargs
        )
        tags.rect.right = pic.rect.right - 5
        tags.rect.y += 480
        self.add_child(tags, current_offset=True)
        self.elements_dict['tags'] = tags

    @property
    def id(self):
        return self.cid
      
    @property
    def name(self):
        return self.elements_dict['name'].text.strip()
        
    @property
    def type(self):
        return self.elements_dict['type'].text
        
    @property
    def description(self):
        return self.elements_dict['desc'].text.strip()
        
    @property
    def tags(self):
        return [tag for tag in self.elements_dict['tags'].text.strip('[]').split(', ') if tag]
        
    @property
    def classname(self):
        cname = ''
        for char in self.name.title().replace(' ', '_'):
            if char.isalnum() or char == '_':
                cname += char
                
        if cname[0].isnumeric():
            cname = '_' + cname

        return cname
        
    @property
    def color(self):
        return list(self.elements_dict['bg'].fill_color)
        
    @property
    def pic(self):
        return self.elements_dict['pic'].original_image
        
    @property
    def image_path(self):
        return f'{CUSTOM_IMG_PATH}{self.cid}.png'
        
    @property
    def sound_path(self):
        return f'{CUSTOM_SND_PATH}{self.cid}.wav'
        
    def get_info(self):
        info = {
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'tags': self.tags, 
            'color': self.color, 
            'image': self.image_path,
            'keep_aspect': self.elements_dict['pic'].keep_aspect,
            'rotation': self.elements_dict['pic'].rotation,
            'outline': bool(self.elements_dict['pic'].outline_color),
            'sound': self.sound,
            'id': self.cid,
            'weight': self.weight, 
            'classname': self.classname, 
            'custom': True,
            'code': self.code,
            'lines': self.lines,
            'published': self.published,
            'node_data': self.node_data
        }
        return info
 
    def is_user(self):
        return self.cid == 0
        
    def set_color(self, color):
        self.elements_dict['bg'].fill_color = color
            
    def update_image(self, img):
        self.elements_dict['pic'].set_image(img, overwrite=True)
        
    def clear_image(self):
        self.elements_dict['pic'].fill(self.color)
        
    def set_image_keep_aspect(self, keep_aspect):
        pic = self.elements_dict['pic']
        pic.keep_aspect = keep_aspect
        pic.reset_image()
        
    def rotate_image(self):
        self.elements_dict['pic'].rotation += 90
        
    def set_image_outline(self, outline):
        self.elements_dict['pic'].outline_color = None if not outline else (0, 0, 0)
        
    def get_card_image(self):
        img = self.image.copy()
        self.draw_on(img, self.rect)
        return img
        
    def export_image(self, filename):
        pg.image.save(self.get_card_image(), filename)
        
    def set_type(self, type):
        tb = self.elements_dict['type']
        tb.set_text(type)

    def add_tag(self, tag):
        tag = tag.strip()
        tags = self.tags
        if tag and tag not in tags and len(tags) < 3:
            tags.append(tag)
            tb = self.elements_dict['tags']
            tb.set_text(str(tags).replace("'", ''))
            return 1
        
    def remove_tag(self, tag):
        tags = self.tags
        if tag in tags:
            tags.remove(tag)
            tb = self.elements_dict['tags']
            tb.set_text(str(tags).replace("'", '') if tags else '')
            
    def set_weight(self, weight):
        self.weight = weight
            
    def set_sound(self):
        path = f'{TEMP_SND_PATH}custom.wav'
        if os.path.exists(path):
            shutil.copyfile(path, self.sound_path)
            self.sound = self.sound_path
        else:
            if os.path.exists(self.sound_path):
                os.remove(self.sound_path)
            self.sound = None

    def set_node_data(self, nodes):
        data = pack(nodes)
        self.node_data = data
        
        prev_code = self.code
        compiler = Compiler(nodes, card=self)
        code = compiler.compile()
        self.set_code(code)
        
        if prev_code != code:
            self.published = False
            
        return compiler
   
    def set_code(self, code):
        self.code = code
            
    def set_lines(self, s, e):
        self.lines = (s, e)
        
    def get_published(self):
        return self.published
        
    def set_published(self, published):
        self.published = published
        
    def publish(self, nodes=None):
        if nodes is not None:
            compiler = self.set_node_data(nodes)
            missing = compiler.missing
            if missing:
                if len(missing) == 1:
                    text = f'Missing {missing[0]} node.\n'
                else:
                    text = f"Missing {', '.join(missing)} nodes.\n"
                Notice(text_kwargs={'text': text}).run()
                return
            
        if not self.code:
            Notice(text_kwargs={'text': 'No writable nodes found.'}).run()
            return
            
        saved = self.save(suppress=True)
        if not saved:
            Notice(text_kwargs={'text': 'An error occurred while saving.'}).run()
            return
        
        if not is_valid_code(self.code):
            Notice(text_kwargs={'text': 'Error: invalid code.'}).run()
            return
  
        passed = tester.run_tester(self)
        if not passed:
            return

        from data.save import SAVE
        s, e = SAVE.publish_card(self)
        self.set_lines(s, e)
        
        self.published = True
        self.save(suppress=True)
        
        Notice(text_kwargs={'text': 'Card has been published successfully!'}).run()
        
    def unpublish(self, nodes=None):
        saved = self.save(nodes=nodes, suppress=True)
        if not saved:
            Notice(text_kwargs={'text': 'An error occurred while saving.'}).run()
            return
            
        from data.save import SAVE
        SAVE.unpublish_card(self.id)
        
        self.set_lines(0, 0)
        self.published = False
        self.save(suppress=True)
        
        Notice(text_kwargs={'text': 'Card has been unpublished.'}).run()
            
    def save(self, nodes=None, suppress=False):
        self.set_sound()
        
        if nodes is not None:
            self.set_node_data(nodes)
            
        from spritesheet.customsheet import CUSTOMSHEET
        saved = CUSTOMSHEET.save_card(self)
        if not suppress:
            if not saved:
                menu = Notice(text_kwargs={'text': 'A card with that name already exists.'}, overlay=True)
                menu.run()
                return
            else:
                menu = Notice(text_kwargs={'text': 'Card saved successfully!'}, overlay=True)
                menu.run()
        return saved