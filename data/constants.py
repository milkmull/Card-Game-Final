import json

IMG_PATH = 'data/img/'
SND_PATH = 'data/snd/'
CUSTOM_IMG_PATH = IMG_PATH + 'custom/'
CUSTOM_SND_PATH = SND_PATH + 'custom/'
TEMP_IMG_PATH = IMG_PATH + 'temp/'
TEMP_SND_PATH = SND_PATH + 'temp/'
CUSTOM_CARDS_FILE = 'game/card/custom_cards.py'
CUSTOM_CARDS_HEADER = 'from . import card_base\n'
SAVE_DATA_PATH = 'data/save/'
SAVE_DATA_FILE = SAVE_DATA_PATH + 'save.json'
TEST_CARD_FILE = 'node/tester/testing_card.py'
TEST_CARD_HEADER = 'from game.card import card_base\n'
NODE_DATA_FILE = 'data/node/node_info.json'
GROUP_DATA_FILE = 'data/node/group_nodes.json'
INFO_SHEET_FILE = 'data/node/sheet_info.json'
SPRITESHEET_FILE = 'data/img/spritesheet.png'
CUSTOMSHEET_FILE = 'data/img/customsheet.png'

BASE_NAMES = (
    'cow', 'fish', 'michael', 'sunflower',
)

CONSTANTS = {
    'width': 1024,
    'height': 576,
    'screen_size': (1024, 576),
    'center': (1024 // 2, 576 // 2),
    'cw': 375 // 8,
    'ch': 525 // 8,
    'mini_card_size': (375 // 8, 525 // 8),
    'card_width': 375,
    'card_height': 525,
    'card_size': (375, 525),
    'fps': 30
}

CONFIRMATION_CODE = 'thisisthecardgameserver'

def get_sorted_names_dict():
    names = sorted(BASE_NAMES)
    
    out = {
        'A-D': {n: None for n in names if n[0] in 'abcd'},
        'E-H': {n: None for n in names if n[0] in 'efgh'},
        'I-L': {n: None for n in names if n[0] in 'ijkl'},
        'M-P': {n: None for n in names if n[0] in 'mnop'},
        'Q-T': {n: None for n in names if n[0] in 'qrst'},
        'U-Z': {n: None for n in names if n[0] in 'uvwxyz'}
    }
    
    return out
    
SORTED_NAMES_DICT = get_sorted_names_dict()
    
TAGS_DICT = {
    'biomes': {
        'city': None,
        'desert': None,
        'forest': None,
        'farm': None,
        'garden': None,
        'graveyard': None,
        'sky': None,
        'water': None
    },
    'descriptors': {
        'animal': None,
        'bug': None,
        'dog': None,
        'human': None,
        'monster': None,
        'plant': None
    }
}
    
TYPES_DICT = {
    'event': None,
    'item': None,
    'landscape': None,
    'play': None,
    'spell': None,
    'treasure': None,
}

DECKS_DICT = {
    'active_spells': None,
    'items': None,
    'landscapes': None,
    'played': None,
    'spells': None,
    'treasure': None,
    'unplayed': None
}

REQUESTS_DICT = {
    'flip': None,
    'roll': None,
    'select': None,
    'og': None
}

LOGS_DICT = {
    'buy': None,
    'cast': None,
    'cfe': None,
    'cont': None,
    'draw': None,
    'dre': None,
    'gp': None,
    'lp': None,
    'p': None,
    'sp': None,
    'ui': None
}

LOG_KEYS_DICT = {
    'c': None,
    'coin': None,
    'deck': None,
    'dice': None,
    'give': None,
    'gp': None,
    'lp': None,
    'sp': None,
    't': None,
    'target': None,
    'u': None
}

EVENTS_DICT = {
    'fishing trip': None,
    'flu': None,
    'harvest': None,
    'hunting season': None,
    'item frenzy': None,
    'negative zone': None,
    'sand storm': None,
    'spell reverse': None,
    'sunny day': None,
    'parade': None,
    'wind gust': None
}

with open(NODE_DATA_FILE, 'r') as f:
    NODE_DATA = list(json.load(f))
        
        
        
        
