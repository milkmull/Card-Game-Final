import time

from ui.element.standard.textbox import Textbox

class Timer(Textbox):
    def __init__(self, client):
        self.client = client
        
        super().__init__(
            text_size=40,
            center_aligned=True,
            text_outline_color=(0, 0, 0),
            text_outline_width=2,
        )
        
        self.start_time = 0
        self.current_time = 0
        
    @property
    def max_time(self):
        return self.client.settings.get('tt', 0)
        
    def reset(self):
        self.current_time = 0
        self.set_text('')
        
    def start(self):
        self.current_time = self.max_time
        self.start_time = time.time()
        self.text_color = self.client.get_current_turn().color
        self.set_text(str(self.current_time))
        
    def tick(self):
        if self.current_time > 0:
            self.current_time = max(int(self.max_time - (time.time() - self.start_time)), 0)
            self.set_text(str(self.current_time))
        
    def update(self):
        self.tick()
        super().update()
        
        