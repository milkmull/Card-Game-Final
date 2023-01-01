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
from .node_base import Node, Port, Port_Types

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
            Port(-1, [Port_Types.FLOW])
        ])

    def _get_text(self):
        return '\n\tdef play(self):\n'
        
class Remove(Node):
    cat = 'func'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs)
        
        self.set_ports([
            Port(-1, [Port_Types.FLOW])
        ])

    def _get_text(self):
        return '\n\tdef remove(self):\n'
        
class Move(Node):
    cat = 'func'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs)
        
        self.set_ports([
            Port(-1, [Port_Types.FLOW])
        ])

    def _get_text(self):
        return '\n\tdef move(self):\n'
        
class Update(Node):
    cat = 'func'
    def __init__(self, id, **kwargs):
        super().__init__(id, tag='func', **kwargs)
        
        self.set_ports([
            Port(-1, [Port_Types.FLOW])
        ])

    def _get_text(self):
        return '\n\tdef update(self):\n'
       
class If(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, [Port_Types.ANY], description='condition'),
            Port(2, [Port_Types.FLOW]),
            Port(-1, [Port_Types.PROCESS, Port_Types.FLOW]),
            Port(-2, [Port_Types.FLOW])
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
            Port(1, [Port_Types.ANY], description='condition'),
            Port(2, [Port_Types.FLOW]),
            Port(-1, [Port_Types.PROCESS, Port_Types.FLOW]),
            Port(-2, [Port_Types.FLOW])
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
            Port(1, [Port_Types.FLOW]),
            Port(-1, [Port_Types.PROCESS, Port_Types.FLOW]),
            Port(-2, [Port_Types.FLOW])
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
            Port(1, [Port_Types.NUM], description='if true'),
            Port(2, [Port_Types.NUM], description='if false'),
            Port(3, [Port_Types.ANY]),
            Port(-1, [Port_Types.NUM], description='out')
        ])
        
        set_input_element(self.get_port(1), 'num')
        set_input_element(self.get_port(2), 'num')
        self.set_port_pos()
        get_transform_button(self)
   
    def tf(self, form=None):
        ip1 = self.get_port(1)
        ip2 = self.get_port(2)
        op = self.get_port(-1)
        
        if form == 1 or (form is None and ip1.has_type(Port_Types.NUM)):
            ip1.set_types([Port_Types.STRING])
            set_input_element(ip1, 'string')
            ip2.set_types([Port_Types.STRING])
            set_input_element(ip2, 'string')
            op.set_types([Port_Types.STRING])
            self.form = 1
        elif form == 2 or (form is None and Port_Types.STRING in ip1.types):
            ip1.set_types([Port_Types.PLAYER])
            ip1.clear_element()
            ip2.set_types([Port_Types.PLAYER])
            ip2.clear_element()
            op.set_types([Port_Types.PLAYER])
            self.form = 2
        elif form == 3 or (form is None and Port_Types.PLAYER in ip1.types):
            ip1.set_types([Port_Types.CARD])
            ip1.clear_element()
            ip2.set_types([Port_Types.CARD])
            ip2.clear_element()
            op.set_types([Port_Types.CARD])
            self.form = 3
        elif form == 0 or (form is None and Port_Types.CARD in ip1.types):
            ip1.set_types([Port_Types.NUM])
            set_input_element(ip1, 'num')
            ip2.set_types([Port_Types.NUM])
            set_input_element(ip2, 'num')
            op.set_types([Port_Types.NUM])
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
            Port(-1, [Port_Types.BOOL])
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
            Port(-1, [Port_Types.NUM])
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
            Port(-1, [Port_Types.STRING])
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
            Port(1, [Port_Types.ANY], description=' '),
            Port(-1, [Port_Types.BOOL], description=' ')
        ])
        
    def connection_update(self):
        ip = self.get_port(1)
        op = self.get_port(-1)

        if ip.connection:
            t = ip.connection_port.types[0]
            if t not in op.types:
                op.update_types([t])
        elif Port_Types.BOOL not in op.types:
            op.update_types([Port_Types.BOOL])
        
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
            Port(1, [Port_Types.ANY], description='x'),
            Port(2, [Port_Types.ANY], description='y'),
            Port(-1, [Port_Types.BOOL], description='x and y')
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
            Port(1, [Port_Types.ANY], description='x'),
            Port(2, [Port_Types.ANY], description='y'),
            Port(-1, [Port_Types.BOOL], description='x or y')
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
            Port(1, [Port_Types.ANY], description='x'),
            Port(-1, [Port_Types.BOOL], description='not x')
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

        self.set_ports([
            Port(1, [Port_Types.ANY], description='x'),
            Port(2, [Port_Types.ANY], description='y'),
            Port(-1, [Port_Types.BOOL], description='x == y')
        ])
        
    def _get_default(self, p):
        ip = self.get_port(1)
        if Port_Types.NUM in ip.types:
            return '1'
        elif Port_Types.STRING in ip.types:
            return "''"
        elif Port_Types.BOOL in ip.types:
            return 'True'
        elif Port_Types.PLAYER in ip.types:
            return 'self.player'
        elif Port_Types.CARD in ip.types:
            return 'self'
        elif Port_Types.SPOT in ip.types:
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
            Port(1, [Port_Types.NUM], description='x'),
            Port(2, [Port_Types.NUM], description='y'),
            Port(-1, [Port_Types.BOOL], description='x > y')
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
            Port(1, [Port_Types.NUM], description='x'),
            Port(2, [Port_Types.NUM], description='y'),
            Port(-1, [Port_Types.BOOL], description='x < y')
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
            Port(1, [Port_Types.NUM_SEQUENCE], description='[0, 1, 2...]'),
            Port(2, [Port_Types.NUM_SEQUENCE], description='[0, 1, 2...]'),
            Port(-1, [Port_Types.NUM], description='max value')
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
            Port(1, [Port_Types.NUM_SEQUENCE], description='[0, 1, 2...]'),
            Port(-1, [Port_Types.NUM], description='min value')
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
            Port(1, [Port_Types.NUM], description='a'),
            Port(2, [Port_Types.NUM], description='b'),
            Port(-1, [Port_Types.NUM], description='a + b')
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
            Port(1, [Port_Types.NUM], description='a'),
            Port(-1, [Port_Types.NUM], description='a + 1')
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
            Port(1, [Port_Types.NUM], description='a'),
            Port(-1, [Port_Types.NUM], description='a - 1')
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
            Port(1, [Port_Types.NUM], description='a'),
            Port(2, [Port_Types.NUM], description='b'),
            Port(-1, [Port_Types.NUM], description='a - b')
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
            Port(1, [Port_Types.NUM], description='a'),
            Port(2, [Port_Types.NUM], description='b'),
            Port(-1, [Port_Types.NUM], description='a * b')
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
            Port(1, [Port_Types.NUM], description='a'),
            Port(-1, [Port_Types.NUM], description='-a')
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
            Port(1, [Port_Types.NUM], description='a'),
            Port(2, [Port_Types.NUM], description='b'),
            Port(-1, [Port_Types.NUM], description='a / b')
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
            Port(1, [Port_Types.PLAYER, Port_Types.CARD], description='x'),
            Port(-1, [Port_Types.BOOL], description='x is not None')
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
            Port(1, [Port_Types.ANY_SEQUENCE], description='list'),
            Port(2, [Port_Types.FLOW]),
            Port(-1, [Port_Types.NUM], description='list value'),
            Port(-2, [Port_Types.PROCESS, Port_Types.FLOW]),
            Port(-3, [Port_Types.FLOW])
        ])

    def connection_update(self):
        ip = self.get_port(1)
        op = self.get_port(-1)

        if ip.connection:
            t = ip.connection_port.get_contains()
            if t not in op.types:
                op.update_types([t])
        elif Port_Types.NUM not in op.types:
            op.update_types([Port_Types.NUM])

    def get_loop_var(self):
        op = self.get_port(-1)
        match op.types[0]:
            case Port_Types.PLAYER:
                return f'p{self.id}'  
            case Port_Types.CARD:
                return f'c{self.id}'
            case Port_Types.SPOT:
                return f's{self.id}'
            case Port_Types.NUM:  
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
        
