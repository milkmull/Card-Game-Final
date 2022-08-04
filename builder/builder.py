from tkinter import Tk, filedialog
Tk().withdraw()

import pygame as pg

from .custom_card_base import Card
from .camera import run as run_camera
from node.editor import Node_Editor

from data.constants import TYPES_DICT, TAGS_DICT
from ui.element.base.base import Base_Element
from ui.element.base.style import Style
from ui.element.elements import Textbox, Image, Button, Check_Box, Input, Flipper, Dropdown, Input_Dropdown
from ui.icons.icons import icons
from ui.menu.menu import Menu
from ui.menu.templates.notice import Notice
from ui.menu.templates.yes_no import Yes_No

from .elements.rgb_slider import RGB_Slider
from .elements.audio_manager import Audio_Manager

def get_section(elements, label, menu):
    r = elements[0].rect.unionall([e.padded_rect for e in elements]).inflate(20, 30)
    section = Style(
        size=r.size,
        pos=r.topleft,
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=10,
        layer=-1
    )
    
    for e in elements:
        section.add_child(e, current_offset=True)
        
    label = Textbox(
        text=label,
        text_size=15,
        fill_color=menu.fill_color,
        left_pad=5,
        right_pad=5
    )
    label.rect.midleft = (section.rect.left + 15, section.rect.top)
    section.add_child(label, current_offset=True)
    
    return section

def builder(menu):
    body = menu.body
    elements = [menu.card]
    menu.elements_dict['card'] = menu.card
    
    button_kwargs = {
        'text_size': 15,
        'size': (150, 25),
        'x_pad': 5,
        'top_pad': 2,
        'centery_aligned': True,
        'hover_color': (100, 100, 100)
    }
    
    icon_kwargs = {
        'font_name': 'icons.ttf',
        'centerx_aligned': True,
        'centery_aligned': True
    }
    
#save section

    x = 15
    y = 10
    save_elements = []
    
    save_button = Button.Text_Button(
        text='Save',
        func=menu.card.save,
        **button_kwargs
    )
    save_button.rect.topleft = (x, y)
    save_elements.append(save_button)
    
    save_icon = Textbox(
        text=icons['save'],
        text_color=(0, 0, 247),
        **icon_kwargs
    )
    save_button.add_child(save_icon, right_anchor='right', right_offset=-2, centery_anchor='centery')
    save_icon.set_enabled(False) 
    
    y += save_button.rect.height + 3
    
    publish_button = Button.Text_Button(
        text='Publish',
        func=menu.card.publish,
        **button_kwargs
    )
    publish_button.rect.topleft = (x, y)
    save_elements.append(publish_button)
    
    publish_icon = Textbox(
        text=icons['x'] if not menu.card.published else icons['check'],
        text_color=(255, 0, 0) if not menu.card.published else (0, 255, 0),
        **icon_kwargs
    )
    publish_button.add_child(publish_icon, right_anchor='right', centery_anchor='centery')
    publish_icon.set_enabled(False) 
    
    y += publish_button.rect.height + 3
    
    export_button = Button.Text_Button(
        text='Export As Image',
        func=menu.export_image,
        **button_kwargs
    )
    export_button.rect.topleft = (x, y)
    save_elements.append(export_button)
    
    export_icon = Textbox(
        text=icons['folder'],
        text_color=(241, 213, 80),
        **icon_kwargs
    )
    export_button.add_child(export_icon, right_anchor='right', centery_anchor='centery')
    export_icon.set_enabled(False) 
    
    save_section = get_section(save_elements, 'Save Card:', menu)
    save_section.rect.topleft = (menu.card.rect.right + 20, 20)
    elements.append(save_section)
    
#weight section

    weight_flipper = Flipper.Text_Flipper.Counter(
        range(1, 5),
        index=menu.card.weight - 1,
        button_kwargs={
            'pad': 5,
            'border_radius': 5
        }
    )
    weight_section = get_section([weight_flipper], 'Card Rarity:', menu)
    weight_section.rect.inflate_ip(100, 0)
    weight_flipper.rect.center = weight_section.rect.center
    weight_flipper.set_stuck(True)
    weight_section.rect.topleft = (save_section.rect.right + 20, save_section.rect.top)
    elements.append(weight_section)
    
    weight_flipper.add_event(
        tag='set',
        func=menu.card.set_weight,
        args=[lambda: int(weight_flipper.get_text())]
    )
    
