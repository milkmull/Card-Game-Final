import pygame as pg

from data.constants import (
    SORTED_NAMES_DICT,
    TAGS_DICT,
    DECKS_DICT,
    WAIT_DICT,
    WAIT_KEYS_DICT,
    LOCAL_GROUP_DICT,
    DIRECTIONS_DICT
)

from . import mapping
from .node_base import Node, Port

from ui.element.elements import Textbox, Input
from .get_elements import (
    set_input_element,
    set_vec_element,
    set_check_element,
    set_dropdown_element,
    get_transform_button,
    get_ar_buttons
)

class Play(Node):
    cat = 'func'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs)
        
        self.set_ports([
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        return '\n\tdef play(self):\n'
        
class Remove(Node):
    cat = 'func'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs)
        
        self.set_ports([
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        return '\n\tdef remove(self):\n'
        
class Move(Node):
    cat = 'func'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs)
        
        self.set_ports([
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        return '\n\tdef move(self):\n'
        
class Update(Node):
    cat = 'func'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs)
        
        self.set_ports([
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        return '\n\tdef update(self):\n'
       
class If(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description='condition'),
            Port(2, ['flow']),
            Port(-1, ['process', 'flow']),
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
            Port(-1, ['process', 'flow']),
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
            Port(-1, ['process', 'flow']),
            Port(-2, ['flow'])
        ])
        
    def can_connect(self, p0, n1, p1):
        if p0.port == 2:
            return isinstance(n1, (If, Elif))
        return True
        
    def _get_text(self):
        text = 'else:\n'  
        return text
 
class Ternary(Node):
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
        
        set_check_element(self.get_port(-1))
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
        
        set_input_element(self.get_port(-1), 'num', value='0')
        self.set_port_pos()
        
    def _get_default(self, p):
        return '0'

    def _get_output(self, p):
        return self.get_port(-1).get_output()
        
class String():
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
        
class Extend(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description=' '),
            Port(-1, ['bool'], description=' ')
        ])
        
    def connection_update(self):
        ip = self.get_port(1)
        op = self.get_port(-1)

        if ip.connection:
            t = ip.connection_port.types[0]
            if t not in op.types:
                op.update_types([t])
        elif 'bool' not in op.types:
            op.update_types(['bool'])
        
    def _get_default(self, p):
        return 'True'
        
    def _get_output(self, p):
        return self.get_input()

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
            return 'self.player'
        elif 'card' in ip.types:
            return 'self'
        elif 'spot' in ip.types:
            return 'self.spot'
        else:
            return '[]'

    def _get_output(self, p):
        text = '({} == {})'.format(*self.get_input())    
        return text
      
class Greater(Node):
    cat = 'numeric'
    subcat = 'boolean'
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
    cat = 'numeric'
    subcat = 'boolean'
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
            Port(2, ['ns'], description='[0, 1, 2...]'),
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
            Port(1, ['num'], description='a'),
            Port(2, ['num'], description='b'),
            Port(-1, ['num'], description='a + b')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        
    def _get_default(self, p):
        return '0'
        
    def _get_output(self, p):
        return '({} + {})'.format(*self.get_input())
        
class Increment(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='a'),
            Port(-1, ['num'], description='a + 1')
        ])
        
    def _get_default(self, p):
        return '0'
        
    def _get_output(self, p):
        return '({} + 1)'.format(*self.get_input())
        
