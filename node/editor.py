import pygame as pg

from .node.node_base import pack, unpack, Port, Node, Group_Node
from .node import mapping
from .compiler import Compiler

from ui.scene.scene import Scene

from .screens.info_sheet import run as run_info_sheet

from ui.element.base.style import Style
from ui.element.elements import Textbox, Button, Check_Box
from ui.element.drag.dragger import Dragger
from ui.element.drag.rect_selector import Rect_Selector
from ui.math import line
from ui.icons.icons import icons

from .element.search_bar import Search_Bar
from .element.node_menu import Node_Menu
from .element.context_manager import Context_Manager
   
def save_group_node(_nodes):
    for node in _nodes[::-1]:
        if node.is_group:
            gn = node
            break
    else:
        return

    import json
    nodes = gn.nodes.copy() + [gn]
    data = pack(nodes)
    with open('data/node/group_nodes.json', 'r') as f:
        group_data = json.load(f)
    group_data[gn.group_name] = data
    with open('data/node/group_nodes.json', 'w') as f:
        json.dump(group_data, f, indent=4)
        
    print('saved')

def get_section(elements, label, scene):
    r = elements[0].rect.unionall([e.padded_rect for e in elements]).inflate(20, 30)
    section = Style(
        size=r.size,
        pos=r.topleft,
        fill_color=scene.fill_color,
        outline_color=(255, 255, 255),
        outline_width=1,
        layer=-1
    )
    
    for e in elements:
        section.add_child(e, current_offset=True)
        
    if label:
        label = Textbox(
            text=label,
            text_size=15,
            fill_color=scene.fill_color,
            left_pad=5,
            right_pad=5
        )
        label.rect.midleft = (section.rect.left + 15, section.rect.top)
        section.add_child(label, current_offset=True)
    
    return section
    
def get_elements(scene):
    body = scene.body
    elements = []
    
    rect_selector = Rect_Selector()
    scene.rect_selector = rect_selector
    elements.append(rect_selector)

    search_bar = Search_Bar(scene)
    elements.append(search_bar)
    
    node_scene = Node_Menu(scene)
    elements.append(node_scene)
    
    button_kwargs = {
        'text_size': 15,
        'size': (150, 25),
        'x_pad': 5,
        'top_pad': 2,
        'centery_aligned': True,
        'hover_color': (100, 100, 100)
    }
    
    icon_kwargs = {
        'font_name': 'icons.ttf',
        'centerx_aligned': True,
        'centery_aligned': True
    }
    
# save section
    
    x = 15
    y = 10
    save_elements = []
    
    save_button = Button.Text_Button(
        text='Save',
        func=scene.builder.save_card,
        **button_kwargs
    )
    save_button.rect.topleft = (x, y)
    save_elements.append(save_button)
    
    save_icon = Textbox(
        text=icons['floppy-disk'],
        text_color=(0, 0, 247),
        **icon_kwargs
    )
    save_button.add_child(save_icon, right_anchor='right', right_offset=-1, centery_anchor='centery')
    save_icon.set_enabled(False) 
    
    y += save_button.rect.height + 3
    
    publish_button = Button.Text_Button(
        text='Publish',
        func=scene.builder.publish_card,
        **button_kwargs
    )
    publish_button.rect.topleft = (x, y)
    save_elements.append(publish_button)
    
    publish_icon = Check_Box(
        value=scene.card.published,
        outline_color=(0, 0, 0),
        outline_width=2
    )
    publish_button.add_child(publish_icon, right_anchor='right', right_offset=-3, centery_anchor='centery', centery_offset=-1)
    publish_icon.set_enabled(False)

    publish_icon.add_event(
        tag='update',
        func=publish_icon.set_value,
        args=[scene.card.get_published]
    )
    
    save_section = get_section(save_elements, 'Save:', scene)
    save_section.rect.topleft = (20, 20)
    elements.append(save_section)
    
# back section

    x = 15
    y = 10
    back_elements = []
    
    back_button = Button.Text_Button(
        text='Back',
        tag='exit',
        **button_kwargs
    )
    back_button.rect.topleft = (x, y)
    back_elements.append(back_button)
    
    back_icon = Textbox(
        text=icons['arrow-left2'],
        text_color=(255, 0, 0),
        **icon_kwargs
    )
    back_button.add_child(back_icon, right_anchor='right', right_offset=-2, centery_anchor='centery')
    back_icon.set_enabled(False) 
    
    y += back_button.rect.height + 3
    
    info_button = Button.Text_Button(
        text='Info Sheet',
        func=run_info_sheet,
        **button_kwargs
    )
    info_button.rect.topleft = (x, y)
    back_elements.append(info_button)
    
    info_icon = Textbox(
        text=icons['file-text'],
        text_color=(255, 255, 0),
        **icon_kwargs
    )
    info_button.add_child(info_icon, right_anchor='right', right_offset=-2, centery_anchor='centery')
    info_icon.set_enabled(False) 
    
    back_section = get_section(back_elements, 'Navigation:', scene)
    back_section.rect.topleft = (save_section.rect.right + 20, 20)
    elements.append(back_section)
    
