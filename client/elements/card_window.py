from ui.element.window.live_window import Live_Window

class Card_Window(Live_Window):
    SEP = 5
    VERTICAL_ORIENTATION = {
        'dir': 1,
        'marginy': SEP,
        'bordery': SEP,
        'centerx_aligned': True
    }
    HORIZONTAL_ORIENTATION = {
        'dir': 0,
        'marginx': SEP,
        'borderx': SEP,
        'centery_aligned': True
    }
    SPOT_ORIENTATION = {
        'dir': 1,
        'marginy': SEP,
        'centerx_aligned': True
    }
    SELECT_ORIENTATION = {
        'dir': 0,
        'marginx': SEP,
        'marginy': SEP,
        'borderx': SEP,
        'bordery': SEP
    }
    def __init__(self, *args, dir=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        match dir:
        
            case 0:
                self.orientation_cache.update(Card_Window.HORIZONTAL_ORIENTATION)
            case 1:
                self.orientation_cache.update(Card_Window.VERTICAL_ORIENTATION)
            case 2:
                self.orientation_cache.update(Card_Window.SPOT_ORIENTATION)
            case 3:
                self.orientation_cache.update(Card_Window.SELECT_ORIENTATION)
            
    def clear(self):
        if self.elements:
            self.join_elements([])
        
    def join_elements(self, *args, **kwargs):
        last_batch = self.elements.copy()
        super().join_elements(*args, use_last=True, **kwargs)
        for c in last_batch:
            if c not in self.elements:
                c.parent = None
                
        if self.inf_height:
            self.y_scroll_bar.go_to_bottom()
        