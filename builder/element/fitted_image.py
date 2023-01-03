import pygame as pg

from ui.element.elements import Image
      
class Fitted_Image(Image):
    @property
    def padded_rect(self):
        w = self.image_rect.width + self.pad["left"] + self.pad["right"]
        h = self.image_rect.height + self.pad["top"] + self.pad["bottom"]
        x = self.image_rect.x - self.pad["left"]
        y = self.image_rect.y - self.pad["top"]
        return pg.Rect(x, y, w, h)