import json

import pygame as pg

from data.constants import GROUP_DATA_FILE

from . import mapping

from ui.element.base.element import Element
from ui.element.standard.textbox import Textbox
from ui.element.drag.dragger import Dragger
from ui.math import line

from .element.input import Logged_Label_Input as Input

def pack(_nodes):
    d = mapping.find_all_nodes(_nodes)
    nodes = {
        'nodes': d[0],
        'groups': d[1]
    }

    data = {
        'nodes': {},
        'groups': {}
    }
    
    for n in nodes['nodes']:
        node_data = {
            'name': n.__class__.__name__,
            'pos': n.rect.topleft,
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
            'pos': g.rect.topleft,
            'nodes': [n.id for n in g.nodes],
            'rel_node_pos': g.get_rel_node_pos(),
            'visible_ports': g.get_visible_port_data()
        }

    return data
        
def unpack(data, manager=None, map=True):
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
        n = Node.from_name(name, id=id if not map else None, pos=pos)
        n.oid = id
        new_id = n.id
        id_map[id] = new_id
        nodes[new_id] = n
        if form:
            n.tf(form=form)
        if manager:
            n.set_manager(manager)

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
            if parent_port:
                p0.remove_child(p0.label)
                p0.label = None
            p0.added = added
            if connection is not None and port < 0:
                connection = id_map.get(connection)
                if connection is not None:
                    n1 = nodes[connection]
                    p1 = n1.get_port(connection_port)
                    Port.new_connection(p0, p1, force=True)
                        
            if element_value is not None:
                p0.value = element_value

    for id, d in sorted(data['groups'].items(), key=lambda i: int(i[0])):
        id = int(id)
        name = d['name']
        group_nodes = [nodes[id_map[nid]] for nid in d['nodes']]
        ports = [nodes[id_map[nid]].get_port(p) for nid, p in d['visible_ports']]
        pos = d['pos']
        n = Group_Node.get_new(group_nodes, id=id if not map else None, ports=ports, pos=pos)
        n.group_name = name
        n.rel_node_pos = {nodes[id_map[int(nid)]]: pos for nid, pos in d['rel_node_pos'].items()}
        new_id = n.id
        id_map[id] = new_id
        nodes[new_id] = n
        if manager:
            n.set_manager(manager)
        
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
        self.dashed_points = line.segment(self.points)

        self.bad = False
        self.last_pos = (
            self.op.rect.center,
            self.ip.rect.center
        )

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
        start = self.op.rect.center
        end = self.ip.rect.center
        
        ox, oy = start
        ix, iy = end
        
        orect = self.op.parent.background_rect
        irect = self.ip.parent.background_rect
        
        if orect.right < irect.left:
            cx = (orect.right + irect.left) // 2
        else:
            cx = (irect.right + orect.left) // 2
        if orect.bottom < irect.top:
            cy = (orect.bottom + irect.top) // 2
        else:
            cy = (irect.bottom + orect.top) // 2
            
        if ix - Port.SIZE < ox:
                 
            r = orect.union(irect)
            shift = Port.SIZE // 2
            xmax = orect.right + shift

            if r.height > orect.height + irect.height:
                xmin = irect.left - shift
                return (
                    start,
                    (xmax, oy),
                    (xmax, cy),
                    (xmin, cy),
                    (xmin, iy),
                    end
                )
                
            else:
                if orect.right > irect.left:
                    if orect.left < irect.left:
                        xmin = orect.left - shift
                    else:
                        xmin = irect.left - shift
                else:
                    xmin = orect.left - shift
            
                if irect.top == r.top:
                    ymax = r.bottom + shift
                    return (
                        start,
                        (xmax, oy),
                        (xmax, ymax),
                        (xmin, ymax),
                        (xmin, iy),
                        end
                    )
                    
                else:
                    ymin = r.top - shift
                    return (
                        start,
                        (xmax, oy),
                        (xmax, ymin),
                        (xmin, ymin),
                        (xmin, iy),
                        end
                    )

        else:
            return (
                start,
                (cx, oy),
                (cx, iy),
                end
            )
     
    def update(self):
        update_points = False
            
        bad = self.is_bad()
        if self.bad != bad:
            self.bad = bad
            update_points = True
            
        current_pos = (
            self.op.rect.center,
            self.ip.rect.center
        )

        if update_points or current_pos != self.last_pos:
            self.points = self.find_points()
            self.dashed_points = line.segment(self.points)
            
        self.last_pos = current_pos

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
        
    @classmethod
    def get_list_types(cls):
        return list(cls.contains_dict)
        
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
        return str(self.port)
        
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
            self.element.reset_value(value)
            
    def _get_output(self):
        if self.element:
            return self.element.get_output()
        return ''
            
    def get_output(self):
        text = self._get_output()
        return text if not self.node.mark else self.node.mark_text(text, port=self.port)
        
    @property
    def is_flow(self):
        return 'flow' in self.types
 
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
        elif main_type == 'process':
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
        
        if self.port > 0 and self.wire:
            self.wire.draw(surf)
            
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
        with open(GROUP_DATA_FILE, 'r') as f:
            cls.GROUP_DATA = json.load(f)
            
    @classmethod
    def get_categories(cls):
        categories = {}
        for name, n in cls.NODE_DATA.items():
            if hasattr(n, 'cat'):
                cat = n.cat
                subcat = getattr(n, 'subcat', 'base')
                if cat not in categories:
                    categories[cat] = {}
                if subcat not in categories[cat]:
                    categories[cat][subcat] = [name]
                else:
                    categories[cat][subcat].append(name)
                    
        cat = 'group'
        categories[cat] = {}
        for name, data in cls.GROUP_DATA.items():
            subcat = data.get('subcat', 'base')
            if subcat not in categories[cat]:
                categories[cat][subcat] = [name]
            else:
                categories[cat][subcat].append(name)
                
        return categories
        
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
        
    @classmethod
    def from_name(cls, name, id=None, **kwargs):
        return cls.NODE_DATA[name](id if id is not None else cls.get_new_id(), **kwargs)

    def __init__(
        self,
        id,
        pos=(0, 0),
        form=0,
        manager=None,
        **kwargs
    ):
        Element.__init__(self, **kwargs)
        Dragger.__init__(self)

        self.manager = manager
        
        self.nid = id
        self.oid = id
        self.form = form
        self.group_node = None
        self.mark = False
        
        self.ports = None
        self.defaults = {}

        self.rect = pg.Rect(0, 0, Node.WIDTH, Node.WIDTH)
        self.rect.topleft = pos

        self.label = self.get_label()

    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def set_manager(self, manager):
        self.manager = manager
        self.manager.add_log({'t': 'add', 'node': self})
        
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
        self.nid = id
        
    @property
    def color(self):
        return (89, 90, 123)
        
    @property
    def label_color(self):
        if self.is_group:
            return (106, 0, 106)
        elif self.is_func:
            return (193, 0, 61)
        elif self.is_flow:
            return (0, 106, 207)
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
        
    def copy(self):
        return unpack(pack([self]))[0]
        
    def same_group(self, n):
        if n.group_node or self.group_node:
            return n.group_node is self.group_node
        
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
        self.add_child(
            label, 
            top_anchor='top',
            top_offset=label.rect.top - self.rect.top,
            centerx_anchor='centerx'
        )
        
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
        
    def get_raw_image(self, scale=1):
        r = self.background_rect

        w = r.width + Port.SIZE + 4
        h = r.height
        
        surf = pg.Surface((w, h)).convert_alpha()
        surf.fill((0, 0, 0, 0))

        self.rect.bottomleft = (
            (Port.SIZE // 2) + 2,
            h - Node.OUTLINE_SPACE
        )
        self.update_position(all=True)
        self.draw(surf)
        return pg.transform.smoothscale(surf, (w * scale, h * scale))

#writing stuff----------------------------------------------------------------------

    def mark_text(self, text, port=0):
        if not text:
            return text

        mark = f'#<{self.id},{port}>#'
        start_lines = 0
        end_lines = 0
        nl = '\n'
        
        while text[0] == nl:
            text = text[1:]
            start_lines += 1
        
        while text[-1] == nl:
            text = text[:-1]
            end_lines += 1
            
        return f"{(nl * start_lines)}{mark}{text}{mark}{(nl * end_lines)}"

    def _get_text(self):
        return ''
        
    def get_text(self):
        text = self._get_text()
        return text if not self.mark else self.mark_text(text)
        
    def _get_output(self, p):
        return ''
        
    def get_output(self, p):
        text = self._get_output(p)
        return text if not self.mark else self.mark_text(text, port=p)

    def _get_default(self, p):
        return ''
        
    def get_default(self, p):
        text = self.defaults.get(p) or self._get_default(p)
        return text if not self.mark else self.mark_text(text, port=p)
        
    def _get_start(self):
        return ''
        
    def get_start(self):
        text = self._get_start()
        return text if not self.mark else self.mark_text(text)
        
    def _get_end(self):
        return ''
        
    def get_end(self):
        text = self._get_end()
        return text if not self.mark else self.mark_text(text)
        
    def get_input(self):
        input = []
        
        for ip in self.get_input_ports():
            if ip.connection:
                input.append(ip.connection.get_output(ip.connection_port.true_port))
            elif self.defaults.get(ip.port):
                input.append(self.get_default(ip.port))
            elif ip.element:
                input.append(ip.get_output())
            else:
                input.append(self.get_default(ip.port))
                
        return input
        
    def get_input_from(self, p):
        ip = self.get_port(p)
        if ip.connection:
            return ip.connection.get_output(ip.connection_port.true_port)
        elif self.defaults.get(p):
            return self.get_default(p)
        elif ip.element:
            return ip.get_output()
        else:
            return self.get_default(p)
            
    def get_func_out(self):
        header = self.get_text()
        start = self.get_start()
        end = self.get_end()
        nl = '\n'
        return f"{header}{start}{f'...{nl}' if end else ''}{end}"
     
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
            
    def kill(self, method='del', d=False):
        self.clear_connections()
        super().kill()
        
        if self.manager and not d:
            self.manager.add_log({'t': 'del', 'node': self, 'm': method})
        
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
        
    def drop(self, *args, **kwargs):
        dist = super().drop()
        
        if self.manager:
            if any(dist):
                self.manager.add_log({
                    't': 'carry',
                    'node': self,
                    'dist': dist
                })
            
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
        
    def context_click(self):
        return self.get_hit() and not any({p.hit or (p.element.hit if p.element else False) for p in self.ports})
        
    def click_up(self, button):
        if self.manager:
            if button == 3 and self.context_click() and not self.manager.cm:
                self.manager.new_context(node=self)
        
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
    def get_new(cls, nodes, id=None, **kwargs):
        n = cls(id if id is not None else Node.get_new_id(), nodes, **kwargs)
        return n
        
    @classmethod
    def from_data(cls, data):
        return unpack(data)[-1]
        
    @classmethod
    def from_name(cls, name):
        return unpack(Node.GROUP_DATA[name])[-1]
    
    def __init__(self, id, nodes, ports=[], pos=None, **kwargs):
        self.nodes = nodes
        self.visible_ports = []
        super().__init__(id, **kwargs)

        self.set_ports(self.get_group_ports(ports=ports))
        self.set_self_pos()
        self.set_rel_node_pos()
        
        if pos is not None:
            self.pos = pos

    @property
    def is_group(self):
        return True
        
    @property
    def group_name(self):
        return self.label.text
        
    @group_name.setter
    def group_name(self, name):
        self.label.reset_value(name)
        
    def get_label(self):
        label = Input(
            self,
            text=self.get_name(),
        )
        label.rect.center = self.label_rect.center
        self.add_child(label, current_offset=True)
        
        return label
        
    def copy(self):
        nodes = unpack(pack([self]))
        for n in nodes:
            if n.is_group:
                return n
        
    def reset_ports(self):
        self.set_ports(self.get_group_ports(ports=self.visible_ports))
   
    def set_rel_node_pos(self):
        rel_node_pos = {}
        x0, y0 = self.rect.center
        for n in self.nodes:
            x1, y1 = n.rect.center
            rel_node_pos[n] = (x1 - x0, y1 - y0)
        self.rel_node_pos = rel_node_pos
        
    def get_rel_node_pos(self):
        return {n.id: pos for n, pos in self.rel_node_pos.items()}
        
    def get_visible_port_data(self):
        return [(p.node.id, p.port) for p in self.ports]
        
    def get_visible_ports(self):
        return self.ports.copy()
        
    def get_group_ports(self, ports=[]):
        ipp = []
        opp = []
        
        for p in ports:
            if p.port > 0:
                ipp.append(p)
            else:
                opp.append(p)
        
        for n in self.nodes:
            n.group_node = self
            n.turn_off()
            
            for p in n.ports:
                if p not in ports:
                    if not p.suppressed and (not p.connection or (p.connection and p.connection_port.parent not in self.nodes)):
                        if p.port > 0:
                            if p not in ipp:
                                ipp.append(p)
                        elif p not in opp:
                            opp.append(p)
                    else:
                        p.turn_off()

        ipp.sort(key=lambda p: 10 if 'process' in p.types else 11 if 'flow' in p.types else p.port)
        opp.sort(key=lambda p: 10 if 'process' in p.types else 11 if 'flow' in p.types else abs(p.port))
        
        return opp + ipp
        
    def del_port(self, port):
        super().del_port(port)
        if port.parent_port:
            self.set_port_pos()
       
    def set_self_pos(self):
        self.rect.centerx = sum([n.rect.centerx for n in self.nodes]) // len(self.nodes)
        self.rect.centery = sum([n.rect.centery for n in self.nodes]) // len(self.nodes)
        self.set_port_pos()
        
    def set_visible_ports(self):
        self.visible_ports = self.ports.copy()

    def ungroup(self):
        self.set_visible_ports()
        sx, sy = self.rect.center
        for n in self.nodes:
            n.turn_on()
            n.held = False
            n.group_node = None
            for p in n.ports:
                p.turn_on()
            rx, ry = self.rel_node_pos[n]
            n.rect.center = (sx + rx, sy + ry)
            n.set_port_pos()
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

 