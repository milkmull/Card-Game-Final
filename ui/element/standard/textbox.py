from ..base.text_element import Text_Element
from .image import Image

class Textbox(Text_Element):
    def to_image(self, **kwargs):
        return Image(image=self.text_surf, **kwargs)
        
    def clear(self):
        self.set_text("")
        