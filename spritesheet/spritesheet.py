import os

import pygame as pg

from data.save import SAVE
from data.constants import CONSTANTS, BASE_NAMES, SPRITESHEET_FILE, CUSTOMSHEET_FILE, IMG_PATH

from . import spritesheet_base
from builder.custom_card_base import Card

class Spritesheet:
    def __init__(self):
        CARD_WIDTH, CARD_HEIGHT = CONSTANTS['card_size']
        
        self.spritesheet = spritesheet_base.Base_Sheet(
            BASE_NAMES,
            SPRITESHEET_FILE,
            (9, CARD_WIDTH, CARD_HEIGHT)
        )
        
        self.customsheet = spritesheet_base.Base_Sheet(
            [c['name'] for c in SAVE.get_data('cards')], 
            CUSTOMSHEET_FILE,
            (9, CARD_WIDTH, CARD_HEIGHT)
        )
        self.customsheet.names[0] = 'player 0'
        
        self.extrasheet = {}
        
        self.mini_cache = {}
        
    def check_name(self, name):
        return self.spritesheet.check_name(name) or self.customsheet.check_name(name)
        
    def add_player(self, pid, color, info):
        info['type'] = 'player'
        info['color'] = color
        info['image'] = IMG_PATH + 'user.png'
        img = Card(**info).get_card_image()
        name = f'player {pid}'
        self.extrasheet[name] = img
        
    def add_extra(self, name):
        img = Card(name=name).get_card_image()
        self.extrasheet[name] = img
        return img
        
    def get_full_size(self, name):
        return (
            self.spritesheet.get_image(name) or
            self.customsheet.get_image(name) or
            self.extrasheet.get(name) or 
            self.add_extra(name)
        )
        
    def add_mini(self, name):
        img = self.get_full_size(name)
        img = pg.transform.smoothscale(img, CONSTANTS['mini_card_size'])
        self.mini_cache[name] = img
        return img
    
    def get_image(self, name, mini=False, scale=None):
        img = None
        
        if mini:
            img = self.mini_cache.get(name)
            if not img:
                img = self.add_mini(name)
        else:
            img = self.get_full_size(name)
            if scale:
                img = pg.transform.smoothscale(img, scale)
            
        return img
