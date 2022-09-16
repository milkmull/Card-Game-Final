import random

import pygame as pg

from data.constants import CONSTANTS
from .exceptions import CommunicationError

from spritesheet.spritesheet import Spritesheet

from ui.menu.menu import Menu

from ui.element.elements import Textbox, Button, Popup, Live_Window
from ui.icons.icons import icons
from ui.color.ops import gen_colors

from ..elements.player import Player
from ..elements.card import Card
from ..elements.card_window import Card_Window
from ..elements.main_button import Main_Button
from ..elements.points import Points
from ..elements.moving_card import Moving_Card
from ..elements.grid import Grid

def client_screen(menu):
    body = menu.body
    sep = Card_Window.SEP
    elements = []
    
    main_button = Main_Button(
        menu,
        text_size=50, 
        pad=5,
        centerx_aligned=True,
        centery_aligned=True,
        hover_color=(100, 100, 100),
        enabled=False
    )
    main_button.set_parent(menu, centerx_anchor='centerx', bottom_anchor='bottom', bottom_offset=-10)
    elements.append(main_button)
    menu.main_button = main_button

    sequence = Card_Window(
        dir=3,
        size=((2 * CONSTANTS['cw']) + (3 * sep), (3 * CONSTANTS['ch']) + (4 * sep)), 
        outline_color=(255, 0, 0),
        outline_width=2
    )
    sequence.rect.bottomleft = (20, body.height - 20)
    elements.append(sequence)
    menu.sequence = sequence

    options = Button.Text_Button(
        text='options'
    )
    options.rect.topright = (body.width - 30, 30)
    elements.append(options)

    scores = Live_Window(
        size=(200, 100)
    )
    scores.rect.topleft = (20, 40)
    elements.append(scores)
    menu.scores = scores
    
    grid = Grid(menu, (4, 4))
    grid.rect.center = body.center
    elements.append(grid)
    menu.grid = grid

    return elements
   
class Client_Base(Menu): 
    COLORS = gen_colors(15)
    
    def __init__(self, connection, set_screen=client_screen):
        super().__init__(set_screen, fill_color=(32, 32, 40))
        
        self.conn = connection
        self.sheet = Spritesheet()
        self.pid = None
        
        self.status = ''
        self.settings = {}
        self.players = []

        self.cards = {}
        
        self.logs = {}
        self.log_queue = []

        self.view_rect = pg.Rect((0, 0), CONSTANTS['card_size'])
        self.view_rect.center = self.body.center
        self.view_card = None
        self.view_image = None
        
        self.hover_card = None
        self.hover_image = None
        self.hover_matches = []
        
        self.held_card = None
        
# start stuff
        
    def start(self):
        self.running = True
        self.pid = self.send('pid')
        
    def reset(self):
        pass
        
    def close(self):
        pass
        
# communication stuff
        
    def send(self, data):
        if self.running:
            reply = self.conn.send_and_recv(data)  
            if reply is None:
                raise CommunicationError
            return reply
            
    def get_info(self):
        logs = self.send('info')
        self.update_logs(logs)
        
    def update_logs(self, logs):
        self.log_queue += logs
        self.parse_logs(self.log_queue[:5])
        self.log_queue = self.log_queue[5:]

    def parse_logs(self, logs):
        points = []
        for log in logs:
            
            print(log)
            
            pid = log.get('u')
        
            type = log.get('t')
            if 'c' in log:
                try:
                    name, cid = log.get('c')
                except (TypeError, ValueError):
                    pass

            if pid == 'g':
            
                match type:
                
                    case 'res':
                        self.reset()
                        
                    case 'add':
                        self.add_player(log['pid'], log['name'])
                        
                    case 'ns':
                        self.main_button.update_status(log['stat'])
                        
                    case 'set':
                        self.settings = log['settings']

                    case 'nt':
                        self.get_player(log['p']).new_turn()
                        
                    case 'sc':
                        if log.get('c'):
                            self.grid.set_card(self.get_card(name, cid, player=self.get_player(log['o'])), log['p'])
                        else:
                            self.grid.clear_card(log['p'])
                    
            else:
                
                if isinstance(pid, str):
                    pid = int(pid)
                p = self.get_player(pid)
                
                match type:
                    
                    case 'score':
                        p.update_score(log['score'])
                        
                    case 'nd':
                        p.new_deck(log['deck'], log['cards'])
                        
        for log, p in points:
            self.new_points(log, p)
            
# player stuff

    @property
    def main_p(self):
        for p in self.players:
            if p.pid == self.pid:
                return p
    
    def get_player(self, pid):
        for p in self.players:
            if p.pid == pid:
                return p

    def add_player(self, pid, name):
        if not any({p.pid == pid for p in self.players}):
            p = Player(self, name, pid, Client_Base.COLORS[pid])
            self.players.append(p)
            self.sheet.add_player(pid, Client_Base.COLORS[pid], {'name': name})

            return p
            
# card stuff

    def set_view_card(self, card):
        self.view_card = card
        self.view_image = card.get_image(mini=False)
        
    def clear_view_card(self):
        self.view_card = None
        self.view_image = None
        
    def set_hover_card(self, card):
        self.hover_card = card
        self.hover_image = card.get_image(
            mini=False, 
            scale=(
                CONSTANTS['card_width'] * 0.15,
                CONSTANTS['card_height'] * 0.15
            )
        )
        
    def clear_hover_card(self):
        self.hover_card = None
        self.hover_image = None
        self.hover_matches.clear()
        
    def set_held_card(self, card):
        card.set_visible(False)
        self.held_card = card
        
    def clear_held_card(self):
        self.held_card.set_visible(True)
        self.held_card = None

    def get_card(self, name, cid, player=None, add=True):
        c = Card(self, name, cid, player=player)
        if add:
            if cards := self.cards.get(cid):
                cards.append(c)
            else:
                self.cards[cid] = [c]
        return c

# running stuff

    def update(self):
        self.get_info()
        super().update()
        
        for p in self.players:
            p.update()
            
        if self.hover_card:
            if not self.hover_card.parent:
                self.clear_hover_card()
            
    def draw(self):
        self.start_draw()
        
        if self.hover_card:
            r = self.hover_image.get_rect()
            r.center = self.hover_card.rect.center
            self.window.blit(self.hover_image, r)
            
            for c in self.hover_matches:
                pg.draw.line(self.window, (255, 0, 0), self.hover_card.rect.center, c.rect.center, width=4)

        if self.view_card:
            self.window.blit(self.view_image, self.view_rect)
            
        if self.held_card:
            r = self.held_card.rect.copy()
            r.center = pg.mouse.get_pos()
            self.window.blit(self.held_card.get_image(), r)

        pg.display.flip()
        
        
        
        
        
        
        
        
        
        
        
        
        
        