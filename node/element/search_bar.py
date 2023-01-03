import difflib

from ..node.node_base import Node

from ui.element.elements import Input, Live_Window, Button
from ui.element.utils.timer import Timer

def sort_strings(a, b):
    return difflib.SequenceMatcher(a=a, b=b, isjunk=None).ratio()

class Search_Bar(Input):
    def __init__(self, menu):
        super().__init__(
            size=(0, 25),
            text_size=15,
            pad=5,
            clip=True
        )
        self.manager = menu

        self.size = self.get_max_size(Node.NODE_DATA | Node.GROUP_DATA)
        self.open_timer = Timer()
        self.search_window = Live_Window(
            size=(self.rect.width + 10, 200),
            fill_color=(0, 0, 0)
        )
        
        self.buttons = []
        button_kwargs = {
            "size": self.size,
            "pad": 5,
            "text_size": self.text_size,
            "hover_color": (100, 100, 100),
            "centery_aligned": True
        }

        for name, obj in Node.NODE_DATA.items():
            b = Button.Text_Button(
                text=name,
                func=self.get_node,
                args=[name],
                **button_kwargs
            )
            self.buttons.append(b)

        for name, data in Node.GROUP_DATA.items():
            b = Button.Text_Button(
                text=name, 
                func=self.get_group_node, 
                args=[name],
                **button_kwargs
            )
            self.buttons.append(b)

        self.max_buttons = 12
        self.search_window.join_elements(self.buttons[:self.max_buttons], border=5, marginy=10)
        self.search_window.rect.midtop = (self.rect.centerx, self.padded_rect.bottom)
        self.add_child(self.search_window, current_offset=True)

        self.set_visible(False)
        self.rect.width += self.search_window.y_scroll_bar.rect.width
        
    @property
    def click_close(self):
        return not (self.hit or self.hit_any()) and self.is_open
       
    def open_search(self, p):
        self.rect.center = p
        self.open()
        self.highlight_section("")
        self.set_visible(True)
       
    def close(self):
        super().close()
        self.set_visible(False)
        
    def set_text(self, text):
        added = super().set_text(text)
        
        if added:
            key = lambda b: sort_strings(self.text.lower(), b.text.lower())
            self.search_window.join_elements(sorted(self.buttons, key=key, reverse=True)[:self.max_buttons], use_last=True)
            self.search_window.y_scroll_bar.go_to_top()
        
        return added
    
    def events(self, events):
        if self.visible:
            super().events(events)

        if not events["clicked"] and (mbd := events.get("mbd")):
            if mbd.button == 1:
                if self.open_timer < self.CLICK_TIMER_MAX:
                    self.open_search(mbd.pos)
                self.open_timer.reset()
                
    def get_node(self, *args, **kwargs):
        self.manager.get_node(*args, **kwargs)
        self.close()
        
    def get_group_node(self, *args, **kwargs):
        self.manager.get_group_node(*args, **kwargs)
        self.close()
            
    def update(self):
        if self.visible:
            super().update()
        self.open_timer.step()
    
    def draw(self, surf):
        Input.draw(self, surf)
        self.child_draw(surf)