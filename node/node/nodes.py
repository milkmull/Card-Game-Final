import pygame as pg

from data.constants import (
    SORTED_NAMES_DICT,
    TAGS_DICT,
    TYPES_DICT,
    DECKS_DICT,
    REQUESTS_DICT,
    LOGS_DICT,
    LOG_KEYS_DICT,
    EVENTS_DICT
)

from . import mapping
from .node_base import Node, Port

from ui.element.elements import Textbox, Input
from .get_elements import (
    set_input_element,
    set_check_element,
    set_dropdown_element,
    get_transform_button,
    get_ar_buttons
)

class Start(Node):
    cat = 'func'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs)
        
        self.set_ports([
            Port(-1, ['flow'])
        ])
        
    def _get_start(self):
        return '\t\tself.reset()\n'
        
    def _get_text(self):
        return '\n\tdef start(self, player):\n'
        
class End(Node):
    cat = 'func'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs)
        
        self.set_ports([
            Port(-1, ['flow'])
        ])
        
    def _get_text(self):
        return '\n\tdef end(self, player):\n'
   
class If(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description='condition'),
            Port(2, ['flow']),
            Port(-1, ['split', 'flow']),
            Port(-2, ['flow'])
        ])
            
        
    def _get_default(self, p):
        if p == 1:
            return 'True'
        
    def _get_text(self):
        text = 'if {0}:\n'.format(*self.get_input())   
        return text
        
class Elif(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description='condition'),
            Port(2, ['flow']),
            Port(-1, ['split', 'flow']),
            Port(-2, ['flow'])
        ])

    def can_connect(self, p0, n1, p1):
        if p0.port == 2:
            return isinstance(n1, (If, Elif))
        return True
 
    def _get_default(self, p):
        if p == 1:
            return 'True'
        
    def _get_text(self):
        text = 'elif {0}:\n'.format(*self.get_input())   
        return text
        
class Else(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['flow']),
            Port(-1, ['split', 'flow']),
            Port(-2, ['flow'])
        ])
        
    def can_connect(self, p0, n1, p1):
        if p0.port == 2:
            return isinstance(n1, (If, Elif))
        return True
        
    def _get_text(self):
        text = 'else:\n'  
        return text
 
class If_Else(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='if true'),
            Port(2, ['num'], description='if false'),
            Port(3, Port.get_comparison_types()),
            Port(-1, ['num'], description='out')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        get_transform_button(self)
   
    def tf(self, form=None):
        ip1 = self.get_port(1)
        ip2 = self.get_port(2)
        op = self.get_port(-1)
        
        if form == 1 or (form is None and 'num' in ip1.types):
            ip1.set_types(['string'])
            set_input_element(ip1, 'string')
            ip2.set_types(['string'])
            set_input_element(ip2, 'string')
            op.set_types(['string'])
            self.form = 1
        elif form == 2 or (form is None and 'string' in ip1.types):
            ip1.set_types(['player'])
            ip1.clear_element()
            ip2.set_types(['player'])
            ip2.clear_element()
            op.set_types(['player'])
            self.form = 2
        elif form == 3 or (form is None and 'player' in ip1.types):
            ip1.set_types(['card'])
            ip1.clear_element()
            ip2.set_types(['card'])
            ip2.clear_element()
            op.set_types(['card'])
            self.form = 3
        elif form == 0 or (form is None and 'card' in ip1.types):
            ip1.set_types(['num'])
            set_input_element(ip1, 'num')
            ip2.set_types(['num'])
            set_input_element(ip2, 'num')
            op.set_types(['num'])
            self.form = 0
            
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1 or p == 2:
            return '1'
        elif p == 3:
            return 'True'
        
    def _get_output(self, p):
        text = '({0} if {2} else {1})'.format(*self.get_input())   
        return text
 
class Bool(Node):
    cat = 'boolean'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['bool'])
        ])
        
        set_check_element(self.get_port(-1), True)
        self.set_port_pos()

    def _get_output(self, p):
        return self.get_port(-1).get_output()
        
class Num(Node):
    cat = 'numeric'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['num'])
        ])
        
        set_input_element(self.get_port(-1), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        return '0'

    def _get_output(self, p):
        return self.get_port(-1).get_output()
        
class String(Node):
    cat = 'string'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['string'])
        ])
        
        set_input_element(self.get_port(-1), 'string')
        self.set_port_pos()
        
    def _get_default(self, p):
        return "''"
        
    def _get_output(self, p):
        return self.get_port(-1).get_output()
 
class Code(Node):
    cat = 'flow'
    subcat = 'other'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['string']),
            Port(2, ['flow']),
            Port(-1, ['flow'])
        ])

        set_input_element(self.get_port(1), 'code')
        self.set_port_pos()
        
    def _get_text(self):
        val = self.get_port(1).value
        if 'import' in val:
            val = 'raise ValueError'
        return f"{val}\n"

class And(Node):
    cat = 'boolean'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description='x'),
            Port(2, Port.get_comparison_types(), description='y'),
            Port(-1, ['bool'], description='x and y')
        ])
        
    def _get_default(self, p):
        return 'True'
        
    def _get_output(self, p):
        text = '({} and {})'.format(*self.get_input())     
        return text
        
class Or(Node):
    cat = 'boolean'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description='x'),
            Port(2, Port.get_comparison_types(), description='y'),
            Port(-1, ['bool'], description='x or y')
        ])
        
    def _get_default(self, p):
        return 'True'
        
    def _get_output(self, p):
        text = '({} or {})'.format(*self.get_input())     
        return text
        
class Not(Node):
    cat = 'boolean'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description='x'),
            Port(-1, ['bool'], description='not x')
        ])
        
    def _get_default(self, p):
        return 'True'

    def _get_output(self, p):
        text = '(not {})'.format(*self.get_input())    
        return text
        
