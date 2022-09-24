import random

from ui.element.elements import Textbox

class Player:
    def __init__(self, client, name, pid, color, spot):
        self.client = client
        self.name = name
        self.pid = pid
        self.color = color
        self.spot = spot
        self.spot.set_player(self)

        self.score = 0
        
    def __repr__(self):
        return self.name
        
    def __str__(self):
        return self.name
        
    @property
    def is_main(self):
        return self.pid == self.client.pid
        
    @property
    def is_turn(self):
        return self.spot.turn_indicator.visible

    def update_score(self, score):
        self.score = score
        self.spot.points_spot.set_score(self.score)
            
    def start_turn(self):
        self.spot.start_turn()

    def end_turn(self):
        self.spot.end_turn()

    def update(self):
        pass
            