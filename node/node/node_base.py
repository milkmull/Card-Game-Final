import json

import pygame as pg

from . import mapping

from ui.math import line
from ui.element.standard.textbox import Textbox
from ui.element.standard.input import Input
from ui.element.drag.dragger import Dragger
from ui.element.base.element import Element

NODE_DATA_PATH = 'data/node/'

def pack(_nodes):
    nodes = {
        'nodes': [],
        'groups': []
    }
    for n in _nodes:
        if n.is_group:
            nodes['groups'].append(n)
        else:
            nodes['nodes'].append(n)
    
    data = {
        'nodes': {},
        'groups': {}
    }
    
    for n in nodes['nodes']:
        node_data = {
            'name': n.__class__.__name__,
            'pos': n.rect.center,
            'contains': getattr(n, 'contains', None),
            'form': n.form
        }
        ports = {}
        for p in n.ports:
            ports[str(p.port)] = {
                'connection': p.connection.id if p.connection else None,
                'connection_port': p.connection_port.port if p.connection_port else None,
                'parent_port': p.parent_port,
                'added': p.added,
                'suppressed': p.suppressed,
                'visible': p.visible,
                'types': p.types,
                'element_value': p.value
            }
        node_data['ports'] = ports
        data['nodes'][str(n.id)] = node_data
        
    for g in nodes['groups']:
        data['groups'][str(g.id)] = {
            'name': g.group_name,
            'pos': g.rect.center,
            'nodes': [n.id for n in g.nodes],
            'rel_node_pos': g.get_rel_node_pos()
        }

    return data
        
def unpack(data):
    if not data:
        return {}
        
    nodes = {}
    id_map = {}

    for id, d in data['nodes'].items():
        id = int(id)
        name = d['name']
        pos = d['pos']
        contains = d['contains']
        form = d['form']
        n = Node.from_name(name, pos=pos)
        new_id = n.id
        id_map[id] = new_id
        nodes[new_id] = n
        if form:
            n.tf(form=form)

    while True:
    
        missed = False
    
        for id, d in data['nodes'].items():
            id = id_map[int(id)]
            n0 = nodes[id]
            ports = d['ports']
            for port in ports:
                connection = ports[port]['connection']
                connection_port = ports[port]['connection_port']
                parent_port = ports[port]['parent_port']
                added = ports[port]['added']
                suppressed = ports[port]['suppressed']
                visible = ports[port]['visible']
                types = ports[port]['types']
                element_value = ports[port]['element_value']
                if added:
                    n0.ap()
                if parent_port is not None:
                    n0.get_port(parent_port).copy()
                port = int(port)
                p0 = n0.get_port(port)
                p0.set_types(types)
                p0.suppressed = suppressed
                p0.visible = visible
                p0.parent_port = parent_port
                p0.added = added
                if connection is not None and port < 0:
                    connection = id_map.get(connection)
                    if connection is not None:
                        n1 = nodes[connection]
                        p1 = n1.get_port(connection_port)
                        if p0 and p1:
                            Port.new_connection(p0, p1, force=True)
                        else:
                            missed = True
                            
                if element_value is not None:
                    p0.value = element_value
      
        if not missed:
            break

    for id, d in data['groups'].items():
        id = int(id)
        name = d['name']
        group_nodes = [nodes[id_map[nid]] for nid in d['nodes']]
        pos = d['pos']
        n = Group_Node.get_new(group_nodes, pos=pos)
        n.group_name = name
        n.rel_node_pos = {nodes[id_map[int(nid)]]: pos for nid, pos in d['rel_node_pos'].items()}
        new_id = n.id
        id_map[id] = new_id
        nodes[new_id] = n
        
    nodes = list(nodes.values())
    for n in nodes:
        n.set_port_pos()
        
    return nodes
     