class Break(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, [Port_Types.FLOW])
        ])
        
    def connection_update(self):
        ip = self.get_port(1)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True, in_type=Port_Types.FLOW)
            for p in ports:
                if p.connection:
                    if isinstance(p.connection, For) and p.connection_port.has_type(Port_Types.PROCESS):
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
            Port(1, [Port_Types.FLOW])
        ])
        
    def connection_update(self):
        ip = self.get_port(1)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True, in_type=Port_Types.FLOW)
            for p in ports:
                if p.connection:
                    if isinstance(p.connection, For) and p.connection_port.has_type(Port_Types.PROCESS):
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
            Port(1, [Port_Types.NUM], description='min'),
            Port(2, [Port_Types.NUM], description='max'),
            Port(-1, [Port_Types.NUM_SEQUENCE], description='[min, ..., max]')
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
            Port(-1, [Port_Types.PLAYER])
        ])

    def _get_output(self, p):
        return 'self.player'
       
class All_Players(Node):
    cat = 'player'
    subcat = 'lists'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, [Port_Types.PLAYER_SEQUENCE], description='player list')
        ])

    def _get_output(self, p):
        return 'self.game.get_players()'
        
class Card(Node):
    cat = 'card'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(-1, [Port_Types.CARD], description='this card')
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
            Port(-1, [Port_Types.NUM], description='length of list')
        ])
        
    def _get_default(self, port):
        return '[]'
        
    def _get_output(self, p):
        return 'len({})'.format(*self.get_input())
         
