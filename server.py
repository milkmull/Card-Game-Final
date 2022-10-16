import socket
import threading
import json
import sys

from network.net_base import Network_Base, get_local_ip
from game.game import Game

from data.constants import CONFIRMATION_CODE

class Server(Network_Base):
    def __init__(self):
        port = int(sys.argv[1])
        super().__init__(get_local_ip(), port)

        self.game = Game('online')
        
    def check_close_host(self):
        return not self.connections

    def close(self):
        super().close()
        print('server closed')
        
    def add_connection(self, conn, address):     
        if not self.connections:
            if address[0] != self.host:
                conn.close()
                return

        super().add_connection(conn, address)
        
        print('connected to', address)

        t = threading.Thread(target=self.threaded_client, args=(address, conn))
        t.start()
        self.threads.append(t)

    def run(self):
        if self.bind():
            self.start_scan()
            self.listen_while()
        
    def verify_connection(self, conn):
        data = None
        try:
            data = self.recv(conn=conn)
        except socket.timeout:
            pass
            
        if data is None:
            return
        data = data.decode()

        return data == CONFIRMATION_CODE
        
    def threaded_client(self, address, conn):
        try:
            self.client_process(conn)
        except Exception as e:
            print(e)
                
        print('lost connection to', address)
        self.close_connection(conn, address)
        
    def client_process(self, conn):
        connected = self.verify_connection(conn)
        if not connected:
            return
        self.send(CONFIRMATION_CODE, conn=conn)

        pid = self.game.add_player()
        if pid is None:
            return

        try:
            self.client_game_process(pid, conn)    
        except OSError:
            pass
            
        self.game.remove_player(pid)
        if pid == 0:
            self.stop_listen()
            
    def client_game_process(self, pid, conn):
        while self.connected:
        
            try:
                data = self.recv(conn=conn)
            except socket.timeout:
                continue

            if data is None:
                break
            data = data.decode()
            
            reply = self.game.update_game(data, pid=pid)
            self.send(json.dumps(reply), conn=conn)
            
    def start_scan(self):
        t = threading.Thread(target=self.scan_broadcast)
        t.start()
        self.threads.append(t)
            
    def scan_broadcast(self):
        while self.connected:
            
            data = None
            try:
                data = Network_Base.recvfrom(5555, raw=False, timeout=0.5)
            except socket.timeout:
                continue
                
            if data is None:
                break
                
            data, address = data
            if data != CONFIRMATION_CODE:
                continue
                
            reply = f'{CONFIRMATION_CODE}-{self.port}'
            Network_Base.sendto(reply, address[0], 5556)
    
s = Server()
s.run()   
        
        
        
        