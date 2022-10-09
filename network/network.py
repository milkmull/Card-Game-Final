import socket
import threading
import json

from .net_base import Network_Base

from data.constants import CONFIRMATION_CODE

def scan_connections():
    connections = []
    
    sent = Network_Base.sendto(CONFIRMATION_CODE, '', 5555, broadcast=True)
    if not sent:
        return connections
    
    while True:
    
        data = None
        try:
            data = Network_Base.recvfrom(5555, raw=False, timeout=0.5)
        except socket.timeout:
            break
            
        if data is None:
            break
            
        data, address = data
        if data != CONFIRMATION_CODE:
            continue
        
        host = address[0]
        name = socket.getfqdn(host)
        connections.append((name, host))
        
    return connections

class Network(Network_Base):
    def __init__(self, host, port):
        super().__init__(host, port, timeout=10)

        self.send_queue = []
        self.update = None
        
    def set_update(self, update):
        self.update = update

    def queue(self, data):
        if data not in self.send_queue:
            self.send_queue.append(data)

    def connect(self):
        if super().connect():
            self.send(CONFIRMATION_CODE)
            t = threading.Thread(target=self.host_process)
            t.start()
            self.threads.append(t)
            
        return self.connected
        
    def host_process(self):
        try:
            self.host_game_process()
        except OSError:
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
                    if not isinstance(reply, list):
                        continue
                except ValueError:
                    continue
                    
                self.update(reply)
