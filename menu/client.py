import sys
import subprocess
import threading

from client.client_base import Client_Base
from game.game import Game
from client.client import Client, HostLeft
from network.network import Network
from network.net_base import get_local_ip, get_lan, get_host_range, scan_connections

from ui.scene.templates.notice import Notice
from .searching import Searching
from .select_local import run_select_local

def scan():
    m = Searching('Searching for games...')

    def _scan():
        results = scan_connections(get_lan(), 5555)
        m.set_return(results)

    t = threading.Thread(target=_scan)
    t.start()
    results = m.run()
    t.join()
    
    return results
    
def start_server():
    m = Searching('Starting game...')

    def _start_server():
        err = b''
        try:
            pipe = subprocess.Popen(
                [sys.executable, 'server.py'],
                stderr=subprocess.PIPE,
                stdout=sys.stdout
            )
            out, err = pipe.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            pass

        if err is not None:
            err = err.decode()
            m.set_return(err)
            
    t = threading.Thread(target=_start_server)
    t.start()
    err = m.run()
    t.join()
    
    return err

def run_client_single():
    g = Game('single')
    c = Client_Base(g)

    c.run()
    
def run_client_online():
    err = start_server()

    if 'PortNotAvailable' in err:
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
    text = ''
    
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
            
            
            
            
            
            
            
            
            
            
            