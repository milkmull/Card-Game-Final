import json

import pygame as pg

from .node import mapping
from .node.node_base import pack, unpack, Port, Node, Group_Node
#from .tester import tester

from .element.search_bar import Search_Bar
from .element.node_menu import Node_Menu
from .element.context_manager import Context_Manager

from ui.math import line
from ui.element.drag.dragger import Dragger
from ui.element.drag.rect_selector import Rect_Selector
from ui.element.elements import Image, Textbox, Button, Input, Label
from ui.menu.menu import Menu
   
def save_group_node(gn):
    nodes = gn.nodes.copy() + [gn]
    data = pack(nodes)
    with open('data/group_nodes.json', 'r') as f:
        group_data = json.load(f)
    group_data[gn.get_name()] = data
    with open('data/group_nodes.json', 'w') as f:
        json.dump(group_data, f, indent=4)
        
def write_node_data(nodes):
    import json
    with open(f'{node_base.NODE_DATA_PATH}node_info.json', 'r') as f:
        data = json.load(f)
        
    for i, old_name in enumerate(data.copy()):
        new_name = list(nodes)[i]
        data[new_name] = data.pop(old_name)

    with open('data/node_info1.json', 'w') as f:
        json.dump(data, f, indent=4)

#menu stuff--------------------------------------------------------------------

def run_data_sheet(ne):
    m = Menu(get_objects=screens.data_sheet_menu, args=[ne])
    m.run()

#sorting stuff-------------------------------------------------------------------------

def move_nodes(nodes, c):
    left = min({n.rect.left for n in nodes})
    right = max({n.rect.right for n in nodes})
    top = min({n.rect.top for n in nodes})
    bottom = max({n.rect.bottom for n in nodes})
    r = pg.Rect(left, top, right - left, bottom - top)
    cx, cy = r.center
    r.center = c
    dx = r.centerx - cx
    dy = r.centery - cy
    
    for n in nodes:
        n.rect.move_ip(dx, dy)

#node editor--------------------------------------------------------------------------

def editor_objects(self):
    objects = []

    buttons = []
    for name, obj in Node.NODE_DATA.items():
        b = Button.text_button(name, size=(100, 30), border_radius=0, func=self.get_node, args=[name], tsize=15)
        buttons.append(b)
    for name, data in Node.GROUP_DATA.items():
        b = Button.text_button(name, size=(100, 30), border_radius=0, func=self.load_group_node, args=[name, data], tsize=15)
        buttons.append(b)

    sb = Search_Bar(buttons, (WIDTH, HEIGHT))
    self.objects_dict['search_bar'] = sb
    objects.append(sb)

    b = Button.text_button('save', func=self.save, tsize=15)
    b.rect.topleft = (5, 5)
    objects.append(b)

    b = Button.text_button('test', tsize=15, func=tester.run_tester, args=[self.card])
    b.rect.topleft = objects[-1].rect.bottomleft
    b.rect.top += 5
    objects.append(b)

    def test_run():
        text = tester.test_run(self.card)
        if text:
            Menu.notice(text)
    
    b = Button.text_button('test game', func=test_run, tsize=15)
    b.rect.topleft = objects[-1].rect.bottomleft
    b.rect.top += 5
    objects.append(b)
            
    b = Button.text_button('publish card', func=self.publish, tsize=15)
    b.rect.top = 5
    b.rect.midleft = objects[-1].rect.midright
    b.rect.y += 5
    objects.append(b)

    b = Button.text_button('group node', func=self.create_new_group_node, tsize=15)
    b.rect.top = 5
    b.rect.left = objects[-1].rect.right + 5
    objects.append(b)
    
    b = Button.text_button('ungroup node', func=self.ungroup_nodes, tsize=15)
    b.rect.top = 5
    b.rect.left = objects[-1].rect.right + 5
    objects.append(b)
    
    b = Button.text_button('data sheet', func=run_data_sheet, args=[self], tsize=15)
    b.rect.top = 5
    b.rect.left = objects[-1].rect.right + 5
    objects.append(b)
    
    b = Button.text_button('save group node', func=self.save_group_node, tsize=15)
    b.rect.midleft = objects[-1].rect.midright
    b.rect.x -= 5
    b.rect.y += 5
    objects.append(b)
    
    b = Button.text_button('exit', func=self.exit, tsize=15)
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    nm = Node_Menu(self)
    objects.append(nm)
    self.objects_dict['menu'] = nm
    
    cm = Context_Manager(self)
    objects.append(cm)
    self.objects_dict['context'] = cm

    return objects
    
