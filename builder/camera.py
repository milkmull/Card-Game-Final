import pygame as pg

from .media.video_capture import Video_Capture

from ui.scene.scene import Scene
from ui.scene.templates.notice import Notice

from ui.element.base.element import Element
from ui.element.elements import Textbox, Image, Button
from ui.icons.icons import icons

def camera(scene):
    body = scene.body
    elements = []
    
    image = scene.camera.get_frame()
    w, h = image.get_size()
    current_frame = Image(
        image=image,
        outline_color=(255, 255, 255),
        outline_width=3,
    )
    current_frame.rect.center = (body.centerx, body.centery - 20)
    
    def update_frame():
        frame = scene.camera.get_frame()
        if frame:
            current_frame.set_image(frame, overwrite=False)
    
    current_frame.add_event(
        func=update_frame
    )
    
    elements.append(current_frame)

    camera_button = Button.Text_Button(
        text=icons['camera'],
        font_name='icons.ttf',
        text_size=40,
        size=(300, 45),
        
        centerx_aligned=True,
        centery_aligned=True,
        
        border_radius=20,
        hover_color=(255, 255, 255)
    )
    camera_button.rect.midbottom = (body.centerx, body.bottom - 10)
    elements.append(camera_button)
    
    camera_button.add_animation([{
        'attr': 'text_color',
        'end': (0, 0, 0)
    }], tag='hover')
    
    flash = Image(
        image=pg.Surface(body.size).convert_alpha(),
    )
    flash.set_enabled(False)
    flash.fill((255, 255, 255))
    flash.alpha = 0
    elements.append(flash)
    
    exit_button = Button.Text_Button(
        text=icons['X'],
        font_name='icons.ttf',
        text_color=(255, 0, 0),
        pad=5,
        centerx_aligned=True,
        centery_aligned=True,
        tag='exit'
    )
    exit_button.rect.topright = (body.right - 20, 20)
    elements.append(exit_button)

    x = current_frame.rect.right - 85
    y = current_frame.rect.top + 10
    
    ok_button = Button.Text_Button(
        text='Ok',
        centery_aligned=True,
        size=(100, 25),
        pad=5,
        hover_color=(0, 255, 0),
        layer=-1,
        func=lambda: current_frame.image,
        tag='return'
    ) 
    ok_button.rect.topleft = (x, y)
    ok_button.set_enabled(False)
    elements.append(ok_button)
    
    ok_button.add_animation(
        [{
            'attr': 'text_color',
            'end': (0, 0, 0)
        }],
        tag='hover'
    )
    
    y += ok_button.rect.height + 15

    retake_button = Button.Text_Button(
        text='Retake',
        centery_aligned=True,
        size=(100, 25),
        pad=5,
        hover_color=(100, 100, 100),
        layer=-1
    ) 
    retake_button.rect.topleft = (x, y)
    retake_button.set_enabled(False)
    elements.append(retake_button)
    
    def start_camera():
        scene.camera.start()
        
        camera_button.set_enabled(True)
        
        ok_button.set_enabled(False)
        retake_button.set_enabled(False)
        retake_button.cancel_animation('hover')
        
        current_frame.add_animation([{
            'attr': 'x',
            'end': current_frame.rect.x + 100,
            'frames': 10
        }])
        
        camera_button.add_animation([{
            'attr': 'x',
            'end': camera_button.rect.x + 100,
            'frames': 10
        }])

    def stop_camera():
        if current_frame.moving:
            return
            
        scene.camera.stop()
        
        camera_button.cancel_animation('hover')
        camera_button.set_enabled(False)
        
        ok_button.set_enabled(True)
        retake_button.set_enabled(True)

        flash.add_animation([{
            'attr': 'alpha',
            'start': 255,
            'end': 0,
            'frames': 10
        }])
        
        current_frame.add_animation([{
            'attr': 'x',
            'end': current_frame.rect.x - 100,
            'frames': 10,
            'delay': 10
        }])
        
        camera_button.add_animation([{
            'attr': 'x',
            'end': camera_button.rect.x - 100,
            'frames': 10,
            'delay': 10
        }])
        
    camera_button.add_event(
        tag='left_click',
        func=stop_camera
    )
    
    retake_button.add_event(
        tag='left_click',
        func=start_camera
    )

    return elements
    
class Camera_Scene(Scene):
    def __init__(self, **kwargs):
        super().__init__(camera, fill_color=(32, 32, 40), **kwargs)
        self.camera = Video_Capture()
        self.camera.start()
        
    def close(self):
        self.camera.close()
        
def run():
    m = Camera_Scene()
    if m.camera.exists:
        return m.run()
    m = Notice(text_kwargs={'text': 'No video capture devices could be found.'})
    m.run() 