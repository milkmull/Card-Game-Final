from ui.element.window.live_window import Live_Window

class Card_Window(Live_Window):
    SEP = 5
    def __init__(self, *args, dir=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.orientation_cache.update({
            'dir': dir,
            'marginx': Card_Window.SEP,
            'marginy': Card_Window.SEP,
            'borderx': Card_Window.SEP,
            'bordery': Card_Window.SEP
        })
            
    def clear(self):
        if self.elements:
            self.join_elements([])
            
    def add_element(self, element):
        self.join_elements(self.elements + [element])
        
    def remove_element(self, cid):
        self.join_elements([c for c in self.elements if c.cid != cid])
        
    def join_elements(self, *args, **kwargs):
        last_batch = self.elements.copy()
        super().join_elements(*args, use_last=True, **kwargs)
        for c in last_batch:
            if c not in self.elements:
                c.parent = None
                
        if self.inf_height:
            self.y_scroll_bar.go_to_bottom()
        