class Wire:
    def __init__(self, p0, p1):
        if p0.port < 0:
            self.op = p0
            self.ip = p1
        else:
            self.op = p1
            self.ip = p0
        self.op.wire = self
        self.ip.wire = self

        self.points = self.find_points()

        self.bad = False
        self.dashed_points = line.segment(self.points)
        
        self.last_pos_out = self.op.rect.center
        self.last_pos_in = self.ip.rect.center
        
    @property
    def manager(self):
        return self.op.manager
        
    def check_intersect(self, a, b):
        for i in range(len(self.points) - 1):
            c = self.points[i]
            d = self.points[i + 1]
            
            if line.intersect(a, b, c, d):
                return True
                    
    def check_break(self, a, b):
        if self.op.visible:
            if self.check_intersect(a, b):
                self.op.clear()
                return True
                
    def is_bad(self):
        onode = self.op.node
        in_flow = onode.get_in_flow()
        if in_flow:
            if not in_flow.connection:
                return True
            else:
                return in_flow.wire.is_bad()
                
    def clip(self):
        Node.del_wire(self)
        
    def find_points(self): 
        onode = self.op.parent
        inode = self.ip.parent
        
        start = self.op.rect.center
        end = self.ip.rect.center
        
        ox, oy = start
        ix, iy = end

        if onode.rect.right < inode.rect.left:
            cx = (onode.rect.right + inode.rect.left) // 2
        else:
            cx = (inode.rect.right + onode.rect.left) // 2
        if onode.rect.bottom < inode.rect.top:
            cy = (onode.rect.bottom + inode.rect.top) // 2
        else:
            cy = (inode.rect.bottom + onode.rect.top) // 2

        if ix - 10 < ox:
                 
            r = onode.rect.union(inode.rect)

            orect = onode.rect
            irect = inode.rect
            
            oshift = 8
            ishift = 8
           
            xmax = orect.right + oshift

            if r.height - 5 > orect.height + irect.height:
                xmin = irect.left - ishift
                return (start, (xmax, oy), (xmax, cy), (xmin, cy), (xmin, iy), end)
                
            else:

                if orect.right > irect.left:
                    if orect.left < irect.left:
                        xmin = orect.left - oshift
                    else:
                        xmin = irect.left - ishift
                else:
                    xmin = orect.left - oshift
            
                if irect.top == r.top:
                    ymax = r.bottom + oshift
                    return (start, (xmax, oy), (xmax, ymax), (xmin, ymax), (xmin, iy), end)
                else:
                    ymin = r.top - oshift
                    return (start, (xmax, oy), (xmax, ymin), (xmin, ymin), (xmin, iy), end)

        else:
            return (start, (cx, oy), (cx, iy), end)
        
    def update(self):
        update_points = False
            
        bad = self.is_bad()
        if self.bad != bad:
            self.bad = bad
            self.update_points = True

        current_pos_out = self.op.rect.center
        current_pos_in = self.ip.rect.center
        if update_points or (self.last_pos_out != current_pos_out or self.last_pos_in != current_pos_in):
            self.points = self.find_points()
            self.dashed_points = line.segment(self.points)
        self.last_pos_out = current_pos_out
        self.last_pos_in = current_pos_in

    def draw(self, surf):
        self.update()
        if self.op.visible and self.ip.visible:
            if not self.bad:
                pg.draw.lines(surf, self.op.color, False, self.points, width=3)
            else:
                for i in range(0, len(self.dashed_points) - 1, 2):
                    p0 = self.dashed_points[i]
                    p1 = self.dashed_points[i + 1]
                    pg.draw.line(surf, self.op.color, p0, p1, width=3)

