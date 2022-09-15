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
from ..elements.player_spot import Player_Spot
from ..elements.card_window import Card_Window
from ..elements.main_button import Main_Button
from ..elements.points import Points
from ..elements.moving_card import Moving_Card

def get_label(window, text):
    label = Textbox(
        size=(window.rect.width, 30),
        text=text,
        centerx_aligned=True,
        centery_aligned=True,
        fill_color=window.fill_color,
        text_outline_color=(0, 0, 0),
        text_outline_width=2,
        border_top_left_radius=5,
        border_top_right_radius=5,
        enabled=False
    )
    window.add_child(
        label,
        left_anchor='left',
        bottom_anchor='top',
        bottom_offset=-5
    )

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
    
    cancel_button = Button.Text_Button(
        text=icons['X'],
        font_name='icons.ttf',
        text_color=(255, 0, 0),
        func=lambda: menu.send('cancel')
    )
    
    def cancel():
        p = menu.main_p
        cancel_button.set_visible(p.can_cancel)
        cancel_button.set_enabled(p.can_cancel)
        
    cancel_button.add_event(
        tag='update',
        func=cancel
    )
    
    cancel_button.set_parent(main_button, left_anchor='right', bottom_anchor='top')
    elements.append(cancel_button)
    
    sequence = Card_Window(
        dir=3,
        size=((2 * CONSTANTS['cw']) + (3 * sep), (3 * CONSTANTS['ch']) + (4 * sep)), 
        outline_color=(255, 0, 0),
        outline_width=2
    )
    sequence.rect.bottomleft = (20, body.height - 20)
    elements.append(sequence)
    menu.sequence = sequence
    
    selection = Card_Window(
        dir=3,
        size=((2 * CONSTANTS['cw']) + (3 * sep), (3 * CONSTANTS['ch']) + (4 * sep)), 
        outline_color=(0, 0, 255),
        outline_width=2
    )
    selection.rect.bottomright = (body.width - 20, body.height - 20)
    elements.append(selection)
    menu.selection = selection
    
    active_card = Card_Window(
        dir=1,
        size=(CONSTANTS['cw'] + (2 * sep), CONSTANTS['ch'] + (2 * sep)),
        outline_color=(255, 255, 255),
        outline_width=2
    )
    active_card.rect.bottomright = (selection.rect.left - 10, selection.rect.bottom)
    elements.append(active_card)
    menu.active_card = active_card

    shop = Card_Window(
        dir=0,
        size=((CONSTANTS['cw'] * 3) + (sep * 4), CONSTANTS['ch'] + (sep * 2)),
        inf_height=False,
        outline_color=(255, 255, 0),
        outline_width=2
    )   
    shop.rect.bottomright = (active_card.rect.left - 10, active_card.rect.bottom)
    elements.append(shop)
    menu.shop = shop
    
    options = Button.Text_Button(
        text='options'
    )
    options.rect.topright = (body.width - 30, 30)
    elements.append(options)
    
    round_text = Textbox(
        text_color=(255, 255, 0),
    )
    round_text.rect.midtop = (options.rect.centerx, options.rect.bottom + 10)
    round_text.set_parent(
        menu,
        centerx_anchor='centerx',
        centerx_offset=round_text.rect.centerx - body.centerx,
        centery_anchor='centery',
        centery_offset=round_text.rect.centery - body.centery
    )
    elements.append(round_text)
    menu.round_text = round_text

    discard = Card_Window(
        dir=1,
        size=active_card.rect.size
    )
    discard.rect.midbottom = (selection.rect.centerx, selection.rect.top - 30) 
    elements.append(discard)
    menu.discard = discard
    
    event = Card_Window(
        dir=1,
        size=active_card.rect.size
    )
    event.rect.midtop = (active_card.rect.centerx, discard.rect.top)
    elements.append(event)
    menu.event = event
    
    scores = Live_Window(
        size=(200, 100)
    )
    scores.rect.topleft = (20, 40)
    elements.append(scores)
    menu.scores = scores
    
    items = Card_Window(
        dir=0,
        size=((CONSTANTS['cw'] * 6) + (7 * sep), CONSTANTS['ch'] + (2 * sep)),
        inf_width=True,
        inf_height=False
    )
    menu.items = items
    
    spells = Card_Window(
        dir=0,
        size=((CONSTANTS['cw'] * 6) + (7 * sep), CONSTANTS['ch'] + (2 * sep)),
        inf_width=True,
        inf_height=False,
    )
    menu.spells = spells
    
    treasure = Card_Window(
        dir=0,
        size=((CONSTANTS['cw'] * 6) + (7 * sep), CONSTANTS['ch'] + (2 * sep)),
        inf_width=True,
        inf_height=False,
    )
    menu.treasure = treasure
    
    extras = Popup.Live_Popup(
        size=((CONSTANTS['cw'] * 6) + (7 * sep), items.rect.height * 3),
        outline_color=(255, 255, 255),
        outline_width=5
    )
    extras.join_elements(
        [items, spells, treasure]
    )
    extras.rect.topleft = (sequence.rect.right + 10, body.height)
    elements.append(extras)
    menu.extras = extras

    return elements
   
