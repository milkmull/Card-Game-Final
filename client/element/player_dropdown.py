from ui.element.compound.dropdown import Dropdown

class Player_Dropdown(Dropdown):
    def __init__(self, client, *args, **kwargs):
        self.client = client
        p = client.get_player(client.pid)
        
        super().__init__(
            [p.name for p in self.client.players], 
            *args, 
            selected=p.name,
            text_color=p.color,            
            **kwargs
        )

    def get_color(self, name):
        for p in self.client.players:
            if p.name == name:
                return p.color
        return (255, 255, 255)
        
    def set_value(self, value):
        self.text_color = self.get_color(value)
        super().set_value(value)
        
    def new_window(self, *args, **kwargs):
        super().new_window(*args, **kwargs)
        
        w = self.children[-1]
        for p, b in zip(self.client.players, w.elements):
            b.text_color = p.color
        