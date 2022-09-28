import socket
import threading

from network.net_base import Network_Base, get_local_ip
from game.game import Game

class Server(Network_Base):
    def __init__(self):
        super().__init__(get_local_ip(), 5555)
        
        self.id = 0
        self.threads = []
        self.game = Game('online')
        
    def check_close(self):
        return not self.id
        
    def close(self):
        super().close()
        for t in self.threads:
            t.join()

        if self.exceptions:
            e, tb = self.exceptions.pop(0)
            if not isinstance(e, socket.error):
                print(f'server closed with error: {e}')
                print(tb)
                return
        print('server closed')
        
    def add_connection(self, conn, address):
        super().add_connection(conn, address)
        t = threading.Thread(target=self.threaded_client, args=(address, conn, self.id))
        t.start()
        self.threads.append(t)
        self.id += 1
        
        print('connected to', address)
        
    def run(self):
        self.start_server()
        if not self.connected: 
            self.raise_last()
        self.listen_while()
        
    def threaded_client(self, address, conn, id):
        connected = self.game.add_player(id, self.game.blank_player_info(id))
        
        try:

            while connected and self.connected:
            
                try:
                    data = self.recv(conn=conn)
                except socket.timeout:
                    continue

                if data is None:
                    break
                    
                data = data.decode()
                reply = self.game.update_game(data, pid=id)
                self.send(self.dump_json(reply), conn=conn)

        except Exception as e:
            self.add_exception(e)
                
        print('lost connection to', address)
            
        self.id -= 1
        self.game.remove_player(id)
        self.close_connection(conn, address)
        
s = Server()
s.run()   
        
        
        
        