class Has_Tag(Node):
    cat = 'card'
    subcat = 'boolean'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.STRING], description='tag'),
            Port(2, [Port_Types.CARD]),
            Port(-1, [Port_Types.BOOL], description='card has tag')
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
            Port(1, [Port_Types.CARD]),
            Port(-1, [Port_Types.STRING], description='card name')
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
            Port(1, [Port_Types.STRING], description='name'),
            Port(2, [Port_Types.CARD]),
            Port(-1, [Port_Types.BOOL], description='card has name')
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
            Port(1, [Port_Types.ANY], description='condition'),
            Port(2, [Port_Types.ANY_SEQUENCE], description='list'),
            Port(-1, [Port_Types.NUM_SEQUENCE], description='filtered list')
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
        elif Port_Types.NUM_SEQUENCE not in op.types:
            op.update_types([Port_Types.NUM_SEQUENCE])
            
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
            Port(1, [Port_Types.CARD], description='extra card'),
            Port(2, [Port_Types.NUM], description='points'),
            Port(3, [Port_Types.PLAYER]),
            Port(4, [Port_Types.FLOW]),
            Port(-1, [Port_Types.FLOW])
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
            Port(1, [Port_Types.CARD], description='extra card'),
            Port(2, [Port_Types.NUM], description='points'),
            Port(3, [Port_Types.PLAYER]),
            Port(4, [Port_Types.PLAYER], description='target'),
            Port(5, [Port_Types.FLOW]),
            Port(-1, [Port_Types.FLOW])
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
            Port(2, [Port_Types.FLOW])
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
            Port(-1, [Port_Types.CARD], description='selected card'),
            Port(-2, [Port_Types.FLOW])
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
            Port(1, [Port_Types.STRING], description='wait type'),
            Port(2, [Port_Types.FLOW])
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
            Port(-2, [Port_Types.FLOW])
        ])
            
    def _get_text(self):
        return '\n\tdef run_wait(self, data):\n'
       
class End_Wait(Node):
    cat = 'func'
    subcat = 'wait'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, [Port_Types.FLOW]),
            Port(-1, [Port_Types.FLOW])
        ])
            
    def _get_text(self):
        return 'self.end_wait()\n'

