from tkinter import Tk, filedialog
Tk().withdraw()

import pygame as pg

from data.constants import TYPES_DICT, TAGS_DICT

from .custom_card_base import Card
from node.editor import Node_Editor
from node.screens.info_sheet import run as run_info_sheet

from ui.scene.scene import Scene
from ui.scene.templates.notice import Notice
from ui.scene.templates.yes_no import Yes_No

from .camera import run as run_camera

from ui.element.base.element import Element
from ui.element.base.style import Style
from ui.element.elements import Textbox, Button, Check_Box, Dropdown, Input_Dropdown, Flipper
from ui.icons.icons import icons

from .elements.rgb_slider import RGB_Slider
from .elements.audio_manager import Audio_Manager

def get_section(elements, label, scene):
    r = elements[0].rect.unionall([e.padded_rect for e in elements]).inflate(20, 30)
    section = Element(
        size=r.size,
        pos=r.topleft,
        outline_color=(255, 255, 255),
        outline_width=2,
        layer=-1
    )
    
    for e in elements:
        section.add_child(e, current_offset=True)
        
    label = Textbox(
        text=label,
        text_size=15,
        fill_color=scene.fill_color,
        left_pad=5,
        right_pad=5,
        layer=-1
    )
    label.rect.midleft = (section.rect.left + 15, section.rect.top)
    section.add_child(label, current_offset=True)
    
    return section

def builder(scene):
    body = scene.body
    scene.card.rect.midleft = (15, body.centery)
    elements = [scene.card]

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
    
