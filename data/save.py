import os
import json
import copy

from .constants import *

for dir in (CUSTOM_IMG_PATH, CUSTOM_SND_PATH, TEMP_IMG_PATH, TEMP_SND_PATH, SAVE_DATA_PATH):
    if not os.path.exists(dir):
        os.mkdir(dir)

def load_json(file):
    with open(file, 'r') as f:
        data = json.load(f)
    return data
  
class Save:
    @staticmethod
    def get_base_settings():
        settings = {
            'size': [5, 5],
            'tt': 200,
            'cpus': 1,
            'diff': 3
        }
        return settings

    @staticmethod
    def get_blank_card_data():
        data = {
            'name': 'Player 0',
            'description': 'description', 
            'tags': ['player'], 
            'color': [161, 195, 161],
            'image': IMG_PATH + 'user.png', 
            'sound': None,
            'id': 0, 
            'weight': 1,
            'classname': 'Player_0',
            'custom': True,
            'code': '',
            'lines': [0, 0],
            'published': False,
            'node_data': {}
        }
        return data
 
    @staticmethod
    def get_blank_data():
        save_data = {
            'username': 'Player 0', 
            'port': 5555, 
            'ips': [],
            'settings': Save.get_base_settings(),
            'cards': [Save.get_blank_card_data()]
        }             
        return save_data
        
    @staticmethod
    def get_sheet_info(info):
        return load_json(INFO_SHEET_FILE).get(info)

    def __init__(self):
        self.save_data = None
        self.archive = None
        self.failed_to_load = False
        self.load_save()
        
    def load_save(self):
        try:
            with open(SAVE_DATA_FILE, 'r') as f:
                save_data = json.load(f)  
            self.save_data = save_data
            self.archive = copy.deepcopy(save_data)
        except:
            self.failed_to_load = True
        
    def reset_save(self):
        self.save_data = Save.get_blank_data()
        self.update_save()

        for f in os.listdir(CUSTOM_IMG_PATH):
            os.remove(CUSTOM_IMG_PATH + f)
        for f in os.listdir(CUSTOM_SND_PATH):
            os.remove(CUSTOM_SND_PATH + f)
                
        from spritesheet.customsheet import CUSTOMSHEET
        CUSTOMSHEET.reset()
            
        with open(CUSTOM_CARDS_FILE, 'w') as f:
            f.write(CUSTOM_CARDS_HEADER)
        with open(TEST_CARD_FILE, 'w') as f:
            f.write(TEST_CARD_HEADER)
            
        self.failed_to_load = False
        
    def save_archive(self):
        with open(SAVE_DATA_FILE, 'w') as f:
            json.dump(self.archive, f, indent=4)
        
    def update_save(self):
        try:
            with open(SAVE_DATA_FILE, 'w') as f:
                json.dump(self.save_data, f, indent=4)
            self.archive = copy.deepcopy(self.save_data)
        except Exception as e:
            self.save_archive()
            raise e
        
    def verify_data(self):
        username = self.get_data('username')
        if not isinstance(username, str):
            self.set_data('username', 'Player 0')
        
        port = self.get_data('port')
        if not isinstance(port, int):
            self.set_data('port', 5555)
            
        ips = self.get_data('ips')
        if not isinstance(ips, list):
            self.set_data('ips', [])
            
        cards = self.get_data('cards')
        if not isinstance(cards, list):
            self.reset_save()
            
        settings = self.get_data('settings')
        if not isinstance(settings, dict):
            self.reset_save()
            
        if len(self.get_data('cards')) == 0:
            cards = [Save.get_blank_card_data()]
            self.set_data('cards', cards)
        
    def get_data(self, key):
        return copy.deepcopy(self.save_data.get(key))
        
    def set_data(self, key, val):
        if self.save_data[key] != val: 
            self.save_data[key] = val
            self.update_save()
        
    def update_ips(self, entry):
        ips = self.get_data('ips')
        if entry not in ips:
            ips.append(entry)
            self.set_data('ips', ips)
        
    def del_ips(self, entry):
        ips = self.get_data('ips')
        if entry in ips:
            ips.remove(entry)
            self.set_data('ips', ips)
        
    def update_cards(self, entry):
        update = False
        cards = self.get_data('cards')

        for i, c in enumerate(cards):
            if c['id'] == entry['id']:
                cards[i] = entry
                update = True
                break

        if not update and entry not in cards:
            cards.append(entry)
            update = True
                
        if update:
            self.set_data('cards', cards)
            
    def unpublish_card(self, id):
        cards = self.get_data('cards')
        for entry in cards:
            if entry['id'] == id:
                break
    
        s, e = entry['lines']
        if s or e:
            text_shift = self.remove_card_text(s, e)
            text_shift_start = e
        
        for i, card in enumerate(cards):
            if text_shift:
                s, e = card['lines']
                if (s or e) and s >= text_shift_start:
                    card['lines'] = (s + text_shift, e + text_shift)
                    
        self.set_data('cards', cards)
            
    def remove_card_text(self, s, e):
        with open(CUSTOM_CARDS_FILE, 'r') as f:
            lines = f.readlines()
        lines = lines[:s] + lines[e:]
        with open(CUSTOM_CARDS_FILE, 'w') as f:
            f.writelines(lines)
        text_shift_start = e
        text_shift = -(e - s)
        return text_shift
      
    def del_card(self, entry):
        from spritesheet.customsheet import CUSTOMSHEET
        CUSTOMSHEET.del_card(entry)
        
        image_file = CUSTOM_IMG_PATH + '{}.png'
        sound_file = CUSTOM_SND_PATH + '{}.wav'
        cards = self.get_data('cards')
        text_shift_start = 0
        text_shift = 0

        image_shift_start = cards.index(entry)
        cards.remove(entry)
        os.remove(entry['image'])
        if entry['sound']:
            os.remove(entry['sound'])
        
        s, e = entry['lines']
        if s or e:
            text_shift = self.remove_card_text(s, e)
            
        for i, card in enumerate(cards):
            if i >= image_shift_start:
                card['id'] -= 1
                id = card['id']
                old_image_path = image_file.format(id + 1)
                new_image_path = image_file.format(id)
                os.rename(old_image_path, new_image_path)
                card['image'] = new_image_path
                if card['sound']:
                    old_sound_path = sound_file.format(id + 1)
                    new_sound_path = sound_file.format(id)
                    os.rename(old_sound_path, new_sound_path)
                    card['sound'] = new_sound_path
            if text_shift:
                s, e = card['lines']
                if (s or e) and s >= text_shift_start:
                    card['lines'] = (s + text_shift, e + text_shift)
            
        self.set_data('cards', cards)
        CUSTOMSHEET.refresh()

    def new_card_id(self):
        return len(self.get_data('cards'))
        
    def get_new_card_data(self):
        data = Save.get_blank_card_data()
        data['id'] = self.new_card_id()
        data['name'] = 'New Card'
        data['tags'].clear()
        return data

    def get_custom_names(self):
        return tuple([c['name'] for c in self.get_data('cards')])
        
    def id_to_name(self, id):
        for c in self.get_data('cards'):
            if c['id'] == id:
                return c['name']
        
    def publish_card(self, card):
        shift_start = 0
        shift = 0
        s, e = card.lines
        text = card.code

        with open(CUSTOM_CARDS_FILE, 'rb') as f:
            lines = f.readlines()
            
        if s or e:
            lines = lines[:s] + lines[e:]
            shift_start = e
            shift = -(e - s)
            
        with open(CUSTOM_CARDS_FILE, 'wb') as f:
            f.writelines(lines)
            f.write(text.encode('utf-8'))
                
        s = len(lines)
        e = s + len(text.splitlines())

        if shift_start:
            self.shift_cards(shift_start, shift)
            
        from game.card import cards
        cards.load_custom_cards()
            
        return (s, e)
            
    def shift_cards(self, shift_start, shift):
        cards = self.get_data('cards')
        for i, card in enumerate(cards):
            s, e = card['lines']
            if (s or e) and s >= shift_start:
                card['lines'] = (s + shift, e + shift)
        
        self.set_data('cards', cards)
        
SAVE = Save()
        
        
        
        
        
        
        
        
        
        