# do section

    x = 15
    y = 10
    do_elements = []
    
    home_button = Button.Text_Button(
        text='Home',
        **button_kwargs
    )
    home_button.rect.topleft = (x, y)
    do_elements.append(home_button)
    
    home_icon = Textbox(
        text=icons['home3'],
        **icon_kwargs
    )
    home_button.add_child(home_icon, right_anchor='right', right_offset=-2, centery_anchor='centery')
    home_icon.set_enabled(False) 
    
    y += home_button.rect.height + 3
    
    undo_button = Button.Text_Button(
        text='Undo',
        func=scene.undo_log,
        **button_kwargs
    )
    undo_button.rect.topleft = (x, y)
    do_elements.append(undo_button)
    
    undo_icon = Textbox(
        text=icons['undo2'],
        **icon_kwargs
    )
    undo_button.add_child(undo_icon, right_anchor='right', right_offset=-2, centery_anchor='centery')
    undo_icon.set_enabled(False) 
    
    y += undo_button.rect.height + 3
    
    redo_button = Button.Text_Button(
        text='Redo',
        func=scene.redo_log,
        **button_kwargs
    )
    redo_button.rect.topleft = (x, y)
    do_elements.append(redo_button)
    
    redo_icon = Textbox(
        text=icons['redo2'],
        **icon_kwargs
    )
    redo_button.add_child(redo_icon, right_anchor='right', centery_anchor='centery')
    redo_icon.set_enabled(False)
    
    do_section = get_section(do_elements, 'Actions:', scene)
    do_section.rect.topleft = (back_section.rect.right + 20, 20)
    elements.append(do_section)

    return elements[::-1]
    
class Node_Editor(Scene):        
    def __init__(self, card, builder):
        self.card = card
        self.builder = builder
        
        self.nodes = []
        Dragger.set(self.nodes)
        self.cm = None
  
        self.anchor = None

        self.no_logs = True
        self.log = []
        self.logs = []
        self.log_history = []
        self.log_index = -1

        self.copy_data = None
        
        super().__init__(get_elements, fill_color=(32, 32, 40))

        if self.card.node_data:
            self.load_save_data(self.card.node_data)
        if not self.nodes:
            self.load_required_nodes()
        self.no_logs = False

    @property
    def anchor_dist(self):
        return line.distance(self.anchor, pg.mouse.get_pos())
        
    def reset(self):
        self.delete_nodes(nodes=self.nodes.copy())
        Node.reset()
        
    def load_save_data(self, data):
        self.reset()
        nodes = unpack(data, manager=self)
        for n in nodes:
            self.add_node(n)
        
# log stuff

    def reset_logs(self):
        self.logs.clear()
        self.log.clear()
        self.log_index = -1

    def add_log(self, log):
        if self.no_logs:
            return
            
        if self.logs and log['t'] == 'disconn':
            last_log = self.logs[-1]
            if last_log['t'] == 'conn':
                if (
                    set(last_log['ports']) == set(log['ports']) and 
                    set(last_log['nodes']) == set(log['nodes'])
                ):
                    self.logs.pop(-1)
                    return
                    
        self.logs.append(log)
        self.card.set_node_data(self.nodes)
        
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

    def undo_log(self):
        if not self.log_history or self.log_index == -1:
            return
            
        logs = self.log_history[self.log_index]

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
                if n.is_group:
                    n.reset_ports()
                n.rect.topleft = log['pos']
                    
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
        self.card.set_node_data(self.nodes)
        
    def redo_log(self):
        if not self.log_history or self.log_index == len(self.log_history) - 1:
            return
            
        logs = self.log_history[self.log_index + 1]

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
        self.card.set_node_data(self.nodes)

# wire stuff
        
    def check_wire_break(self):
        a = self.anchor
        b = pg.mouse.get_pos()
        for w in Node.WIRES.copy():
            w.check_break(a, b)

