import pygame as pg

from .spritesheet_base import Base_Sheet
from builder.custom_card_base import Card

from data.save import SAVE
from data.constants import CONSTANTS, BASE_NAMES

CARD_WIDTH, CARD_HEIGHT = CONSTANTS["card_size"]

def to_classname(name):
    cname = ""
    for char in name.title().replace(" ", "_"):
        if char.isalnum() or char == "_":
            cname += char
            
    if cname[0].isnumeric():
        cname = "_" + cname

    return cname
    
class Customsheet(Base_Sheet):
    @staticmethod
    def get_blank_custom():
        import os
        if os.path.exists("data/img/user.png"):
            img = pg.image.load("data/img/user.png").convert()
        else:
            img = pg.Surface((1, 1)).convert() 
        img = pg.transform.smoothscale(img, (CARD_WIDTH - 75, 210))
        return img
    
    def __init__(self):
        names = tuple([c["name"] for c in self.cards])
        super().__init__(names, "data/img/customsheet.png", (9, CARD_WIDTH, CARD_HEIGHT))
        if self.failed_to_load():
            self.create_blank_sheet()
            self.restore_data()
        for d in self.cards:
            path = d["image"]
            self.get_card_image(path)
            
    @property
    def cards(self):
        return SAVE.get_data("cards")
            
    def reset(self):
        self.create_blank_sheet()
        c = Card(**self.cards[0])
        self.save_card(c)
        
    def refresh_names(self):
        self.names = tuple([c["name"] for c in self.cards])
        
    def refresh(self):
        self.refresh_names()
        self.refresh_sheet()
    
    def create_blank_sheet(self):
        cards = self.cards
        if len(cards) < 9:
            w = CARD_WIDTH * len(cards)
            h = CARD_HEIGHT
        else:
            w = CARD_WIDTH * 9
            h = CARD_HEIGHT * ((len(cards) // 9) + 1)
        surf = pg.Surface((w, h)).convert()
        self.resave_sheet(surf)
        
    def restore_data(self):
        data = self.cards
        for d in data:
            c = Card(**d)
            self.save_card(c)
            
    def get_card_image(self, path):
        loaded = False
        try:
            image = pg.image.load(path).convert()
            loaded = True
        except:
            image = Customsheet.get_blank_custom()
        finally:
            if not loaded:
                pg.image.save(image, path)
        return image
        
    def get_id(self, name):
        if name in self.names:
            return self.names.index(name)
            
    def check_exists(self, card):
        for name in BASE_NAMES:
            if card.name.lower() == name.lower() or card.classname == to_classname(name):
                return True
                
        for name in self.names:
            if card.id != self.get_id(card.name):
                if card.name.lower() == name.lower() or card.classname == to_classname(name):
                    return True
            
    def save_card(self, card):
        if self.check_exists(card):
            return

        id = card.id
        cards = self.cards
        sheet = self.sheet
        
        num = len(cards)

        if id <= num - 1:
            surf = sheet
            pos = ((id % self.columns) * CARD_WIDTH, (id // self.columns) * CARD_HEIGHT)
        elif not cards:
            surf = pg.Surface((CARD_WIDTH, CARD_HEIGHT)).convert()
            pos = (0, 0)
        elif not num % self.columns:
            surf = pg.Surface((sheet.get_width(), sheet.get_height() + CARD_HEIGHT)).convert()
            pos = (0, sheet.get_height())
        elif num < self.columns:
            surf = pg.Surface((sheet.get_width() + CARD_WIDTH, CARD_HEIGHT)).convert()
            pos = (num * CARD_WIDTH, 0)
        else:
            surf = pg.Surface(sheet.get_size()).convert()
            pos = ((num % self.columns) * CARD_WIDTH, (num // self.columns) * CARD_HEIGHT)

        surf.blit(sheet, (0, 0))
        surf.blit(card.get_card_image(), pos)

        pg.image.save(card.pic, card.image_path)
        self.resave_sheet(surf)  
        SAVE.update_cards(card.get_info())
        self.refresh_names()
        return True
        
    def del_card(self, entry):        
        id = entry["id"]
        sheet = self.sheet
        cards = self.cards
        
        if id == 0:
            return
            
        if len(cards) < self.columns + 1:
            surf = pg.Surface((sheet.get_width() - CARD_WIDTH, CARD_HEIGHT)).convert()
            x = id * CARD_WIDTH
            surf.blit(sheet, (0, 0), (0, 0, x, CARD_HEIGHT))
            surf.blit(
                sheet,
                (x, 0),
                (x + CARD_WIDTH, 0, sheet.get_width() - (x + CARD_WIDTH), CARD_HEIGHT)
            )

        else:
            if (len(cards) - 1) % self.columns == 0:
                size = (CARD_WIDTH * self.columns, sheet.get_height() - CARD_HEIGHT)
            else:
                size = (CARD_WIDTH * self.columns, sheet.get_height())
                
            surf = pg.Surface(size).convert()
            found = False
            
            for row in range(sheet.get_height() // CARD_HEIGHT):
                
                if not found:
                    if id // self.columns == row:           
                        x = (id % self.columns) * CARD_WIDTH
                        y = row * CARD_HEIGHT
                        surf.blit(sheet, (0, y), (0, y, x, CARD_HEIGHT))
                        surf.blit(
                            sheet,
                            (x, y),
                            (x + CARD_WIDTH, y, sheet.get_width() - (x + CARD_WIDTH), CARD_HEIGHT)
                        )
                        found = True
                    else:
                        surf.blit(
                            sheet, 
                            (0, row * CARD_HEIGHT), 
                            (0, row * CARD_HEIGHT, sheet.get_width(), CARD_HEIGHT)
                        )
                else:
                    surf.blit(
                        sheet,
                        ((self.columns - 1) * CARD_WIDTH, (row - 1) * CARD_HEIGHT),
                        (0, row * CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT)
                    )
                    surf.blit(
                        sheet, 
                        (0, row * CARD_HEIGHT), 
                        (CARD_WIDTH, row * CARD_HEIGHT, (self.columns - 1) * CARD_WIDTH, CARD_HEIGHT)
                    )
        
        self.resave_sheet(surf)
        
CUSTOMSHEET = Customsheet()
