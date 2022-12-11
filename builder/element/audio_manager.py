import os
from tkinter import filedialog
import shutil

import pygame as pg

from ..media.audio_capture import Audio_Capture, get_sound_length

from ui.scene.scene import Scene
from ui.scene.templates.notice import Notice

from ui.element.base.position import Position
from ui.element.elements import Textbox, Button, Slider, Live_Window, Label, Dropdown
from ui.icons.icons import icons

def select_device(scene, mic):
    body = scene.body
    elements = []
    
    mic_select = Dropdown(
        [name for name, i in mic.devices],
        selected=mic.device[0],
        fill_color=(255, 255, 255),
        text_color=(0, 0, 0),
        y_pad=5,
        left_pad=5,
        right_pad=20,
        window_kwargs={
            'fill_color': (0, 0, 0),
            'outline_color': (255, 255, 255),
            'outline_width': 3
        }
    )
    mic_select.rect.width = max(300, mic_select.rect.width)
    mic_select.rect.center = (body.centerx, body.centery - 50)
    elements.append(mic_select)
        
    def select():
        selected_name = mic_select.text
        for i, (name, index) in enumerate(mic.devices):
            if name == selected_name:
                mic.device_index = i
                break
            
    mic_select.add_event(
        tag='set',
        func=select
    )
    
    label = Textbox(
        text='Audio Input Device:',
        text_size=18
    )
    label.rect.bottomleft = (mic_select.rect.left, mic_select.padded_rect.top - 5)
    mic_select.add_child(label, current_offset=True)

    def refresh():
        mic.refresh()
        scene.refresh()
        
    exit_button = Button.Text_Button(
        text=icons['cross'],
        font_name='icons.ttf',
        centerx_aligned=True,
        centery_aligned=True,
        left_pad=5,
        right_pad=2,
        top_pad=4,
        bottom_pad=2,
        text_color=(255, 0, 0),
        hover_color=(100, 100, 100),
        tag='exit'
    )
    exit_button.rect.bottomright = (
        mic_select.padded_rect.right,
        mic_select.padded_rect.top - 5
    )
    mic_select.add_child(exit_button, current_offset=True)
    
    refresh_button = Button.Text_Button(
        text=icons['spinner11'],
        font_name='icons.ttf',
        text_size=17,
        centerx_aligned=True,
        centery_aligned=True,
        pad=5,
        text_color=(0, 255, 0),
        hover_color=(100, 100, 100),
        func=refresh,
        description='Refresh'
    )
    refresh_button.rect.topright = (exit_button.padded_rect.left - 10, exit_button.rect.top)
    mic_select.add_child(refresh_button, current_offset=True)

    b = Button.Text_Button(
        size=body.size,
        cursor=0,
        tag='exit',
        layer=-1
    )
    elements.append(b)

    return elements
    
def run_select_device(mic):
    if mic.devices:
        Scene(select_device, init_args=[mic], overlay=True).run()
    else:
        Notice(text_kwargs={'text': 'No audio recording devices could be found'}).run()

def audio_manager(manager):
    elements = []
    
    slider = Slider(
        range(200),
        size=(255, 5),
        fill_color=(255, 255, 255),
        handel_kwargs={
            'size': (10, 10),
            'fill_color': (255, 0, 0),
            'outline_color': None
        }
    )
    slider.set_enabled(False)
    manager.slider = slider
    elements.append(slider)
    
    def draw_slider(surf):
        w = slider.handel.rect.centerx - slider.rect.left
        h = slider.rect.height
        pg.draw.rect(surf, (255, 0, 0), pg.Rect(slider.rect.topleft, (w, h)))
    
    slider.add_event(
        tag='draw',
        func=draw_slider,
        args=[pg.display.get_surface()]
    )
    
    button_Kwargs = {
        'centerx_aligned': True,
        'centery_aligned': True,
        'pad': 5,
        'hover_color': (100, 100, 100)
    }
    
    x = slider.rect.x
    
    record_button = Button.Text_Button(
        text=icons['mic'],
        font_name='icons.ttf',
        text_color=(255, 0, 0),
        func=manager.record,
        description='Record',
        **button_Kwargs
    )
    record_button.rect.bottomleft = (slider.rect.left + 5, slider.rect.top - 20)
    elements.append(record_button)
    
    x += record_button.padded_rect.width + 10
    
    play_button = Button.Text_Button(
        text=icons['play3'],
        font_name='icons.ttf',
        text_color=(0, 255, 0),
        func=manager.play_stop,
        description='Play',
        **button_Kwargs
    )
    play_button.rect.midleft = (x, record_button.rect.centery)
    elements.append(play_button)
    
    x = slider.rect.right
    
    settings_button = Button.Text_Button(
        text=icons['cog'],
        font_name='icons.ttf',
        text_color=(200, 200, 200),
        func=run_select_device,
        args=[manager.mic],
        description='Settings',
        **button_Kwargs
    )
    settings_button.rect.bottomright = (x - 5, slider.rect.top - 20)
    elements.append(settings_button)
    
    x -= settings_button.padded_rect.width + 10
    
    file_button = Button.Text_Button(
        text=icons['folder'],
        font_name='icons.ttf',
        text_color=(241, 213, 80),
        func=manager.import_file,
        description='Import Sound',
        **button_Kwargs
    )
    file_button.rect.midright = (x, settings_button.rect.centery)
    elements.append(file_button)
    
    x -= file_button.padded_rect.width + 5

    clear_button = Button.Text_Button(
        text=icons['cross'],
        font_name='icons.ttf',
        text_color=(255, 0, 0),
        func=manager.clear_sound,
        description='Clear',
        **button_Kwargs
    )
    clear_button.rect.midright = (x, file_button.rect.centery)
    elements.append(clear_button)

    return elements

