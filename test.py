from game.game_base import Game_Base
from game.card import cards as card_manager

cards = card_manager.get_base_card_data()
settings = {
    'ss': 20,
    'cards': 8
}

g = Game_Base('test', settings, cards)
g.add_cpus(num=2)
g.new_game()

while not g.done:
    g.main()
    
print(g.grid.grid)
print(g.log)