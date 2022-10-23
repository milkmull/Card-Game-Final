import random

import pygame as pg

from data.constants import CONSTANTS
from .exceptions import CommunicationError

from spritesheet.spritesheet import Spritesheet

from ui.scene.scene import Scene
from ui.scene.templates.yes_no import Yes_No

from ui.element.elements import Textbox, Button, Popup, Live_Window
from ui.icons.icons import icons
from ui.color.ops import gen_colors
from ui.particles.get_particles import explode_no_grav

from .settings import run_settings

from .element.player import Player
from .element.card import Card
from .element.animation_manager import Animation_Manager
from .element.card_window import Card_Window
from .element.grid import Grid
from .element.player_spot import Player_Spot
from .element.turn_timer import Timer
from .element.win_screen import Winner_Text
from .element.chat import Chat

def client_screen(scene):
    body = scene.body
    sep = Card_Window.SEP
    elements = []
    
    grid = Grid(scene)
    grid.rect.center = body.center
    elements.append(grid)
    scene.grid = grid
    
    main_button = Button.Text_Button(
        text='Start',
        size=(100, 30),
        text_size=30, 
        pad=5,
        center_aligned=True,
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=5,
        hover_color=(0, 255, 0),
        hover_text_color=(0, 0, 0)
    )
    main_button.rect.bottomright = (scene.rect.right - 40, scene.rect.bottom - 40)
    main_button.set_parent(scene, centerx_anchor='right', centerx_offset=-110, centery_anchor='bottom', centery_offset=-50)
    elements.append(main_button)
    scene.main_button = main_button
    main_button.turn_off()
    
    def click_main():
        if scene.pid == 0:
            match main_button.text:
                case 'Reset':
                    scene.send('reset')
                case 'Start':
                    scene.send('start')
                    
    main_button.add_event(func=click_main, tag='left_click')
    
    if not scene.is_single:
        chat = Chat(scene)
        chat.rect.midbottom = (main_button.rect.centerx, main_button.rect.top - 20)
        elements.append(chat)
        scene.chat = chat

    def get_size(w, h):
        return (
            (w * CONSTANTS['cw']) + ((w + 1) * sep),
            (h * CONSTANTS['ch']) + ((h + 1) * sep)
        )

    public = Card_Window(
        dir=0,
        size=get_size(3, 3), 
        outline_color=(255, 0, 0),
        outline_width=2
    )
    public.rect.topleft = (25, 40)
    elements.append(public)
    scene.public = public
    
    public_label = Textbox(
        text='Public:',
        text_size=15,
        #fill_color=scene.fill_color,
        text_color=(255, 0, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    )
    public_label.rect.midleft = (public.rect.left + 3, public.rect.top - 10)
    public.add_child(public_label, current_offset=True)
    
    private = Card_Window(
        dir=0,
        size=get_size(3, 1), 
        inf_width=True,
        inf_height=False,
        outline_color=(255, 255, 0),
        outline_width=2
    )
    private.rect.topleft = (public.rect.left, public.rect.bottom + 35)
    elements.append(private)
    scene.private = private
    
    private_label = Textbox(
        text='Private:',
        text_size=15,
        text_color=(255, 255, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    )
    private_label.rect.midleft = (private.rect.left + 3, private.rect.top - 10)
    private.add_child(private_label, current_offset=True)
    
    selection = Card_Window(
        dir=0,
        size=get_size(3, 2),
        outline_color=(100, 150, 255),
        outline_width=2
    )
    selection.rect.topleft = (private.rect.left, private.rect.bottom + 45)
    elements.append(selection)
    scene.selection = selection
    
    selection_label = Textbox(
        text='Selection:',
        text_size=15,
        text_color=(100, 150, 255),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    )
    selection_label.rect.midleft = (selection.rect.left + 3, selection.rect.top - 10)
    selection.add_child(selection_label, current_offset=True)

    settings_button = Button.Text_Button(
        text=icons['cog'],
        font_name='icons.ttf',
        text_size=30,
        center_aligned=True,
        func=run_settings,
        args=[scene],
        hover_color=(100, 100, 100),
        pad=5,
        border_radius=5
    )
    settings_button.rect.topright = (scene.rect.width - 20, 20)
    elements.append(settings_button)
    scene.settings_button = settings_button
    
    turn_timer = Timer(scene)
    turn_timer.set_parent(scene, centerx_anchor='right', centerx_offset=-100, top_anchor='top', top_offset=30)
    elements.append(turn_timer)
    scene.turn_timer = turn_timer
    
    wt = Winner_Text(scene)
    scene.win_screen = wt
    elements.append(wt)

    return elements
   
class Client_Base(Scene): 
    COLORS = gen_colors(15)
    
    def __init__(self, connection, set_screen=client_screen):
        super().__init__(set_screen, fill_color=(32, 32, 40))
        
        self.conn = connection
        self.sheet = Spritesheet()
        self.pid = None

        self.settings = {}
        self.players = []
        self.turn = 0

        self.animation_manager = Animation_Manager(self)
        self.cards = {}
        self.kill_particles = []

        self.log_queue = []

        self.view_rect = pg.Rect((0, 0), CONSTANTS['card_size'])
        self.view_rect.center = self.body.center
        self.view_card = None
        self.view_image = None
        
        self.hover_card = None
        self.hover_image = None
        self.hover_matches = []
        
        self.held_card = None
        
    @property
    def is_single(self):
        return type(self) == Client_Base
        
    @property
    def is_host(self):
        return self.pid == 0
        
# start stuff
        
    def start(self):
        self.running = True
        
    def reset(self):
        self.cards.clear()

        self.clear_view_card()
        self.clear_held_card()
        self.clear_held_card()
        
        self.public.clear()
        self.private.clear()
        self.selection.clear()
        self.grid.reset()
        self.animation_manager.reset()
        self.turn = 0

        for p in self.players:
            p.end_turn()
            
        self.main_button.set_text('Start')
        self.main_button.hover_color = (0, 255, 0)
            
        self.turn_timer.reset()
        self.win_screen.reset()
        
    def close(self):
        pass
        
    def get_settings(self):
        return self.settings
        
# communication stuff
        
    def send(self, data):
        if self.running:
            reply = self.conn.update_game(data)  
            return reply
            
    def get_info(self):
        logs = self.send('info')
        self.update_logs(logs)
        
    def update_logs(self, logs):
        self.log_queue += logs
        self.parse_logs(self.log_queue[:10])
        self.log_queue = self.log_queue[10:]

    def parse_logs(self, logs):
        for log in logs:
            
            print(log)

            match log['t']:
                
                case 'pid':
                    self.pid = log['pid']
                    if self.pid == 0:
                        self.main_button.turn_on()
            
                case 'res':
                    self.reset()

                case 'ap':
                    self.add_player(log)
                case 'rp':
                    self.remove_player(log['p'])
                    
                case 'set':
                    self.update_settings(log)

                case 'nt':
                    self.new_turn(log)
 
                case 'sc':
                    self.set_card(log)
                case 'cc':
                    self.clear_card(log)

                case 'ac':
                    self.add_card(log['d'], *log['c'])
                case 'rc':
                    self.remove_card(log['d'], log['c'])
                    
                case 'score':
                    self.update_score(log)
                case 'gp' | 'sp':
                    self.add_points(log)
                    
                case 'p':
                    self.play_card(log)
                case 'own':
                    self.set_owner(log)
                    
                case 'fin':
                    self.end_game(log)
                    
                case 'msg':
                    self.chat.add_message(log)
            
# log process stuff

    def update_settings(self, log):
        self.settings = log['settings']
        self.grid.set_size(self.settings['size'])
        for p in self.players:
            p.spot.update_name()
        
    def new_turn(self, log):
        for p in self.players:
            p.end_turn()
        self.get_player(log['p']).start_turn()
        
        if not self.turn:
            self.main_button.set_text('Reset')
            self.main_button.hover_color = (255, 0, 0)
        
        self.turn += 1
        self.turn_timer.start()
        
    def set_card(self, log):
        p = self.get_player(log['p'])
        start = None
        
        if (card := self.grid.get_card(log['c'][0])):
            start = card.rect.center
        else:
            card = self.get_card(log['c'][1], log['c'][0], player=p, add=False)
            
        if (parent := log['parent']):
            start = self.grid.get_card(parent).rect.center
            
        self.grid.set_card(card, log['pos'])
        if start:
            self.animation_manager.add_card(card, 'shift', start=start, delay=20 if p is not self.main_p else 0)
            
    def clear_card(self, log):
        self.grid.clear_card(log['pos'])
        if log['k']:
            self.animation_manager.add_card(self.grid.cards[log['c']], 'kill')
            
    def add_card(self, deck, cid, name):
        card = self.get_card(name, cid, deck=deck)
        
        match deck:
            
            case 'private':
                self.private.add_element(card)
            case 'public':
                self.public.add_element(card)
            case 'selection':
                self.selection.add_element(card)
                
    def remove_card(self, deck, cid):
        match deck:
            
            case 'private':
                self.private.remove_element(cid)
            case 'public':
                self.public.remove_element(cid)
            case 'selection':
                self.selection.remove_element(cid)
            
    def update_score(self, log):
        p = self.get_player(log['u'])
        p.update_score(log['score'])
        
    def play_card(self, log):
        p = self.get_player(log['u'])
        
        if not p.is_main:

            if not (card := self.cards.get(log['c'])):
                card = self.grid.get_card(log['c'])
                start = self.public.rect.center
            else:
                start = self.cards[log['c']].rect.center

            self.animation_manager.add_card(self.grid.cards[log['c']], 'play', start=start)
            
    def set_owner(self, log):
        self.grid.cards[log['c']].player = self.get_player(log['u'])
        self.animation_manager.add_card(self.grid.cards[log['c']], 'own')
        
    def end_game(self, log):
        self.turn += 1
        self.turn_timer.reset()
        self.win_screen.start()

        for p in self.players:
            p.end_turn()

# player stuff

    @property
    def main_p(self):
        for p in self.players:
            if p.pid == self.pid:
                return p
                
    def get_current_turn(self):
        for p in self.players:
            if p.is_turn:
                return p
    
    def get_player(self, pid):
        for p in self.players:
            if p.pid == pid:
                return p

    def add_player(self, log):
        pid = log['p']
        if not self.get_player(pid):
            ps = Player_Spot()
            self.add_element(ps)
            
            p = Player(self, log['name'], pid, Client_Base.COLORS[pid], ps, log['cpu'])
            self.players.append(p)

            self.organize_screen()

            return p
            
    def remove_player(self, pid):
        if (p := self.get_player(pid)):
            self.remove_element(p.spot)
            self.players.remove(p)
            
            self.organize_screen()
            
    def organize_screen(self):
        spots = [p.spot for p in self.players]
        x = self.rect.right - 60
        y = 80
        for s in spots:
            s.rect.topright = (x, y)
            y += s.rect.height + 10
            
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
        if self.held_card:
            self.held_card.set_visible(True)
            self.held_card = None

    def get_card(self, name, cid, player=None, deck=None, add=True):
        c = Card(self, name, cid, player=player, deck=deck)
        if add:
            self.cards[cid] = c
        return c
        
    def start_card_shifts(self):
        pass
        
# points stuff

    def add_points(self, log):
        self.animation_manager.add_points(
            log['t'],
            self.get_player(log['u']),
            self.grid.cards.get(log['c']),
            log['points'],
            extra=self.grid.cards.get(log['e']) if log['e'] else None,
            target=self.get_player(log.get('target'))
        )
                
# particle stuff

    def get_kill_particles(self, r, color):
        if isinstance(r, tuple):
            r = pg.Rect(r, (1, 1))
        self.kill_particles += explode_no_grav(100, r, (-10, 10), (1, 5), (5, 20), color=color)

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

    def exit(self):
        m = Yes_No(text_kwargs={'text': 'Are you sure you want to exit the game?'}, overlay=True)
        if m.run():
            super().exit()
    
    def run(self):
        self.start()
        super().run()
    
    def events(self):
        events = super().events()   
        
        if self.held_card or self.view_card:
        
            if (mbu := events.get('mbu')):
                match mbu.button:
                    
                    case 1:
                        if self.held_card:
                            self.clear_held_card()
                    case 3:
                        if self.view_card:
                            self.clear_view_card()
                
        if self.hover_card:
            if not self.hover_card.rect.collidepoint(pg.mouse.get_pos()):
                self.clear_hover_card()

    def update(self):
        self.get_info()
        super().update()
        
        self.animation_manager.update()
        
        for p in self.players:
            p.update()
            
        if self.hover_card:
            if not self.hover_card.parent:
                self.clear_hover_card()
                
        self.update_particles()
   
    def draw(self):
        self.start_draw()
        
        self.animation_manager.draw(self.window)
        
        if self.hover_card:
            if not self.hover_card.visible:
                self.clear_hover_card()
            else:
                r = self.hover_image.get_rect()
                r.center = self.hover_card.rect.center
                self.window.blit(self.hover_image, r)
                
                other = self.grid.cards.get(self.hover_card.cid)
                if other and other is not self.hover_card:
                    pg.draw.line(self.window, other.player.color, self.hover_card.rect.center, other.rect.center, width=3)

        if self.view_card:
            self.window.blit(self.view_image, self.view_rect)
            
        if self.held_card:
            r = self.held_card.rect.copy()
            r.center = pg.mouse.get_pos()
            self.window.blit(self.held_card.get_image(), r)
            
        for p, _, r, _, color in self.kill_particles:
            pg.draw.circle(self.window, color, p, r)

        pg.display.flip()
        
        
        
        
        
        
        
        
        
        
        
        
        
        