class Equal(Node):
    cat = 'boolean'
    subcat = 'numeric'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        types = Port.get_comparison_types()
        types = types[1:] + [types[0], 'string']
        self.set_ports([
            Port(1, types, description='x'),
            Port(2, types.copy(), description='y'),
            Port(-1, ['bool'], description='x == y')
        ])
        
    def _get_default(self, p):
        ip = self.get_port(1)
        if 'num' in ip.types:
            return '1'
        elif 'string' in ip.types:
            return "''"
        elif 'bool' in ip.types:
            return 'True'
        elif 'player' in ip.types:
            return 'player'
        elif 'card' in ip.types:
            return 'self'
        else:
            return '[]'

    def _get_output(self, p):
        text = '({} == {})'.format(*self.get_input())    
        return text
      
class Greater(Node):
    cat = 'boolean'
    subcat = 'numeric'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='x'),
            Port(2, ['num'], description='y'),
            Port(-1, ['bool'], description='x > y')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        return '0'

    def _get_output(self, p):
        text = '({0} > {1})'.format(*self.get_input())    
        return text
        
class Less(Node):
    cat = 'boolean'
    subcat = 'numeric'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='x'),
            Port(2, ['num'], description='y'),
            Port(-1, ['bool'], description='x < y')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        return '0'

    def _get_output(self, p):
        text = '({0} < {1})'.format(*self.get_input())    
        return text
     
class Max(Node):
    cat = 'numeric'
    subcat = 'statistic'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['ns'], description='[0, 1, 2...]'),
            Port(-1, ['num'], description='max value')
        ])
        
    def _get_default(self, p):
        return '[]'

    def _get_output(self, p):
        text = 'max({0}, 0)'.format(*self.get_input())    
        return text
        
class Min(Node):
    cat = 'numeric'
    subcat = 'statistic'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['ns'], description='[0, 1, 2...]'),
            Port(-1, ['num'], description='min value')
        ])
        
    def _get_default(self, p):
        return '[]'

    def _get_output(self, p):
        text = 'min({0}, 0)'.format(*self.get_input())    
        return text
     
class Add(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='x'),
            Port(2, ['num'], description='y'),
            Port(-1, ['num'], description='x + y')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        return '0'
        
    def _get_output(self, p):
        return '({} + {})'.format(*self.get_input())
        
class Incriment(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='x'),
            Port(-1, ['num'], description='x + 1')
        ])
        
    def _get_default(self, p):
        return '0'
        
    def _get_output(self, p):
        return '({} + 1)'.format(*self.get_input())
        
class Decriment(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='x'),
            Port(-1, ['num'], description='x - 1')
        ])
        
    def _get_default(self, p):
        return '0'
        
    def _get_output(self, p):
        return '({} - 1)'.format(*self.get_input())
        
class Subtract(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='x'),
            Port(2, ['num'], description='y'),
            Port(-1, ['num'], description='x - y')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        return '0'
        
    def _get_output(self, p):
        return '({0} - {1})'.format(*self.get_input())
        
class Multiply(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='x'),
            Port(2, ['num'], description='y'),
            Port(-1, ['num'], description='x * y')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        return '0'
        
    def _get_output(self, p):
        return '({0} * {1})'.format(*self.get_input())
        
class Negate(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='x'),
            Port(-1, ['num'], description='-x')
        ])
        
    def _get_default(self, p):
        return '0'
        
    def _get_output(self, p):
        return '(-1 * {0})'.format(*self.get_input())
        
class Divide(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='x'),
            Port(2, ['num'], description='y'),
            Port(-1, ['num'], description='x / y')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        return str(p)
        
    def _get_output(self, p):
        return '({0} // {1})'.format(*self.get_input())
  
class Exists(Node):
    cat = 'boolean'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
            
        self.set_ports([
            Port(1, ['player', 'card'], description='x'),
            Port(-1, ['bool'], description='x is not None')
        ])
        
    def _get_default(self, p):
        return '1'
        
    def _get_output(self, p):
        return '({0} is not None)'.format(*self.get_input())
  
class For(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, ['cs', 'ps', 'ns', 'ss', 'bs'], description='list'),
            Port(2, ['flow']),
            Port(-1, ['num'], description='list value'),
            Port(-2, ['split', 'flow']),
            Port(-3, ['flow'])
        ])

    def connection_update(self):
        ip = self.get_port(1)
        op = self.get_port(-1)

        if ip.connection:
            t = ip.connection_port.get_contains()
            if t not in op.types:
                op.update_types([t])
        elif 'num' not in op.types:
            op.update_types(['num'])

    def get_loop_var(self):
        op = self.get_port(-1)
        contains = op.types[0]
        if contains == 'player':
            loop_var = f'p{self.id}'  
        elif contains == 'num':  
            loop_var = f'i{self.id}'
        elif contains == 'card':
            loop_var = f'c{self.id}'
        elif contains == 'string':
            loop_var = f's{self.id}'
        elif contains == 'bool':
            loop_var = f'b{self.id}'
        return loop_var
        
    def _get_default(self, p):
        if p == 1:
            return 'range(1)'
        
    def _get_text(self):
        input = [self.get_loop_var()] + self.get_input()
        text = 'for {0} in {1}:\n'.format(*input)   
        return text
        
    def _get_output(self, p):
        return self.get_loop_var()
        