class Decrement(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['num'], description='a'),
            Port(-1, ['num'], description='a - 1')
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
            Port(1, ['num'], description='a'),
            Port(2, ['num'], description='b'),
            Port(-1, ['num'], description='a - b')
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
            Port(1, ['num'], description='a'),
            Port(2, ['num'], description='b'),
            Port(-1, ['num'], description='a * b')
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
            Port(1, ['num'], description='a'),
            Port(-1, ['num'], description='-a')
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
            Port(1, ['num'], description='a'),
            Port(2, ['num'], description='b'),
            Port(-1, ['num'], description='a / b')
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
            Port(1, ['as', 'cs', 'ps', 'ss', 'ns'], description='list'),
            Port(2, ['flow']),
            Port(-1, ['num'], description='list value'),
            Port(-2, ['process', 'flow']),
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
        match op.types[0]:
            case 'player':
                return f'p{self.id}'  
            case 'card':
                return f'c{self.id}'
            case 'spot':
                return f's{self.id}'
            case 'num':  
                return f'i{self.id}'
        
    def _get_default(self, p):
        if p == 1:
            return 'range(1)'
        
    def _get_text(self):
        input = [self.get_output(-1)] + self.get_input()
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
            Port(1, ['as', 'cs', 'ps', 'ss', 'ns'], description='list 1'),
            Port(2, ['as', 'cs', 'ps', 'ss', 'ns'], description='list 2'),
            Port(3, ['flow']),
            Port(-1, ['num'], description='value 1'),
            Port(-2, ['num'], description='value 2'),
            Port(-3, ['process', 'flow']),
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
        match op.types[0]:
            case 'player':
                return f'p{self.id}{abs(p)}'  
            case 'card':
                return f'c{self.id}{abs(p)}'
            case 'spot':
                return f's{self.id}{abs(p)}'
            case 'num':  
                return f'i{self.id}{abs(p)}'
        
    def _get_default(self, p):
        return 'range(1)'
        
    def _get_text(self):
        vars = [self.get_output(-1), self.get_output(-2)]
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
                    if isinstance(p.connection, (For, Zipped_For)) and 'process' in p.connection_port.types:
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
                    if isinstance(p.connection, (For, Zipped_For)) and 'process' in p.connection_port.types:
                        break
            else:
                ip.clear()
        
    def _get_text(self):
        return 'continue\n'
        
class Range(Node):
    cat = 'iterator'
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
       
class Player(Node):
    cat = 'player'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(-1, ['player'], description='player')
        ])

    def _get_output(self, p):
        return 'self.player'
       
class All_Players(Node):
    cat = 'player'
    subcat = 'lists'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, ['ps'], description='player list')
        ])

    def _get_output(self, p):
        return 'self.game.get_players()'
        
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
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

        self.set_ports([
            Port(1, ['as', 'ps', 'cs', 'ss', 'ns'], description='list'),
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
        elif form == 2 or (form is None and 'cs' in op.types):
            for p in self.ports:
                p.set_types(['ss'])
            self.form = 2
        elif form == 0 or (form is None and 'ss' in op.types):
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
            ip1.set_types(['player'])
            set_input_element(ip1, 'player')
            ip2.set_types(['ps'])
            self.form = 1
            
        elif form == 2 or (form is None and 'player' in ip1.types):
            ip1.set_types(['card'])
            ip2.set_types(['cs'])
            self.form = 2
            
        elif form == 3 or (form is None and 'card' in ip1.types):
            ip1.set_types(['spot'])
            set_input_element(ip1, 'spot')
            ip2.set_types(['ss'])
            self.form = 3
            
        elif form == 0 or (form is None and 'spot' in ip1.types):
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
    cat = 'card'
    subcat = 'boolean'
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
        text = '{1}.has_tag({0})'.format(*self.get_input())
        return text
      
class Get_Name(Node):
    cat = 'card'
    subcat = 'attributes'
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
    cat = 'card'
    subcat = 'boolean'
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
        text = '{1}.has_name({0})'.format(*self.get_input())
        return text
        
class Filter(Node):
    cat = 'iterator'
    subcat = 'filter'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port.get_comparison_types(), description='condition'),
            Port(2, ['cs', 'ps', 'ss', 'ns'], description='list'),
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

class Gain(Node):
    cat = 'player'
    subcat = 'points'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

        self.set_ports([
            Port(1, ['card'], description='extra card'),
            Port(2, ['num'], description='points'),
            Port(3, ['player']),
            Port(4, ['flow']),
            Port(-1, ['flow'])
        ])
        
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
     
    def _get_default(self, p):
        match p:
            case 1:
                return 'None'
            case 2:
                return '0'
            case 3:
                return 'self.player'
        
    def _get_text(self):
        text = '{2}.gain({1}, self, extra={0})\n'.format(*self.get_input())
        return text      

class Steal(Node):
    cat = 'player'
    subcat = 'points'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, ['card'], description='extra card'),
            Port(2, ['num'], description='points'),
            Port(3, ['player']),
            Port(4, ['player'], description='target'),
            Port(5, ['flow']),
            Port(-1, ['flow'])
        ])
        
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
     
    def _get_default(self, p):
        match p:
            case 1:
                return 'None'
            case 2:
                return '0'
            case 3 | 4:
                return 'self.player'
        
    def _get_text(self):
        text = '{2}.steal({1}, self, {3}, extra={0})\n'.format(*self.get_input())
        return text      
          