def get_elements(menu):
    body = menu.body
    elements = []
    
    node_menu = Node_Menu(menu)
    elements.append(node_menu)

    search_bar = Search_Bar(menu)
    elements.append(search_bar)
    
    rect_selector = Rect_Selector()
    elements.append(rect_selector)
    
    return elements
    
class Node_Editor(Menu):        
    def __init__(self, card):
        self.card = card
        
        self.nodes = []
        Dragger.set(self.nodes)
        self.cm = None

        super().__init__(get_elements, fill_color=(32, 32, 40))
        
        self.anchor = None

        self.log = []
        self.logs = []
        self.log_history = []
        self.log_index = -1

        self.copy_data = None
        self.input = []

        if self.card.node_data:
            self.load_save_data(self.card.node_data)
            
    @property
    def wires(self):
        return Node.WIRES
        
    @property
    def active_port(self):
        return Port.ACTIVE_PORT
        
    @property
    def anchor_dist(self):
        return line.distance(self.anchor, pg.mouse.get_pos())
        
    def exists(self, name):
        return any({n.name == name for n in self.nodes})
        
#log stuff--------------------------------------------------------------------

    def reset_logs(self):
        self.logs.clear()
        self.log.clear()
        self.log_index = -1

    def add_log(self, log):
        self.logs.append(log)
        
    def get_logs(self):
        logs = self.logs.copy()
        self.logs.clear()
        return logs

    def update_log(self):
        new_logs = self.get_logs()
        if new_logs:

            if self.log_index == -1:
                self.log_history.clear()

            if self.log_index == 14:
                self.log_history = self.log_history[1:]
            else:
                if self.log_index > -1:
                    self.log_history = self.log_history[:self.log_index + 1]
                else:
                    self.log_history.clear()
                self.log_index += 1
                
            self.log_history.append(new_logs)
            
            print('d', new_logs)

    def undo_log(self):
        if not self.log_history or self.log_index == -1:
            return
            
        logs = self.log_history[self.log_index]
        
        print('u', logs)
        
        for log in logs[::-1]:
            type = log['t']
            
            if type == 'carry':
                n = log['node']
                dx, dy = log['dist']
                n.move(-dx, -dy)
                n.pickup_pos = None
                    
            elif type == 'add':
                n = log['node']
                if not n.is_group:
                    self.del_node(n, d=True)
                else:
                    self.ungroup_node(n, d=True)
                    
            elif type == 'del':
                n = log['node']
                m = log['m']
                self.add_node(n, d=True) 
                if m == 'ug':
                    n.recall_port_mem()
                    n.reset_ports()
                    
            elif type == 'conn':
                p0, p1 = log['ports']
                Port.disconnect(p0, p1, d=True)
                
            elif type == 'disconn':
                n0, n1 = log['nodes']
                p0, p1 = log['ports']
                if p0.parent_port:
                    if p0 not in n0.ports:
                        n0.ports.append(p0)
                    if p0.group_node:
                        if p0 not in p0.group_node.ports:
                            p0.group_node.ports.append(p0)
                if p1.parent_port:
                    if p1 not in n1.ports:
                        n1.ports.append(p1)
                    if p1.group_node:
                        if p1 not in p1.group_node.ports:
                            p1.group_node.ports.append(p1)
                Port.new_connection(p0, p1, force=True, d=True)

            elif type == 'val':
                e = log['e']
                v0, v1 = log['v']
                e.set_value(v0)
                
            elif type == 'transform':
                n = log['node']
                n.transform(form=log['form0'], d=True)
                    
            elif type == 'suppress':
                p = log['p']
                s = log['s']
                p.set_suppressed(not s, d=True)
                
            elif type == 'ap':
                n = log['node']
                p = log['port']
                n.rp(p=p)
                
            elif type == 'rp':
                n = log['node']
                p = log['port']
                n.ap(p=p)
                
        self.log_index -= 1
        
    def redo_log(self):
        if not self.log_history or self.log_index == len(self.log_history) - 1:
            return
            
        logs = self.log_history[self.log_index + 1]
        
        print('r', logs)
        
        for log in logs:
            type = log['t']
            
            if type == 'carry':
                n = log['node']
                dx, dy = log['dist']
                n.move(dx, dy)
                n.pickup_pos = None
                    
            elif type == 'del':
                n = log['node']
                m = log['m']
                if m == 'ug':
                    self.ungroup_node(n, d=True)
                else:
                    self.del_node(n, d=True)   
                    
            elif type == 'add':
                n = log['node']
                self.add_node(n, d=True)
                if n.is_group:
                    n.reset_ports()
                    
            elif type == 'disconn':
                p0, p1 = log['ports']
                Port.disconnect(p0, p1, d=True)
                
            elif type == 'conn':
                n0, n1 = log['nodes']
                p0, p1 = log['ports']
                if p0.parent_port:
                    if p0 not in n0.ports:
                        n0.ports.append(p0)
                    if p0.group_node:
                        if p0 not in p0.group_node.ports:
                            p0.group_node.ports.append(p0)
                if p1.parent_port:
                    if p1 not in n1.ports:
                        n1.ports.append(p1)
                    if p1.group_node:
                        if p1 not in p1.group_node.ports:
                            p1.group_node.ports.append(p1)
                Port.new_connection(p0, p1, d=True)
                
            elif type == 'val':
                e = log['e']
                v0, v1 = log['v']
                e.set_value(v1)
                
            elif type == 'transform':
                n = log['node']
                n.transform(form=log['form1'], d=True)
                    
            elif type == 'suppress':
                p = log['p']
                s = log['s']
                p.set_suppressed(s, d=True)
                
            elif type == 'ap':
                n = log['node']
                p = log['port']
                n.ap(p=p)
                
            elif type == 'rp':
                n = log['node']
                p = log['port']
                n.rp(p=p)
                
        self.log_index += 1