class Audio_Manager(Position):
    def __init__(self, card):
        super().__init__()

        self.card = card
        self.mic = Audio_Capture(5)
        
        self.sound = None
        self.playing_sound = False
        self.start_time = 0
        
        elements = audio_manager(self)
        self.rect = elements[0].rect.unionall([e.padded_rect for e in elements])
        for e in elements:
            self.add_child(e, current_offset=True)
            
        self.bar = elements[0]
        self.record_button = elements[1]
        self.play_button = elements[2]
        self.clear_button = elements[-1]
        
        if card.sound:
            self.load_sound(path=card.sound_path)
        else:
            self.play_button.turn_off()
            self.clear_button.turn_off()
            
    @property
    def padded_rect(self):
        return self.rect
        
    @property
    def sound_length(self):
        if self.sound:
            return self.sound.get_length()
        return 0
            
    def kill(self):
        self.mic.close()
        
    def record(self):
        if not self.mic.devices:
            Notice(text_kwargs={'text': 'No audio recording devices could be found'}).run()
            return

        if not self.mic.recording:
            self.start_record()
        else:
            self.stop_record()

    def start_record(self):
        if self.playing_sound:
            self.stop_sound()
        self.mic.start()
        
        self.record_button.text_color = (0, 0, 255)
        self.record_button.set_text(icons['stop2'])
        self.record_button.description = 'Stop'

    def stop_record(self):
        self.mic.stop()
        
        if self.mic.saved_file:
            self.load_sound()
        else:
            Notice(text_kwargs={'text': 'Sound could.not be saved'}).run()
            
        self.mic.reset()
        self.bar.set_state(0)
        
        self.record_button.text_color = (255, 0, 0)
        self.record_button.set_text(icons['mic'])
        self.record_button.description = 'Record'
        
    def import_file(self):
        files = (
            ('All Audio Files', ('*.wav', '*.ogg')),
            ('WAV', '*.wav'),
            ('OGG', '*.ogg')
        )
        file = filedialog.askopenfilename(
            initialdir='/',
            title='Import Audio File',
            filetypes=files
        )
        if file:
            self.load_sound(path=file)
            
    def load_sound(self, path=None):
        temp_path = self.mic.get_path()
        if path is not None and not path.endswith(temp_path):
            shutil.copyfile(path, temp_path)
        
        try:
            self.sound = pg.mixer.Sound(temp_path)
        except pg.error:
            self.clear_sound()
            Notice(text_kwargs={'text': 'Error: Unable to load file'}).run()
            return
        
        length = self.sound.get_length()
        
        if 0.5 < length <= 5:
            self.play_button.turn_on()
            self.clear_button.turn_on()
            
        else:
            self.clear_sound()
            Notice(text_kwargs={'text': 'Error: Sound length must be between 0.5 and 5 seconds'}).run()
        
    def play_stop(self):
        if not self.playing_sound:
            self.play_sound()
        else:
            self.stop_sound()
 
    def play_sound(self):
        if self.sound:
            self.playing_sound = True
            self.start_time = pg.time.get_ticks()
            self.sound.play()
            
            self.play_button.text_color = (0, 0, 255)
            self.play_button.set_text(icons['stop2'])
            self.play_button.description = 'Stop'
        
    def stop_sound(self):
        if self.sound:
            self.sound.stop()
            self.playing_sound = False
            self.bar.set_state(0)
            
            self.play_button.text_color = (0, 255, 0)
            self.play_button.set_text(icons['play3'])
            self.play_button.description = 'Play'
        
    def clear_sound(self):
        if self.sound:
            self.stop_sound()
            self.sound = None
        self.mic.clear_path()
            
        self.play_button.turn_off()
        self.clear_button.turn_off()
            
    def update(self):
        super().update()

        if self.mic.recording:
            s = self.mic.get_current_length() / 5
            self.bar.set_state_as_ratio(s)
        if self.mic.finished:
            self.stop_record()
                
        if self.playing_sound:
            s = (pg.time.get_ticks() - self.start_time) / (1000 * self.sound_length)
            self.bar.set_state_as_ratio(s)
            if s >= 1:
                self.stop_sound()
                
    def draw(self, surf):
        super().draw(surf)
        
        w = self.slider.handel.rect.centerx - self.slider.rect.left
        h = self.slider.rect.height
        pg.draw.rect(surf, (255, 0, 0), pg.Rect(self.slider.rect.topleft, (w, h)))
  