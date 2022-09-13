import inspect
import importlib

from . import card_base
from . import base_cards
from . import extra_cards
from . import custom_cards

def load_custom_cards():
    importlib.reload(custom_cards)

def predicate(obj):
    return inspect.isclass(obj) and issubclass(obj, card_base.Card) and not obj is card_base.Card
    
def get_vote_card(game):
    return extra_cards.VoteCard(game)
    
def get_base_card_data():
    data = {}
    for name, cls in inspect.getmembers(base_cards, predicate):
        if cls.type not in data:
            data[cls.type] = {}
        data[cls.type][cls.name] = cls
    return data

def get_custom_card_data():
    data = {}
    for name, cls in inspect.getmembers(custom_cards, predicate):
        if cls.type not in data:
            data[cls.type] = {}
        data[cls.type][cls.name] = cls
    return data
    
def get_extra_card_data():
    data = {}
    for name, cls in inspect.getmembers(extra_cards, predicate):
        if cls.type not in data:
            data[cls.type] = {}
        data[cls.type][cls.name] = cls
    return data
    
def get_playable_card_data():
    data = (
        get_base_card_data(),
        get_custom_card_data(),
        get_extra_card_data()
    )
    
    playable = {}
    
    for d in data:
        for type, cards in d.items():
            if type not in playable:
                playable[type] = cards
            else:
                playable[type].update(cards)

    return playable
    
    
    
    
    
    