import socket
import threading

from .net_base import Network_Base

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
        return self.connected
        
    def request(self, send_data):
        while self.connected:
            if not self.send_queue:
            
                self.send(send_data)
                recv_data = self.recv()
                if recv_data is None:
                    break
                    
                return recv_data.decode()
                
        self.connected = False

    def connect(self):
        if super().connect():
            self.send(bin(1))
            t = threading.Thread(target=self.threaded_host)
            t.start()
            self.thread = t
            
        return self.connected
        
    def threaded_host(self):
        try:

            while self.connected:
            
                if self.send_queue:
                
                    send_data = self.send_queue[0]
                    self.send(send_data)
                    
                    recv_data = self.recv()
                    if recv_data is None:
                        break
                    recv_data = self.load_json(recv_data.decode())
                    self.send_queue.pop(0)
                    
                elif self.update:

                    self.send('info')
                    
                    recv_data = self.recv()
                    if recv_data is None:
                        break
                    recv_data = self.load_json(recv_data.decode())
                    self.update(recv_data)

        except Exception as e:
            self.add_exception(e)
            
        self.connected = False
