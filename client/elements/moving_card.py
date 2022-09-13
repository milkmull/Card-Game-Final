import pygame as pg

from ui.element.base.element import Element

class Moving_Card(Element):
    def __init__(self, client, player, type, card):   
        self.client = client
        self.player = player
        self.card = card
        self.card.turn_off()
        
        self.base_image = self.card.get_image(mini=False)
        super().__init__(
            size=self.base_image.get_size(),
            enabled=False
        )

        self.rect.center = self.card.rect.center
        self.client.elements.append(self)
        
        inf_size = self.card.rect.inflate(4 * self.card.rect.width, 4 * self.card.rect.height).size

        match type:
            
            case 'play':
                self.animation = self.add_animation([
                    {
                        'attr': 'size',
                        'start': (0, 0) if not self.player.is_main else self.card.rect.size,
                        'end': inf_size,
                        'frames': 20,
                        'method': 'ease_out_expo'
                    },
                    {
                        'attr': 'size',
                        'start': inf_size,
                        'end': self.card.rect.size,
                        'frames': 20,
                        'method': 'ease_in_expo'
                    }
                ])
                
                if self.player.is_main:
                    self.add_animation([{
                        'attr': 'center',
                        'start': self.client.cards[self.card.uid][-2].rect.center,
                        'end': self.card.rect.center,
                        'frames': 20,
                        'method': 'ease_out_expo'
                    }])
        
            case 'buy':
                self.animation = self.add_animation([
                    {
                        'attr': 'size',
                        'start': self.card.rect.size,
                        'end': inf_size,
                        'frames': 20,
                        'method': 'ease_out_expo'
                    },
                    {
                        'attr': 'size',
                        'start': inf_size,
                        'end': (0, 0),
                        'frames': 20,
                        'method': 'ease_in_expo'
                    }
                ])
                
                self.add_animation([{
                    'attr': 'center',
                    'start': self.client.cards[self.card.uid][-2 if self.player.is_main else 0].rect.center,
                    'end': self.player.spot.label.rect.center if not self.player.is_main else self.client.cards[self.card.uid][-1].rect.center,
                    'frames': 20,
                    'method': 'ease_out_expo'
                }])
                
            case 'cast':
                self.animation = self.add_animation([
                    {
                        'attr': 'size',
                        'start': self.card.rect.size,
                        'end': inf_size,
                        'frames': 20,
                        'method': 'ease_out_expo'
                    },
                    {
                        'attr': 'size',
                        'start': inf_size,
                        'end': self.card.rect.size,
                        'frames': 20,
                        'method': 'ease_in_expo'
                    }
                ])
                self.add_animation([{
                    'attr': 'center',
                    'start': self.client.cards[self.card.uid][-2].rect.center,
                    'end': self.card.rect.center,
                    'frames': 20,
                    'delay': 20,
                    'method': 'ease_in_expo'
                }])
                
            case 'discard':
                self.animation = self.add_animation([
                    {
                        'attr': 'size',
                        'start': (0, 0) if not self.player.is_main else self.card.rect.size,
                        'end': inf_size,
                        'frames': 20,
                        'method': 'ease_out_expo'
                    },
                    {
                        'attr': 'size',
                        'start': inf_size,
                        'end': self.card.rect.size,
                        'frames': 20,
                        'method': 'ease_in_expo'
                    }
                ])
                self.add_animation([{
                    'attr': 'center',
                    'start': self.player.spot.label.rect.center if not self.player.is_main else self.client.cards[self.card.uid][-2].rect.center,
                    'end': self.card.rect.center,
                    'frames': 20,
                    'delay': 20,
                    'method': 'ease_in_expo'
                }])
                
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
        self.client.del_moving_card(self.card.uid)
        
    def update(self):
        self.update_animations()
        
        if self.animation.finished:
            self.end()
            return

    def draw(self, surf):
        surf.blit(pg.transform.smoothscale(self.base_image, self.rect.size), self.rect)