class Start_Select(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['cs'], description='selection'),
            Port(2, ['flow'])
        ])

    def _get_text(self):
        text = 'self.player.start_select(self, {0})\n'.format(*self.get_input())
        return text

class Select(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['card'], description='selected card'),
            Port(-2, ['flow'])
        ])
            
    def _get_text(self):
        return '\n\tdef select(self, card):\n'
        
    def _get_output(self, p):
        return 'card'

class Start_Wait(Node):
    cat = 'func'
    subcat = 'wait'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['string'], description='wait type'),
            Port(2, ['flow'])
        ])
        
        set_dropdown_element(self.get_port(1), WAIT_DICT)
        self.set_port_pos()
                
    def _get_text(self):
        text = 'self.start_wait({0})'.format(*self.get_input())
        return text
        
    def _get_default(self, p):
        return "''"
        
class Run_Wait(Node):
    cat = 'func'
    subcat = 'wait'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs) 
        
        self.set_ports([
            Port(-1, ['log'], description='data'),
            Port(-2, ['flow'])
        ])
            
    def _get_text(self):
        return '\n\tdef run_wait(self, data):\n'
       
class End_Wait(Node):
    cat = 'func'
    subcat = 'wait'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['flow']),
            Port(-1, ['flow'])
        ])
            
    def _get_text(self):
        return 'self.end_wait()\n'

class Extract_Value(Node):
    cat = 'func'
    subcat = 'wait'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, ['string'], description='key'),
            Port(2, ['log'], description='log'),
            Port(-1, ['num'], description='value')
        ])
        
        set_dropdown_element(self.get_port(1), WAIT_KEYS_DICT, const=True)
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
        match text:
            case 'card':
                return 'card'
            case 'player':
                return 'player'
        
    def connection_update(self):
        ip = self.get_port(1)
        op = self.get_port(-1)
        
        text = ip.value
        t = self.eval_text(text)
        if t and t not in op.types:
            op.update_types([t])
       
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
        
        if form == 1 or (form is None and 'ss' in ip.types):
            ip.set_types(['cs'])
            op.set_types(['card'])
            self.form = 1
        elif form == 2 or (form is None and 'cs' in ip.types):
            ip.set_types(['ps'])
            op.set_types(['player'])
            self.form = 2
        elif form == 0 or (form is None and 'ps' in ip.types):
            ip.set_types(['ss'])
            op.set_types(['spot'])
            self.form = 0
            
    def _get_output(self, p):
        return '{1}[{0}]'.format(*self.get_input())
        
    def _get_default(self, p):
        if p == 1:
            return '-1'
        elif p == 2:
            return "player.string_to_deck('played')"
            
class Copy_Card(Node):
    cat = 'card'
    subcat = 'operators'
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
   
class Get_New_Card(Node):
    cat = 'card'
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
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['string'], description='new card name'),
            Port(2, ['card']),
            Port(3, ['flow']),
            Port(-1, ['card'], description='new card'),
            Port(-2, ['flow'])
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        self.set_port_pos()
        
    def _get_output(self, p):
        return f'c{self.id}'

    def _get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output(-1))
        text = '{0} = self.game.transform({2}, self.game.get_card({1}))\n'.format(*input)
        return text
        
    def _get_default(self, p):
        if p == 1:
            return 'self.name'
        elif p == 2:
            return 'self'
            
