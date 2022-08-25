from ui.element.base.text_element import Text_Element
from ui.element.standard.input import Input
from ui.color.ops import style_text

class Logged_Input(Input):
    def __init__(
        self,
        port,
        text='',
        **kwargs
    ):
        super().__init__(text=text, **kwargs)
        self.last_text = self.text
        
    @property
    def port(self):
        return self.parent
        
    @property
    def value(self):
        return self.text
        
    def get_output(self):
        return self.text
            
    def set_value(self, text):
        self.set_text(text)
        
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
            
    def get_input_text(self):
        return self.port.connection.get_output(self.port.connection_port.true_port).strip("'")
        
    def update(self):
        super().update()
        
        if self.port.port > 0:
        
            if self.port.connection:
                self.set_enabled(False)
                super(Text_Element, self).set_text(self.get_input_text())
                
            elif not self.enabled:
                self.set_enabled(True)
                self.set_text(self.last_text)
                
class Logged_Num_Input(Logged_Input):
    def __init__(
        self,
        port,
        text=''
    ):
        super().__init__(
            port,
            text=text,
            default=port.node.get_default(port.port),
            size=(port.node.WIDTH - 19, 22),
            pad=2,
            inf_width=True,
            inf_height=False,
            centery_aligned=True,
            text_check=lambda text: f"{text.lstrip('-+')}0".isnumeric(),
            max_length=3,
            max_lines=1,
            outline_color=(0, 0, 0),
            outline_width=3
        )
        
    def get_input_text(self):
        out = super().get_input_text()
        try:
            out = str(eval(out))
        except:
            pass
        return out
        
    def get_output(self):
        out = super().get_output()
        if not out.lstrip('-'):
            return '0'
        return out
        
class Logged_String_Input(Logged_Input):
    def __init__(
        self,
        port,
        text=''
    ):
        super().__init__(
            port,
            text=text.strip("'"),
            default=port.node.get_default(port.port).strip("'"),
            size=(port.node.WIDTH - 19, 22),
            pad=2,
            inf_width=True,
            inf_height=False,
            centery_aligned=True,
            text_check=lambda text: "'" not in text and '"' not in text,
            max_length=20,
            max_lines=1,
            outline_color=(0, 0, 0),
            outline_width=3
        )
        
        self.add_animation([{
            'attr': 'width',
            'end': 200,
            'frames': 10
        }],
        tag='open')
        
    def get_output(self):
        return f"'{super().get_output()}'"
        
class Logged_Code_Input(Logged_Input):
    def __init__(
        self,
        port,
        text=''
    ):
        super().__init__(
            port,
            text=text,
            font_name='JetBrainsMonoNL-Regular.ttf',
            default=port.node.get_default(port.port),
            size=(port.node.WIDTH - 19, 22),
            x_pad=2,
            top_pad=2,
            bottom_pad=0,
            inf_width=False,
            inf_height=True,
            max_line_width=300,
            max_length=500,
            max_lines=10,
            text_size=15,
            fill_color=(41, 49, 52),
            text_color=(224, 226, 228),
            outline_color=(0, 0, 0),
            outline_width=3
        )

        self.add_animation(
            [{
                'attr': 'width',
                'end': 300,
                'frames': 10
            }],
            tag='open'
        )
        self.add_animation(
            [{
                'attr': 'height',
                'end': 300,
                'frames': 10
            }],
            tag='open'
        )
        
    def set_text(self, text):
        self.text_style = style_text(text)
        super().set_text(text)
        
class Logged_Label_Input(Logged_Input):
    def __init__(
        self,
        node,
        text=''
    ):
        super().__init__(
            node,
            text=text,
            text_color=(255, 255, 255),
            size=node.label_rect.size,
            inf_width=False,
            centerx_aligned=True,
            centery_aligned=True,
            fill_color=None
        )
        
    def update(self):
        Input.update(self)
        
INPUTS = {
    'num': Logged_Num_Input,
    'string': Logged_String_Input,
    'code': Logged_Code_Input,
    'label': Logged_Label_Input
}
            
            