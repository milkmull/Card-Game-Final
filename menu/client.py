from client.client.client_base import Client_Base
from game.game import Game

def run_client_single():
    g = Game('single')
    c = Client_Base(g)
 
    c.start()
    c.run()