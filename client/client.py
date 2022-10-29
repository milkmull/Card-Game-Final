import traceback

import pygame as pg

from .client_base import Client_Base

class HostLeft(Exception):
    pass

class Client(Client_Base):
    def refresh(self):
        super().refresh()
        self.conn.client = self
        
    def send(self, data):
        if self.conn.connected:
            self.conn.queue(data)
            
    def get_info(self):
        pass

    def remove_player(self, pid):
        super().remove_player(pid)
        if pid == 0:
            raise OSError
        
    def close(self):
        self.conn.close()
        super().close()
        
    def update(self):
        if not self.conn.connected:
            raise OSError
            
        super().update()
        
    def run(self):
        try:
            super().run()
        except Exception as e:
            self.close()
            
            print(e)
            print(traceback.format_exc())
            raise e
            
    def add_player(self, log):
        p = super().add_player(log)
        if p:
            if not p.is_cpu:
                self.animation_manager.add_text(
                    text=f'{p.name} joined!',
                    text_size=30,
                    text_color=p.color,
                    text_outline_color=(0, 0, 0),
                    text_outline_width=3
                )
            
        return p
        
    def remove_player(self, pid):
        p = super().remove_player(pid)
        if p:
            if not p.is_cpu:
                self.animation_manager.add_text(
                    text=f'{p.name} left the game',
                    text_size=30,
                    text_color=p.color,
                    text_outline_color=(0, 0, 0),
                    text_outline_width=3
                )
                
        return p
        
    def update_settings(self, log):
        s = bool(self.settings)
        super().update_settings(log)
        
        if s:
            self.animation_manager.add_text(
                text='Game settings have been updated!',
                text_size=30,
                text_color=(255, 255, 0),
                text_outline_color=(0, 0, 0),
                text_outline_width=3
            )
        