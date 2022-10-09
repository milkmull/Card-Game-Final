import sys
import subprocess
import threading
import time

from client.client_base import Client_Base
from game.game import Game
from client.client import Client, HostLeft
from network.network import Network, scan_connections
from network.net_base import get_local_ip, port_in_use

from ui.scene.templates.notice import Notice
from .searching import Searching
from .select_local import run_select_local
from .find_online import run_find_online

def scan():
    m = Searching('Searching for games...')

    def _scan():
        results = scan_connections()
        m.set_return(results)

    t = threading.Thread(target=_scan)
    t.start()
    results = m.run()
    t.join()
    
    return results
    
def start_server():
    m = Searching('Starting game...')

    def _start_server(): 
        if port_in_use(5555):
            m.set_return(0)
            return
            
        subprocess.Popen(
            [sys.executable, 'server.py'],
            stderr=sys.stderr,
            stdout=sys.stdout
        )

        time.sleep(1)
        m.set_return(1)
            
    t = threading.Thread(target=_start_server)
    t.start()
    r = m.run()
    t.join()
    
    return r
    
def connect(n):
    m = Searching('Searching for game...')
    
    def _connect():
        n.connect()
        m.set_return(1)
        
    t = threading.Thread(target=_connect)
    t.start()
    m.run()
    t.join()

def run_client_single():
    g = Game('single')
    c = Client_Base(g)
    c.run()
    
def run_client_online():  
    r = start_server()
    if not r:
        text = 'The specified port is currently in use.'
        m = Notice(text_kwargs={'text': text})
        m.run()
        return
    
    n = Network(get_local_ip(), 5555)
    n.connect()
    
    if not n.connected:
        text = 'Game could not be started.'
        m = Notice(text_kwargs={'text': text})
        m.run()
        return

    c = Client(n)
    try:
        c.run()
    except OSError:
        pass
        
def find_local_game():
    results = scan()
    if not results:
        m = Notice(text_kwargs={'text': 'No games could be found'})
        m.run()  
        return

    host = run_select_local(results)
    if host is None:
        return

    n = Network(host, 5555)
    n.connect()

    if not n.connected:
        text = 'Failed to connect to game.'
        m = Notice(text_kwargs={'text': text})
        m.run()
        return

    c = Client(n)
    try:
        c.run()
    except OSError:
        text = 'The game has been closed.'
        m = Notice(text_kwargs={'text': text})
        m.run()   
        return
            
def find_global_game():
    result = run_find_online()
    if result is None:
        return
        
    host, port = result
    
    n = Network(host, port)
    connect(n)
    
    if not n.connected:
        text = 'No game could be found.'
        m = Notice(text_kwargs={'text': text})
        m.run()
        return    
            
    c = Client(n)
    try:
        c.run()
    except OSError:
        text = 'The game has been closed.'
        m = Notice(text_kwargs={'text': text})
        m.run()   
        return      
            
            
            
            
            
            