class Client_Base(Menu): 
    COLORS = gen_colors(15)
    
    def __init__(self, connection, set_screen=client_screen):
        super().__init__(set_screen, fill_color=(32, 32, 40))
        
        self.conn = connection
        self.sheet = Spritesheet()
        self.pid = None
        
        self.status = ''
        self.players = []
        self.settings = {}
        
        self.cards = {}
        self.moving_cards = {}
        
        self.logs = {}
        self.log_queue = []
        
        self.round = 1
        
        self.view_rect = pg.Rect((0, 0), CONSTANTS['card_size'])
        self.view_rect.center = self.body.center
        self.view_card = None
        self.view_image = None
        
        self.hover_card = None
        self.hover_image = None
        self.hover_matches = []
        
# start stuff
        
    def start(self):
        self.running = True
        self.pid = self.send('pid')
        
    def reset(self):
        self.round = 1
        
        self.shop.clear()
        self.event.clear()
        self.discard.clear()
        
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
        #if logs:
        #    print('logs:', logs)
        self.update_logs(logs)
        
    def update_logs(self, logs):
        self.log_queue += logs
        self.parse_logs(self.log_queue[:5])
        self.log_queue = self.log_queue[5:]

    def parse_logs(self, logs):
        points = []
        for log in logs:
            
            #print(log)
            
            pid = log.get('u')
        
            type = log.get('t')
            if 'c' in log:
                try:
                    name, uid = log.get('c')
                except (TypeError, ValueError):
                    pass

            if pid == 'g':
            
                match type:
                
                    case 'res':
                        self.reset()
                        
                    case 'add':
                        self.add_player(log['pid'], log['name'])
                    case 'ord':
                        self.reorder(log.get('ord'))
                        
                    case 'ns':
                        self.main_button.update_status(log['stat'])
                        
                    case 'set':
                        self.settings = log['settings']
                        
                    case 'se':
                        self.set_event(name, uid)
                    case 'fill':
                        self.fill_shop(log['cards'])
                    case 'disc':
                        if log['c']:
                            self.discard.join_elements([self.get_card(name, uid)])
                        else:
                            self.discard.clear()

                    case 'ur':
                        self.round_text.set_text(log['s'])
                    case 'nt':
                        for p in self.players:
                            p.new_turn()
                    
            else:
                
                if isinstance(pid, str):
                    pid = int(pid)
                p = self.get_player(pid)
                
                match type:
                    
                    case 'score':
                        p.update_score(log['score'])
                        
                    case 'nd':
                        p.new_deck(log['deck'], log['cards'])
                    case 'aac':
                        p.set_active_card(
                            self.get_card(name, uid, add=not p.is_main),
                            wait=log.get('w'),
                            can_cancel=log.get('cancel')
                        )
                    case 'rac':
                        p.set_active_card(None)
                        
                    case 'cfs':
                        p.start_flip()
                    case 'cfe':
                        p.end_flip(log['coin'])
                    case 'drs':
                        p.start_roll()
                    case 'dre':
                        p.end_roll(log['dice'])
                        
                    case 'play':
                        p.play(uid, log.get('d'))
                    case 'buy':
                        p.buy(uid)
                    case 'cast':
                        p.cast(uid)
                    case 'disc' | 'ui':
                        p.discard(uid)
                        
                    case 'gp' | 'lp' | 'sp' | 'give':
                        points.append((log, p))
                        
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
            ps = Player_Spot()
            self.elements.append(ps)
            
            p = Player(self, name, pid, Client_Base.COLORS[pid], ps)
            self.players.append(p)
            self.sheet.add_player(pid, Client_Base.COLORS[pid], {'name': name})
            
            self.players.sort(key=lambda p: p.pid)
            self.organize_spots()

            return p

    def reorder(self, pids):
        players = sorted(self.players, key=lambda p: pids.index(p.pid))
        self.players = players
        
    def organize_spots(self):
        rects = []
        x = 0
        y = 0
        
        for p in self.players:
            p.spot.rect.topleft = (x, y)
            rects.append(p.spot.rect)
            
            x += p.spot.total_rect.width + 40

        br = rects[0].unionall(rects)
        
        dx = self.body.centerx - br.centerx
        dy = self.body.centery - br.centery
        
        for r in rects:
            r.move_ip(dx, dy)
            
    def new_turn(self):
        for p in self.players: 
            p.start_turn()
            