class Zipped_For(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, ['cs', 'ps', 'ns', 'bs', 'ss'], description='list 1'),
            Port(2, ['cs', 'ps', 'ns', 'bs', 'ss'], description='list 2'),
            Port(3, ['flow']),
            Port(-1, ['num'], description='value 1'),
            Port(-2, ['num'], description='value 2'),
            Port(-3, ['split', 'flow']),
            Port(-4, ['flow'])
        ])

    def connection_update(self):
        for p in (1, 2):
        
            ip = self.get_port(p)
            op = self.get_port(-p)
            
            if ip.connection:
                t = ip.connection_port.get_contains()
                if t not in op.types:
                    op.update_types([t])
            elif 'num' not in op.types:
                op.update_types(['num'])

    def get_loop_var(self, p):   
        op = self.get_port(p)
        contains = op.types[0]
        if contains == 'player':
            return f'p{self.id}{abs(p)}'  
        elif contains == 'num':  
            return f'i{self.id}{abs(p)}'
        elif contains == 'card':
            return f'c{self.id}{abs(p)}'
        elif contains == 'string':
            return f's{self.id}{abs(p)}'
        elif contains == 'bool':
            return f'b{self.id}{abs(p)}'
        
    def _get_default(self, p):
        return 'range(1)'
        
    def _get_text(self):
        vars = [self.get_loop_var(-1), self.get_loop_var(-2)]
        input = vars + self.get_input()
        text = 'for {0}, {1} in zip({2}.copy(), {3}.copy()):\n'.format(*input)   
        return text
        
    def _get_output(self, p):
        return self.get_loop_var(p)
        
class Break(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['flow'])
        ])
        
    def connection_update(self):
        ip = self.get_port(1)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True, in_type='flow')
            for p in ports:
                if p.connection:
                    if isinstance(p.connection, (For, Zipped_For)) and 'split' in p.connection_port.types:
                        break
            else:
                ip.clear()
        
    def _get_text(self):
        return 'break\n'
        
class Continue(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['flow'])
        ])
        
    def connection_update(self):
        ip = self.get_port(1)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True, in_type='flow')
            for p in ports:
                if p.connection:
                    if isinstance(p.connection, (For, Zipped_For)) and 'split' in p.connection_port.types:
                        break
            else:
                ip.clear()
        
    def _get_text(self):
        return 'continue\n'
        
class Range(Node):
    cat = 'numeric'
    subcat = 'iterator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='min'),
            Port(2, ['num'], description='max'),
            Port(-1, ['ns'], description='[min, ..., max]')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        return '0'
        
    def _get_output(self, p):
        text = 'range({0}, {1})'.format(*self.get_input()) 
        return text
       
class User(Node):
    cat = 'player'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(-1, ['player'], description='player')
        ])

    def _get_output(self, p):
        return 'player'
       
class All_Players(Node):
    cat = 'player'
    subcat = 'lists'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['ps'], description='player list')
        ])

    def _get_output(self, p):
        return 'self.get_players()'
        
class Stored_Players(Node):
    cat = 'card attributes'
    subcat = 'player'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['ps'], description='player list')
        ])
        
    def _get_output(self, p):
        return 'self.players'
        
class Stored_Cards(Node):
    cat = 'card attributes'
    subcat = 'card'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['cs'], description='card list')
        ])
        
    def _get_output(self, p):
        return 'self.cards'
        
class Opponents(Node):
    cat = 'player'
    subcat = 'lists'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['ps'], description='player list')
        ])
        
    def _get_output(self, p):
        return 'self.get_opponents(player)'
        
class Card(Node):
    cat = 'card'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(-1, ['card'], description='this card')
        ])

    def _get_output(self, p):
        return 'self'
      
class Length(Node):
    cat = 'iterator'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

        self.set_ports([
            Port(1, ['ps', 'cs', 'ns', 'bs'], description='list'),
            Port(-1, ['num'], description='length of list')
        ])
        
    def _get_default(self, port):
        return '[]'
        
    def _get_output(self, p):
        return 'len({})'.format(*self.get_input())

class Merge_Lists(Node):
    cat = 'iterator'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
            
        self.set_ports([
            Port(1, ['ps'], description='list 1'),
            Port(2, ['ps'], description='list 2'),
            Port(-1, ['ps'], description='list 1 + list 2')
        ])
        
        get_transform_button(self)
        
    def tf(self, form=None):
        op = self.get_port(-1)
        if form == 1 or (form is None and 'ps' in op.types):
            for p in self.ports:
                p.set_types(['cs'])
            self.form = 1
        elif form == 0 or (form is None and 'cs' in op.types):
            for p in self.ports:
                p.set_types(['ps'])
            self.form = 0

    def _get_default(self, p):
        return '[]'
        
    def _get_output(self, p):
        return '({} + {})'.format(*self.get_input())
        
class Contains(Node):
    cat = 'iterator'
    subcat = 'boolean'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, ['num'], description='value'),
            Port(2, ['ns'], description='list'),
            Port(-1, ['bool'], description='value in list')
        ])
        
        set_input_element(self.get_port(1), 'num')
        self.set_port_pos()
        get_transform_button(self)

    def tf(self, form=None):
        ip1 = self.get_port(1)
        ip2 = self.get_port(2)
        
        if form == 1 or (form is None and 'num' in ip1.types):
            ip1.set_types(['string'])
            set_input_element(ip1, 'string')
            ip2.set_types(['ss'])
            self.form = 1
            
        elif form == 2 or (form is None and 'string' in ip1.types):
            ip1.set_types(['bool'])
            set_check_element(ip1)
            ip2.set_types(['bs'])
            self.form = 2
            
        elif form == 3 or (form is None and 'bool' in ip1.types):
            ip1.set_types(['player'])
            ip1.clear_element()
            ip2.set_types(['ps'])
            self.form = 3
            
        elif form == 4 or (form is None and 'player' in ip1.types):
            ip1.set_types(['card'])
            ip2.set_types(['cs'])
            self.form = 4
            
        elif form == 0 or (form is None and 'card' in ip1.types):
            ip1.set_types(['num'])
            set_input_element(ip1, 'num')
            ip2.set_types(['ns'])
            self.form = 0

        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return '[]'
        
    def _get_output(self, p):
        text = '({0} in {1})'.format(*self.get_input())
        return text
  
