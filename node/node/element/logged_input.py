from ui.element.base.position import Position
from ui.element.base.text_element import Text_Element
from ui.element.standard.input import Input

class Logged_Input(Input):
    def __init__(
        self,
        port,
        text="",
        **kwargs
    ):
        super().__init__(text=text, **kwargs)
        self.port = port
        self.last_text = self.text
        
    @property
    def value(self):
        return self.text
        
    def get_output(self):
        return self.text
            
    def set_value(self, text, undo=False):
        self.set_text(text)
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
                    "t": "val",
                    "e": self,
                    "v": (self.last_text, self.text)
                })
                self.last_text = self.text
        
    def update(self):
        super().update()
        
        if self.port.port > 0:
        
            if self.port.connection:
                self.set_enabled(False)
                super(Text_Element, self).set_text("-")
                
            elif not self.enabled:
                self.set_enabled(True)
                self.set_text(self.last_text)
                
class Logged_Num_Input(Logged_Input):
    def __init__(
        self,
        port,
        text=""
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
        
    def get_output(self):
        out = super().get_output()
        if not out.lstrip("-"):
            return "0"
        return out
        
class Logged_String_Input(Logged_Input):
    def __init__(
        self,
        port,
        text=""
    ):
        super().__init__(
            port,
            text=text.strip("'\""),
            default=port.node.get_default(port.port).strip("'\""),
            size=(port.node.WIDTH - 19, 22),
            pad=2,
            inf_width=True,
            inf_height=False,
            centery_aligned=True,
            text_check=lambda text: "'" not in text and "\"" not in text and text.isascii(),
            max_length=25,
            max_lines=1,
            outline_color=(0, 0, 0),
            outline_width=3
        )
        
        self.add_animation([{
            "attr": "width",
            "end": 200,
            "frames": 10
        }],
        tag="open")
        
    def get_output(self):
        return f"\"{super().get_output()}\""
        
class Logged_Code_Input(Logged_Input):
    def __init__(
        self,
        port,
        text=""
    ):
        super().__init__(
            port,
            text=text,
            font_name="JetBrainsMonoNL-Regular.ttf",
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
                "attr": "width",
                "end": 300,
                "frames": 10
            }],
            tag="open"
        )
        self.add_animation(
            [{
                "attr": "height",
                "end": 300,
                "frames": 10
            }],
            tag="open"
        )
        
    def set_text(self, text):
        self.text_style = self.style_text(text)
        return super().set_text(text)
        
class Logged_Label_Input(Logged_Input):
    def __init__(
        self,
        node,
        text=""
    ):
        super().__init__(
            node,
            text=text,
            max_length=25,
            text_color=(255, 255, 255),
            size=node.label_rect.size,
            inf_width=False,
            centerx_aligned=True,
            centery_aligned=True,
            text_check=lambda text: text.replace(" ", "").isalnum(),
            fill_color=None
        )
        
    def update(self):
        Input.update(self)
        
class Logged_Vec_Input(Position):
    def __init__(
        self,
        port,
        text=""
    ):
        super().__init__()
        self.port = port
    
        self.x_val = Logged_Num_Input(port)
        self.x_val.width = port.node.WIDTH // 2 - 18
        self.y_val = Logged_Num_Input(port)
        self.y_val.width = port.node.WIDTH // 2 - 18
        
        self.add_child(self.x_val, left_anchor="left", top_anchor="top")
        self.add_child(self.y_val, left_anchor="left", left_offset=self.x_val.rect.width + 16, top_anchor="top")
        
        if text:
            x, y = text.strip("()").split(", ")
            self.x_val.set_value(x)
            self.y_val.set_value(y)
            
    @property
    def hit(self):
        return self.x_val.hit or self.y_val.hit
        
    @property
    def value(self):
        return f"({self.x_val.value}, {self.y_val.value})"
        
    def get_output(self):
        return f"({self.x_val.get_output()}, {self.y_val.get_output()})"
            
    def set_value(self, text, undo=False):
        x, y = text.strip("()").split(", ")
        self.x_val.set_value(x)
        self.y_val.set_value(y)
        
    def reset_value(self, text):
        x, y = text.strip("()").split(", ")
        self.x_val.reset_value(x)
        self.y_val.reset_value(y)
        
INPUTS = {
    "num": Logged_Num_Input,
    "string": Logged_String_Input,
    "code": Logged_Code_Input,
    "label": Logged_Label_Input,
    "vec": Logged_Vec_Input
}     