#base node stuff--------------------------------------------------------------------

    def reset(self):
        self.delete_nodes(nodes=self.nodes.copy())
        Node.reset()
        
    def load_required_nodes(self):
        t = self.card.type
        if t == 'play':
            if not self.exists('Start'):
                self.get_node('Start')
        elif t == 'item':
            if not self.exists('Can_Use'):
                self.get_node('Can_Use')
        elif t == 'spell':
            if not self.exists('Can_Cast'):
                self.get_node('Can_Cast')
            if not self.exists('Ongoing'):
                self.get_node('Ongoing')
        elif t == 'treasure':
            if not self.exists('End'):
                self.get_node('End')
        elif t == 'landscape':
            if not self.exists('Ongoing'):
                self.get_node('Ongoing')
        elif t == 'event':
            if not self.exists('Ongoing'):
                self.get_node('Ongoing')
            if not self.exists('End'):
                self.get_node('End')
        self.spread()
        self.reset_logs()
     
#wire stuff--------------------------------------------------------------------
        
    def check_wire_break(self):
        breaks = 0
        a = self.anchor
        b = pg.mouse.get_pos()
        for w in self.wires.copy():
            if w.check_break(a, b):
                breaks += 1
        return breaks

#node management stuff--------------------------------------------------------------------

    def add_nodes(self, nodes):
        for n in nodes:
            n.manager = self
            self.add_node(n)

    def add_node(self, n, d=False):
        self.nodes.append(n)
        n.manager = self
        if not d:
            self.add_log({'t': 'add', 'node': n})
             
    def get_node(self, name, val=None, pos=(0, 0), held=True):
        if len(self.nodes) == 50:
            return

        n = Node.from_name(name, val=val, pos=pos)
        
        if held:
            n.rect.center = pg.mouse.get_pos()
            n.start_held()
            
        self.add_node(n)
        return n
        
    def get_group_node(self, name, pos=(0, 0), held=True):
        data = Node.GROUP_DATA[name]
        
        if len(self.nodes) + len(data['nodes']) + 1 > 50:
            return
        
        nodes = unpack(data)
        for n in nodes:
            self.add_node(n)
        n = nodes[-1]
        
        if held:
            n.rect.center = pg.mouse.get_pos()
            n.start_held()
  
        return n
        
    def make_group_node(self, nodes, name='group', pos=(0, 0)):
        n = Group_Node.get_new(nodes, name=name, pos=pos)
        self.add_node(n)
        self.add_log({'t': 'gn', 'gn': n, 'nodes': nodes})
        return n

    def create_new_group_node(self):
        nodes = [n for n in self.get_selected() if not n.is_group]
        if len(nodes) <= 1:
            return
        n = self.make_group_node(nodes)
        return n

    def ungroup_nodes(self):
        nodes = [n for n in self.get_selected() if n.is_group]
        for n in nodes:
            self.ungroup_node(n)
                
    def ungroup_node(self, n, d=False):
        n.ungroup()
        self.del_node(n, method='ug', d=d)

    def delete_nodes(self, nodes=None):
        if nodes is None:
            nodes = self.get_all_selected()
        for n in nodes:
            self.del_node(n)
            
    def del_node(self, n, method='del', d=False):
        n.kill()
        self.nodes.remove(n)
        
        if not d:
            self.add_log({'t': 'del', 'node': n, 'm': method})
            
    def get_required(self, n):
        nodes = []
        for name in n.get_required():
            if not self.exists(name):
                nodes.append(self.get_node(name))
        self.spread(nodes=nodes)