class Transfom2(Node):
    cat = 'card'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['card'], description='new card'),
            Port(2, ['card']),
            Port(3, ['flow']),
            Port(-1, ['card'], description='new card'),
            Port(-2, ['flow'])
        ])

    def _get_output(self, p):
        return f'c{self.id}'

    def _get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output(-1))
        text = '{0} = self.game.transform({2}, {1})\n'.format(*input)
        return text
        
    def _get_default(self, p):
        return 'self'
            
class Swap_With(Node):
    cat = 'card'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, ['card']),
            Port(2, ['flow']),
            Port(-1, ['flow'])
        ])

    def _get_text(self):
        text = 'self.swap_with({0})\n'.format(*self.get_input())
        return text
        
    def _get_default(self, p):
        return 'self'
              
class Get_Deck(Node):
    cat = 'player'
    subcat = 'lists'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, ['string'], description='deck name'),
            Port(2, ['player']),
            Port(-1, ['cs'], description='deck')
        ])
        
        set_dropdown_element(self.get_port(1), DECKS_DICT, value='played')
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
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['player']),
            Port(-1, ['num'], description='score')
        ])
        
    def _get_default(self, p):
        return 'player'

    def _get_output(self, p):
        return "{0}.score".format(*self.get_input())
    
class Cards_From_Vector(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['vec'], description='dx, dy'),
            Port(2, ['num'], description='steps'),
            Port(3, ['num'], description='da'),
            Port(4, ['bool'], description='condition'),
            Port(5, ['bool'], description='stop on empty'),
            Port(6, ['bool'], description='stop on fail'),
            Port(7, ['bool'], description='reverse'),
            Port(-1, ['cs'], description='cards')
        ])
        
        set_vec_element(self.get_port(1))
        set_input_element(self.get_port(2), 'num')
        set_input_element(self.get_port(3), 'num')
        set_check_element(self.get_port(5))
        self.get_port(5).hide()
        set_check_element(self.get_port(6))
        set_check_element(self.get_port(7))
        self.get_port(7).hide()
        self.set_port_pos()
        
    def _get_default(self, p):
        match p:
            case 1:
                return '0'
            case 2:
                return '1'
            case 3:
                return '360'
            case 4:
                return 'True'
            case 5 | 6 | 7:
                return 'False'

    def _get_output(self, p):
        ipp = mapping.find_all_input_ports(self)
        for ip in ipp:
            if 'card' in ip.types:
                ip.node.defaults[ip.port] = 'c'
                
        text = (
            'self.spot.cards_from_vector('
                '{0}, '
                'steps={1}, '
                'da={2}, '
                'check=lambda c: {3}, '
                'stop_on_empty={4}, '
                'stop_on_fail={5}, '
                'reverse={6}'
            ')'
        ).format(*self.get_input())
        return text
        
class Get_Spot_Group(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='group'),
            Port(-1, ['ss'], description='spots')
        ])
        
        set_dropdown_element(self.get_port(1), LOCAL_GROUP_DICT, const=True)
        self.set_port_pos()
        
    def _get_output(self, p):
        text = 'self.spot.get_spot_group({0})'.format(*self.get_input())
        return text
        
class Get_Card_Group(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='group'),
            Port(2, ['bool'], description='check'),
            Port(-1, ['cs'], description='spots')
        ])
        
        set_dropdown_element(self.get_port(1), LOCAL_GROUP_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return 'True'
        
    def _get_output(self, p):
        ipp = mapping.find_all_input_ports(self)
        for ip in ipp:
            if 'card' in ip.types:
                ip.node.defaults[ip.port] = 'c'
                
        text = 'self.spot.get_card_group({0}, check=lambda c: {1})'.format(*self.get_input())
        return text
        
class Register(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['card']),
            Port(-1, ['bool'], description='new card?')
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_output(self, p):
        return 'self.register({})'.format(*self.get_input())
        
class Get_Player(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['card']),
            Port(-1, ['player'], description='owner')
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_output(self, p):
        return '{0}.player'.format(*self.get_input())
        
class Set_Player(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['player']),
            Port(2, ['card']),
            Port(3, ['flow']),
            Port(-1, ['bool'], description='changed?'),
            Port(-2, ['flow'])
        ])
        
    def _get_output(self, p):
        return f'b{self.id}'
        
    def _get_default(self, p):
        match p:
            case 1:
                return 'self.player'
            case 2:
                return 'self'

    def _get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output(-1))
        return '{0} = {2}.change_player({1})\n'.format(*input)
        