#type section

    type_select = Dropdown(
        TYPES_DICT,
        selected=menu.card.type,
        left_pad=5,
        right_pad=25,
        y_pad=2,
        hover_color=(100, 100, 100),
        window_kwargs = {
            'fill_color': menu.fill_color,
            'outline_color': (255, 255, 255),
            'outline_width': 3
        }
    )
    type_select.arrow.set_anchors(left='right', left_offset=7, centery='centery')
    
    type_section = get_section([type_select], 'Card Type:', menu)
    type_section.rect.topleft = (weight_section.rect.left, weight_section.rect.bottom + 20)
    type_section.layer = 2
    elements.append(type_section)
    
    type_select.add_event(
        tag='set',
        func=menu.card.set_type,
        args=[type_select.get_text]
    )
    
#tag section
    
    tag_elements = []

    tags = []
    y = 0
    for _ in range(3):
        tag = Textbox(
            size=(150, 25),
            centery_aligned=True
        )
        tag.rect.topright = (0, y)
        tags.append(tag)
        
        b = Button.Text_Button(
            text=icons['x'],
            text_color=(255, 0, 0),
            **icon_kwargs
        )
        b.turn_off()
        b.rect.midright = (tag.rect.right - 5, tag.rect.centery)
        tag.add_child(b, current_offset=True)
        
        def clear(tag=tag, b=b, tags=tags):
            menu.card.remove_tag(tag.text)
            tag.clear()
            current_tags = sorted([t.text for t in tags], key=lambda text: not text)
            for tag, text in zip(tags, current_tags):
                tag.set_text(text)
                tag.first_born.set_on_off(text)
   
        b.add_event(
            tag='left_click',
            func=clear
        )

        y += tag.rect.height + 5
        
    for tag, textbox in zip(menu.card.tags, tags):
        textbox.set_text(tag)
        textbox.first_born.turn_on()
        
    tag_elements += tags

    add_button = Button.Text_Button(
        text=icons['left-arrow-2'],
        pad=5,
        hover_color=(100, 100, 100),
        border_radius=5,
        **icon_kwargs
    )
    add_button.rect.midleft = (tag_elements[0].rect.right + 5, tag_elements[0].rect.centery)
    tag_elements.append(add_button)

    tag_select = Input_Dropdown(
        TAGS_DICT,
        selected=menu.card.tags[0],
        max_length=9,
        max_lines=1,
        centery_aligned=True,
        left_pad=5,
        right_pad=20,
        y_pad=2,
        fill_color=(255, 255, 255),
        text_color=(0, 0, 0),
        window_kwargs={
            'fill_color': menu.fill_color,
            'outline_color': (255, 255, 255),
            'outline_width': 3
        }    
    )
    tag_select.height = 25
    tag_select.rect.midleft = (add_button.padded_rect.right + 10, add_button.rect.centery)
    tag_elements.append(tag_select)
    
    tags_section = get_section(tag_elements, 'Card Tags:', menu)
    tags_section.rect.topleft = (save_section.rect.left, type_section.rect.bottom + 20)
    tags_section.layer = 1
    elements.append(tags_section)
    
    def add_tag():
        text = tag_select.text
        if menu.card.add_tag(text):
            for tag in tags:
                if not tag.text:
                    tag.set_text(text)
                    tag.first_born.turn_on()
                    break
                
    add_button.add_event(
        tag='left_click',
        func=add_tag
    )
    
    tag_select.add_event(
        tag='enter',
        func=add_tag
    )
  