#selection stuff--------------------------------------------------------------------
            
    def get_selected(self):
        return [n for n in Dragger.get_selected() if n.visible]
        
    def get_all_selected(self):
        nodes = self.get_selected()
        for n in nodes:
            if n.is_group:
                nodes += n.nodes
        return nodes
        
#copy and paste stuff--------------------------------------------------------------------
        
    def copy_nodes(self, nodes=None):
        if nodes is None:
            nodes = self.get_selected()
        self.copy_data = pack(nodes)

    def paste_nodes(self):
        data = self.copy_data
        if not data or len(self.nodes) + len(data['nodes']) > 50:
            return
        nodes = unpack(data)
        if nodes:
            move_nodes(nodes, pg.mouse.get_pos())
            for n in nodes:
                self.add_node(n)
                n.start_held() 
        return nodes

#loading stuff--------------------------------------------------------------------

    def load_group_node(self, name, data):
        nodes = unpack(data)
        nodes[-1].set_name(name)
        for n in nodes:
            self.add_node(n)

    def load_save_data(self, data):
        self.reset()
        nodes = unpack(data)
        for n in nodes:
            self.add_node(n)
        self.reset_logs()

#saving stuff--------------------------------------------------------------------

    def get_save_data(self):
        return pack(self.nodes)

    def save(self):
        self.card.save(nodes=self.nodes)
    
    def publish(self):
        self.card.publish(nodes=self.nodes)

    def save_group_node(self):
        gn = None
        nodes = self.get_selected()
        for n in nodes:
            if n.is_group:
                gn = n
                break
        else:
            return

        save_group_node(gn)