class Port(Element):
    ACTIVE_PORT = None
    CLOSE_ACIVE_PORT = False
    
    SIZE = 10
    ELEMENT_SPACING = 6
    
    comparison_types = [
        'bool',
        'num',
        'string',
        'ps',
        'cs',
        'ns',
        'ss', 
        'bs',
        'player',
        'card'
    ]
    contains_dict = {
        'ps': 'player',
        'cs': 'card',
        'ns': 'num',
        'ss': 'string',
        'bs': 'bool'
    }
    desc_cache = {}

    @classmethod
    def get_comparison_types(cls):
        return cls.comparison_types.copy()
        
    @staticmethod
    def new_connection(p0, p1, force=False, d=False):
        n0 = p0.node
        n1 = p1.node
        
        if (any({t in p1.types for t in p0.types}) or force) and p0.is_output() != p1.is_output():
        
            p0.connect(n1, p1)
            p1.connect(n0, p0)
            
            local_funcs, scope_output, loop_output = mapping.check_bad_connection(n0, n1)
            can_connect0 = n0.can_connect(p0, n1, p1)
            can_connect1 = n1.can_connect(p1, n0, p0)
            if not can_connect0 or not can_connect1 or (len(local_funcs) > 1 or scope_output or loop_output):
                p0.clear()
                p1.clear()
                
            else:
                Node.new_wire(p0, p1)
                
                if p0.manager and not d:
                    p0.manager.add_log({
                        't': 'conn',
                        'nodes': (n0, n1),
                        'ports': (p0, p1)
                    })
    
    @staticmethod
    def disconnect(p0, p1, d=False):
        n0 = p0.node
        n1 = p1.node
        
        if p0.manager and not d:
            p0.manager.add_log({
                't': 'disconn',
                'ports': (p0, p1),
                'nodes': (n0, n1)
            })
            
        if p0.wire:
            p0.wire.clip()
        if p1.wire:
            p1.wire.clip()
            
        p0.connection = None
        p0.connection_port = None
        p0.wire = None
        
        p1.connection = None
        p1.connection_port = None
        p1.wire = None
            
    @classmethod
    def set_active_port(cls, port):
        cls.ACTIVE_PORT = port
            
    @classmethod
    def close_active_port(cls):
        cls.ACTIVE_PORT = None
        cls.CLOSE_ACIVE_PORT = False

    def __init__(self, port, types, description=None):
        super().__init__()
        
        self.port = port
        self.types = types
     
        self.parent_port = None
        self.node = None
        self.added = False
        
        self.element = None
       
        self.connection = None
        self.connection_port = None
        
        self.wire = None
        self.suppressed = False
        
        self.rect = pg.Rect(0, 0, Port.SIZE, Port.SIZE)

        self.label = Textbox(
            text=description if description else self.types[0] if self.types else '',
            text_size=15,
            size=(Node.WIDTH - 18, 0),
            inf_width=False,
            inf_height=True,
            auto_fit=True
        )
        self.label.set_enabled(False)
        
        if self.port > 0:
            self.label.rect.topleft = (self.rect.right + 5, self.rect.y)
        else:
            self.label.rect.topright = (self.rect.left - 5, self.rect.y)
        self.add_child(self.label, current_offset=True)
        
    def __str__(self):
        data = {
            'port': self.port,
            'connection_id': getattr(self.connection, 'id', None),
            'connection_node': getattr(self.connection, 'name', None),
            'connection_port': getattr(self.connection_port, 'port', None)
        }
        return json.dumps(data, indent=4)
        
    def __repr__(self):
        return str(self)
        
    @property
    def manager(self):
        return self.node.manager
        
    @property
    def group_node(self):
        return self.node.group_node
        
    @property
    def current_node(self):
        return self.parent
        
    @property
    def true_port(self):
        if self.parent_port is not None:
            return self.parent_port
        return self.port
        
    @property
    def value(self):
        if self.element:
            return self.element.value
            
    @value.setter
    def value(self, value):
        if self.element:
            self.element.set_value(value)
            
    def get_output(self):
        if self.element:
            return self.element.get_output()
        return ''
 
    def set_element(self, e):
        self.clear_element()
        self.update_position()
        if self.port > 0:
            e.rect.topleft = (
                self.label.rect.left,
                self.label.rect.bottom + Port.ELEMENT_SPACING
            )
        elif self.port < 0:
            e.rect.topright = (
                self.label.rect.right,
                self.label.rect.bottom + Port.ELEMENT_SPACING
            )
        self.add_child(e, current_offset=True)
        self.element = e
    
    def clear_element(self):
        self.remove_child(self.element)
        self.element = None
    
    def set_node(self, node):
        if not node.is_group:
            self.node = node

    def copy(self):
        n = self.node
        p = Port(self.node.get_new_output_port(), self.types)
        p.parent_port = self.port
        p.node = n
        p.rect = self.rect.copy()
        n.ports.append(p)
        if n.group_node:
            n.group_node.ports.append(p)
            n.group_node.add_child(p, current_offset=True)
        else:
            n.add_child(p, current_offset=True)
        return p

#visibility stuff-------------------------------------------------------------------

    def set_suppressed(self, suppressed, d=False):
        if self.suppressed != suppressed:
            if not self.suppressed:
                self.clear()
            self.suppressed = suppressed
            
            if self.manager and not d:
                self.manager.add_log({
                    't': 'suppress',
                    's': suppressed,
                    'p': self
                })

    def get_parent_port(self):
        if self.parent_port is not None:
            return self.node.get_port(self.parent_port)
        
