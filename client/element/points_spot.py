from ui.element.elements import Textbox

class Points_Spot(Textbox):
    def __init__(self, player_spot):
        self.player_spot = player_spot
        
        super().__init__(
            text='0',
            text_outline_color=(0, 0, 0),
            text_outline_width=2
        )
        
    def set_score(self, score):
        self.set_text(str(score))