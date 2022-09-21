import random

import pygame as pg

from data.constants import CONSTANTS
from .exceptions import CommunicationError

from spritesheet.spritesheet import Spritesheet

from ui.menu.menu import Menu

from ui.element.elements import Textbox, Button, Popup, Live_Window
from ui.icons.icons import icons
from ui.color.ops import gen_colors
from ui.particles.get_particles import explode_no_grav

from ..elements.player import Player
from ..elements.card import Card
from ..elements.moving_card import Moving_Card
from ..elements.card_window import Card_Window
from ..elements.main_button import Main_Button
from ..elements.grid import Grid
from ..elements.player_spot import Player_Spot
from ..elements.points import Points

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

    community = Card_Window(
        dir=3,
        size=((3 * CONSTANTS['cw']) + (4 * sep), (3 * CONSTANTS['ch']) + (4 * sep)), 
        outline_color=(255, 0, 0),
        outline_width=2
    )
    community.rect.topleft = (20, 50)
    elements.append(community)
    menu.community = community
    
    play = Card_Window(
        dir =3,
        size=((3 * CONSTANTS['cw']) + (4 * sep), (1 * CONSTANTS['ch']) + (2 * sep)), 
        outline_color=(255, 255, 0),
        outline_width=2
    )
    play.rect.topleft = (community.rect.left, community.rect.bottom + 20)
    elements.append(play)
    menu.play = play
    
    selection = Card_Window(
        dir=3,
        size=((3 * CONSTANTS['cw']) + (4 * sep), (2 * CONSTANTS['ch']) + (3 * sep)),
        outline_color=(0, 0, 255),
        outline_width=2
    )
    selection.rect.topleft = (play.rect.left, play.rect.bottom + 20)
    elements.append(selection)
    menu.selection = selection

    options = Button.Text_Button(
        text='options'
    )
    options.rect.topright = (body.width - 30, 30)
    elements.append(options)
    menu.options = options
    
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
        self.points = {}
        self.kill_particles = []
        
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

            match log['t']:
            
                case 'res':
                    self.reset()
                    
                case 'ap':
                    self.add_player(log['p'], log['name'])
                    
                case 'ns':
                    self.main_button.update_status(log['stat'])
                    
                case 'set':
                    self.settings = log['settings']

                case 'nt':
                    for p in self.players:
                        p.end_turn()
                    self.get_player(log['p']).start_turn()
                    
                case 'sc':
                    p = self.get_player(log['p'])
                    start = None
                    if (card := self.cards.get(log['c'][0])):
                        start = card.rect.center
                    else:
                        card = self.get_card(log['c'][1], log['c'][0], player=p)
                    self.grid.set_card(card, log['pos'])
                    if start:
                        Moving_Card(self, p, 'move', card, start=start)
                case 'cc':
                    self.grid.clear_card(log['pos'])
                    if log['k']:
                        self.kill_particles += explode_no_grav(100, self.cards[log['c']].rect, (-10, 10), (1, 5), (5, 20))

                case 'ac':
                    self.add_card(log['d'], *log['c'])
                case 'rc':
                    self.remove_card(log['d'], log['c'])
                    
                case 'score':
                    p = self.get_player(log['u'])
                    p.update_score(log['score'])
                case 'gp' | 'sp':
                    p = self.get_player(log['u'])
                    points.append((log, p, log['c']))
                    
                case 'play':
                    p = self.get_player(log['u'])
                    if not p.is_main:
                        Moving_Card(self, p, 'play', self.cards[log['c']])
                case 'own':
                    self.cards[log['c']].player = self.get_player(log['u'])
                        
        for log, p, cid in points:
            self.new_points(
                log['t'],
                p,
                self.cards.get(cid),
                log['points'],
                extra=self.cards.get(log['e']) if log['e'] else None,
                target=self.get_player(log.get('target'))
            )
                
            
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
            ps = Player_Spot()
            self.elements.append(ps)
            
            p = Player(self, name, pid, Client_Base.COLORS[pid], ps)
            self.players.append(p)
            self.sheet.add_player(pid, Client_Base.COLORS[pid], {'name': name})
            
            self.organize_screen()

            return p
            
    def organize_screen(self):
        spots = [p.spot for p in self.players]
        x = y = 0
        for s in spots:
            r = s.total_rect
            sx, sy = r.topright
            s.rect.move_ip(x - sx, y - sy)
            y += r.height + 10
        r = s.rect.unionall([o.total_rect for o in spots])
        x0, y0 = r.topleft
        r.topright = (self.rect.right - 30, self.options.rect.bottom + 20)
        x1, y1 = r.topleft
        for s in spots:
            s.rect.move_ip(x1 - x0, y1 - y0)
            
            
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

    def get_card(self, name, cid, player=None, deck=None, add=True):
        c = Card(self, name, cid, player=player, deck=deck)
        if add:
            self.cards[cid] = c
        return c
        
    def add_card(self, deck, cid, name):
        card = self.get_card(name, cid, deck=deck, add=False)
        
        match deck:
            
            case 'play':
                self.play.add_element(card)
            case 'community':
                self.community.add_element(card)
            case 'selection':
                self.selection.add_element(card)
                
    def remove_card(self, deck, cid):
        match deck:
            
            case 'play':
                self.play.remove_element(cid)
            case 'community':
                self.community.remove_element(cid)
            case 'selection':
                self.selection.remove_element(cid)
        
# points stuff

    def new_points(self, type, p, card, points, extra=None, target=None):    
        if not (parent_points := self.points.get(card.cid)):
            parent_points = Points(self, p, 0 if extra else points, card)
            self.points[card.cid] = parent_points
            
        if extra:
            parent_points.add_child_points(points, extra)
            
            if target:
                self.new_points(type, target, extra, -points)
                
# particle stuff

    def update_particles(self):
        i = 0
        while i in range(len(self.kill_particles)):
            p = self.kill_particles[i]
            p[0][0] += p[1][0]
            p[0][1] += p[1][1]
            p[3] -= 1
            if p[3] <= 0:
                self.kill_particles.pop(i)
            else:
                i += 1

# running stuff

    def update(self):
        self.get_info()
        super().update()
        
        for p in self.players:
            p.update()
            
        if self.hover_card:
            if not self.hover_card.parent:
                self.clear_hover_card()
                
        self.update_particles()
            
    def draw(self):
        self.start_draw()
        
        if self.hover_card:
            if not self.hover_card.visible:
                self.clear_hover_card()
            else:
                r = self.hover_image.get_rect()
                r.center = self.hover_card.rect.center
                self.window.blit(self.hover_image, r)
                
                other = self.cards.get(self.hover_card.cid)
                if other and other is not self.hover_card:
                    pg.draw.line(self.window, other.player.color, self.hover_card.rect.center, other.rect.center, width=3)

        if self.view_card:
            self.window.blit(self.view_image, self.view_rect)
            
        if self.held_card:
            r = self.held_card.rect.copy()
            r.center = pg.mouse.get_pos()
            self.window.blit(self.held_card.get_image(), r)
            
        for p, _, r, _ in self.kill_particles:
            pg.draw.circle(self.window, (255, 0, 0), p, r)

        pg.display.flip()
        
        
        
        
        
        
        
        
        
        
        
        
        
        