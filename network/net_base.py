import socket
import json
import urllib.request
import re
import subprocess
import threading
import ipaddress
import struct
    
def get_lan():
    out = subprocess.check_output(['arp', '-a']).decode()
    hosts = re.findall(r'[0-9]+(?:\.[0-9]+){3}', out)
    return hosts
    
def get_host_range(start, end):
    start = struct.unpack('>I', socket.inet_aton(start))[0]
    end = struct.unpack('>I', socket.inet_aton(end))[0]
    return [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end)]

def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(('8.8.8.8', 80))
        ip = sock.getsockname()[0]
        return ip
    
def get_public_ip():
    ip = None
    try:
        ip = urllib.request.urlopen('https://api.ipify.org').read().decode()
    except urllib.error.URLError:
        pass
    return ip

def scan_connections(hosts, port):
    results = {}

    def verify_connection(host):
        sock = Network_Base.TCP(timeout=1)
        connected = True
        try:
            sock.connect((host, port))
        except socket.error:
            connected = False
        finally:
            sock.close()
        results[host] = connected
        
    threads = []

    for host in hosts:
        t = threading.Thread(target=verify_connection, args=(host,))
        t.start()
        threads.append(t)
        
    while any(t.is_alive() for t in threads):
        continue
        
    available = []
    for host, connected in results.items():
        if connected:
            name = socket.getfqdn(host)
            available.append((name, host))
            
    return available
  
def port_in_use(port, host=None):
    if host is None:
        host = get_local_ip()
        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((host, port))
        return result == 0
   
class Network_Base:
    @staticmethod
    def pack_data(data):
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data, encoding='utf-8')
        size = len(data).to_bytes(4, byteorder='big')
        return size + data
        
    @staticmethod
    def sendto(data, host, port, broadcast=False):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if broadcast:
                host = '<broadcast>'
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            data = Network_Base.pack_data(data)[4:]
            sent = False
            
            try:
                sock.sendto(data, (host, port))
                sent = True
            except socket.error:
                pass

            return sent
    
    @staticmethod
    def recvfrom(port, size=4096, timeout=1, raw=True): 
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(timeout)
            
            try:
                sock.bind(('', port))
            except socket.error:
                return

            data, address = sock.recvfrom(size) 
            if not raw:
                data = data.decode()
            
            return (data, address)
            
    @staticmethod
    def TCP(timeout=3):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        return sock
 
    def __init__(self, host, port, timeout=3):
        self.host = host
        self.port = port

        self.connections = {}
        self.connected = False
        self.listening = False
        self.threads = []
        
        self.timeout = timeout
        self.sock = Network_Base.TCP(timeout=self.timeout)
        self.buffer = b''
        
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        try:
            self.close()
        except Exception:
            pass
        
    @property
    def address(self):
        return (self.host, self.port)
        
    def close(self):
        for address, conn in self.connections.copy().items():
            self.close_connection(conn, address)
        if hasattr(self, 'sock'):
            self.sock.close()
        self.connected = False
        self.listening = False
        self.buffer = b''
        
        for t in self.threads:
            t.join()
        self.threads.clear()

    def bind(self):
        self.connected = False
        
        if port_in_use(self.port):
            raise Exception('PortNotAvailable')
            
        try: 
            self.sock.bind(self.address)
            self.connected = True
        except socket.error:
            pass
            
        return self.connected
        
    def connect(self):
        self.connected = False
        try:
            self.sock.connect(self.address)
            self.connected = True
        except socket.error:
            pass
        return self.connected
            
    def add_connection(self, conn, address):
        self.connections[address] = conn
        conn.settimeout(self.timeout)
        
    def close_connection(self, conn, address):
        conn.close()
        self.connections.pop(address, None)
        
    def check_close_host(self):
        pass
        
    def stop_listen(self):
        self.sock.close()
        self.listening = False
        
    def listen(self):
        self.sock.listen()
        self.listening = True

        try:
            conn, address = self.sock.accept()
            self.add_connection(conn, address)
        except (OSError, socket.timeout):
            pass
            
        self.close()

    def listen_while(self):
        self.sock.listen()
        self.listening = True
        
        try:

            while self.connected:    

                try:
                    conn, address = self.sock.accept()
                    self.add_connection(conn, address)
                    continue
                except socket.timeout:
                    pass
                except OSError:
                    break
                    
                if self.check_close_host():
                    break  
                    
        except Exception:
            pass
                
        self.close()
        
    def verify_connection(self, conn):
        return True
        
    def trim(self, data, size):
        self.buffer += data[size:]
        return data[:size]
        
    def read_buffer(self, size=None):
        if size is None:
            size = len(self.buffer)
        data = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return data

    def send(self, data, conn=None):
        if conn is None:
            conn = self.sock
 
        data = Network_Base.pack_data(data)

        try:
            conn.sendall(data) 
            return True
        except socket.error:
            pass
        
    def recv(self, conn=None, raw=True):
        if conn is None:
            conn = self.sock
            
        size = self.read_buffer(size=4)
        while len(size) < 4:
            d = conn.recv(4 - len(size))
            if not d:
                return
            size += d
            
        size = self.trim(size, 4)
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