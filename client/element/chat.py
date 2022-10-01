from ui.element.base.element import Element
from ui.element.elements import Textbox, Button, Live_Window, Input
from ui.icons.icons import icons

class Chat(Button.Text_Button):
    def __init__(self, client):
        self.client = client
        
        super().__init__(
            text=icons['bubble2'],
            font_name='icons.ttf',
            text_size=30,
            center_aligned=True,
            hover_color=(100, 100, 100),
            pad=5,
            border_radius=5,
            func=self.switch,
            layer=20
        )
        
        self.chat = Element(
            size=(350, 300),
            fill_color=(50, 50, 50),
            outline_color=(255, 255, 255),
            outline_width=2,
            border_radius=5
        )
        self.chat.rect.center = client.rect.center
        self.add_child(self.chat)
        self.chat.turn_off()
        
        self.message_box = Input(
            size=(250, 30),
            centery_aligned=True,
            outline_color=(0, 0, 0),
            outline_width=2,
            x_pad=5,
            max_lines=1
        )
        self.message_box.rect.midbottom = (self.chat.rect.centerx, self.chat.rect.bottom - 20)
        self.chat.add_child(self.message_box, current_offset=True)
        
        self.message_box.add_event(
            tag='enter',
            func=self.send
        )
        
        self.window = Live_Window(
            size=(self.chat.rect.width - 40, 200),
            fill_color=(0, 0, 0)
        )
        self.window.rect.midtop = (self.chat.rect.centerx, self.chat.rect.top + 10)
        self.chat.add_child(self.window, current_offset=True)
        
        self.window.orientation_cache |= {
            'dir': 1,
            'marginy': 5,
            'borderx': 5,
            'bordery': 5
        }
        
    def open(self):
        self.chat.turn_on()
        self.is_open = True
        
        self.text_color = (255, 255, 255)
        self.set_text(icons['bubble2'])
        
    def close(self):
        self.chat.turn_off()
        self.is_open = False
        
    def switch(self):
        if self.is_open:
            self.close()
        else:
            self.open()
        
    def add_message(self, log):
        player = self.client.get_player(log['p'])
        message = log['text']

        name = player.name
        if len(name) > 10:
            name = f'{name[:10]}...'
        header = f'<{name}> '
        
        style = {i: {'fgcolor': player.color} for i in range(len(header))}
        text = header + message
        
        tb = Textbox(
            text=text,
            text_size=15, 
            max_line_width=self.window.rect.width - 20,
            text_style=style
        )
        tb.chop_to_width()
        self.window.add_element(tb)
        self.window.y_scroll_bar.go_to_bottom()
        
        if not self.is_open:
            self.text_color = (255, 0, 0)
            self.set_text(icons['bubble'])
        
    def send(self):
        self.client.send(f'msg-{self.message_box.text}')

        
        
        
        
        
        
        
        
        
        