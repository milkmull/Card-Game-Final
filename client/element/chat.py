from ui.element.base.element import Element
from ui.element.elements import Textbox, Image, Button, Live_Window, Input
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
            size=(420, 340),
            fill_color=(50, 50, 50),
            outline_color=(255, 255, 255),
            outline_width=2,
            border_radius=5
        )
        self.chat.rect.center = client.rect.center
        self.add_child(self.chat)
        self.chat.turn_off()

        self.window = Live_Window(
            size=(self.chat.rect.width - 50, 250),
            fill_color=(0, 0, 0),
            outline_color=(255, 255, 255),
            outline_width=2
        )
        self.window.rect.midtop = (self.chat.rect.centerx, self.chat.rect.top + 20)
        self.chat.add_child(self.window, current_offset=True)
        
        self.window.orientation_cache |= {
            'dir': 1,
            'marginy': 5,
            'borderx': 5,
            'bordery': 5
        }
        
        self.message_box = Input(
            size=(250, 30),
            centery_aligned=True,
            outline_color=(0, 0, 0),
            outline_width=2,
            x_pad=5,
            y_pad=2,
            max_lines=1
        )
        self.message_box.rect.topleft = (self.window.rect.left + 20, self.window.rect.bottom + 20)
        self.chat.add_child(self.message_box, current_offset=True)
        
        self.message_box.add_event(
            tag='enter',
            func=self.send
        )
        
        self.send_button = Button.Text_Button(
            text='Send',
            center_aligned=True,
            text_color=(0, 0, 0),
            fill_color=(255, 255, 255),
            outline_color=(0, 0, 0),
            outline_width=2,
            border_radius=3,
            x_pad=5,
            y_pad=2,
            func=self.send
        )
        self.send_button.rect.midleft = (self.message_box.rect.right + 30, self.message_box.rect.centery)
        self.chat.add_child(self.send_button, current_offset=True)
        
        self.animated_box = None
        
    def open(self):
        self.animated_box = Image.from_element(self.chat, keep_aspect=False)
        self.animated_box.auto_fit = False
        self.animated_box.rect.topleft = self.chat.rect.topleft
        self.add_child(
            self.animated_box,
            centerx_anchor='centerx',
            centerx_offset=self.animated_box.rect.centerx - self.rect.centerx
        )

        self.animated_box.add_animation([{
            'attr': 'height',
            'start': 0,
            'end': self.chat.rect.height,
            'frames': 8,
            'method': 'ease_in_quart'
        }])
        
        self.animated_box.add_animation(
            [{
                'attr': 'width',
                'start': 5,
                'end': self.chat.rect.width,
                'frames': 8,
                'delay': 8,
                'method': 'ease_in_quart'
            }],
            end_func=self.end_open
        )
        
    def end_open(self):
        self.animated_box.turn_off()
        self.chat.turn_on()
        
        self.is_open = True
        
        self.text_color = (255, 255, 255)
        self.set_text(icons['bubble2'])
        
    def close(self):
        self.is_open = False
        self.animated_box.turn_on()
        self.chat.turn_off()
        
        self.animated_box.add_animation([{
            'attr': 'width',
            'end': 5,
            'frames': 8,
            'method': 'ease_out_quart'
        }])
        
        self.animated_box.add_animation(
            [{
                'attr': 'height',
                'end': 0,
                'frames': 8,
                'delay': 8,
                'method': 'ease_out_quart'
            }],
            end_func=self.end_close
        )
        
    def end_close(self):
        self.remove_child(self.animated_box)
        self.animated_box = None
        
    def switch(self):
        if self.is_open:
            self.close()
        elif not self.animated_box:
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
        tb.wrap_to_width()
        self.window.add_element(tb)
        self.window.y_scroll_bar.go_to_bottom()
        
        if not self.is_open:
            self.text_color = (255, 0, 0)
            self.set_text(icons['bubble'])
        
    def send(self):
        text = self.message_box.text.strip()
        if text:
            self.client.send(f'msg-{self.message_box.text}')
            self.message_box.clear()
            
    def clear(self):
        self.window.clear()

    def events(self, events):
        super().events(events)
        
        if self.is_open:
            if (mbd := events.get('mbd')):
                if not self.chat.hit:
                    self.close()
        
        
        
        
        
        
        
        
        