class Has_Tag(Node):
    cat = 'string'
    subcat = 'card attributes'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='tag'),
            Port(2, ['card'], description='card'),
            Port(-1, ['bool'], description='card has tag')
        ])
        
        set_dropdown_element(self.get_port(1), TAGS_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return 'self'
        
    def _get_output(self, p):
        text = '({0} in {1}.tags)'.format(*self.get_input())
        return text
        
class Has_Type(Node):
    cat = 'string'
    subcat = 'card attributes'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='type'),
            Port(2, ['card'], description='card'),
            Port(-1, ['bool'], description='card is type')
        ])
        
        set_dropdown_element(self.get_port(1), TYPES_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "'play'"
        elif p == 2:
            return 'self'
        
    def _get_output(self, p):
        text = '({1}.type == {0})'.format(*self.get_input())
        return text
      
class Get_Name(Node):
    cat = 'string'
    subcat = 'card attributes'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['card'], description='card'),
            Port(-1, ['string'], description='card name')
        ])
        
    def _get_default(self, p):
        return 'self'
        
    def _get_output(self, p):
        text = '{0}.name'.format(*self.get_input())
        return text 
      
class Has_Name(Node):
    cat = 'string'
    subcat = 'card attributes'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='name'),
            Port(2, ['card'], description='card'),
            Port(-1, ['bool'], description='card has name')
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return 'self'
        
    def _get_output(self, p):
        text = '({1}.name == {0})'.format(*self.get_input())
        return text
    
class Find_Owner(Node):
    cat = 'card'
    subcat = 'player'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['card'], description='card'),
            Port(-1, ['player'], description='card owner')
        ])
        
    def _get_default(self, p):
        return 'self'
        
    def _get_output(self, p):
        text = 'self.game.find_owner({0})'.format(*self.get_input())
        return text

class Tag_Filter(Node):
    cat = 'iterator'
    subcat = 'filter'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['string'], description='tag'),
            Port(2, ['bool'], description='filter self'),
            Port(3, ['cs'], description='card list'),
            Port(-1, ['cs'], description='cards with tag from list')
        ])
        
        set_dropdown_element(self.get_port(1), TAGS_DICT)
        set_check_element(self.get_port(2))
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "''"
        elif p == 3:
            return '[]'
        
    def _get_output(self, p):
        ip = self.get_port(2)
        if ip.connection:
            if ip.connection_port.value:
                text = "[x for x in {2} if {0} in x.tags and x != self]"
            else:
                text = "[x for x in {2} if {0} in x.tags]"
        else:
            text = "[x for x in {2} if {0} in x.tags]"
        text = text.format(*self.get_input())
        return text
        
class Name_Filter(Node):
    cat = 'iterator'
    subcat = 'filter'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['string'], description='name'),
            Port(2, ['bool'], description='include self'),
            Port(3, ['cs'], description='list'),
            Port(-1, ['cs'], description='cards with name from list')
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        set_check_element(self.get_port(2))
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "''"
        elif p == 3:
            return '[]'
        
    def _get_output(self, p):
        ip = self.get_port(2)
        if ip.connection:
            if ip.connection_port.value:
                text = "[x for x in {2} if x.name == {0} and x != self]"
            else:
                text = "[x for x in {2} if x.name == {0}]"
        else:
            text = "[x for x in {2} if x.name == {0}]"
        text = text.format(*self.get_input())
        return text
        
class Custom_Filter(Node):
    cat = 'iterator'
    subcat = 'filter'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description='condition'),
            Port(2, ['cs', 'ps', 'ns', 'ss', 'bs'], description='list'),
            Port(-1, ['ns'], description='filtered list')
        ])
        
        set_check_element(self.get_port(1))
        self.set_port_pos()
        
    def get_list_var(self):
        return f'x{self.id}'
        
    def connection_update(self):
        ip = self.get_port(2)
        op = self.get_port(-1)

        if ip.connection:
            t = ip.connection_port.types
            if t != op.types:
                op.update_types(t)
        elif 'ns' not in op.types:
            op.update_types(['ns'])
            
    def _get_default(self, p):
        if p == 1:
            return 'True'
        elif p == 2:
            return '[]'
            
    def _get_output(self, p):
        ipp = mapping.find_all_input_ports(self)
        contains = self.get_port(-1).get_contains()
        for ip in ipp:
            if contains in ip.types:
                ip.node.defaults[ip.port] = self.get_list_var()
        input = self.get_input() + [self.get_list_var()]
        for ip in ipp:
            ip.node.defaults.clear()
        text = '[{2} for {2} in {1} if {0}]'.format(*input)
        return text
        
class Any(Node):
    cat = 'iterator'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['cs', 'ps', 'ns', 'ss', 'bs'], description='list'),
            Port(-1, ['bool'], description='any is True')
        ])
            
    def _get_default(self, p):
        return '[]'
            
    def _get_output(self, p):
        text = 'any({})'.format(*self.get_input())
        return text
   
class Gain(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

        self.set_ports([
            Port(1, ['num'], description='points'),
            Port(2, ['player']),
            Port(3, ['flow']),
            Port(-1, ['flow'])
        ])
        
        set_input_element(self.get_port(1), 'num')
        self.set_port_pos()
     
    def _get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'player'
        
    def _get_text(self):
        text = '{1}.gain(self, {0})\n'.format(*self.get_input())
        return text      

class Lose(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, ['num'], description='points'),
            Port(2, ['player']),
            Port(3, ['flow']),
            Port(-1, ['flow'])
        ])
        
        set_input_element(self.get_port(1), 'num')
        self.set_port_pos()
     
    def _get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'player'
        
    def _get_text(self):
        text = '{1}.lose(self, {0})\n'.format(*self.get_input())
        return text      
        
