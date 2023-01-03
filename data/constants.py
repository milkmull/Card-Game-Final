import json

IMG_PATH = "data/img/"
SND_PATH = "data/snd/"
CUSTOM_IMG_PATH = IMG_PATH + "custom/"
CUSTOM_SND_PATH = SND_PATH + "custom/"
TEMP_IMG_PATH = IMG_PATH + "temp/"
TEMP_SND_PATH = SND_PATH + "temp/"
CUSTOM_CARDS_FILE = "game/card/custom_cards.py"
CUSTOM_CARDS_HEADER = "from . import card_base\n"
SAVE_DATA_PATH = "data/save/"
SAVE_DATA_FILE = SAVE_DATA_PATH + "save.json"
TEST_CARD_FILE = "node/tester/testing_card.py"
TEST_CARD_HEADER = "from game.card import card_base\n"
NODE_DATA_FILE = "data/node/node_info.json"
GROUP_DATA_FILE = "data/node/group_nodes.json"
INFO_SHEET_FILE = "data/node/sheet_info.json"
SPRITESHEET_FILE = "data/img/spritesheet.png"
CUSTOMSHEET_FILE = "data/img/customsheet.png"

BASE_NAMES = (
    "big sand worm", "cactus", "cow", "dom", "dragon", "fish", "fishing pole", "fox", "future orb", 
    "gambling man", "ghost", "michael", "mystery seed", "negative zone", "ninja", "parade", "pelican", "robber",
    "sunflower", "treasure chest", "vines", "wind gust", "zombie"
)

WEIGHTS = (
    2,
    1.75,
    1.5,
    1.25,
    1,
    0.95,
    0.9,
    0.85,
    0.8,
    0.75,
    0.7,
    0.65,
    0.6,
    0.55,
    0.5,
    0.45,
    0.4,
    0.35,
    0.3,
    0.25,
    0.2,
    0.175,
    0.15,
    0.125,
    0.1,
    0.075,
    0.05,
    0.025,
    0.005,
    0.001,
    0.0001
)

CONSTANTS = {
    "width": 1024,
    "height": 576,
    "screen_size": (1024, 576),
    "cw": 375 // 8,
    "ch": 525 // 8,
    "mini_card_size": (375 // 8, 525 // 8),
    "card_width": 375,
    "card_height": 525,
    "card_size": (375, 525),
    "fps": 30
}

CONFIRMATION_CODE = "thisisthecardgameserver"

def get_sorted_names_dict():
    names = sorted(BASE_NAMES)
    
    out = {
        "A-D": {n.title(): None for n in names if n[0] in "abcd"},
        "E-H": {n.title(): None for n in names if n[0] in "efgh"},
        "I-L": {n.title(): None for n in names if n[0] in "ijkl"},
        "M-P": {n.title(): None for n in names if n[0] in "mnop"},
        "Q-T": {n.title(): None for n in names if n[0] in "qrst"},
        "U-Z": {n.title(): None for n in names if n[0] in "uvwxyz"}
    }
    
    return out
    
SORTED_NAMES_DICT = get_sorted_names_dict()
    
TAGS_DICT = {
    "biomes": {
        "city": None,
        "desert": None,
        "forest": None,
        "farm": None,
        "garden": None,
        "graveyard": None,
        "sky": None,
        "water": None
    },
    "descriptors": {
        "animal": None,
        "bug": None,
        "dog": None,
        "human": None,
        "monster": None,
        "plant": None
    }
}

DECKS_DICT = {
    "public": None,
    "private": None
}

WAIT_DICT = {
    "nt": None
}

WAIT_KEYS_DICT = {
    "player": None,
    "card": None
}

LOCAL_GROUP_DICT = {
    "border": None,
    "corner": None,
    "around": None,
    "row": None,
    "column": None,
    "x": None,
    "y": None
}

DIRECTIONS_DICT = {
    "top": None,
    "topleft": None,
    "left": None,
    "bottomleft": None,
    "bottom": None,
    "bottomright": None,
    "right": None,
    "topright": None
}

with open(NODE_DATA_FILE, "r") as f:
    NODE_DATA = list(json.load(f))