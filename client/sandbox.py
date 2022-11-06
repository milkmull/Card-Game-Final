import pygame as pg

from ui.element.elements import Textbox, Button, Popup, Live_Window
from ui.icons.icons import icons

from .client_base import client_screen, Client_Base, Player
from .element.chat import Chat
from .add_card import run_add_card
from ui.scene.templates.yes_no import Yes_No

from .element.player_spot import Sandbox_Player_Spot

def sandbox_screen(scene):
    elements = client_screen(scene)
    
    scene.turn_timer.turn_off()

    turn_button = Button.Text_Button(
        text='Next Turn',
        text_size=20, 
        pad=5,
        center_aligned=True,
        outline_color=(255, 255, 255),
        outline_width=2,
        border_radius=5,
        hover_color=(0, 255, 0),
        hover_text_color=(0, 0, 0),
        func=scene.game.skip_turn
    )
    turn_button.rect.midbottom = (scene.main_button.rect.centerx, scene.main_button.rect.top - 25)
    elements.append(turn_button)
    scene.turn_button = turn_button
    
    b = Button.Text_Button(
        text=icons['plus'],
        font_name='icons.ttf',
        text_size=10,
        center_aligned=True,
        text_color=(0, 255, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    )
    b.rect.bottomright = (scene.public.rect.right, scene.public.rect.top - 5)
    scene.public.add_child(b, current_offset=True)

    b.add_event(
        tag='left_click',
        func=scene.click_button,
        args=[b],
        kwargs={'deck': 'public'}
    )
    
    b = Button.Text_Button(
        text=icons['plus'],
        font_name='icons.ttf',
        text_size=10,
        center_aligned=True,
        text_color=(0, 255, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    )
    b.rect.bottomright = (scene.private.rect.right, scene.private.rect.top - 5)
    scene.private.add_child(b, current_offset=True)

    b.add_event(
        tag='left_click',
        func=scene.click_button,
        args=[b],
        kwargs={'deck': 'private'}
    )
    
    return elements

class Sandbox(Client_Base):
    def __init__(self, game):
        super().__init__(game, set_screen=sandbox_screen)
        
        self.pid = 0
        self.spot_buttons = {}
        
    @property
    def game(self):
        return self.conn
        
    @property
    def is_host(self):
        return True
        
    def reset(self):
        super().reset()
        self.add_spot_buttons()
        
    def update_settings(self, *args, **kwargs):
        super().update_settings(*args, **kwargs)
        self.add_spot_buttons()
        
# new checks
        
    def get_selecting_player(self):
        for p in self.game.players:
            if p.decks['selection']:
                return self.get_player(p.pid)
                
    def switch_view(self, pid):
        if pid != self.pid:
            self.get_info()
            p = self.get_player(self.pid)
            p.spot.unfreeze_animation('hover')
            if not p.spot.hit:
                p.spot.run_animations('hover', reverse=True)

            self.pid = pid
            self.game.switch_view(pid)
            
            p = self.get_player(pid)
            p.spot.run_animations('hover')
            p.spot.freeze_animation('hover')
            
    def check_player_selecting(self):
        if (p := self.get_selecting_player()):
            m = Yes_No(
                text_kwargs={'text': 'Cannot make changes while player is selecting.\n\nGo to selecting player?'},
                overlay=True
            )
            if m.run():
                self.switch_view(p.pid)
            return True
        return False
                
    def send(self, data):
        if not self.running:
            return
            
        if data.startswith('play'):
            if self.check_player_selecting():
                return
            self.game.set_turn(self.pid)

        reply = self.game.update_game(data, pid=self.pid)  
        return reply
        
# setting cards

    def set_card(self, log):
        super().set_card(log)
        
        spot = self.spot_buttons[log['pos']]
        spot.text_color = (255, 0, 0)
        spot.set_text(icons['X'])
        
    def clear_card(self, log):
        super().clear_card(log)
        
        spot = self.spot_buttons[log['pos']]
        spot.text_color = (0, 255, 0)
        spot.set_text(icons['plus'])
            
    def manual_set_card(self, spot, name, player_name):
        c = self.game.get_card(name)
        self.game.add_public(c)
        
        p = self.game.get_player(self.get_player_by_name(player_name).pid)
        self.switch_view(p.pid)
        self.send(f'play-public-{c.cid}-{spot._pos[0]}-{spot._pos[1]}')
        
    def manual_delete_card(self, spot):
        s = self.game.grid.get_spot(spot._pos)
        if not s.card:
            return
        self.clear_hover_card()
        s.clear_card()
        
    def add_public_card(self, name):
        c = self.game.get_card(name)
        self.game.add_public(c)
            
    def add_private_card(self, name, player_name):
        p = self.game.get_player(self.get_player_by_name(player_name).pid)
        c = self.game.get_card(name)
        self.game.set_turn(p.pid)
        p.add_card('private', c)
        
# new ui
            
    def add_player(self, log):
        pid = log['p']
        if not self.get_player(pid):
            ps = Sandbox_Player_Spot()
            self.add_element(ps)
            
            p = Player(self, log['name'], pid, Client_Base.COLORS[pid], ps, log['cpu'])
            self.players.append(p)

            self.organize_screen()

            ps.add_event(
                tag='left_click',
                func=self.switch_view,
                args=[p.pid]
            )
            
            def update_score():
                text = ps.points_spot.text
                score = int(text)
                self.game.get_player(p.pid).update_score(score)
            
            ps.points_spot.add_event(
                tag='close',
                func=update_score
            )
            
            if p.pid == self.pid:
                ps.run_animations('hover')
                ps.freeze_animation('hover')
                
            return p

    def click_button(self, b, spot=None, deck=None):
        if self.game.status != 'playing':
            return
            
        if self.check_player_selecting():
            return

        if b.text == icons['plus']:
            run_add_card(self, spot=spot, deck=deck)
        elif b.text == icons['X']:
            if spot.card.visible:
                self.manual_delete_card(spot)
                
        if self.check_player_selecting():
            return
                
    def add_spot_buttons(self):
        for b in self.spot_buttons.values():
            self.remove_element(b)
        self.spot_buttons.clear()
        
        for spot in self.grid.spots:
            
            b = Button.Text_Button(
                text=icons['plus'],
                font_name='icons.ttf',
                text_size=10,
                center_aligned=True,
                text_color=(0, 255, 0),
                text_outline_color=(0, 0, 0),
                text_outline_width=2,
                layer=2,
                visible=False
            )
            
            b.set_parent(
                spot,
                right_anchor='right',
                right_offset=-5,
                top_anchor='top',
                top_offset=5
            )
  
            b.add_event(
                tag='left_click',
                func=self.click_button,
                args=[b],
                kwargs={'spot': spot}
            )
            
            self.add_element(b)
            self.spot_buttons[spot._pos] = b
        
# base stuff
        
    def draw(self):
        self.start_draw()
        
        self.animation_manager.draw(self.window)
        
        if self.hover_card:
            self.draw_hover_card()
            
        if self.game.status == 'playing':
            for b in self.spot_buttons.values():
                b.draw(self.window)
            
        if self.view_card:
            self.draw_view_card()
        if self.held_card:
            self.draw_held_card()

        for p, _, r, _, color in self.kill_particles:
            pg.draw.circle(self.window, color, p, r)

        pg.display.flip()
        
        
        
        