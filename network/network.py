import socket
import threading

from .net_base import Network_Base, list_connections

class Network(Network_Base):
    def __init__(self, server, port):
        super().__init__(server, port, timeout=10)
        
        self.thread = None
        self.send_queue = []
        self.recv_queue = []
        
    def close(self):
        super().close()
        if self.thread:
            self.thread.join()
            self.thread = None
        
    def queue(self, data):
        if data not in self.send_queue:
            self.send_queue.append(data)
        return self.connected
        
    def pop_queue(self, num):
        data = self.recv_queue[:num]
        self.recv_queue = self.recv_queue[num:]
        return data
            
    def connect(self):
        if super().connect():
            t = threading.Thread(target=self.threaded_server)
            t.start()
            self.thread = t
            
        return self.connected
        
    def threaded_server(self):
        try:

            while self.connected:

                if self.send_queue:
                    send_data = self.send_queue.pop(0)
                    self.send(send_data)

                    recv_data = self.recv()
                    if recv_data is None:
                        break
                    recv_data = self.load_json(recv_data.decode())
                    self.recv_queue.append(recv_data)

        except Exception as e:
            self.add_exception(e)
