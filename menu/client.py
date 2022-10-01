import sys
import subprocess

from client.client_base import Client_Base
from game.game import Game
from client.client import Client, HostLeft
from network.network import Network
from network.net_base import get_local_ip

from ui.scene.templates.notice import Notice

def run_client_single():
    g = Game('single')
    c = Client_Base(g)

    c.run()
    
def run_client_online():
    text = ''
    
    pipe = subprocess.Popen([sys.executable, 'server.py'], stderr=sys.stderr, stdout=sys.stdout)
    
    try:
        _, error = pipe.communicate(timeout=1)
    except subprocess.TimeoutExpired:
        pass

    n = Network(get_local_ip(), 5555)
    n.connect()
    
    if not n.connected:
        text = 'Game could not be started.'
        
    else:
        c = Client(n)
        c.run()
            
    if text:
        m = Notice(text_kwargs={'text': text})
        m.run()
        
def join_game():
    text = ''
    
    n = Network(get_local_ip(), 5555)
    n.connect()
    
    if not n.connected:
        text = 'No games could be found.'
        
    else:
        c = Client(n)
        try:
            c.run()
        except HostLeft:
            text = 'The host closed the game.'
            
    if text:
        m = Notice(text_kwargs={'text': text})
        m.run()   
            
            
            
            
            
            
            
            
            
            
            