#type stuff-------------------------------------------------------------------
        
    def set_types(self, types):
        self.types.clear()
        self.types += types
        
    def update_types(self, types):
        if not self.check_connection(types):
            self.clear()
        self.set_types(types)
        
    def add_type(self, type):
        self.types.append(type)
        
    def remove_type(self, type):
        if type in self.types:
            self.types.remove(type)
            
    def clear_types(self):
        self.types.clear()
        self.clear()
        
    def get_contains(self):
        return Port.contains_dict.get(self.types[0])
        
    def check_connection(self, types):
        if not self.connection:
            return True
        return any({t in types for t in self.connection_port.types})

#connection stuff-------------------------------------------------------------------

    def connect(self, connection, connection_port):
        self.set_suppressed(False)
        self.connection = connection_port.node
        self.connection_port = connection_port
        
    def clear(self):
        if self.connection:
            p0 = self
            p1 = self.connection_port
            Port.disconnect(p0, p1)
            
    def is_output(self):
        return self.port < 0
        
    def is_input(self):
        return self.port > 0

    def left_click(self):
        if not self.connection:
            self.set_suppressed(False)
            Port.set_active_port(self)
        elif 'flow' not in self.types and self.port < 0:
            Port.set_active_port(self.copy())
            
    def click_up(self, button):
        if self.hit:
            
            if button == 1:
                ap = Port.ACTIVE_PORT

                if ap and ap.node is not self.node:
                    if not self.connection:
                        Port.new_connection(ap, self)
                        Port.close_active_port()
                    elif 'flow' not in self.types and self.port < 0:
                        Port.new_connection(self.copy(), ap.active_port)
                        Port.close_active_port()

            elif button == 3:
                self.node.suppress_port(self)
                
    def events(self, events):
        super().events(events)
        
        if events.get('mbu'):
            Port.CLOSE_ACIVE_PORT = True
        elif Port.CLOSE_ACIVE_PORT:
            Port.CLOSE_ACIVE_PORT = False
            Port.ACTIVE_PORT = None
        
    def update(self):
        if Port.ACTIVE_PORT is not self and (self.parent_port and not self.connection):
            self.node.del_port(self)
            if self.group_node:
                self.group_node.del_port(self)
            return

        super().update()
        
#draw stuff--------------------------------------------------------------------------
        
    @property
    def color(self):
        if not self.types:
            return (0, 0, 0)
        main_type = self.types[0]
        if main_type == 'bool':
            return (255, 255, 0)
        elif main_type == 'player':
            return (255, 0, 0)
        elif main_type in ('cs', 'ps', 'ns', 'ss', 'bs'):
            return (0, 255, 0)
        elif main_type == 'log':
            return (255, 128, 0)
        elif main_type == 'num':
            return (0, 0, 255)
        elif main_type == 'string':
            return (255, 0, 255)
        elif main_type == 'card':
            return (145, 30, 180)
        elif main_type == 'split':
            return (128, 128, 128)
        elif main_type == 'flow':
            return (255, 255, 255)
        else:
            return (100, 100, 100)

    @property
    def contains_color(self):
        if 'ps' in self.types and 'cs' in self.types:
            return (0, 255, 0)
        elif 'ps' in self.types:
            return (255, 0, 0)
        elif 'cs' in self.types:
            return (145, 30, 180)
        elif 'ns' in self.types:
            return (0, 0, 255)
        elif 'ss' in self.types:
            return (255, 0, 255)
        elif 'bs' in self.types:
            return (255, 255, 0)
        else:
            return (0, 255, 0)

    def draw(self, surf):
        if getattr(self.parent_port, 'visible', False):
            return
        
        r = self.rect.width // 2 if not self.suppressed else 2
        
        pg.draw.circle(
            surf, (0, 0, 0),
            self.rect.center,
            r + 2
        )
        
        pg.draw.circle(
            surf,
            self.color,
            self.rect.center,
            r
        )

        if not self.suppressed and self.get_contains():
            pg.draw.circle(
                surf,
                self.contains_color,
                self.rect.center,
                r - 2
            )

        super().draw(surf)
            
    def draw_wire(self, surf):
        pg.draw.line(
            surf,
            self.color,
            self.rect.center,
            pg.mouse.get_pos(),
            width=3
        )