# node management stuff

    def add_node(self, n, d=False):
        self.nodes.append(n)
        if not n.manager:
            n.set_manager(self)
             
    def get_node(self, name, val=None, pos=(0, 0), held=True):
        if len(self.nodes) >= 50:
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
        
        nodes = unpack(data, manager=self)
        for n in nodes:
            self.add_node(n)
        n = nodes[-1]
        
        if held:
            n.rect.center = pg.mouse.get_pos()
            n.start_held()
  
        return n

    def create_new_group_node(self):
        nodes = [n for n in self.get_selected()]
        if len(self.nodes) >= 50 or len(nodes) <= 1:
            return
        n = Group_Node.get_new(nodes)
        self.add_node(n)
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
        n.kill(method=method, d=d)
        self.nodes.remove(n)
        
    def get_required(self):
        return Compiler(self.nodes, self.card).missing
        
    def load_required_nodes(self):
        nodes = []
        for name in self.get_required():
            nodes.append(self.get_node(name))
        self.clean_up(nodes=nodes)

# selection stuff
            
    def get_selected(self):
        return [n for n in Dragger.get_selected() if n.visible]
        
    def get_all_selected(self):
        nodes = self.get_selected()
        for n in nodes:
            if n.is_group:
                nodes += n.nodes
        return nodes
        
# copy and paste stuff
        
    def copy_nodes(self, nodes=None):
        if nodes is None:
            nodes = self.get_selected()
        self.copy_data = pack(nodes)

    def paste_nodes(self):
        Dragger.deselect_all()
        
        data = self.copy_data
        if not data or len(self.nodes) + len(data['nodes']) > 50:
            return
        nodes = unpack(data, manager=self)
        
        if nodes:
            
            visible_nodes = [n for n in nodes if n.visible]
            r = visible_nodes[0].rect.unionall([n.rect for n in visible_nodes])
            cx, cy = r.center
            r.center = pg.mouse.get_pos()
            dx = r.centerx - cx
            dy = r.centery - cy
            
            for n in nodes:
                n.rect.move_ip(dx, dy)
                self.add_node(n)
                
                if n.visible:
                    n.start_held() 
                
        return nodes

# other stuff

    def clean_up(self, nodes=None):
        if nodes is None:
            nodes = self.nodes
            
        chunks = []
        for n in self.nodes:
            chunk = set(mapping.find_visible_chunk(n, []))
            if chunk and chunk not in chunks:
                chunks.append(chunk)
        chunks = [sorted(chunk, key=lambda n: n.id) for chunk in chunks]

        for chunk in chunks:
            map = mapping.map_flow(chunk[0], chunk.copy(), {})

            x, y = self.body.center
            space = 5
            
            for column in sorted(map):
                row = [map[column][row] for row in sorted(map[column])]
                for n in row:
                    n.start_held()
                    n.rect.topleft = (x, y)
                    y += n.background_rect.height + space
                    
                r = row[0].background_rect.unionall([n.background_rect for n in row])
                dy = self.body.centery - r.centery
                for n in row:
                    n.rect.move_ip(0, dy)
                
                x += max({n.background_rect.width for n in row}) + (2 * space)
                y = self.body.centery
                
        x = 20
        y = 130
        space = 5
        x_shift = 0
        
        chunks.sort(key=lambda chunk: chunk[0].background_rect.unionall([n.background_rect for n in chunk]).width)

        for chunk in chunks: 
            r = chunk[0].background_rect.unionall([n.background_rect for n in chunk])
            cx, cy = r.center
            r.topleft = (x, y)
            dx = r.centerx - cx
            dy = r.centery - cy
            for n in chunk:
                n.rect.move_ip(dx, dy)
                n.drop()
                
            if r.width > x_shift:
                x_shift = r.width
        
            y += r.height + (2 * space)
            if y > self.body.height - 100:
                y = 130
                x += x_shift + (2 * space)
                x_shift = 0
               
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

# run stuff

    def quit(self):
        if self.builder.ask_save() is not None:
            return super().quit()

    def sub_events(self, events):
        split = 4 if not self.cm else 5
        batch1 = self.elements[:split]
        batch2 = self.elements[split:]
        if batch2[-2].visible:
            batch1.append(batch2.pop(-2))
        for e in (batch1 + self.nodes[::-1] + batch2):
            if e.enabled:
                e.events(events)
    
    def events(self):
        events = super().events()
        if not events:
            return

        if kd := events.get('kd'):
            
            if events['ctrl']:
                
                if kd.key == pg.K_s:
                    self.builder.save_card()
                elif kd.key == pg.K_c:
                    self.copy_nodes()
                elif kd.key == pg.K_v:
                    self.paste_nodes()
                elif kd.key == pg.K_q:
                    self.clean_up()
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
                
        if (mbd := events.get('mbd')):
            self.close_context()
            if not events['clicked'] and mbd.button == 3:
                self.anchor = mbd.pos
        
        elif (mbu := events.get('mbu')):
            if mbu.button == 3:
                if not self.cm:
                    if self.anchor and self.anchor_dist < 2:
                        self.new_context()
                if self.anchor:
                    self.check_wire_break()
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