class Steal(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, ['num'], description='points'),
            Port(2, ['player']),
            Port(3, ['player'], description='target'),
            Port(4, ['flow']),
            Port(-1, ['flow'])
        ])
        
        set_input_element(self.get_port(1), 'num')
        self.set_port_pos()
     
    def _get_default(self, p):
        if p == 1:
            return '0'
        elif p in (2, 3):
            return 'player'
        
    def _get_text(self):
        text = '{1}.steal(self, {0}, {2})\n'.format(*self.get_input())
        return text      

class Start_Flip(Node):
    cat = 'func'
    subcat = 'flip'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['flow'])
        ])

    def _get_text(self):
        pf = mapping.find_parent_func(self)
        if pf:
            if isinstance(pf, (Flip, Roll, Select)):
                return "self.wait = 'flip'\n"
        return "player.add_request(self, 'flip')\n"
        
    def get_required(self):
        return ['Flip']

class Flip(Node):
    cat = 'func'
    subcat = 'flip'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['bool'], description='flip result'),
            Port(-2, ['flow'])
        ])
            
    def _get_start(self):
        return '\t\tself.t_coin = coin\n'
            
    def _get_text(self):
        return '\n\tdef flip(self, player, coin):\n'
        
    def _get_output(self, p):
        if p == -1:
            return 'coin'
            
    def get_required(self):
        return ['Start_Flip']

class Start_Roll(Node):
    cat = 'func'
    subcat = 'roll'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['flow'])
        ])
        
    def _get_text(self):
        pf = mapping.find_parent_func(self)
        if pf:
            if isinstance(pf, (Flip, Roll, Select)):
                return "self.wait = 'roll'\n"
        return "player.add_request(self, 'roll')\n"
            
    def get_required(self):
        return ['Roll']

class Roll(Node):
    cat = 'func'
    subcat = 'roll'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['num'], description='roll result'),
            Port(-2, ['flow'])
        ])

    def _get_start(self):
        return '\t\tself.t_roll = dice\n'
            
    def _get_text(self):
        return '\n\tdef roll(self, player, dice):\n'
        
    def _get_output(self, p):
        if p == -1:
            return 'dice'
            
    def get_required(self):
        return ['Start_Roll']
            
class Start_Select(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['flow'])
        ])

    def _get_text(self):
        pf = mapping.find_parent_func(self)
        if pf:
            if isinstance(pf, (Flip, Roll, Select)):
                return "self.wait = 'select'\n"
        return "player.add_request(self, 'select')\n"
        
    def get_required(self):
        return ['Get_Selection', 'Select']
            
class Get_Selection(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['ps'], description='selection'),
            Port(-2, ['cs'], description='selection'),
            Port(-3, ['flow'])
        ])
            
    def _get_start(self):
        ports = mapping.map_ports(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if isinstance(p.connection, Return_List):
                    return ''
        else:
            return '\t\tselection = []\n'
            
    def _get_text(self):
        return '\n\tdef get_selection(self, player):\n'
        
    def _get_end(self):
        ports = mapping.map_ports(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if isinstance(p.connection, Return_List):
                    return ''
        else:
            return '\t\treturn selection\n'
        
    def _get_output(self, p):
        return 'selection'
        
    def get_required(self):
        return ['Start_Select', 'Select']
        
class Return_List(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
            
        self.set_ports([
            Port(1, ['cs', 'ps'], description='list'),
            Port(2, ['flow'])
        ])
        
    def connection_update(self):
        ip = self.get_port(2)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True)
            for p in ports:
                if isinstance(p.connection, Get_Selection):
                    break
            else:
                ip.clear()
        
    def _get_default(self, p):
        return '[]'
        
    def _get_text(self):
        return 'return {0}\n'.format(*self.get_input())

class Select(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['num'], description='number selected'),
            Port(-2, ['player'], description='selected player'),
            Port(-3, ['card'], description='selected card'),
            Port(-4, ['flow'])
        ])
                
    def _get_start(self):
        return '\t\tif not num:\n\t\t\treturn\n\t\tsel = player.selected[-1]\n\t\tself.t_select = sel\n\t\tsel_c = None\n\t\tsel_p = None\n\t\tif isinstance(sel, Card):\n\t\t\tsel_c = sel\n\t\telse:\n\t\t\tsel_p = sel\n'
            
    def _get_text(self):
        return '\n\tdef select(self, player, num):\n'
        
    def _get_output(self, p):
        if p == -1:
            return 'num'
        elif p == -2:
            return 'sel_p'
        elif p == -3:
            return 'sel_c'
            
    def get_required(self):
        return ['Start_Select', 'Get_Selection']
  
class Return_Bool(Node):
    cat = 'func'
    subcat = 'item and spell'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description='return bool'),
            Port(2, ['flow'])
        ])
        
    def connection_update(self):
        ip = self.get_port(2)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True)
            for p in ports:
                if isinstance(p.connection, (Can_Use, Can_Cast)):
                    break
            else:
                ip.clear()
        
    def _get_default(self, p):
        return 'True'
        
    def _get_text(self):
        return 'return {0}\n'.format(*self.get_input())

class Can_Cast(Node):
    cat = 'func'
    subcat = 'item and spell'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['bool'], description='can cast'),
            Port(-2, ['flow'])
        ])
            
    def _get_start(self):
        return '\t\tcancast = True\n'
            
    def _get_text(self):
        return '\n\tdef can_cast(self, player):\n'
        
    def _get_end(self):
        ports = map_scope(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if isinstance(p.connection, Return_Bool):
                    return ''
        else:
            return '\t\treturn cancast\n'

    def _get_output(self, p):
        if p == -1:
            return 'cancast'   

class Can_Use(Node):
    cat = 'func'
    subcat = 'item and spell'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['bool'], description='can use'),
            Port(-2, ['flow'])
        ])
            
    def _get_start(self):
        return '\t\tcanuse = True\n'
            
    def _get_text(self):
        return '\n\tdef can_use(self, player):\n'
        
    def _get_end(self):
        ports = mapping.map_ports(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if isinstance(p.connection, Return_Bool):
                    return ''
        else:
            return '\t\treturn canuse\n'

    def _get_output(self, p):
        if p == -1:
            return 'canuse'             
  
class Start_Ongoing(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['flow'])
        ])
                
    def _get_text(self):
        return "self.start_ongoing(player)\n"
        
    def get_required(self):
        return ['Init_Ongoing', 'Add_To_Ongoing', 'Ongoing']
        
