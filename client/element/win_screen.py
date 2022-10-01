import pygame as pg

import random

from ui.element.standard.textbox import Textbox
        
class Winner_Text(Textbox):
    def __init__(self, client):
        self.client = client
        
        super().__init__(
            text_size=100,
            fill_color=(40, 40, 32),
            text_outline_color=(0, 0, 0),
            text_outline_width=5,
            layer=10,
            pad=10,
            border_radius=5,
            outline_color=(255, 255, 255),
            outline_width=2
        )

        self.turn_off()
        
    @property
    def winners(self):
        hs = max({p.score for p in self.client.players})
        return [p for p in self.client.players if p.score == hs]
        
    @property
    def colors(self):
        return [p.color for p in self.winners]
        
    def get_win_style(self):
        colors = self.colors
        
        style = {}
        i = 0
        for j, char in enumerate('Game Over!'): 
            if char.isspace():
                continue

            style[j] = {'fgcolor': colors[i % len(colors)]}
            i += 1
   
        return style

    def start(self):
        self.turn_on()
        
        self.set_text('Game Over!', style=self.get_win_style())
        self.bottom_pad = 10
        self.rect.centerx = self.client.rect.centerx

        players = sorted(self.client.players, key=lambda p: p.score, reverse=True)
        scores = []
        for p in players:
            if p.score not in scores:
                scores.append(p.score)
                
        textboxes = []

        for p in players:
            place = scores.index(p.score) + 1
            
            match place:
                case 1:
                    suffix = 'st'
                    text_color = (255, 215, 0)
                case 2:
                    suffix = 'nd'
                    text_color = (192, 192, 192)
                case 3:
                    suffix = 'rd'
                    text_color = (205, 127, 50)
                case _:
                    suffix = 'th'
                    text_color = (150, 150, 170)
                    
            text = f'{place}{suffix}: {p.name}'
            l1 = len(text.split(':')[0]) + 1
            style1 = {i: {'fgcolor': text_color} for i in range(l1)}
            style2 = {i: {'fgcolor': p.color} for i in range(l1, len(text))}
                    
            tb = Textbox(
                text=text,
                text_outline_color=(0, 0, 0),
                text_outline_width=2,
                text_style=(style1 | style2),
                enabled=False
            )
            textboxes.append(tb)
            
        line_space = 5
            
        w = self.rect.width
        h = self.rect.height + sum([tb.rect.height + line_space for tb in textboxes])
        
        r = pg.Rect(0, 0, w, h)
        r.center = self.client.rect.center

        self.add_animation([{
            'attr': 'y',
            'start': -self.rect.height,
            'end': r.top,
            'frames': 20,
            'method': 'ease_out_expo'
        }])
        
        self.add_animation([{
            'attr': 'bottom_pad',
            'end': r.height - self.rect.height + 10,
            'frames': 10,
            'delay': 15,
            'method': 'ease_in_back'
        }])
 
        y = r.top + self.rect.height
        for i, tb in enumerate(textboxes):
            tb.rect.y = y
            tb.add_animation([{
                'attr': 'centerx',
                'start': self.client.rect.width + (tb.rect.width // 2),
                'end': self.client.rect.centerx,
                'frames': 10,
                'delay': 20 + (5 * (i + 1)),
                'method': 'ease_out_expo'
            }])
            self.add_child(tb)
            y += tb.rect.height + line_space

    def reset(self):
        self.clear()
        self.turn_off()
        self.clear_children()
        
    def fireworks(self):
        w, h = self.client.rect.inflate(-100, -100).size
        points = [(random.random() * w, random.random() * h) for _ in range(5)]
        for p in points:
            self.client.get_kill_particles(p, random.choice(self.colors))
        
    def update(self):
        super().update()

        if not int(100 * random.random()) % 15:
            self.fireworks()
            
            
            
            
            
            
            
            
            
            
            
            
            
            