# card stuff

    @property
    def visible_cards(self):
        cards = (
            self.sequence.elements +
            self.selection.elements +
            self.active_card.elements +
            self.discard.elements + 
            self.event.elements +
            self.shop.elements
        )
        
        if self.extras.is_open:
            cards += (
                self.items.elements + 
                self.spells.elements +
                self.treasure.elements
            )
            
        for p in self.players:
            cards += (
                p.spot.elements +
                p.spot.ongoing.elements + 
                p.spot.active_card.elements
            )
            
        return cards
        
    def find_matches(self, card):
        return [c for c in self.visible_cards if c == card and c is not card]
    
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
        self.hover_matches = self.find_matches(card)
        
    def clear_hover_card(self):
        self.hover_card = None
        self.hover_image = None
        self.hover_matches.clear()

    def get_card(self, name, uid, add=True):
        c = Card(self, name, uid)
        if add:
            if cards := self.cards.get(uid):
                cards.append(c)
            else:
                self.cards[uid] = [c]
        return c
        
    def get_moving_card(self, player, type, card):
        if not self.moving_cards.get(card.uid):
            self.moving_cards[card.uid] = Moving_Card(self, player, type, card)

    def del_moving_card(self, uid):
        self.moving_cards.pop(uid)

    def fill_shop(self, cards):
        self.shop.join_elements(
            [self.get_card(name, uid) for name, uid in cards]
        )
        
    def set_event(self, name, uid):
        self.event.join_elements(
            [self.get_card(name, uid)]
        )
        
# points stuff

    def new_points(self, log, p):
        if log.get('d'):
            return

        type = log['t']
        target = self.get_player(log.get('target'))
        
        match type:
            case 'gp':
                points = log.get('gp')
            case 'lp':
                points = -log.get('lp')
            case 'sp':
                points = log.get('sp')
            case 'give':
                points = -log.get('gp')
            
        if not points:
            return
            
        card = p.spot.find_card(log['c'][1])
        if card:
            self.elements.append(Points(self, p, type, points, card, target))
        else:
            p.spot.add_points(points)

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

        pg.display.flip()
        
        
        
        
        
        
        
        
        
        
        
        
        
        