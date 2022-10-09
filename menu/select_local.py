from ui.scene.scene import Scene
from ui.element.base.style import Style
from ui.element.elements import Textbox, Button
from ui.element.utils.image import get_arrow

def join_game(scene, games):
    elements = []

    s = Style(
        size=(350, 150),
        fill_color=(100, 100, 100),
        outline_color=(0, 0, 128),
        outline_width=5,
        border_radius=10,
        layer=-10
    )
    s.rect.center = scene.rect.center
    elements.append(s)
    
    name = Textbox(centery_aligned=True)
    name.rect.topleft = (s.rect.left + 10, s.rect.top + 10)
    elements.append(name)
    
    host = Textbox(centery_aligned=True)
    host.rect.topleft = name.rect.bottomleft
    host.rect.y += 5
    elements.append(host)
    
    index = None
    if len(games) > 1:
        index = Textbox(center_aligned=True)
        s.add_child(
            index,
            centerx_anchor='centerx',
            bottom_anchor='top',
            bottom_offset=-20
        )
    
    current_index = [-1]
    
    def swap(dir):
        current_index[0] = (current_index[0] + dir) % len(games)
        
        _name, _host = games[current_index[0]]
        name.set_text(_name)
        name.chop_to_width(width=s.rect.width - 15)
        host.set_text(_host)
        host.set_visible(_name != _host)
        
        if index:
            index.set_text(str(current_index[0] + 1))
        
    swap(1)
    
    if len(games) > 1:
    
        right_arrow = Button.Image_Button(
            image=get_arrow('>', size=(30, 30)),
            func=swap,
            args=(1,)
        )
        right_arrow.rect.midleft = (s.rect.right + 20, s.rect.centery)
        elements.append(right_arrow)
        
        left_arrow = Button.Image_Button(
            image=get_arrow('<', size=(30, 30)),
            func=swap,
            args=(-1,)
        )
        left_arrow.rect.midright = (s.rect.left - 20, s.rect.centery)
        elements.append(left_arrow)
        
    def return_host():
        host = host.get_text()
        scene.set_return(host)

    b = Button.Text_Button(
        text='Join Game!',
        text_size=35,
        inf_width=False,
        inf_height=False,
        center_aligned=True,
        size=(200, 80),
        fill_color=(0, 200, 0),
        text_color=(0, 0, 0),
        border_radius=10,
        func=return_host,
        outline_color=(0, 0, 0),
        outline_width=3
    )
    b.rect.top = host.rect.bottom + 15
    b.set_parent(
        s,
        left_anchor='left',
        left_offset=15,
        right_anchor='right',
        right_offset=-15,
        bottom_anchor='bottom',
        bottom_offset=-15,
        top_anchor='top',
        top_offset=b.rect.top - s.rect.top
    )
    elements.append(b)
    
    cancel_button = Button.Text_Button(
        text='Cancel',
        size=(100, 30),
        center_aligned=True,
        hover_color=(255, 0, 0),
        text_hover_color=(0, 0, 0),
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=5,
        tag='exit'
    )
    cancel_button.rect.midtop = (s.rect.centerx, s.rect.bottom + 20)
    elements.append(cancel_button)
    
    return elements
    
def run_select_local(games):
    s = Scene(join_game, init_args=(games,))
    host = s.run()
    return host
    