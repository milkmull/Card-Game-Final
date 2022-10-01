import pygame as pg

from ui.element.standard.base import Element
        
class Reset_Image(Image):
    def __init__(self, client):
        self.client = client
        super().__init__()
        self.turn_off()
        
    def start(self):
        self.turn_on()
        self.set_image(self.client.window.copy())
        
        print('hello')
        
        self.add_animation(
            [{
                'attr': 'y',
                'start': 0,
                'end': self.client.rect.height,
                'frames': 20
            }],
            end_func=self.end
        )
            
    def end(self):
        self.clear_image()
        self.turn_off()
        print('end')
            
            
            
            
            
            
            
            
            
            