class Node(Dragger, Element):
    cat = 'base'
    subcat = 'base'

    LABEL_HEIGHT = 20
    OUTLINE_SPACE = 3
    PORT_SPACING = 8
    WIDTH = 150

    WIRES = []
    
    ID = 0
    NODE_DATA = {}
    GROUP_DATA = {}

    @classmethod
    def get_subclasses(cls):
        sc = cls.__subclasses__()
        sc.remove(Group_Node)
        return sc
        
    @classmethod
    def set_node_data(cls):
        subclasses = cls.get_subclasses()
        for subcls in subclasses:
            cls.NODE_DATA[subcls.__name__] = subcls
          
    @classmethod
    def set_group_data(cls):
        with open(f'{NODE_DATA_PATH}group_nodes.json', 'r') as f:
            cls.GROUP_DATA = json.load(f)
        
    @classmethod
    def new_wire(cls, p0, p1):
        cls.WIRES.append(Wire(p0, p1))
        
    @classmethod
    def del_wire(cls, wire):
        if wire in cls.WIRES:
            cls.WIRES.remove(wire)
        
    @classmethod
    def get_new_id(cls):
        id = cls.ID
        cls.ID += 1
        return id
        
    @classmethod
    def reset(cls):
        Port.close_active_port()
        cls.WIRES.clear()
        cls.ID = 0
        Dragger.reset()
        
    @classmethod
    def from_name(cls, name, **kwargs):
        return cls.NODE_DATA[name](Node.get_new_id(), **kwargs)

    def __init__(
        self,
        id,
        val=None,
        pos=(0, 0),
        form=0,
        manager=None,
        **kwargs
    ):
        Element.__init__(self, **kwargs)
        Dragger.__init__(self)

        self.manager = manager
        
        self.nid = id
        self.val = val
        self.form = form
        self.group_node = None

        self.rect = pg.Rect(0, 0, Node.WIDTH, Node.WIDTH)
        self.rect.center = pos

        self.label = self.get_label()

    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def set_manager(self, manager):
        self.manager = manager
        
    @property
    def name(self):
        return type(self).__name__
        
    def get_name(self):
        return self.name.replace('_', ' ')
        
    @property
    def id(self):
        return self.nid
        
    @id.setter
    def id(self, id):
        pass
        
    @property
    def color(self):
        return (89, 90, 123)
        
    @property
    def label_color(self):
        if self.is_func:
            return (193, 0, 61)
        elif self.is_flow:
            return (0, 106, 207)
        elif self.is_group:
            return (106, 0, 106)
        return (0, 106, 0)

    @property
    def label_rect(self):
        return pg.Rect(
            self.rect.x,
            self.rect.y - Node.LABEL_HEIGHT - Node.OUTLINE_SPACE,
            self.rect.width,
            Node.LABEL_HEIGHT
        )
        
    @property
    def background_rect(self):
        return pg.Rect(
            self.rect.x - Node.OUTLINE_SPACE,
            self.rect.y - (2 * Node.OUTLINE_SPACE) - Node.LABEL_HEIGHT,
            self.rect.width + (2 * Node.OUTLINE_SPACE),
            self.rect.height + (3 * Node.OUTLINE_SPACE) + Node.LABEL_HEIGHT
        )

    @property
    def is_group(self):
        return False

    @property
    def is_func(self):
        return self.tag == 'func'
        
    @property
    def is_flow(self):
        return any({'flow' in p.types for p in self.ports})

    def set_ports(self, ports):
        self.ports = ports
        self.set_port_pos()
        
    def get_required(self):
        return []
        
