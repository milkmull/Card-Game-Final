import pygame as pg

from .client_base import Client_Base

class HostLeft(Exception):
    pass

class Client(Client_Base):
    def refresh(self):
        super().refresh()
        self.conn.set_update(self.update_logs)
        
    def send(self, data):
        if self.conn.connected:
            self.conn.queue(data)
            
    def request(self, data):
        reply = self.conn.request(data)
        if data is None:
            raise Exception
        return data
            
    def get_info(self):
        pass

    def remove_player(self, pid):
        super().remove_player(pid)
        if pid == 0:
            raise HostLeft
        
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
            raise e
        