import pygame as pg

from ..utils.image import swap_colors

class Image:
    @staticmethod
    def get_max_aspect(images):
        mw = 0
        mh = 0
        for i in images:
            w, h = i.get_size()
            if w > mw:
                mw = w
            if h > mh:
                mh = h
        return (mw, mh)
        
    def __init__(
        self, 
        
        image=None,

        auto_fit=True,
        keep_aspect=True,
        
        rotation=0,
        
        **kwargs
    ):

        self.original_image = image
        self.image = image.copy() if image else None

        self.auto_fit = auto_fit
        self.keep_aspect = keep_aspect
        
        self._rotation = rotation

        self.fit_image()

    @property
    def image_size(self):
        if self.image:
            return self.image.get_size()
        return self.rect.size
        
    @property
    def image_rect(self):
        if self.image:
            r = self.image.get_rect()
            r.center = self.rect.center
            return r
        return pg.Rect(0, 0, 0, 0)
        
    @property
    def alpha(self):
        return self.image.get_alpha()
        
    @alpha.setter
    def alpha(self, alpha):
        self.image.set_alpha(alpha)
        
    @property
    def rotation(self):
        return self._rotation
        
    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
        self.fit_image()
        
    def fill(self, color):
        self.image.fill(color)
        
    def swap_colors(self, old_color, new_color, overwrite=True):
        self.set_image(swap_colors(self.image, old_color, new_color), overwrite=overwrite)
        
    def reset_image(self):
        self.set_image(
            self.original_image.copy(),
            overwrite=False
        )
        
    def set_image(self, image, overwrite=True):
        self.image = image
        if overwrite:
            self.original_image = image.copy()
        self.fit_image()
        
    def clear_image(self, overwrite=True):
        self.image = None
        self.original_image = None
            
    def transform(self, mode, *args, overwrite=False, **kwargs):
        self.set_image(
            getattr(pg.transform, mode)(self.original_image, *args, **kwargs),
            overwrite=overwrite
        )
            
    def get_scaled(self, size):
        return pg.transform.smoothscale(self.original_image, size)
        
    def scale_image(self, size):
        w, h = size
        if w < 0:
            w = 0
        if h < 0:
            h = 0
        self.image = self.get_scaled((w, h))
        
    def scale_by_factor(self, factor):
        if factor != 1:
            w, h = self.image.get_size()
            self.scale_image((w * factor, h * factor))

    def fit_image(self):
        if self.image:
            
            c = self.rect.center

            self.image = pg.transform.rotate(self.original_image, self._rotation)
        
            if self.auto_fit:
                self.rect.size = self.image.get_size()

            if self.keep_aspect:
                r = self.image.get_rect()
                fitted = r.fit(self.rect)
                self.image = pg.transform.smoothscale(self.image, fitted.size)
                    
            elif not self.auto_fit:
                self.image = pg.transform.smoothscale(self.image, self.rect.size)
                
            self.rect.center = c
        
    def fit_to_image(self, width=False, height=False):
        w, h = self.image_size
        if not width:
            w = self.rect.width
        if not height:
            h = self.rect.height
        self.size = (w, h)
        
    def draw_image(self, surf):
        if self.image:
            surf.blit(self.image, self.image_rect)
        