# save section

    x = 15
    y = 10
    save_elements = []
    
    save_button = Button.Text_Button(
        text='Save',
        func=scene.save_card,
        **button_kwargs
    )
    save_button.rect.topleft = (x, y)
    save_elements.append(save_button)
    
    save_icon = Textbox(
        text=icons['floppy-disk'],
        text_color=(0, 0, 247),
        **icon_kwargs
    )
    save_button.add_child(save_icon, right_anchor='right', right_offset=-1, centery_anchor='centery')
    save_icon.set_enabled(False) 
    
    y += save_button.rect.height + 3
    
    if scene.card.id != 0:
    
        publish_button = Button.Text_Button(
            text='Publish',
            func=scene.publish_card,
            **button_kwargs
        )
        publish_button.rect.topleft = (x, y)
        save_elements.append(publish_button)
        
        publish_icon = Check_Box(
            value=scene.card.published,
            outline_color=(0, 0, 0),
            outline_width=2
        )
        publish_button.add_child(publish_icon, right_anchor='right', right_offset=-3, centery_anchor='centery', centery_offset=-1)
        publish_icon.set_enabled(False) 
        scene.published = publish_icon

        publish_icon.add_event(
            tag='update',
            func=publish_icon.set_value,
            args=[scene.card.get_published]
        )
        
        y += publish_button.rect.height + 3
    
    export_button = Button.Text_Button(
        text='Export As Image',
        func=scene.export_image,
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
    
    save_section = get_section(save_elements, 'Save:', scene)
    save_section.rect.topleft = (scene.card.rect.right + 20, 20)
    elements.append(save_section)
    
# weight section

    if scene.card.id != 0:

        weight_flipper = Flipper.Counter(
            range(1, 5),
            index=scene.card.weight - 1,
            button_kwargs={
                'pad': 5,
                'border_radius': 5
            }
        )
        weight_section = get_section([weight_flipper], 'Rarity:', scene)
        weight_section.rect.inflate_ip(100, 0)
        weight_flipper.rect.center = weight_section.rect.center
        weight_flipper.set_stuck(True)
        elements.append(weight_section)

        weight_flipper.add_event(
            tag='set',
            func=scene.card.set_weight,
            args=[lambda: int(weight_flipper.get_text())]
        )
    
# type section

        type_select = Dropdown(
            TYPES_DICT,
            selected=scene.card.type,
            left_pad=5,
            right_pad=25,
            y_pad=2,
            hover_color=(100, 100, 100),
            window_kwargs = {
                'fill_color': scene.fill_color,
                'outline_color': (255, 255, 255),
                'outline_width': 3
            }
        )

        type_section = get_section([type_select], 'Type:', scene)
        type_section.layer = 2
        elements.append(type_section)

        type_select.add_event(
            tag='set_text',
            func=scene.card.set_type,
            args=[type_select.get_text]
        )
    
# tag section
    
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
                text=icons['X'],
                text_color=(255, 0, 0),
                **icon_kwargs
            )
            b.turn_off()
            b.rect.midright = (tag.rect.right + 21, tag.rect.centery)
            tag.add_child(b, current_offset=True)
            
            def clear(tag=tag, b=b, tags=tags):
                scene.card.remove_tag(tag.text)
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
            
        for tag, textbox in zip(scene.card.tags, tags):
            textbox.set_text(tag)
            textbox.first_born.turn_on()
            
        tag_elements += tags

        add_button = Button.Text_Button(
            text=icons['plus'],
            text_color=(0, 255, 0),
            pad=5,
            hover_color=(100, 100, 100),
            border_radius=5,
            **icon_kwargs
        )
        tag_elements.append(add_button)

        tag_select = Input_Dropdown(
            TAGS_DICT,
            selected=scene.card.tags[0] if scene.card.tags else None,
            max_length=10,
            max_lines=1,
            text_check=lambda text: text.isalpha(),
            centery_aligned=True,
            left_pad=5,
            right_pad=20,
            y_pad=2,
            fill_color=(255, 255, 255),
            text_color=(0, 0, 0),
            window_kwargs={
                'fill_color': scene.fill_color,
                'outline_color': (255, 255, 255),
                'outline_width': 3
            },
            layer=1
        )
        tag_select.height = 25
        tag_select.rect.bottomleft = (tags[0].rect.left, tags[0].rect.top - 25)
        add_button.rect.midleft = (tag_select.padded_rect.right + 15, tag_select.rect.centery)
        tag_elements.append(tag_select)
        
        line = Style(
            size=(add_button.rect.right - tag_select.rect.left, 2),
            fill_color=(255, 255, 255)
        )
        line.rect.center = (
            (add_button.rect.right + tag_select.rect.left) // 2, 
            (tag_select.padded_rect.bottom + tags[0].padded_rect.top) // 2
        )
        tag_elements.append(line)
        
        tags_section = get_section(tag_elements, 'Tags:', scene)
        elements.append(tags_section)

        def add_tag():
            text = tag_select.text
            if scene.card.add_tag(text):
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
  
