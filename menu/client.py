import sys
import subprocess
import threading
import time

from client.client_base import Client_Base
from client.sandbox import Sandbox
from game.game import Game
from game.sandbox import Sandbox as Sandbox_Game
from client.client import Client
from network.network import Network, scan_connections
from network.net_base import get_local_ip, port_in_use

from ui.scene.templates.notice import Notice
from .searching import Searching
from .select_local import run_select_local
from .find_online import run_find_online
from .host_game import run_host_game

def scan():
    m = Searching("Searching for games...")

    def _scan():
        results = scan_connections()
        m.set_return(results)

    t = threading.Thread(target=_scan)
    t.start()
    results = m.run()
    t.join()
    
    return results
    
def start_server(port):
    m = Searching("Starting game...")

    def _start_server(): 
        if port_in_use(port):
            m.set_return(0)
            return
            
        proc = subprocess.Popen(
            [sys.executable, "server.py", str(port)],
            stdout=sys.stdout,
            stderr=sys.stderr,
            start_new_session=True
        )

        m.set_return(1)
            
    t = threading.Thread(target=_start_server)
    t.start()
    r = m.run()
    t.join()
    
    return r
    
def connect(n, timeout=5):
    m = Searching("Connecting to game...")
    
    def _connect():
        t = time.time()
        while time.time() - t < timeout:
            n.connect()
            if n.connected:
                break
        m.set_return(1)
        
    t = threading.Thread(target=_connect)
    t.start()
    m.run()
    t.join()

def run_client_single():
    g = Game("single")
    c = Client_Base(g)
    c.run()
    
def run_sandbox():
    g = Sandbox_Game("single")
    c = Sandbox(g)
    c.run()
    
def host_game():  
    port = run_host_game()
    if port is None:
        return

    r = start_server(port)
    if not r:
        text = "The specified port is currently in use."
        m = Notice(text_kwargs={"text": text})
        m.run()
        return
        
    with Network(get_local_ip(), port) as n:
        connect(n)
        
        if not n.connected:
            text = "Game could not be started."
            m = Notice(text_kwargs={"text": text})
            m.run()
            return

        try:
            with Client(n) as c:
                c.run()
        except OSError:
            pass
        except Exception:
            text = "An error occurred."
            m = Notice(text_kwargs={"text": text})
            m.run()   
            return
        
def find_local_game():
    results = scan()
    if not results:
        m = Notice(text_kwargs={"text": "No games could be found."})
        m.run()  
        return

    choice = run_select_local(results)
    if choice is None:
        return
        
    host, port = choice
    
    with Network(host, port) as n:
        connect(n)

        if not n.connected:
            text = "Failed to connect to game."
            m = Notice(text_kwargs={"text": text})
            m.run()
            return

        try:
            with Client(n) as c:
                c.run()
        except OSError:
            text = "The game has been closed."
            m = Notice(text_kwargs={"text": text})
            m.run()   
            return
        except Exception:
            text = "An error occurred."
            m = Notice(text_kwargs={"text": text})
            m.run()   
            return
            
def find_global_game():
    result = run_find_online()
    if result is None:
        return
        
    host, port = result
    
    with Network(host, port) as n:
        connect(n)
        
        if not n.connected:
            text = "No game could be found."
            m = Notice(text_kwargs={"text": text})
            m.run()
            return    

        try:
            with Client(n) as c:
                c.run()
        except OSError:
            text = "The game has been closed."
            m = Notice(text_kwargs={"text": text})
            m.run()   
            return  
        except Exception:
            text = "An error occurred."
            m = Notice(text_kwargs={"text": text})
            m.run()   
            return
            
            
            
            
            
            