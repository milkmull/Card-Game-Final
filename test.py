import random

from game.game_base import Game_Base
from game.card import cards as card_manager

cards = card_manager.get_playable_card_data()

settings = {
    'rounds': 1, 
    'ss': 20, 
    'cards': 5,
    'items': 3,
    'spells': 1,
    'cpus': 3,
    'diff': 1
}

i = 0
err_seed = 1182

while True:
    random.seed(err_seed)
    print('seed:', i)
    
    g = Game_Base.simulator(settings, cards)

    try:
        while not g.done():
            g.main()
    except KeyboardInterrupt:
        break
        
    i += 1