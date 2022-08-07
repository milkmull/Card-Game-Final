from ui.element.base.text_element import Text_Element
from ui.element.standard.input import Input

class Logged_Input(Input):
    def __init__(
        self,
        port,
        type,
        text=''
    ):
        self.type = type
        
        if type == 'num':
            text_check = lambda text: f"{text.lstrip('-+')}0".isnumeric()
            max_length = 3
            max_lines = 1
            
        elif type == 'string':
            text_check = lambda text: text.count("'") < 3
            max_length = 50
            max_lines = 1
                
        elif type == 'code':
            text_check = lambda t: True
            max_length = 500
            max_lines = 10

        super().__init__(
            text=text.strip("'"),
            default=port.node.get_default(port.port).strip("'"),
            size=(port.node.WIDTH - 19, 22),
            pad=2,
            inf_width=(type != 'code'),
            inf_height=(type == 'code'),
            max_line_width=None if type != 'code' else 300,
            centery_aligned=(type != 'code'),
            text_check=text_check,
            max_length=max_length,
            max_lines=max_lines,
            outline_color=(0, 0, 0),
            outline_width=3
        )
        
        if type == 'string':
            self.add_animation([{
                'attr': 'width',
                'end': 200,
                'frames': 10
            }],
            tag='open')
            
        elif type == 'code':
            self.pad['bottom'] = 0
            self.add_animation([{
                'attr': 'width',
                'end': 300,
                'frames': 10
            }],
            tag='open')
            self.add_animation([{
                'attr': 'height',
                'end': 300,
                'frames': 10
            }],
            tag='open')
        
        self.last_text = self.text
        
    @property
    def port(self):
        return self.parent
        
    @property
    def value(self):
        return self.text
        
    def get_output(self):
        if self.type == 'num':
            return self.text
        elif self.type == 'string':
            return f"'{self.text}'"
        elif self.type == 'code':
            return self.text
            
    def set_value(self, text):
        self.set_text(text)
            
    def close(self):
        super().close()
        
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
                if self.type == 'num':
                    try:
                        out = str(eval(out))
                    except:
                        pass
                super(Text_Element, self).set_text(out)
                
            elif not self.enabled:
                self.set_enabled(True)
                self.set_text(self.last_text)
            
            
            
            