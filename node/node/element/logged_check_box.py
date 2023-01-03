from ui.element.standard.check_box import Check_Box

class Logged_Check_Box(Check_Box):
    def __init__(
        self,
        port,
        value=True
    ):
        
        super().__init__(
            value=value,
            outline_color=(0, 0, 0),
            outline_width=3
        )
        
        self.last_value = self.value
        
    @property
    def port(self):
        return self.parent
        
    def get_output(self):
        return str(self.value)
        
    def set_value(self, value, undo=False):
        super().set_value(value)
        if undo:
            self.last_value = value
        
    def reset_value(self, value):
        self.set_value(value)
        self.last_value = self.value
        
    def left_click(self):
        super().left_click()
        
        if self.port.manager:
            if self.value != self.last_value:
                self.port.manager.add_log({
                    "t": "val",
                    "e": self,
                    "v": (self.last_value, self.value)
                })
                self.last_value = self.value
            
    def update(self):
        super().update()
        
        if self.port.port > 0:
        
            if self.port.connection:
                self.set_enabled(False)
                out = self.port.connection.get_output(self.port.connection_port.true_port)
                try:
                    out = eval(out)
                except:
                    pass
                self.set_value(out)
                
            else:
                self.set_enabled(True)         