#image section
    
    image_elements = []

    x = 15
    y = 10
    
    file_button = Button.Text_Button(
        text='Import Image',
        func=menu.open_image,
        **button_kwargs
    )
    file_button.rect.topleft = (x, y)
    image_elements.append(file_button)
    
    file_icon = Textbox(
        text=icons['folder'],
        text_color=(241, 213, 80),
        **icon_kwargs
    )
    file_button.add_child(file_icon, right_anchor='right', centery_anchor='centery')
    file_icon.set_enabled(False)

    y += file_button.rect.height + 3

    def take_picture():
        picture = run_camera()
        if picture:
            menu.card.update_image(picture)
            
    camera_button = Button.Text_Button(
        text='Use Camera',
        func=take_picture,
        **button_kwargs
    )
    camera_button.rect.topleft = (x, y)
    image_elements.append(camera_button)
    
    camera_icon = Textbox(
        text=icons['camera'],
        **icon_kwargs
    )
    camera_button.add_child(camera_icon, right_anchor='right', centery_anchor='centery')
    camera_icon.set_enabled(False) 

    y += camera_button.rect.height + 20

    rotate_button = Button.Text_Button(
        text='Rotate Image',
        func=menu.card.rotate_image,
        **button_kwargs
    )
    rotate_button.rect.topleft = (x, y)
    image_elements.append(rotate_button)
    
    rotate_icon = Textbox(
        text=icons['rotate'],
        text_size=18,
        **icon_kwargs
    ).to_image()
    rotate_icon.transform('flip', True, False, overwrite=True)
    rotate_icon.transform('rotate', -90)
    rotate_button.add_child(rotate_icon, right_anchor='right', centery_anchor='centery')
    rotate_icon.set_enabled(False)
    
    y += rotate_button.rect.height + 3

    aspect_button = Button.Text_Button(
        text='Keep Aspect',
        **button_kwargs
    )
    aspect_button.rect.topleft = (x, y)
    image_elements.append(aspect_button)
    
    keep_aspect = menu.card.elements_dict['pic'].keep_aspect
    aspect_icon = Textbox(
        text=icons['check'] if keep_aspect else icons['x'],
        text_color=(0, 255, 0) if keep_aspect else (255, 0, 0),
        **icon_kwargs
    )
    aspect_button.add_child(aspect_icon, right_anchor='right', centery_anchor='centery')
    aspect_icon.set_enabled(False)
    
    def set_keep_aspect():
        keep_aspect = menu.card.elements_dict['pic'].keep_aspect
        menu.card.set_image_keep_aspect(not keep_aspect)
        keep_aspect = not keep_aspect
        
        if keep_aspect:
            aspect_icon.text_color = (0, 255, 0)
            aspect_icon.set_text(icons['check'])
        else:
            aspect_icon.text_color = (255, 0, 0)
            aspect_icon.set_text(icons['x'])
            
    aspect_button.add_event(tag='left_click', func=set_keep_aspect)
    
    y += aspect_button.rect.height + 3

    outline_button = Button.Text_Button(
        text='Outline Image',
        **button_kwargs
    )
    outline_button.rect.topleft = (x, y)
    image_elements.append(outline_button)
    
    outline = bool(menu.card.elements_dict['pic'].outline_color)
    outline_icon = Textbox(
        text=icons['check'] if outline else icons['x'],
        text_color=(0, 255, 0) if outline else (255, 0, 0),
        **icon_kwargs
    )
    outline_button.add_child(outline_icon, right_anchor='right', centery_anchor='centery')
    outline_icon.set_enabled(False)
    
    def set_outline():
        outline = bool(menu.card.elements_dict['pic'].outline_color)
        menu.card.set_image_outline(not outline)
        outline = not outline
        
        if outline:
            outline_icon.text_color = (0, 255, 0)
            outline_icon.set_text(icons['check'])
        else:
            outline_icon.text_color = (255, 0, 0)
            outline_icon.set_text(icons['x'])
            
    outline_button.add_event(tag='left_click', func=set_outline)

    image_section = get_section(image_elements, 'Card Image:', menu)
    image_section.rect.topleft = (tags_section.rect.left, tags_section.rect.bottom + 20)
    elements.append(image_section)

    def draw_line(surf):
        y = (camera_button.padded_rect.bottom + rotate_button.padded_rect.top) // 2
        pg.draw.line(
            surf,
            (255, 255, 255),
            (camera_button.rect.left, y),
            (camera_button.rect.right, y),
            width=2
        )

    elements.append(Base_Element(draw=draw_line))
    
