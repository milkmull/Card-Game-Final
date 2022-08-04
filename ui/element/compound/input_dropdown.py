from ..standard.input import Input
from .dropdown import Dropdown

class Input_Dropdown(Dropdown, Input):
    def __init__(
        self,
        selection,
        **kwargs
    ):
        Input.__init__(self, **kwargs)
        Dropdown.__init__(
            self,
            selection,
            cursor=self.cursor,
            **kwargs
        )
        
        self.arrow.set_enabled(True)
        self.arrow.add_event(
            tag='left_click',
            func=self.flip
        )
        
        self.listeners.pop(-1)
        
    @property
    def click_close(self):
        return not (self.hit or self.hit_any()) and self.is_open