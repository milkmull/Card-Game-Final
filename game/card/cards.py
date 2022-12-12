import inspect
import importlib

from . import card_base
from . import base_cards
from . import custom_cards

def load_custom_cards():
    importlib.reload(custom_cards)

def predicate(obj):
    return inspect.isclass(obj) and issubclass(obj, card_base.Card) and not obj is card_base.Card
    
def get_vote_card(game):
    return extra_cards.VoteCard(game)
    
def get_base_card_data():
    return {cls.name: cls for name, cls in inspect.getmembers(base_cards, predicate)}

def get_custom_card_data():
    return {cls.name: cls for name, cls in inspect.getmembers(custom_cards, predicate)}
    
def get_playable_card_data():
    return get_base_card_data() | get_custom_card_data()
    
    
    
    
    
    