#other stuff--------------------------------------------------------------------

    def spread(self, nodes=None):
        if nodes is None:
            nodes = self.nodes
            
        funcs = []
        for n in nodes:
            if n.visible:
                func = mapping.find_visible_chunk(n, [])
                if not any({set(o) == set(func) for o in funcs}):
                    funcs.append(func)

        for nodes in funcs:
            lead = mapping.find_lead(nodes)
            columns = mapping.map_flow(lead, nodes.copy(), {})
            columns = [columns[key][::-1] for key in sorted(columns)]
            
            x = self.body.width // 2
            y = self.body.height // 2
            cy = y
            
            for col in columns:
                r = pg.Rect(0, 0, 0, 0)
                for n in col:
                    n.start_held()
                    n.rect.topleft = (x, y)
                    y += n.background_rect.height + 10
                    r.height += n.background_rect.height + 10
                    
                r.top = col[0].rect.top
                dy = cy - r.centery
                for n in col:
                    n.rect.move_ip(0, dy)

                x += max({n.background_rect.width for n in col}) + 20
                y = self.body.height // 2

        x = 50
        y = 50
            
        for nodes in funcs:
            left = min({n.background_rect.left for n in nodes})
            right = max({n.background_rect.right for n in nodes})
            top = min({n.background_rect.top for n in nodes})
            bottom = max({n.background_rect.bottom for n in nodes})
            r = pg.Rect(left, top, right - left, bottom - top)
            cx, cy = r.center
            r.topleft = (x, y)
            dx = r.centerx - cx
            dy = r.centery - cy
            
            for n in nodes:
                n.rect.move_ip(dx, dy)
                n.drop()
                
            y += r.height + 20
            if y > self.body.height - 100:
                y = 50
                x += r.width + 20
                
    def new_context(self, node=None):
        if node and self.anchor:
            return
            
        self.close_context()
        cm = Context_Manager(self, node=node)
        if cm.height:
            self.elements.insert(1, cm)
            self.cm = cm
        
    def close_context(self):
        if self.cm:
            self.elements.remove(self.cm)
            self.cm = None

#run stuff--------------------------------------------------------------------

    def sub_events(self, events):
        split = 1 if not self.cm else 2
        for e in (self.elements[:split] + self.nodes[::-1] + self.elements[split:]):
            if e.enabled:
                e.events(events)
    
    def events(self):
        events = super().events()
        if not events:
            return

        if kd := events.get('kd'):
            
            if events['ctrl']:

                if kd.key == pg.K_c:
                    self.copy_nodes()
                elif kd.key == pg.K_v:
                    self.paste_nodes()
                elif kd.key == pg.K_q:
                    self.spread()
                elif kd.key == pg.K_z:
                    self.undo_log()
                elif kd.key == pg.K_y:
                    self.redo_log()
                    
                elif kd.key == pg.K_g:
                    self.create_new_group_node()
                elif kd.key == pg.K_u:
                    self.ungroup_nodes()
                
                
            elif kd.key == pg.K_DELETE:
                self.delete_nodes()
                
        if 'mbd_a' in events:
            self.close_context()

        if mbd := events.get('mbd'):
            if mbd.button == 3:
                self.anchor = pg.mouse.get_pos()

        elif mbu := events.get('mbu'):
            if mbu.button == 3:
                if not self.cm:
                    if self.anchor and self.anchor_dist < 2:
                        self.new_context()
                if self.anchor:
                    breaks = self.check_wire_break()
                    self.anchor = None

    def update(self):   
        super().update()

        for n in self.nodes:
            if n.visible:
                n.update()

        self.update_log()
                
    def draw(self):
        self.window.fill(self.fill_color)

        for n in self.nodes:
            if n.visible:
                n.draw(self.window)

        if Port.ACTIVE_PORT:
            Port.ACTIVE_PORT.draw_wire(self.window)
            
        if self.anchor:
            if self.anchor_dist > 2:
                pg.draw.line(
                    self.window,
                    (0, 0, 255),
                    self.anchor,
                    pg.mouse.get_pos(),
                    width=4
                )
                
        super().lite_draw()
       
        pg.display.flip()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            