class Extract_Value(Node):
    cat = 'func'
    subcat = 'wait'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, [Port_Types.STRING], description='key'),
            Port(2, ['log'], description='log'),
            Port(-1, [Port_Types.NUM], description='value')
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
            Port(1, [Port_Types.NUM], description='index'),
            Port(2, [Port_Types.PLAYER_SEQUENCE], description='list'),
            Port(-1, [Port_Types.PLAYER], description='list value at index')
        ])
        
        set_input_element(self.get_port(1), 'num')
        self.set_port_pos()
        get_transform_button(self)
        
    def tf(self, form=None):
        ip = self.get_port(2)
        op = self.get_port(-1)
        
        if form == 1 or (form is None and Port_Types.SPOT_SEQUENCE in ip.types):
            ip.set_types(['cs'])
            op.set_types([Port_Types.CARD])
            self.form = 1
        elif form == 2 or (form is None and 'cs' in ip.types):
            ip.set_types([Port_Types.PLAYER_SEQUENCE])
            op.set_types([Port_Types.PLAYER])
            self.form = 2
        elif form == 0 or (form is None and Port_Types.PLAYER_SEQUENCE in ip.types):
            ip.set_types([Port_Types.SPOT_SEQUENCE])
            op.set_types([Port_Types.SPOT])
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
            Port(1, [Port_Types.CARD]),
            Port(-1, [Port_Types.CARD], description='card copy')
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
            Port(1, [Port_Types.STRING], description='card name'),
            Port(-1, [Port_Types.CARD])
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
            Port(1, [Port_Types.STRING], description='new card name'),
            Port(2, [Port_Types.CARD]),
            Port(-1, [Port_Types.CARD], description='new card')
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        self.set_port_pos()
        
        
    def _get_default(self, p):
        match p:
            case 1:
                return 'self.name'
            case 2:
                return 'self'

    def _get_output(self, p):
        text = 'self.game.transform({2}, self.game.get_card({1}))'.format(*self.get_input())
        return text
            
class Swap_With(Node):
    cat = 'card'
    subcat = 'operators'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, [Port_Types.CARD]),
            Port(2, [Port_Types.FLOW]),
            Port(-1, [Port_Types.FLOW])
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
            Port(1, [Port_Types.STRING], description='deck name'),
            Port(2, [Port_Types.PLAYER]),
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
            Port(1, [Port_Types.PLAYER]),
            Port(-1, [Port_Types.NUM], description='score')
        ])
        
    def _get_default(self, p):
        return 'player'

    def _get_output(self, p):
        return "{0}.score".format(*self.get_input())
    
class Cards_From_Vector(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.VEC], description='dx, dy'),
            Port(2, [Port_Types.NUM], description='steps'),
            Port(3, [Port_Types.NUM], description='da'),
            Port(4, [Port_Types.BOOL], description='condition'),
            Port(5, [Port_Types.BOOL], description='stop on empty'),
            Port(6, [Port_Types.BOOL], description='stop on fail'),
            Port(7, [Port_Types.BOOL], description='reverse'),
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
            if Port_Types.CARD in ip.types:
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
            Port(1, [Port_Types.STRING], description='group'),
            Port(-1, [Port_Types.SPOT_SEQUENCE], description='spots')
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
            Port(1, [Port_Types.STRING], description='group'),
            Port(2, [Port_Types.BOOL], description='check'),
            Port(-1, ['cs'], description='spots')
        ])
        
        set_dropdown_element(self.get_port(1), LOCAL_GROUP_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return 'True'
        
    def _get_output(self, p):
        ipp = mapping.find_all_input_ports(self)
        for ip in ipp:
            if Port_Types.CARD in ip.types:
                ip.node.defaults[ip.port] = 'c'
                
        text = 'self.spot.get_card_group({0}, check=lambda c: {1})'.format(*self.get_input())
        return text
        
class Register(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.CARD]),
            Port(-1, [Port_Types.BOOL], description='new card?')
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_output(self, p):
        return 'self.register({})'.format(*self.get_input())
        
class Get_Player(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.CARD]),
            Port(-1, [Port_Types.PLAYER], description='owner')
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_output(self, p):
        return '{0}.player'.format(*self.get_input())

class Set_Player(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.PLAYER]),
            Port(2, [Port_Types.CARD]),
            Port(-1, [Port_Types.BOOL], description='changed?')
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
            Port(1, [Port_Types.CARD]),
            Port(-1, [Port_Types.SPOT])
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_output(self, p):
        return '{0}.spot'.format(*self.get_input())
        
