from ui.element.elements import Button
from ui.icons.icons import icons

from .client_base import Client_Base, client_screen

def test_client_screen(menu):
    body = menu.body
    elements = client_screen(menu)
    
    return elements

class Test_Client(Client_Base):
    def __init__(self, connection):
        super().__init__(connection, set_screen=test_client_screen)

    def add_player(self, pid, name):
        if p := super().add_player(pid, name):
            
            b = Button.Text_Button(
                text=icons['plus'],
                font_name='icons.ttf',
                centerx_aligned=True,
                centery_aligned=True,
                text_color=(0, 255, 0),
                hover_color=(100, 100, 100),
                border_radius=5
            )
            
            b.rect.topleft = 