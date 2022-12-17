from ui.element.base.text_element import Text_Element
from ui.element.compound.dropdown import Dropdown
from ui.element.compound.input_dropdown import Input_Dropdown

class Logged_Dropdown(Dropdown):
    def __init__(
        self,
        port,
        selection,
        value=None
    ):
        
        super().__init__(
            selection,
            selected=value,
            size=(port.node.rect.width - 38, 22),
            y_pad=2,
            left_pad=2,
            right_pad=20,
            centery_aligned=True,
            inf_width=False,
            inf_height=False,
            max_length=25,
            max_lines=1,
            text_check=lambda text: "'" not in text and '"' not in text and text.isascii(),
            text_color=(255, 255, 255),
            cursor_color=(255, 255, 255),
            fill_color=(32, 32, 40),
            outline_color=(0, 0, 0),
            outline_width=3,
            border_radius=5,
            window_kwargs={
                'fill_color': (32, 32, 40),
                'outline_color': (200, 200, 200),
                'outline_width': 3
            },
            max_buttons=6
        )
        
        self.add_event(
            func=self.close,
            tag='enter'
        )

        self.add_animation(
            [{
                'attr': 'width',
                'end': 200,
                'frames': 10
            }],
            tag='open'
        )
        
        self.last_text = self.text
        
    @property
    def port(self):
        return self.parent
        
    @property
    def value(self):
        return self.text
        
    def get_output(self):
        return f"'{self.text}'" 
        
    def set_value(self, text, undo=False):
        super().set_value(text)
        if undo:
            self.last_text = self.text
        
    def reset_value(self, text):
        self.set_text(text)
        self.last_text = self.text
        
    def close(self):
        super().close()
        
        if self.port.manager:
            if self.text != self.last_text:
                self.port.manager.add_log({
                    't': 'val',
                    'e': self,
                    'v': (self.last_text, self.text)
                })
                self.last_text = self.text
        
    def update(self):
        super().update()
        
        if self.port.port > 0:
        
            if self.port.connection:
                self.set_enabled(False)
                out = self.port.connection.get_output(self.port.connection_port.true_port).strip("'")
                super(Text_Element, self).set_text(out)
                
            elif not self.enabled:
                self.set_enabled(True)
                self.set_text(self.last_text)      

class Logged_Input_Dropdown(Input_Dropdown):
    def __init__(
        self,
        port,
        selection,
        value=None
    ):
        
        super().__init__(
            selection,
            selected=value,
            size=(port.node.rect.width - 38, 22),
            y_pad=2,
            left_pad=2,
            right_pad=20,
            centery_aligned=True,
            inf_width=False,
            inf_height=False,
            max_length=25,
            max_lines=1,
            text_check=lambda text: "'" not in text and '"' not in text and text.isascii(),
            text_color=(255, 255, 255),
            cursor_color=(255, 255, 255),
            fill_color=(32, 32, 40),
            outline_color=(0, 0, 0),
            outline_width=3,
            border_radius=5,
            window_kwargs={
                'fill_color': (32, 32, 40),
                'outline_color': (200, 200, 200),
                'outline_width': 3
            },
            max_buttons=6
        )
        
        self.add_event(
            func=self.close,
            tag='enter'
        )

        self.add_animation(
            [{
                'attr': 'width',
                'end': 200,
                'frames': 10
            }],
            tag='open'
        )
        
        self.last_text = self.text
        
    @property
    def port(self):
        return self.parent
        
    @property
    def value(self):
        return self.text
        
    def get_output(self):
        return f"'{self.text}'" 
        
    def set_value(self, text, undo=False):
        super().set_value(text)
        if undo:
            self.last_text = self.text
        
    def reset_value(self, text):
        self.set_text(text)
        self.last_text = self.text
        
    def close(self):
        super().close()
        
        if self.port.manager:
            if self.text != self.last_text:
                self.port.manager.add_log({
                    't': 'val',
                    'e': self,
                    'v': (self.last_text, self.text)
                })
                self.last_text = self.text
        
    def update(self):
        super().update()
        
        if self.port.port > 0:
        
            if self.port.connection:
                self.set_enabled(False)
                out = self.port.connection.get_output(self.port.connection_port.true_port).strip("'")
                super(Text_Element, self).set_text(out)
                
            elif not self.enabled:
                self.set_enabled(True)
                self.set_text(self.last_text)      