class Get_Direction_Of(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.SPOT]),
            Port(-1, [Port_Types.STRING], description='direction')
        ])
        
    def _get_default(self, p):
        return 'self.spot'

    def _get_output(self, p):
        return 'self.spot.get_direction({0})'.format(*self.get_input())
        
class Get_Direction(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(-1, [Port_Types.STRING], description='direction')
        ])

    def _get_output(self, p):
        return 'self.direction'
        
class Set_Direction(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.STRING], description='direction'),
            Port(-1, [Port_Types.BOOL], description='valid direction?')
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return "''"

    def _get_output(self, p):
        return 'self.set_direction({0})'.format(*self.get_input())
        
class Get_Card_At(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.STRING], description='direction'),
            Port(2, [Port_Types.BOOL], description='check'),
            Port(-1, [Port_Types.CARD])
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
        ipp = mapping.find_all_input_ports(self)
        for ip in ipp:
            if Port_Types.CARD in ip.types:
                ip.node.defaults[ip.port] = 'c'
                
        return 'self.spot.get_card_at({0}, check=lambda c: {1})'.format(*self.get_input())
        
class Get_Spot_At(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.STRING], description='direction'),
            Port(-1, [Port_Types.SPOT])
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return 'self.direction'

    def _get_output(self, p):
        return 'self.spot.get_spot_at({0})'.format(*self.get_input())
        
class Copy_To(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.SPOT]),
            Port(-1, [Port_Types.BOOL], description='coppied?')
        ])
        
    def _get_default(self, p):
        return 'self.spot'

    def _get_output(self, p):
        return 'self.copy_to({0})'.format(*self.get_input())
        
class Move_In(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.STRING], description='direction'),
            Port(2, [Port_Types.CARD]),
            Port(-1, [Port_Types.BOOL], description='moved?')
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return 'self'

    def _get_output(self, p):
        return '{1}.move_in({0})'.format(*self.get_input())
        
class Kill_Card(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.CARD]),
            Port(2, [Port_Types.FLOW]),
            Port(-1, [Port_Types.FLOW])
        ])
        
    def _get_default(self, p):
        return 'self'

    def _get_text(self):
        return '{0}.kill(self)\n'.format(*self.get_input())
        
class Slide_Card(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.VEC], description='dx, dy'),
            Port(2, [Port_Types.NUM], description='max distance'),
            Port(3, [Port_Types.CARD]),
            Port(-1, [Port_Types.NUM], description='distance')
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
        return 'self.game.grid.slide({2}, {0}, max_dist={1})'.format(*self.get_input())
        
class Add_To_Private(Node):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, [Port_Types.PLAYER]),
            Port(2, [Port_Types.CARD]),
            Port(3, [Port_Types.FLOW]),
            Port(-1, [Port_Types.FLOW])
        ])
        
    def _get_default(self, p):
        match p:
            case 1:
                return 'self.player'
            case 2:
                return 'self'

    def _get_text(self):
        return "{0}.add_card('private', {1}.copy())\n".format(*self.get_input())
        
class Process(Node):
    cat = 'flow'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  

        self.set_ports([
            Port(1, [Port_Types.ANY], description='value'),
            Port(2, [Port_Types.FLOW]),
            Port(-1, [Port_Types.FLOW])
        ])

    def _get_default(self, p):
        return ''
        
    def _get_text(self):
        text = '{0}\n'.format(*self.get_input())   
        return text
        
class Store_Value(Node):
    cat = 'flow'
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  

        self.set_ports([
            Port(1, [Port_Types.ANY], description='value'),
            Port(2, [Port_Types.FLOW]),
            Port(-1, [Port_Types.NUM], description='value'),
            Port(-2, [Port_Types.FLOW])
        ])

    def connection_update(self):
        ip = self.get_port(1)
        op = self.get_port(-1)

        if ip.connection:
            t = ip.connection_port.types[0]
            if t not in op.types:
                op.update_types([t])
        elif Port_Types.NUM not in op.types:
            op.update_types([Port_Types.NUM])

    def _get_output(self, p):
        return f'value_{self.id}'
        
    def _get_default(self, p):
        return '0'
        
    def _get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output(-1))
        text = '{0} = {1}\n'.format(*input)   
        return text