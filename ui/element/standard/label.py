from ..base.text_element import Text_Element

class Label(Text_Element):
    defaults = {
        "centerx_aligned": True,
        "centery_aligned": True,
        "border_top_left_radius": 10,
        "border_top_right_radius": 10
    }
    def __init__(
        self,
        parent,
        **kwargs
    ):
        super().__init__(**(Label.defaults | kwargs))
        self.set_parent(parent)
        
    def update(self):
        super().update()
        tr = self.parent.total_rect
        self.size = (tr.width, self.rect.height)
        self.rect.bottomleft = self.parent.rect.topleft
        