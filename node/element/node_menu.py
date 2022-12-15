import pygame as pg

from ..node.node_base import Node, unpack

from ui.element.elements import Textbox, Button, Label, Popup
from ui.element.utils.image import get_arrow

class Node_Menu(Popup.Live_Popup):
    def __init__(self, manager):
        self.manager = manager
        
        super().__init__(
            size=(560, 450),
            fill_color=(0, 0, 0),
            arrow_kwargs={
                'color': (0, 0, 0)
            },
            button_kwargs={
                'hover_color': None
            },
            animation_kwargs={
                'frames': 5,
                'method': 'ease_out_sine'
            },
            layer=4
        )
        self.button.rect.top += 8
        self.button.rect.left -= 8
        self.button.set_stuck(True)
        self.rect.midtop = manager.body.midbottom

        self.tabs = Node.get_categories()
        self.buttons = {}

        x = self.rect.x - 5
        y = self.rect.y + 5
        for tab, _ in self.tabs.items():
            b = Button.Text_Button(
                text=tab.title(),
                pad=2,
                fill_color=(155, 88, 108),
                outline_color=(0, 0, 0),
                outline_width=2,
                func=self.set_tab,
                args=[tab],
                hover_color=(253, 180, 100)
            )
            b.rect.topright = (x, y)
            
            b.add_animation(
                [{
                    'attr': 'text_color',
                    'end': (0, 0, 0)
                }],
                tag='hover'
            )
            
            self.buttons[tab] = b
            self.add_child(b, current_offset=True)
            
            y += b.padded_rect.height + 5

        tab = list(self.tabs)[0]
        self.buttons[tab].run_animations('hover')
        self.set_tab(tab)
        
        self.label = Label(
            self,
            height=30,
            text='Nodes',
            fill_color=(0, 198, 195),
            text_color=(0, 0, 0),
            layer=self.layer - 1
        )

        self.label.add_event(
            tag='left_click',
            func=self.open_close
        )
        
    @property
    def total_rect(self):
        if self.y_scroll_bar.visible:
            return self.outline_rect.union(self.y_scroll_bar.total_rect)
        return self.outline_rect
        
    @property
    def safety_rect(self):
        return list(self.buttons.values())[0].rect.unionall([b.rect for b in self.buttons.values()])

    def get_hit(self):
        return self.hit_any() or self.safety_rect.collidepoint(pg.mouse.get_pos()) or self.label.hit
        
    def set_tab(self, tab):
        elements = []
        style = {'fgcolor': (255, 255, 255), 'style': 4}
        for subtab, names in self.tabs[tab].items():
        
            label = Textbox(
                text=subtab.title(),
                text_size=40,
                size=(self.rect.width - 30, 40),
                text_style={i: style for i in range(len(subtab))}
            )
            elements.append(label)
            
            buttons = []
            
            for name in names:
                if tab == 'group':
                    data = Node.GROUP_DATA[name]
                    b = Button.Image_Button(
                        image=unpack(data, map=False)[-1].get_raw_image(scale=0.75),
                        pad=5,
                        func=self.get_group_node,
                        args=[name],
                        hover_color=(100, 100, 100),
                        border_radius=10
                    )
                else:
                    b = Button.Image_Button(
                        image=Node.NODE_DATA[name](0).get_raw_image(scale=0.75),
                        pad=5,
                        func=self.get_node,
                        args=[name],
                        hover_color=(100, 100, 100),
                        border_radius=10
                    )
                buttons.append(b)
                
            buttons.sort(key=lambda b: b.rect.height)
            elements += buttons
            
        self.join_elements(elements, dir=0, margin=10, border=10)
        self.y_scroll_bar.go_to_top()
        
        for t, b in self.buttons.items():
            b.unfreeze_animations('hover')
            if not b.hit:
                b.run_animations('hover', reverse=True)
            if t == tab:
                b.run_animations('hover')
                b.freeze_animations('hover')

    def get_node(self, *args, **kwargs):
        self.manager.get_node(*args, **kwargs)
        self.close()
        
    def get_group_node(self, *args, **kwargs):
        self.manager.get_group_node(*args, **kwargs)
        self.close()
        
    def events(self, events):
        super().events(events)
        self.label.events(events)

        if (mbd := events.get('mbd')) and (not self.get_hit() and self.is_open):
            if mbd.button == 1 or mbd.button == 3:
                self.close() 
                    
    def update(self):
        super().update()
        self.label.update()
        
    def draw(self, surf):
        self.label.draw(surf)
        super().draw(surf)