#image and element stuff-------------------------------------------------------------------
               
    def get_label(self):
        label = Textbox(
            text=self.get_name(),
            text_color=(255, 255, 255),
            size=self.label_rect.size,
            inf_width=False,
            centerx_aligned=True,
            centery_aligned=True
        )
        label.set_enabled(False)
        label.rect.center = self.label_rect.center
        self.add_child(label, current_offset=True)
        
        return label
               
    def set_port_pos(self):
        ip = self.get_input_ports()
        op = self.get_output_ports()
        ex = []
        for p in op.copy():
            if (not self.is_group and p.parent_port) or (self.is_group and getattr(p.parent_port, 'visible', False)):
                op.remove(p)
                ex.append(p)

        y = self.rect.y + Node.PORT_SPACING * 2
        
        for i, p in enumerate(ip + op):
            p.set_node(self)
            p.rect.center = (self.rect.x if p.port > 0 else self.rect.right, y)
            p.layer = -i
            self.add_child(p, current_offset=True)
                
            y += p.total_rect.height + Node.PORT_SPACING
                
        for p in ex:
            p.set_node(self)
            p.rect.center = p.get_parent_port().rect.center
            self.add_child(p, current_offset=True)
            
        tl = self.rect.topleft
        self.rect.width = self.WIDTH
        self.rect.height = y - self.rect.y
        self.rect.topleft = tl

#writing stuff----------------------------------------------------------------------

    def get_text(self):
        return ''
        
    def get_output(self, p):
        return ''
        
    def get_dec(self):
        return ''
        
    def get_default(self, p):
        return ''
        
    def get_start(self):
        return ''
        
    def get_end(self):
        return ''
        
    def get_input(self):
        input = []
        
        for ip in self.get_input_ports():
            if ip.connection:
                input.append(ip.connection.get_output(ip.connection_port.true_port))
            elif ip.element:
                input.append(ip.get_output())
            else:
                input.append(self.get_default(ip.port))
                
        return input
        
    def get_input_from(self, p):
        ip = self.get_port(p)
        if ip.connection:
            return ip.connection.get_output(ip.connection_port.true_port)
        elif ip.element:
            return ip.get_output()
        else:
            return self.get_default(ip.port)
     
#port stuff-------------------------------------------------------------------

    def get_port(self, num):
        for p in self.ports:
            if p.port == num:
                return p
        
    def get_input_ports(self):
        return [p for p in self.ports if p.port > 0]
    
    def get_output_ports(self):
        return [p for p in self.ports if p.port < 0]
    
    def get_extra_ports(self):
        return [p for p in self.ports if p.parent_port is not None]
        
    def get_new_input_port(self):
        return max({p.port for p in self.get_input_ports()}, default=0) + 1
        
    def get_new_output_port(self):
        return min({p.port for p in self.get_output_ports()}, default=0) - 1
        
    def get_in_flow(self):
        for ip in self.get_input_ports():
            if 'flow' in ip.types:
                return ip
            
    def clear_connections(self):
        for p in self.ports.copy(): 
            p.clear()
            
    def kill(self):
        self.clear_connections()
        super().kill()
        
    def del_port(self, port):
        self.ports.remove(port)
        self.remove_child(port)
        
    def suppress_port(self, port):
        port.set_suppressed(not port.suppressed)
        for p in self.get_extra_ports():
            if port.port == p.parent_port:
                p.set_suppressed(not p.suppressed)

    def can_connect(self, p0, n1, p1):
        return True

    def add_port(self):
        p = self.ap()
        if p:
            p.added = True
            
            if self.manager:
                self.manager.add_log({
                    't': 'ap',
                    'node': self,
                    'port': p
                })
        
    def remove_port(self):
        p = self.rp()
        if p and self.manager:
            self.manager.add_log({
                't': 'rp',
                'node': self,
                'port': p
            })
        
#input stuff-------------------------------------------------------------------
        
    def transform(self, form=None, d=False):
        self.clear_connections()
        
        if d or not self.manager:
            self.tf(form=form)
            
        elif not d:
            log = {
                't': 'transform',
                'node': self,
                'form0': self.form
            }
            self.manager.add_log(log)
            self.tf(form=form)
            log['form1'] = self.form
            
    def get_hit(self):
        return self.background_rect.collidepoint(pg.mouse.get_pos())
        
    def update(self):
        super().update()
        self.connection_update()
        
    def connection_update(self):
        pass
        
#draw stuff-------------------------------------------------------------------
        
    def draw(self, surf):
        pg.draw.rect(
            surf,
            (0, 0, 0) if not self.selected else (255, 0, 0),
            self.background_rect,
            border_radius=10
        )
        
        pg.draw.rect(
            surf,
            self.label_color,
            self.label_rect,
            border_top_left_radius=5,
            border_top_right_radius=5
        )
        
        pg.draw.rect(
            surf,
            self.color,
            self.rect,
            border_bottom_left_radius=5,
            border_bottom_right_radius=5
        )

        super().draw(surf)
        
