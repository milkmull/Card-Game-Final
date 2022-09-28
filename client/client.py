from .client_base import Client_Base

class HostLeft(Exception):
    pass

class Client(Client_Base):

    def send(self, data):
        if not self.conn.queue(data):
            raise Exception
            
    def get_info(self):
        self.send('info')
        data = self.conn.pop_queue(5)
        logs = []
        for d in data:
            if isinstance(d, list):
                logs += d
        self.update_logs(logs)
        
    def remove_player(self, pid):
        super().remove_player(pid)
        if pid == 0:
            raise HostLeft
        
    def close(self):
        self.conn.close()
        super().close()
        
    def run(self):
        try:
            super().run()
        except Exception as e:
            self.close()
            raise e
        