# image section
    
    image_elements = []

    x = 15
    y = 10
    
    file_button = Button.Text_Button(
        text='Import Image',
        func=scene.open_image,
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
            scene.card.update_image(picture)
            
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
        func=scene.card.rotate_image,
        **button_kwargs
    )
    rotate_button.rect.topleft = (x, y)
    image_elements.append(rotate_button)
    
    rotate_icon = Textbox(
        text=icons['spinner11'],
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
    
    keep_aspect = scene.card._pic.keep_aspect
    aspect_icon = Textbox(
        text=icons['check'] if keep_aspect else icons['X'],
        text_color=(0, 255, 0) if keep_aspect else (255, 0, 0),
        **icon_kwargs
    )
    aspect_button.add_child(aspect_icon, right_anchor='right', centery_anchor='centery')
    aspect_icon.set_enabled(False)
    
    def set_keep_aspect():
        keep_aspect = scene.card._pic.keep_aspect
        scene.card.set_image_keep_aspect(not keep_aspect)
        keep_aspect = not keep_aspect
        
        if keep_aspect:
            aspect_icon.text_color = (0, 255, 0)
            aspect_icon.set_text(icons['check'])
        else:
            aspect_icon.text_color = (255, 0, 0)
            aspect_icon.set_text(icons['X'])
            
    aspect_button.add_event(tag='left_click', func=set_keep_aspect)
    
    y += aspect_button.rect.height + 3

    outline_button = Button.Text_Button(
        text='Outline Image',
        **button_kwargs
    )
    outline_button.rect.topleft = (x, y)
    image_elements.append(outline_button)
    
    outline = bool(scene.card._pic.outline_color)
    outline_icon = Textbox(
        text=icons['check'] if outline else icons['X'],
        text_color=(0, 255, 0) if outline else (255, 0, 0),
        **icon_kwargs
    )
    outline_button.add_child(outline_icon, right_anchor='right', centery_anchor='centery')
    outline_icon.set_enabled(False)
    
    def set_outline():
        outline = bool(scene.card._pic.outline_color)
        scene.card.set_image_outline(not outline)
        outline = not outline
        
        if outline:
            outline_icon.text_color = (0, 255, 0)
            outline_icon.set_text(icons['check'])
        else:
            outline_icon.text_color = (255, 0, 0)
            outline_icon.set_text(icons['X'])
            
    outline_button.add_event(tag='left_click', func=set_outline)
    
    line = Style(
        size=(outline_button.rect.width - 5, 2),
        fill_color=(255, 255, 255)
    )
    line.rect.center = (
        camera_button.rect.centerx, 
        (camera_button.padded_rect.bottom + rotate_button.padded_rect.top) // 2
    )
    image_elements.append(line)

    image_section = get_section(image_elements, 'Image:', scene)
    elements.append(image_section)
    
# color section
    
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
        rgb_slider.set_state(scene.card.color[i])
        rgb_slider.rect.topleft = (x, y)
        color_elements.append(rgb_slider)

        y += rgb_slider.rect.height + 20

    color_section = get_section(color_elements, 'Color:', scene)
    elements.append(color_section)

    color_section.add_event(
        tag='update',
        func=lambda: scene.card.set_color([e.get_state() for e in color_elements])
    )
 
# audio section

    am = Audio_Manager(scene.card)
    audio_section = get_section([am], 'Audio:', scene)
    audio_section.rect.topleft = (color_section.rect.left, color_section.rect.bottom + 20)
    
    elements.append(audio_section)
    
# navigation

    x = 15
    y = 10
    navigation_elements = []
    
    back_button = Button.Text_Button(
        text='Return To Menu',
        tag='exit',
        **button_kwargs
    )
    back_button.rect.topleft = (x, y)
    navigation_elements.append(back_button)
    
    back_icon = Textbox(
        text=icons['arrow-left2'],
        text_color=(255, 0, 0),
        **icon_kwargs
    )
    back_button.add_child(back_icon, right_anchor='right', right_offset=-2, centery_anchor='centery')
    back_icon.set_enabled(False) 
    
    y += back_button.rect.height + 3
    
    if scene.card.id != 0:
    
        node_button = Button.Text_Button(
            text='Node Editor',
            func=scene.node_editor.run,
            **button_kwargs
        )
        node_button.rect.topleft = (x, y)
        navigation_elements.append(node_button)
        
        node_icon = Textbox(
            text=icons['arrow-right2'],
            text_color=(0, 255, 0),
            **icon_kwargs
        )
        node_button.add_child(node_icon, right_anchor='right', right_offset=-2, centery_anchor='centery')
        node_icon.set_enabled(False) 
        
        y += node_button.rect.height + 3
        
        info_button = Button.Text_Button(
            text='Info Sheet',
            func=run_info_sheet,
            **button_kwargs
        )
        info_button.rect.topleft = (x, y)
        navigation_elements.append(info_button)
        
        info_icon = Textbox(
            text=icons['file-text'],
            text_color=(255, 255, 0),
            **icon_kwargs
        )
        info_button.add_child(info_icon, right_anchor='right', right_offset=-2, centery_anchor='centery')
        info_icon.set_enabled(False) 
    
    navigation_section = get_section(navigation_elements, 'Navigation:', scene)
    navigation_section.rect.topleft = (save_section.rect.right + 20, 20)
    elements.append(navigation_section)
    
# selection
    
    if scene.card.id != 0:
        sections = {
            'type': type_section,
            'image': image_section,
            'color': color_section,
            'tags': tags_section,
            'rarity': weight_section,
            'audio': audio_section
        }
    else:
        sections = {
            'image': image_section,
            'color': color_section,
            'audio': audio_section
        } 

    buttons = {}
    
    def set_tab(tab):
        for t, section in sections.items():
            b = buttons[t]
            if t != tab:
                section.turn_off()
                b.unfreeze_animation('hover')
                if not b.hit:
                    b.run_animations('hover', reverse=True)
            else:
                section.turn_on()
                section.rect.center = (
                    (body.right + scene.card.rect.right) // 2,
                    body.centery
                )
                b.freeze_animation('hover')
    
    x = save_section.rect.left
    y = save_section.rect.bottom + 25
    for tab, section in sections.items():
        b = Button.Text_Button(
            text=tab.title(),
            pad=2,
            fill_color=(155, 88, 108),
            outline_color=(0, 0, 0),
            outline_width=2,
            func=set_tab,
            args=[tab],
            hover_color=(253, 180, 100)
        )
        
        b.add_animation(
            [{
                'attr': 'text_color',
                'end': (0, 0, 0)
            }],
            tag='hover'
        )
        
        buttons[tab] = b
        b.rect.topleft = (x, y)
        elements.append(b)
        y += b.padded_rect.height + 15
        
    if scene.card.id != 0:
        
        buttons['type'].run_animations('hover')
        set_tab('type')
        
        b = Button.Text_Button(
            size=scene.card._type.rect.size,
            func=set_tab,
            args=['type'],
            layer=1
        )
        b.set_parent(scene.card._type, left_anchor='left', top_anchor='top')
        elements.append(b)
        
        b = Button.Text_Button(
            size=scene.card._tags.rect.size,
            func=set_tab,
            args=['tags'],
            layer=1
        )
        b.set_parent(scene.card._tags, left_anchor='left', top_anchor='top')
        elements.append(b)
        
    else:
        
        buttons['image'].run_animations('hover')
        set_tab('image')
    
    b = Button.Text_Button(
        size=scene.card._pic.rect.size,
        func=set_tab,
        args=['image'],
        layer=1
    )
    elements.append(b)
    
    b.add_event(
        tag='update',
        func=lambda: setattr(b, 'rect',  scene.card._pic.image_rect.copy())
    )
    
    return elements
  
def run(info):
    b = Builder(info)
    b.run()
  
class Builder(Scene):
    def __init__(self, card_info):
        self.card = Card(**card_info)
        self.node_editor = Node_Editor(self.card, self)
        self.last_save_data = self.card.get_info()

        super().__init__(builder, fill_color=(32, 32, 40))
        
    def events(self):
        events = super().events()
        
        if events.get('ctrl'):
            if kd := events.get('kd'):
                if kd.key == pg.K_s:
                    self.save_card()
                    
    def ask_save(self):
        r = 1
        if self.card.get_info() != self.last_save_data:
            m = Yes_No(text_kwargs={'text': 'Save before quitting?'})
            r = m.run()
            if r:
                self.card.save()
        return r

    def exit(self):
        if self.ask_save() is not None:
            return super().exit()
        
    def quit(self):
        if self.ask_save() is not None:
            return super().quit()

    def open_image(self):        
        files = (
            ('All Image Files', ('*.jpg', '*.jpeg', '*.png', '*.bmp')),
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
            initialfile=self.card.classname,
            initialdir='/',
            title='Save As',
            filetypes=files,
            defaultextension='*.*'
        )
        if file:
            self.card.export_image(file)

    def save_card(self):
        self.card.save(nodes=self.node_editor.nodes)
        self.last_save_data = self.card.get_info()
        
    def publish_card(self):
        if not self.card.published:
            self.card.publish(nodes=self.node_editor.nodes)
        else:
            self.card.unpublish(nodes=self.node_editor.nodes)
        self.last_save_data = self.card.get_info()