class Group_Node(Node):
    @classmethod
    def get_new(cls, nodes, **kwargs):
        n = cls(Node.get_new_id(), nodes, **kwargs)
        return n
        
    @classmethod
    def from_data(cls, data):
        return unpack(data)[-1]
        
    @classmethod
    def from_name(cls, name):
        return unpack(Node.GROUP_DATA[name])[-1]
    
    def __init__(self, id, nodes, **kwargs):
        self.nodes = nodes
        self.port_mem = {}
        super().__init__(id, **kwargs)

        self.set_ports(self.get_group_ports(nodes))
        self.set_self_pos()
        self.set_rel_node_pos()

    @property
    def is_group(self):
        return True
        
    @property
    def group_name(self):
        return self.label.text
        
    @group_name.setter
    def group_name(self, name):
        self.label.set_text(name)
        
    def get_label(self):
        label = Input(
            text=self.get_name(),
            text_color=(255, 255, 255),
            size=self.label_rect.size,
            inf_width=False,
            centerx_aligned=True,
            centery_aligned=True,
            fill_color=None
        )
        label.rect.center = self.label_rect.center
        self.add_child(label, current_offset=True)
        
        setattr(label, 'last_text', label.text)
        def close(self, label):
            if label.text != label.last_text:
                self.manager.add_log({
                    't': 'val',
                    'e': label,
                    'v': (label.last_text, label.text)
                })
                label.last_text = label.text
        label.add_event(
            tag='close',
            func=close,
            args=[self, label]
        )
        
        return label
        
    def reset_ports(self):
        self.ports = self.get_group_ports(self.nodes)
        self.set_port_pos()
        
    def recall_port_mem(self):
        for p, visible in self.port_mem.items():
            p.set_visible(visible)
   
    def set_rel_node_pos(self):
        rel_node_pos = {}
        x0, y0 = self.rect.center
        for n in self.nodes:
            x1, y1 = n.rect.center
            rel_node_pos[n] = (x1 - x0, y1 - y0)
        self.rel_node_pos = rel_node_pos
        
    def get_rel_node_pos(self):
        return {n.id: pos for n, pos in self.rel_node_pos.items()}
        
    def get_group_ports(self, nodes):
        ipp = []
        opp = []
        
        for n in nodes:
            n.group_node = self
            n.turn_off()
            
            for ip in n.get_input_ports():
                if (not ip.suppressed or (ip.suppressed and self.port_mem.get(ip, False))) and ip.connection not in nodes:
                    ipp.append(ip)
                else:
                    ip.turn_off()
                    
            for op in n.get_output_ports():
                if (not op.suppressed or (op.suppressed and self.port_mem.get(op, False))) and op.connection not in nodes:
                    opp.append(op)
                else:
                    op.turn_off()

        ipp.sort(key=lambda p: p.port if 'flow' not in p.types else 10)
        opp.sort(key=lambda p: abs(p.port) if 'flow' not in p.types else 10)
        ports = opp + ipp
        
        return ports
        
    def del_port(self, port):
        super().del_port(port)
        if port.parent_port:
            self.set_port_pos()
       
    def set_self_pos(self):
        self.rect.centerx = sum([n.rect.centerx for n in self.nodes]) // len(self.nodes)
        self.rect.centery = sum([n.rect.centery for n in self.nodes]) // len(self.nodes)
        self.set_port_pos()
        
    def set_port_mem(self):
        self.port_mem.clear()
        for n in self.nodes:
            for p in n.ports:
                self.port_mem[p] = p.visible

    def ungroup(self):
        self.set_port_mem()
        sx, sy = self.rect.center
        for n in self.nodes:
            n.turn_on()
            n.group_node = None
            for p in n.ports:
                p.turn_on()
            rx, ry = self.rel_node_pos[n]
            n.rect.center = (sx + rx, sy + ry)
            n.set_port_pos()
            n.drop()
        self.ports.clear()
        
    def new_output_port(self, parent):
        p = parent.copy()
        self.add_child(p, current_offset=True)
        self.ports.append(p)
        return p
        
    def update(self):
        for n in self.nodes:
            n.connection_update()
        super().update() 

 