class Init_Ongoing(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['flow'])
        ])
            
    def _get_text(self):
        return '\n\tdef start_ongoing(self, player):\n'
        
    def get_required(self):
        return ['Start_Ongoing', 'Add_To_Ongoing', 'Ongoing']
        
class Add_To_Ongoing(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['string'], description='log type'),
            Port(2, ['flow']),
            Port(-1, ['flow'])
        ])

        set_dropdown_element(self.get_port(1), LOGS_DICT)
        self.set_port_pos()
        
    def connection_update(self):
        ip = self.get_port(2)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True)
            for p in ports:
                if isinstance(p.connection, Init_Ongoing):
                    break
            else:
                ip.clear()
            
    def _get_default(self, p):
        return "''"
            
    def _get_text(self):
        return 'player.add_og(self, {0})\n'.format(*self.get_input())
        
    def get_required(self):
        return ['Start_Ongoing', 'Init_Ongoing', 'Ongoing']
        
class Ongoing(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['log'], description='log info'),
            Port(-2, ['flow'])
        ])
        
    def _get_text(self):
        return '\n\tdef ongoing(self, player, log):\n'
        
    def _get_output(self, p):
        if p == -1:
            return 'log'
            
    def get_required(self):
        return ['Start_Ongoing', 'Init_Ongoing', 'Add_To_Ongoing']

class Extract_Value(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['string'], description='key'),
            Port(2, ['log'], description='log'),
            Port(-1, ['num'], description='value')
        ])
        
        set_dropdown_element(self.get_port(1), LOG_KEYS_DICT)
        self.set_port_pos()
        
    def _get_output(self, p):
        text = "{1}.get({0})".format(*self.get_input())
        return text
        
    def _get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return '{}'
        
    def eval_text(self, text):
        if text == 'c':
            return 'card'
        elif text in ('gp', 'lp', 'sp', 'give', 'dice'):
            return 'num'
        elif text in ('t', 'deck'):
            return 'string'
        elif text in ('u', 'target'):
            return 'player'
        elif text == 'coin':
            return 'bool'
        
    def connection_update(self):
        ip = self.get_port(1)
        op = self.get_port(-1)
        
        if ip.connection:
            text = ip.connection.get_string_val()
            t = self.eval_text(text)
            if t and t not in op.types:
                op.update_types([t])
        elif 'num' not in op.types:
            op.update_types(['num'])

class Deploy(Node):
    cat = 'func'
    subcat = 'deploy'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['string'], description='type'),
            Port(2, ['ps'], description='players to send to'),
            Port(3, ['card'], description='set stored card'),
            Port(4, ['player'], description='set stored player'),
            Port(5, ['flow']),
            Port(-1, ['flow'])
        ])
        
        set_dropdown_element(self.get_port(1), REQUESTS_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return '[]'
        elif p == 3 or p == 4:
            return 'None'
            
    def _get_text(self):
        input = self.get_input()
        request = input[0]
        if request.strip("'") not in ('', 'flip', 'roll', 'select', 'og'):
            input[0] = "''"
        return "self.deploy(player, {1}, {0}, extra_card={2}, extra_player={3})\n".format(*input)

class Get_Flip_Results(Node):
    cat = 'func'
    subcat = 'deploy'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['flow']),
            Port(-1, ['ps'], description='players'),
            Port(-2, ['bs'], description='flip results'),
            Port(-3, ['flow'])
        ])
        
    def _get_text(self):
        return f'players{self.id}, results{self.id} = self.get_flip_results()\n'
        
    def _get_output(self, p):
        if p == -1:
            return f'players{self.id}'
        elif p == -2:
            return f'results{self.id}'
            
class Get_Roll_Results(Node):
    cat = 'func'
    subcat = 'deploy'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['flow']),
            Port(-1, ['ps'], description='players'),
            Port(-2, ['ns'], description='roll results'),
            Port(-3, ['flow'])
        ])
        
    def _get_text(self):
        return f'players{self.id}, results{self.id} = self.get_roll_results()\n'
        
    def _get_output(self, p):
        if p == -1:
            return f'players{self.id}'
        elif p == -2:
            return f'results{self.id}'
            
class Get_Select_Results(Node):
    cat = 'func'
    subcat = 'deploy'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['flow']),
            Port(-1, ['ps'], description='players'),
            Port(-2, ['cs'], description='select results'),
            Port(-3, ['flow'])
        ])
        
    def _get_text(self):
        return f'players{self.id}, results{self.id} = self.get_select_results()\n'
        
    def _get_output(self, p):
        if p == -1:
            return f'players{self.id}'
        elif p == -2:
            return f'results{self.id}'

class Self_Index(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 

        self.set_ports([
            Port(-1, ['num'])
        ])

    def _get_output(self, p):
        return 'player.played.index(self)'
        
class Index_Above(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(-1, ['num'], description='self index - 1')
        ])

    def _get_output(self, p):
        return 'max({player.played.index(self) - 1, 0})'
        
class Index_Below(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(-1, ['num'], description='self index + 1')
        ])

    def _get_output(self, p):
        return 'min({player.played.index(self) + 1, len(player.played)})'
        
