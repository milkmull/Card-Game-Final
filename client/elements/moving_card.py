import pygame as pg

from ui.element.base.element import Element

class Moving_Card(Element):
    def __init__(self, client, player, type, card, **kwargs):   
        self.client = client
        self.player = player
        self.card = card
        self.card.turn_off()
        
        self.base_image = self.card.get_image(mini=False)
        super().__init__(
            size=self.base_image.get_size() if type != 'move' else self.card.rect.size,
            enabled=False,
            layer=2
        )

        self.rect.center = self.card.rect.center
        
        inf_size = self.card.rect.inflate(1.5 * self.card.rect.width, 1.5 * self.card.rect.height).size

        match type:
            
            case 'play':
                
                self.add_animation([{
                    'attr': 'center',
                    'start': self.player.spot.rect.center,
                    'end': self.card.rect.center,
                    'frames': 10,
                    'method': 'ease_out_expo'
                }])

                self.animation = self.add_animation([
                    {
                        'attr': 'size',
                        'start': (0, 0),
                        'end': inf_size,
                        'frames': 10,
                        'method': 'ease_out_expo'
                    },
                    {
                        'attr': 'size',
                        'end': self.card.rect.size,
                        'frames': 10,
                        'delay': 5,
                        'method': 'ease_in_expo'
                    }
                ])
                
            case 'move':
                self.animation = self.add_animation([{
                    'attr': 'center',
                    'start': kwargs['start'],
                    'end': self.card.rect.center,
                    'frames': 10,
                    'method': 'ease_in_out_expo'
                }])
                
        self.client.elements.append(self)
                
    @property
    def size(self):
        return self.rect.size
        
    @size.setter
    def size(self, size):
        c = self.rect.center
        self.rect.size = size
        self.rect.center = c
                
    @property
    def center(self):
        return self.rect.center
        
    @center.setter
    def center(self, center):
        self.rect.center = center
        
    def end(self):
        self.client.elements.remove(self)
        self.card.turn_on()
        
    def events(self, events):
        pass
        
    def update(self):
        self.update_animations()
        
        if self.animation.finished:
            self.end()
            return

    def draw(self, surf):
        surf.blit(pg.transform.smoothscale(self.base_image, self.rect.size), self.rect)