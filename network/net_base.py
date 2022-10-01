import socket
import json
import urllib.request
import traceback
import base64
import re
import subprocess

def list_connections():
    out = subprocess.check_output(['arp', '-a']).decode()
    ips = re.findall(r'[0-9]+(?:\.[0-9]+){3}', out)
    return ips

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
    
def get_public_ip():
    ip = None
    try:
        ip = urllib.request.urlopen('https://api.ipify.org').read().decode()
    except urllib.error.URLError:
        pass
    return ip
        
class Network_Base:
    @staticmethod
    def load_json(data):
        return json.loads(data) 
        
    @staticmethod
    def dump_json(data):
        return json.dumps(data)
        
    @staticmethod
    def b64encode(data):
        return base64.b64encode(data).decode('utf-8')
        
    @staticmethod
    def b64decode(data):
        return base64.b64decode(data)
        
    @staticmethod
    def encode(data):
        return bytes(data, encoding='utf-8')
        
    @staticmethod
    def decode(data):
        return data.decode()
        
    @staticmethod
    def get_sock(timeout=3):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        return sock
        
    def __init__(self, server, port, timeout=3):
        self.server = server
        self.port = port

        self.connections = {}
        self.connected = False
        self.listening = False
        
        self.timeout = timeout
        self.sock = self.get_sock(timeout=timeout)
        self.buffer = b''
        
        self.exceptions = []
        
    @property
    def address(self):
        return (self.server, self.port)
        
    def add_exception(self, err):
        info = (err, traceback.format_exc())
        self.exceptions.append(info)

    def raise_exception(self, e):
        self.close()
        raise e
        
    def raise_last(self):
        if self.exceptions:
            info = self.exceptions.pop(-1)
            self.raise_exception(info[0])
            
    def raise_first(self):
        if self.exceptions:
            info = self.exceptions.pop(0)
            self.raise_exception(info[0])
        
    def close(self):
        for address, conn in self.connections.copy().items():
            self.close_connection(conn, address)
        if hasattr(self, 'sock'):
            self.sock.close()
        self.connected = False
        self.listening = False
        self.buffer = b''
        
    def __del__(self):
        self.close()

    def start_server(self):
        self.connected = False
        try: 
            self.sock.bind(self.address)
            self.connected = True
        except Exception as e:
            self.add_exception(e)
        return self.connected
        
    def connect(self):
        self.connected = False
        try:
            self.sock.connect(self.address)
            self.connected = True
        except Exception as e:
            self.add_exception(e)
        return self.connected
            
    def add_connection(self, conn, address):
        self.connections[address] = conn
        conn.settimeout(self.timeout)
        
    def close_connection(self, conn, address):
        conn.close()
        self.connections.pop(address)
        
    def check_close(self):
        return bool(self.exceptions)
        
    def listen(self):
        self.listening = True
        self.sock.listen()

        try:
            conn, address = self.sock.accept()
            self.add_connection(conn, address)
        except socket.timeout:
            self.close()
        except Exception as e:
            self.raise_exception(e)

    def listen_while(self):
        self.listening = True
        self.sock.listen()
        while self.listening:
            try:
                conn, address = self.sock.accept()
                self.add_connection(conn, address)
            except socket.timeout:
                pass
            except Exception as e:
                self.raise_exception(e)
            if self.check_close():
                break      
        self.close()
        
    def trim(self, data, size):
        self.buffer += data[size:]
        return data[:size]
        
    def read_buffer(self, size=None):
        if self.buffer:
            print(self.buffer)
        if size is None:
            size = len(self.buffer)
        data = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return data
        
    def send(self, data, conn=None):
        if conn is None:
            conn = self.sock
            
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data, encoding='utf-8')
        size = len(data).to_bytes(32, byteorder='big')
        
        conn.sendall(size + data) 
        
    def recv(self, conn=None, raw=True):
        if conn is None:
            conn = self.sock
            
        size = self.read_buffer(size=32)
        while len(size) < 32:
            d = conn.recv(32 - len(size))
            if not d:
                return
            size += d
            
        size = self.trim(size, 32)
        size = int.from_bytes(size, byteorder='big')

        data = self.read_buffer(size=size)
        while len(data) < size:
            d = conn.recv(size - len(data))
            if not d:
                return
            data += d
            
        data = self.trim(data, size)  
        if not raw:
            data = data.decode()
        
        return data