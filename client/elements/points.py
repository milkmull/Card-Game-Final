from ui.element.standard.textbox import Textbox

class Points(Textbox):
    def __init__(self, client, player, type, points, card, target):
        super().__init__(
            text=str(points) if points < 0 else f'+{points}',
            text_size=30,
            text_color=(255, 0, 0) if points < 0 else (0, 255, 0),
            text_outline_color=(0, 0, 0),
            text_outline_width=2,
            layer=1,
            enabled=False
        )
        
        self.client = client
        self.player = player
        self.target = target
        self.type = type
        
        self.rect.center = card.rect.center
  
        if not target:
            end = player.spot.points.rect.topleft
            delay = 30
        elif type == 'sp':
            end = player.spot.points.rect.topleft
            delay = 30
            target.spot.add_points(-points)
        else:
            end = target.spot.points.rect.topleft
            delay = 30
            player.spot.add_points(-points)

        self.animation = self.add_animation([{
            'attr': 'pos',
            'end': end,
            'delay': delay,
            'frames': 20
        }])
            
    def end(self):
        self.client.elements.remove(self)
        self.player.spot.add_points(int(self.text))
        
    def update(self):
        super().update()
        
        if self.animation.finished:
            self.end()
            return
        