class Check_Index(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  

        self.set_ports([
            Port(1, ['player']),
            Port(2, ['num'], description='index'),
            Port(3, ['string'], description='tag'),
            Port(4, ['flow']),
            Port(-1, ['card'], description='card at index'),
            Port(-2, ['bool'], description='new card'),
            Port(-3, ['flow'])
        ])
        
        set_input_element(self.get_port(2), 'num')
        set_dropdown_element(self.get_port(3), TAGS_DICT)
        self.set_port_pos()
 
    def _get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return '-1'
        elif p == 3:
            return ''
        
    def _get_text(self):
        ip = self.get_port(3)
        input = self.get_input()
        if ip.connection:
            if ip.connection.get_string_val().strip("'"):
                text = f"added{self.id}, c{self.id} = self.check_index({'{0}'}, {'{1}'}, tags=[{'{2}'}])\n"
            else:
                text = f"added{self.id}, c{self.id} = self.check_index({'{0}'}, {'{1}'})\n"
                input.pop(-1)
        else:
            text = f"added{self.id}, c{self.id} = self.check_index({'{0}'}, {'{1}'})\n"
            input.pop(-1)
        return text.format(*input)
        
    def _get_output(self, p):
        if p == -1:
            return f'c{self.id}'
        elif p == -2:
            return f'added{self.id}'
       
class Check_First(Node):
    cat = 'player'
    subcat = 'boolean'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['player']),
            Port(-1, ['bool'], description='player is first')
        ])
        
    def _get_default(self, p):
        if p == 1:
            return 'player'
        
    def _get_output(self, p):
        return 'self.game.check_first({0})'.format(*self.get_input())  
        
class Check_Last(Node):
    cat = 'player'
    subcat = 'boolean'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
            
        self.set_ports([
            Port(1, ['player']),
            Port(-1, ['bool'], description='player is last')
        ])
        
    def _get_default(self, p):
        if p == 1:
            return 'player'
        
    def _get_output(self, p):
        return 'self.game.check_last({0})'.format(*self.get_input())  

class Draw_Cards(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='type'),
            Port(2, ['num'], description='number of cards'),
            Port(3, ['player']),
            Port(4, ['flow']),
            Port(-1, ['cs'], description='cards'),
            Port(-2, ['flow'])
        ])
        
        set_dropdown_element(self.get_port(1), TYPES_DICT)
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "'treasure'"
        elif p == 2:
            return '1'
        elif p == 3:
            return 'player'
        
    def _get_text(self):
        input = self.get_input()
        input.insert(0, self._get_output(0))
        return "{0} = {3}.draw_cards({1}, num={2})\n".format(*input)
        
    def _get_output(self, p):
        return f'seq{self.id}'
        
class Is_Event(Node):
    cat = 'card'
    subcat = 'boolean'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='event name'),
            Port(-1, ['bool'], description='event has name')
        ])
        
        set_dropdown_element(self.get_port(1), EVENTS_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        return "''"
        
    def _get_output(self, p):
        return 'self.game.is_event({0})'.format(*self.get_input())
                
class Play_Card(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['card']),
            Port(2, ['player']),
            Port(3, ['flow']),
            Port(-1, ['flow'])
        ])
        
    def _get_default(self, p):
        if p == 1:
            return 'self'
        elif p == 2:
            return 'player'
        
    def _get_text(self):
        return "{1}.play_card({0})\n".format(*self.get_input())
           
class Copy_Card(Node):
    cat = 'card'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['card']),
            Port(-1, ['card'], description='card copy')
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_output(self, p):
        return "{0}.copy()".format(*self.get_input())

class Set_Extra_Card(Node):
    cat = 'card attributes'
    subcat = 'card'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['card'], description='new extra card'),
            Port(2, ['flow']),
            Port(-1, ['flow'])
        ])
            
    def _get_text(self):
        return 'self.extra_card = {0}\n'.format(*self.get_input())
        
    def _get_default(self, p):
        return 'None'

class Get_Extra_Card(Node):
    cat = 'card attributes'
    subcat = 'card'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['card'], description='extra card')
        ])
            
    def _get_output(self, p):
        return 'self.extra_card'   
        
class Set_Extra_Player(Node):
    cat = 'card attributes'
    subcat = 'player'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['player'], description='new extra player'),
            Port(2, ['flow']),
            Port(-1, ['flow'])
        ])
            
    def _get_text(self):
        return 'self.extra_player = {0}\n'.format(*self.get_input())
        
    def _get_default(self, p):
        return 'None'

class Get_Extra_Player(Node):
    cat = 'card attributes'
    subcat = 'player'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['player'], description='extra player')
        ])
            
    def _get_output(self, p):
        return 'self.extra_player' 
        
class Index(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='index'),
            Port(2, ['ps'], description='list'),
            Port(-1, ['player'], description='list value at index')
        ])
        
        set_input_element(self.get_port(1), 'num')
        self.set_port_pos()
        get_transform_button(self)
        
    def tf(self, form=None):
        ip = self.get_port(2)
        op = self.get_port(-1)
        
        if form == 1 or (form is None and 'ps' in ip.types):
            ip.set_types(['cs'])
            op.set_types(['card'])
            self.form = 1
        elif form == 0 or (form is None and 'cs' in ip.types):
            ip.set_types(['ps'])
            op.set_types(['player'])
            self.form = 0
            
    def _get_output(self, p):
        return '{1}[{0}]'.format(*self.get_input())
        
    def _get_default(self, p):
        if p == 1:
            return '-1'
        elif p == 2:
            return "player.string_to_deck('played')"
        
class Safe_Index(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='index'),
            Port(2, ['ps'], description='list'),
            Port(-1, ['player'], description='list value at index')
        ])

        set_input_element(self.get_port(1), 'num')
        self.set_port_pos()
        
    def tf(self, form=None):
        ip = self.get_port(2)
        op = self.get_port(-1)
        
        if form == 1 or (form is None and 'ps' in ip.types):
            ip.set_types(['cs'])
            op.set_types(['card'])
            self.form = 1
        elif form == 0 or (form is None and 'cs' in ip.types):
            ip.set_types(['ps'])
            op.set_types(['player'])
            self.form = 0
            
    def _get_output(self, p):
        return '{1}[{0}] if {0} < len({1}) else None'.format(*self.get_input())
        
    def _get_default(self, p):
        if p == 1:
            return '-1'
        elif p == 2:
            return "player.string_to_deck('played')"
        
