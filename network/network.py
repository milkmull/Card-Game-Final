import socket
import threading
import json
import time
import traceback

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
            data = Network_Base.recvfrom(5556, raw=False, timeout=0.5)
        except socket.timeout:
            break
            
        if data is None:
            break
            
        data, address = data
        data = data.split('-')
        
        if len(data) <= 1 or data.pop(0) != CONFIRMATION_CODE:
            continue
        
        host = address[0]
        name = socket.getfqdn(host)
        port = int(data[0])
        connections.append((name, host, port))
        
    return connections

class Network(Network_Base):
    def __init__(self, host, port):
        super().__init__(host, port, timeout=10)

        self.send_queue = []
        self.recv_queue = []
        self.client = None

    def queue(self, data):
        if data not in self.send_queue:
            self.send_queue.append(data)
            
    def verify_connection(self):
        data = None
        try:
            data = self.recv()
        except socket.timeout:
            pass
            
        if data is None:
            return
        data = data.decode()

        return data == CONFIRMATION_CODE

    def connect(self):
        if super().connect():
        
            self.send(CONFIRMATION_CODE)
            if not self.verify_connection():
                self.close()
                return False

            t = threading.Thread(target=self.host_process)
            t.start()
            self.threads.append(t)
            
        return self.connected
        
    def host_process(self):
        try:
            self.host_game_process()
        except (OSError, KeyboardInterrupt):
            pass
        except Exception:
            print(traceback.format_exc())
        self.connected = False

    def host_game_process(self):
        last_ping = 0
        
        while self.connected:
        
            if self.send_queue:
                data = self.send_queue.pop(0)
                self.send(data)
 
            else:
                last_ping = time.time()
                
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
                    
                self.recv_queue += reply
                    
            if self.client:
                if self.recv_queue or self.client.log_queue:
                    self.client.update_logs(self.recv_queue)
                    self.recv_queue.clear()
