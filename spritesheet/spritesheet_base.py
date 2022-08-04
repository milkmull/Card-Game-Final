import pygame as pg

from data.save import CONSTANTS

CARD_WIDTH, CARD_HEIGHT = CONSTANTS['card_size']
    
class Sheet_Manager:
    CACHE = {}
    
    @classmethod
    def get_sheet(cls, path):
        if path not in cls.CACHE:
            try:
                cls.CACHE[path] = pg.image.load(path).convert()
            except:
                cls.CACHE[path] = None
        return cls.CACHE[path]
        
    @classmethod
    def reload_sheet(cls, path):
        cls.CACHE[path] = pg.image.load(path).convert()
        
class Base_Sheet:
    def __init__(self, names, path, dimensions):
        self.names = names
        self.path = path
        self.columns, self.item_width, self.item_height = dimensions
        Sheet_Manager.get_sheet(path)
        
    def failed_to_load(self):
        return not self.sheet
        
    @property
    def sheet(self):
        return Sheet_Manager.get_sheet(self.path)
        
    def refresh_sheet(self):
        Sheet_Manager.reload_sheet(self.path)
        
    def resave_sheet(self, surf):
        pg.image.save(surf, self.path)
        self.refresh_sheet()
        
    def check_name(self, name):
        return name in self.names
        
    def get_image(self, name, size=None):
        if not self.check_name(name):
            return
            
        i = self.names.index(name)
        x = (i % self.columns) * self.item_width
        y = (i // self.columns) * self.item_height
        
        img = pg.Surface((self.item_width, self.item_height)).convert()
        img.blit(self.sheet, (0, 0), (x, y, self.item_width, self.item_height))
        if size:
            img = pg.transform.smoothscale(img, size)
        
        return img
    
    