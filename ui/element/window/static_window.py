from .window_base import Window_Base
from ..base.image_element import Image_Element
from ..utils.image import get_surface

class Static_Window(Window_Base, Image_Element):
    def __init__(
        self,
        **kwargs
    ):
        Image_Element.__init__(
            self,
            const_size=False,
            keep_aspect=False,
            **kwargs
        )
        Window_Base.__init__(self, **kwargs)

        if not self.image:
            self.set_image(
                get_surface(
                    self.size,
                    color=self.fill_color
                ),
                overwrite=True
            )

    def set_window(self, *args, **kwargs):
        super().set_window(*args, **kwargs)
        self.redraw()
 
    def redraw(self):
        self.reset_image()
        for e in self.elements: 
            e.update_position()
            if e.rect.colliderect(self.rect):
                e.draw_on(self.image, self.rect)

        
    