class Set_Player2(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['player']),
            Port(2, ['card']),
            Port(-1, ['bool'], description='changed?')
        ])

    def _get_default(self, p):
        match p:
            case 1:
                return 'self.player'
            case 2:
                return 'self'

    def _get_output(self, p):
        return '{1}.change_player({0})'.format(*self.get_input())
        
class Get_Spot(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['card']),
            Port(-1, ['spot'], description='spot')
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_output(self, p):
        return '{0}.spot'.format(*self.get_input())
        
class Get_Direction_Of(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['spot']),
            Port(-1, ['string'], description='direction')
        ])
        
    def _get_default(self, p):
        return 'self.spot'

    def _get_output(self, p):
        return 'self.spot.get_direction({0})'.format(*self.get_input())
        
class Get_Direction(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(-1, ['string'], description='direction')
        ])

    def _get_output(self, p):
        return 'self.direction'
        
class Set_Direction(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='direction'),
            Port(2, ['flow']),
            Port(-1, ['bool'], description='valid direction?'),
            Port(-2, ['flow'])
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return "''"
        
    def _get_output(self, p):
        return f'b{self.id}'

    def _get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output(-1))
        return '{0} = self.set_direction({1})\n'.format(*input)
        
class Get_Card_At(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='direction'),
            Port(2, ['bool'], description='check'),
            Port(3, ['flow']),
            Port(-1, ['card']),
            Port(-2, ['flow'])
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        match p:
            case 1:
                return 'self.direction'
            case 2:
                return 'True'
        
    def _get_output(self, p):
        return f'c{self.id}'

    def _get_text(self):
        ipp = mapping.find_all_input_ports(self)
        for ip in ipp:
            if 'card' in ip.types:
                ip.node.defaults[ip.port] = 'c'
                
        input = self.get_input()
        input.insert(0, self.get_output(-1))
        return '{0} = self.spot.get_card_at({1}, check=lambda c: {2})\n'.format(*input)
        
class Move_In(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['string'], description='direction'),
            Port(2, ['card']),
            Port(3, ['flow']),
            Port(-1, ['bool'], description='moved?'),
            Port(-2, ['flow'], description='direction')
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return 'self'
        
    def _get_output(self, p):
        return f'b{self.id}'

    def _get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output(-1))
        return '{0} = {2}.move_in({1})\n'.format(*input)
        
class Kill_Card(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['card']),
            Port(2, ['flow']),
            Port(-1, ['flow'])
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_text(self):
        return '{0}.kill(self)\n'.format(*self.get_input())
        
class Slide_Card(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['vec'], description='dx, dy'),
            Port(2, ['num'], description='max distance'),
            Port(3, ['card']),
            Port(4, ['flow']),
            Port(-1, ['num'], description='distance'),
            Port(-2, ['flow'])
        ])
        
        set_vec_element(self.get_port(1))
        set_input_element(self.get_port(2), 'num')
        self.get_port(2).hide()
        self.set_port_pos()
        
    def _get_default(self, p):
        match p:
            case 1:
                return '0'
            case 2:
                return '99'
            case 3:
                return 'self'
                
    def _get_output(self, p):
        return f'c{self.id}'

    def _get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output(-1))
        return '{0} = self.game.grid.slide({3}, {1}, max_dist={2})\n'.format(*input)
        
class Add_To_Private(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, ['player']),
            Port(2, ['card']),
            Port(3, ['flow']),
            Port(-1, ['flow'])
        ])
        
    def _get_default(self, p):
        match p:
            case 1:
                return 'self.player'
            case 2:
                return 'self'

    def _get_text(self):
        return "{0}.add_card('private', {1}.copy())\n".format(*self.get_input())