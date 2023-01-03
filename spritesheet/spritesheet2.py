import os

import pygame as pg

from data.constants import CONSTANTS
from data.save import SAVE, BASE_NAMES
from . import spritesheet_base
from builder.custom_card_base import Card

from ui.image import rect_outline

CARD_WIDTH, CARD_HEIGHT = CONSTANTS["card_size"]

def load_sounds():
    sounds = {}
    
    files = os.listdir("data/snd/cards")
    for f in files:
        name = f[:-4]
        try:
            sounds[name] = pg.mixer.Sound(f"data/snd/cards/{f}")
        except pg.error:
            continue
            
    files = os.listdir("data/snd/custom")
    for f in files:
        name = SAVE.id_to_name(int(f[:-4]))
        try:
            sounds[name] = pg.mixer.Sound(f"data/snd/custom/{f}")
        except pg.error:
            continue
        
    return sounds
    
class Spritesheet:
    def __init__(self):
        self.spritesheet = spritesheet_base.Base_Sheet(
            BASE_NAMES,
            "data/img/spritesheet.png",
            (9, CARD_WIDTH, CARD_HEIGHT)
        )
        self.customsheet = spritesheet_base.Base_Sheet(
            SAVE.get_custom_names(), 
            "data/img/customsheet.png",
            (9, CARD_WIDTH, CARD_HEIGHT)
        )
        self.extras = {"back": pg.image.load("data/img/back.png").convert()}
        self.sounds = load_sounds()
        
    def refresh_custom(self):
        self.customsheet = spritesheet_base.Base_Sheet(
            SAVE.get_custom_names(),
            "data/img/customsheet.png",
            (9, CARD_WIDTH, CARD_HEIGHT)
        )
        self.sounds = load_sounds()
        for name in self.extras.copy():
            if name != "back":
                self.extras.pop(name)
        
    def check_name(self, name):
        return self.spritesheet.check_name(name) or self.customsheet.check_name(name) or name in self.extras

    def add_extra(self, info):
        image = Card.build_card(info)
        self.extras[info["name"]] = image
        return image
        
    def remove_extra(self, name):
        if name in self.extras:
            self.extras.pop(name)
            
    def get_image(self, name, scale=(0, 0), olcolor=None):
        scale = tuple([int(s) for s in scale])
        
        img = self.spritesheet.get_image(name)
        if not img:
            img = self.customsheet.get_image(name)
            if not img:
                if name in self.extras:
                    img = self.extras[name]
                else:
                    img = self.add_extra({"name": name, "description": "extra"})     
            
        if any(scale):
            img = pg.transform.smoothscale(img, scale)
        elif olcolor is not None:
            img = rect_outline(img, color=olcolor)

        return img
        
    def get_sound(self, name):
        return self.sounds.get(name)
        
SPRITESHEET = Spritesheet()

        