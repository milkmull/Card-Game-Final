import socket
import threading
import json

from .net_base import Network_Base

from data.constants import CONFIRMATION_CODE

class Network(Network_Base):
    def __init__(self, host, port):
        super().__init__(host, port, timeout=10)
        
        self.thread = None
        self.send_queue = []
        self.update = None
        
    def set_update(self, update):
        self.update = update
        
    def close(self):
        super().close()
        if self.thread:
            self.thread.join()
            self.thread = None

    def queue(self, data):
        if data not in self.send_queue:
            self.send_queue.append(data)

    def connect(self):
        if super().connect():
            self.send(CONFIRMATION_CODE)
            t = threading.Thread(target=self.host_process)
            t.start()
            self.thread = t
            
        return self.connected
        
    def host_process(self):
        try:
            self.host_game_process()
        except:
            pass
        self.connected = False
        
    def host_game_process(self):
        while self.connected:
        
            if self.send_queue:
                data = self.send_queue.pop(0)
                self.send(data)
                
            elif self.update:
                self.send('info')
                
                try:
                    reply = self.recv()
                except socket.timeout:
                    continue
                    
                if reply is None:
                    break
                    
                try:
                    reply = json.loads(reply.decode())
                except ValueError:
                    reply = []
                self.update(reply)