#color section
    
    color_elements = []
    x = 15
    y = 10

    for i, channel in enumerate(('r', 'g', 'b')):
        
        rgb_slider = RGB_Slider(
            channel,
            size=(255, 10),
            dir=0,
            outline_color=(255, 255, 255),
            outline_width=1
        )
        rgb_slider.set_state(menu.card.color[i])
        rgb_slider.rect.topleft = (x, y)
        color_elements.append(rgb_slider)
        menu.elements_dict[channel] = rgb_slider
        
        y += rgb_slider.rect.height + 20

    color_section = get_section(color_elements, 'Card Color:', menu)
    color_section.rect.topleft = (image_section.rect.right + 20, image_section.rect.top)
    elements.append(color_section)
 
#audio section

    am = Audio_Manager(menu.card)
    audio_section = get_section([am], 'Card Audio:', menu)
    audio_section.rect.topleft = (color_section.rect.left, color_section.rect.bottom + 20)
    
    elements.append(audio_section)
    
#other
    
    return_button = Button.Text_Button(
        text='Return To Menu',
        size=(200, 30),
        centerx_aligned=True,
        centery_aligned=True,
        hover_color=(100, 100, 100),
        tag='exit'
    )
    return_button.rect.topleft = (weight_section.rect.right + 30, weight_section.rect.top)
    elements.append(return_button)
    
    node_button = Button.Text_Button(
        text='Node Editor',
        size=(200, 30),
        centerx_aligned=True,
        centery_aligned=True,
        hover_color=(100, 100, 100),
        func=menu.node_editor.run
    )
    node_button.rect.midtop = (return_button.rect.centerx, return_button.rect.bottom + 20)
    elements.append(node_button)
    
    return elements
  
def run(info):
    b = Builder(info)
    b.run()
  
class Builder(Menu):
    def __init__(self, card_info):
        self.card = Card(**card_info)
        self.node_editor = Node_Editor(self.card)

        super().__init__(builder, fill_color=(32, 32, 40))

    def update(self):
        super().update()  
        self.update_color()
        
    def exit(self):
        m = Yes_No(text_kwargs={'text': 'Save before quitting?'})
        if m.run():
            self.card.save()
        return super().exit()
        
    def quit2(self):
        m = Yes_No(text_kwargs={'text': 'Save before quitting?'})
        if m.run():
            self.card.save()
        return super().quit()
            
#image stuff--------------------------------------------------------------------------------------

    def open_image(self):
        files = (
            ('All Image Files', ('*.jpg', '*.jpeg', '*.png', '*.bmp'))
            ('JPEG', ('*.jpg', '*.jpeg')),
            ('PNG', '*.png'),
            ('BMP', '*.bmp'),
        )
        file = filedialog.askopenfilename(
            initialdir='/',
            title='Select An Image',
            filetypes=files
        )
        if file:
        
            try:
                image = pg.image.load(file).convert_alpha()
                self.card.update_image(image)
            except pg.error:
                Notice(text_kwargs={'text': 'Error: Unable to load file'}).run()
        
    def export_image(self):
        files = (
            ('JPEG', '*.jpg'),
            ('PNG', '*.png'),
            ('BMP', '*.bmp')
        )
        file = filedialog.asksaveasfilename(
            initialdir='/',
            title='Save As',
            filetypes=files
        )
        if file:
            self.card.export_image(file)

    def update_published(self):
        t = self.elements_dict['published']
        if self.card.published and 'True' not in t.message:
            t.fgcolor = (0, 255, 0)
            t.set_message('published: True')
        elif not self.card.published and 'False' not in t.message:
            t.fgcolor = (255, 0, 0)
            t.set_message('published: False')

    def update_color(self):
        color = [
            self.elements_dict['r'].get_state(),
            self.elements_dict['g'].get_state(),
            self.elements_dict['b'].get_state()
        ]
        self.card.set_color(color)
        
#card stuff-------------------------------------------------------------------------------------

    def save_card(self):
        self.card.save()#nodes=self.node_editor.nodes)
        
    def publish_card(self):
        self.card.publish(nodes=self.node_editor.nodes)



