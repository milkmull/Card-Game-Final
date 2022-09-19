from ui.element.standard.button import Button

class Main_Button(Button.Text_Button):
    CLICKABLE_STATUS = (
        'play', 
        'flip', 
        'roll', 
        'next round', 
        'new game', 
        'start'
    )
    
    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.client = client
        
    def cancel(self):
        if self.client.main_p.can_cancel:
            self.client.send('cancel')
            
    def set_button(self, text, color):
        if text != self.text:
            self.text_color = color
            self.set_text(text.title())
            
            self.set_enabled(self.text.lower() in Main_Button.CLICKABLE_STATUS)
            if not self.enabled:
                self.cancel_animation('hover')

    def update_status(self, stat):
        if stat == 'waiting' and len(self.client.players) > 1:
            stat = 'start'

        self.client.status = stat
        self.set_button(stat, (0, 255, 0))
        
    def update_option(self):
        p = self.client.main_p
        text = ''
        color = None

        if self.text != text:
            self.set_button(text, color)
        
    def update(self):
        if self.client.status == 'playing':
            self.update_option()

        super().update()

    def left_click(self):
        option = self.text

        if option == 'Play':
            self.client.send('play')  
            
        elif option == 'Flip':
            self.client.send('flip')

        elif option == 'Roll':
            self.client.send('roll')
            
        elif option == 'Start':
            self.client.send('start')
            
        elif option in ('Next Round', 'New Game'):
            self.client.send('continue')
            