class Discard(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['player']),
            Port(2, ['card']),
            Port(3, ['flow']),
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        return '{0}.discard_card({1})\n'.format(*self.get_input())
        
    def _get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return 'None'
                     
class Use_Item(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['card'], description='item'),
            Port(2, ['flow']),
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        return 'player.use_item({0})\n'.format(*self.get_input())
        
    def _get_default(self, p):
        return 'self'
        
class Cast_Spell(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['card'], description='spell card'),
            Port(2, ['player'], description='target'),
            Port(3, ['flow']),
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        return 'player.cast({1}, {0})\n'.format(*self.get_input())
        
    def _get_default(self, p):
        if p == 1:
            return 'self'
        elif p == 2:
            return 'player'
            
class Give_Card(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['card']),
            Port(2, ['player'], description='target'),
            Port(3, ['flow']),
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        return 'player.give_card({0}, {1})\n'.format(*self.get_input())
        
    def _get_default(self, p):
        if p == 1:
            return 'self'
        elif p == 2:
            return 'player'
     
class Get_New_Card(Node):
    cat = 'card'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['string'], description='card name'),
            Port(-1, ['card'])
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        self.set_port_pos()

    def _get_output(self, p):
        return 'self.game.get_card({0})'.format(*self.get_input())
        
    def _get_default(self, p):
        return 'self.name'
     
class Transfom(Node):
    cat = 'card'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['string'], description='new card name'),
            Port(2, ['card']),
            Port(3, ['flow']),
            Port(-1, ['flow'])
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        self.set_port_pos()

    def _get_text(self):
        return 'self.game.transform({1}, {0})\n'.format(*self.get_input())
        
    def _get_default(self, p):
        if p == 1:
            return 'self.name'
        elif p == 2:
            return 'self'
            
class Swap(Node):
    cat = 'card'
    subcat = 'operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['card']),
            Port(2, ['card']),
            Port(3, ['flow']),
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        return 'self.game.swap({0}, {1})\n'.format(*self.get_input())
        
    def _get_default(self, p):
        return 'self'
        
class Get_Discard(Node):
    cat = 'card'
    subcat = 'iterator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['cs'], description='discarded cards')
        ])
        
    def _get_output(self, p):
        return 'self.game.get_discard()'
     
class Set_Mode(Node):
    cat = 'card attributes'
    subcat = 'mode'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

        self.set_ports([
            Port(1, ['num'], description='new mode'),
            Port(2, ['flow']),
            Port(-1, ['flow'])
        ])
        
        set_input_element(self.get_port(1), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return '0'
        
    def _get_text(self):
        return 'self.mode = {0}\n'.format(*self.get_input())
        
class Get_Mode(Node):
    cat = 'card attributes'
    subcat = 'mode'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(-1, ['num'], description='mode')
        ])
        
    def _get_output(self, p):
        return 'self.mode'

class Steal_Random(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 

        self.set_ports([
            Port(1, ['string'], description='type'),
            Port(2, ['player'], description='target'),
            Port(3, ['flow']),
            Port(-1, ['card']),
            Port(-2, ['flow'])
        ])
        
        set_dropdown_element(self.get_port(1), TYPES_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "'treasure'"
        elif p == 2:
            return 'player'

    def _get_text(self):
        input = self.get_input()
        input.insert(0, self._get_output())
        return "{0} = player.steal_random_card({1}, {2})\n".format(*input)
        
    def _get_output(self):
        return f'c{self.id}'
        
class Add_Card(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['player']),
            Port(2, ['card']),
            Port(3, ['string'], description='deck'),
            Port(4, ['num'], description='index'),
            Port(5, ['flow']),
            Port(-1, ['flow'])
        ])
        
        set_dropdown_element(self.get_port(3), DECKS_DICT)
        set_input_element(self.get_port(4), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 4:
            return '-1'
        else:
            return 'None'

    def _get_text(self):
        return "{0}.add_card({1}, deck_string={2}, i={3})\n".format(*self.get_input())
                
class Get_Deck(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, ['string'], description='deck name'),
            Port(2, ['player']),
            Port(-1, ['cs'], description='deck')
        ])
        
        set_dropdown_element(self.get_port(1), DECKS_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "'played'"
        elif p == 2:
            return 'player'
            
    def _get_output(self, p):
        return '{1}.string_to_deck({0})'.format(*self.get_input())
        
class Get_Score(Node):
    cat = 'player'
    subcat = 'score'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['player']),
            Port(-1, ['num'], description='points')
        ])
        
    def _get_default(self, p):
        return 'player'

    def _get_output(self, p):
        return "{0}.score".format(*self.get_input())
        
class Has_Card(Node):
    cat = 'player'
    subcat = 'boolean'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='card name'),
            Port(2, ['player']),
            Port(-1, ['bool'], description='player has card')
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return 'self.name'
        elif p == 2:
            return 'player'

    def _get_output(self, p):
        return "{1}.has_card({0})".format(*self.get_input())
        
class Is_Player(Node):
    cat = 'player'
    subcat = 'boolean'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 

        self.set_ports([
            Port(1, ['card', 'player']),
            Port(-1, ['bool'])
        ])
        
    def _get_default(self, p):
        return 'player'

    def _get_output(self):
        return "{0}.type == 'player'".format(*self.get_input())        
        
class Is_Card(Node):
    cat = 'card'
    subcat = 'boolean'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['card', 'player']),
            Port(-1, ['bool'])
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_output(self):
        return "isinstance({0}, card_base.Card)".format(*self.get_input())  
        