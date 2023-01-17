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
from .categories import Categories

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
    categories = ((Categories.FUNCTION, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, tag="func", **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.FLOW)
        ])

    def _get_text(self):
        return "\n\tdef play(self):\n"
        
class Remove(Node):
    categories = ((Categories.FUNCTION, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, tag="func", **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.FLOW)
        ])

    def _get_text(self):
        return "\n\tdef remove(self):\n"
        
class Move(Node):
    categories = ((Categories.FUNCTION, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, tag="func", **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.FLOW)
        ])

    def _get_text(self):
        return "\n\tdef move(self):\n"
        
class Run_Move(Node):
    categories = ((Categories.PROCESS, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, tag="func", **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW)
        ])

    def _get_text(self):
        return "self.move()\n"
        
class Update(Node):
    categories = ((Categories.FUNCTION, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, tag="func", **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.FLOW)
        ])

    def _get_text(self):
        return "\n\tdef update(self):\n"
        
class Spawn(Node):
    categories = ((Categories.FUNCTION, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, tag="func", **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.FLOW)
        ])

    def _get_text(self):
        return "\n\tdef spawn(self):\n"
        
class Multiplier(Node):
    categories = ((Categories.FUNCTION, Categories.MULTIPLIER),)
    def __init__(self, id, **kwargs):
        super().__init__(id, tag="func", **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.NUM, is_reference=True),
            Port(-2, Port_Types.CARD, is_reference=True),
            Port(-3, Port_Types.FLOW)
        ])
        
    def get_output(self, p):
        match p:
            case -1:
                return "m"
            case -2:
                return "card"

    def _get_text(self):
        return "\n\tdef multiply(self, card):\n"
        
    def _get_start(self):
        return "\t\tm = 1\n"
        
    def _get_end(self):
        return "\t\treturn m\n"
       
class If(Node):
    categories = (
        (Categories.PROCESS, Categories.CONDITIONAL), 
        (Categories.BOOLEAN, Categories.PROCESS)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="condition"),
            Port(2, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW, is_process=True),
            Port(-2, Port_Types.FLOW)
        ])

    def _get_default(self, p):
        if p == 1:
            return "True"
        
    def _get_text(self):
        return "if {0}:\n".format(*self.get_input()) 
        
class Elif(Node):
    categories = (
        (Categories.PROCESS, Categories.CONDITIONAL), 
        (Categories.BOOLEAN, Categories.PROCESS)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="condition"),
            Port(2, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW, is_process=True),
            Port(-2, Port_Types.FLOW)
        ])

    def can_connect(self, p0, n1, p1):
        if p0.port == 2:
            return isinstance(n1, (If, Elif))
        return True
 
    def _get_default(self, p):
        if p == 1:
            return "True"
        
    def _get_text(self): 
        return "elif {0}:\n".format(*self.get_input())
        
class Else(Node):
    categories = (
        (Categories.PROCESS, Categories.CONDITIONAL), 
        (Categories.BOOLEAN, Categories.PROCESS)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW, is_process=True),
            Port(-2, Port_Types.FLOW)
        ])
        
    def can_connect(self, p0, n1, p1):
        if p0.port == 2:
            return isinstance(n1, (If, Elif))
        return True
        
    def _get_text(self):
        return "else:\n" 
 
class Ternary(Node):
    categories = (
        (Categories.PROCESS, Categories.CONDITIONAL), 
        (Categories.BOOLEAN, Categories.PROCESS)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="if true"),
            Port(2, Port_Types.ANY_TYPE_OR_ARRAY, description="if false"),
            Port(3, Port_Types.ANY_TYPE_OR_ARRAY, description="condition"),
            Port(-1, Port_Types.NUM, description="out")
        ])
        
    def connection_update(self):
        c1 = self.get_port(1).connection
        c2 = self.get_port(2).connection
        if c1 and not c2:
            self.port_sync(1, 1, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(2, 1, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(-1, 1, Port_Types.NUM, default_is_array=False)
        elif c2 and not c1:
            self.port_sync(2, 2, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(1, 2, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(-1, 2, Port_Types.NUM, default_is_array=False)
        elif c1 and c2:
            self.port_sync(-1, 1, Port_Types.NUM, default_is_array=False)
        else:
            self.port_sync(1, 1, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(2, 1, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(-1, 1, Port_Types.NUM, default_is_array=False)
     
    def _get_default(self, p):
        if p == 1 or p == 2:
            return "1"
        elif p == 3:
            return "True"
        
    def _get_output(self, p):  
        return "({0} if {2} else {1})".format(*self.get_input())
 
class Bool(Node):
    categories = (
        (Categories.TYPES, Categories.BASE), 
        (Categories.BOOLEAN, Categories.BASE)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.BOOL)
        ])
        
        set_check_element(self.get_port(-1))
        self.set_port_pos()

    def _get_output(self, p):
        return self.get_port(-1).get_output()
        
class Num(Node):
    categories = (
        (Categories.TYPES, Categories.BASE), 
        (Categories.NUMERIC, Categories.BASE)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.NUM)
        ])
        
        set_input_element(self.get_port(-1))
        self.set_port_pos()
        
    def _get_default(self, p):
        return "0"

    def _get_output(self, p):
        return self.get_port(-1).get_output()
        
class String(Node):
    categories = ((Categories.TYPES, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.STRING)
        ])
        
        set_input_element(self.get_port(-1))
        self.set_port_pos()
        
    def _get_default(self, p):
        return "\"\""
        
    def _get_output(self, p):
        return self.get_port(-1).get_output()
        
class Extend(Node):
    categories = ((Categories.OTHER, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description=" "),
            Port(-1, Port_Types.BOOL, description=" ")
        ])
        
    def can_connect(self, p0, n1, p1):
        if p0.port == 1:
            self.get_port(-1).is_reference = p1.is_reference
        return True
        
    def connection_update(self):
        self.port_sync(-1, 1, Port_Types.BOOL, default_is_array=False)
        ip = self.get_port(1)
        if not ip.connection:
            self.clear_connections()
            self.get_port(-1).is_reference = False
        
    def _get_default(self, p):
        return "True"
        
    def _get_output(self, p):
        return self.get_input()[0]

class And(Node):
    categories = ((Categories.BOOLEAN, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="x"),
            Port(2, Port_Types.ANY_TYPE_OR_ARRAY, description="y"),
            Port(-1, Port_Types.BOOL, description="x and y")
        ])
        
    def _get_default(self, p):
        return "True"
        
    def _get_output(self, p): 
        return "({} and {})".format(*self.get_input())  
        
class Or(Node):
    categories = ((Categories.BOOLEAN, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="x"),
            Port(2, Port_Types.ANY_TYPE_OR_ARRAY, description="y"),
            Port(-1, Port_Types.BOOL, description="x or y")
        ])
        
    def _get_default(self, p):
        return "True"
        
    def _get_output(self, p):   
        return "({} or {})".format(*self.get_input()) 
        
class Not(Node):
    categories = ((Categories.BOOLEAN, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="x"),
            Port(-1, Port_Types.BOOL, description="not x")
        ])
        
    def _get_default(self, p):
        return "True"

    def _get_output(self, p):  
        return "(not {})".format(*self.get_input())
        
class Equal(Node):
    categories = (
        (Categories.BOOLEAN, Categories.COMPARE),
        (Categories.NUMERIC, Categories.COMPARE)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="x"),
            Port(2, Port_Types.ANY_TYPE_OR_ARRAY, description="y"),
            Port(-1, Port_Types.BOOL, description="x == y")
        ])
        
    def _get_default(self, p):
        ip = self.get_port(1)
        if ip.is_array:
            return "[]"
        match ip.type:
            case Port_Types.NUM:
                return "1"
            case Port_Types.STRING:
                return "\"\""
            case Port_Types.BOOL:
                return "True"
            case Port_Types.PLAYER:
                return "self.player"
            case Port_Types.CARD:
                return "self"
            case Port_Types.SPOT:
                return "self.spot"
            case _:
                return "None"

    def _get_output(self, p): 
        return "({} == {})".format(*self.get_input()) 
      
class Greater(Node):
    categories = (
        (Categories.BOOLEAN, Categories.COMPARE),
        (Categories.NUMERIC, Categories.COMPARE)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="x"),
            Port(2, Port_Types.NUM, description="y"),
            Port(-1, Port_Types.BOOL, description="x > y")
        ])
        
        set_input_element(self.get_port(1))
        set_input_element(self.get_port(2))
        self.set_port_pos()
        
    def _get_default(self, p):
        return "0"

    def _get_output(self, p):  
        return "({0} > {1})".format(*self.get_input())
        
class Less(Node):
    categories = (
        (Categories.BOOLEAN, Categories.COMPARE),
        (Categories.NUMERIC, Categories.COMPARE)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="x"),
            Port(2, Port_Types.NUM, description="y"),
            Port(-1, Port_Types.BOOL, description="x < y")
        ])
        
        set_input_element(self.get_port(1))
        set_input_element(self.get_port(2))
        self.set_port_pos()
        
    def _get_default(self, p):
        return "0"

    def _get_output(self, p):
        return "({0} < {1})".format(*self.get_input()) 
     
class Max(Node):
    categories = ((Categories.NUMERIC, Categories.COMPARE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="a"),
            Port(2, Port_Types.NUM, description="b"),
            Port(-1, Port_Types.NUM, description="max(a, b)")
        ])
        
    def _get_default(self, p):
        return "0"

    def _get_output(self, p): 
        return "max({0}, {1})".format(*self.get_input()) 
        
class Min(Node):
    categories = ((Categories.NUMERIC, Categories.COMPARE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="a"),
            Port(2, Port_Types.NUM, description="b"),
            Port(-1, Port_Types.NUM, description="min(a, b)")
        ])
        
    def _get_default(self, p):
        return "0"

    def _get_output(self, p):
        return "min({0}, {1})".format(*self.get_input())    
     
class Add(Node):
    categories = ((Categories.NUMERIC, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="a"),
            Port(2, Port_Types.NUM, description="b"),
            Port(-1, Port_Types.NUM, description="a + b")
        ])
        
        set_input_element(self.get_port(1))
        set_input_element(self.get_port(2))
        self.set_port_pos()
        
    def _get_default(self, p):
        return "0"
        
    def _get_output(self, p):
        return "({} + {})".format(*self.get_input())
        
class Increment(Node):
    categories = ((Categories.NUMERIC, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="a"),
            Port(-1, Port_Types.NUM, description="a + 1")
        ])
        
    def _get_default(self, p):
        return "0"
        
    def _get_output(self, p):
        return "({} + 1)".format(*self.get_input())
        
class Decrement(Node):
    categories = ((Categories.NUMERIC, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="a"),
            Port(-1, Port_Types.NUM, description="a - 1")
        ])
        
    def _get_default(self, p):
        return "0"
        
    def _get_output(self, p):
        return "({} - 1)".format(*self.get_input())
        
class Subtract(Node):
    categories = ((Categories.NUMERIC, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="a"),
            Port(2, Port_Types.NUM, description="b"),
            Port(-1, Port_Types.NUM, description="a - b")
        ])
        
        set_input_element(self.get_port(1))
        set_input_element(self.get_port(2))
        self.set_port_pos()
        
    def _get_default(self, p):
        return "0"
        
    def _get_output(self, p):
        return "({0} - {1})".format(*self.get_input())
        
class Multiply(Node):
    categories = ((Categories.NUMERIC, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="a"),
            Port(2, Port_Types.NUM, description="b"),
            Port(-1, Port_Types.NUM, description="a * b")
        ])
        
        set_input_element(self.get_port(1))
        set_input_element(self.get_port(2))
        self.set_port_pos()
        
    def _get_default(self, p):
        return "0"
        
    def _get_output(self, p):
        return "({0} * {1})".format(*self.get_input())
        
class Negate(Node):
    categories = ((Categories.NUMERIC, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="a"),
            Port(-1, Port_Types.NUM, description="-a")
        ])
        
    def _get_default(self, p):
        return "0"
        
    def _get_output(self, p):
        return "(-1 * {0})".format(*self.get_input())
        
class Divide(Node):
    categories = ((Categories.NUMERIC, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="a"),
            Port(2, Port_Types.NUM, description="b"),
            Port(-1, Port_Types.NUM, description="a / b")
        ])
        
        set_input_element(self.get_port(1))
        set_input_element(self.get_port(2))
        self.set_port_pos()
        
    def _get_default(self, p):
        return str(p)
        
    def _get_output(self, p):
        return "({0} // {1})".format(*self.get_input())
  
class Exists(Node):
    categories = ((Categories.BOOLEAN, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
            
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="x"),
            Port(-1, Port_Types.BOOL, description="x is not None")
        ])
        
    def _get_default(self, p):
        return "1"
        
    def _get_output(self, p):
        return "({0} is not None)".format(*self.get_input())
  
class For(Node):
    categories = ((Categories.PROCESS, Categories.LOOP),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE, description="list", is_array=True),
            Port(2, Port_Types.FLOW),
            Port(-1, Port_Types.NUM, description="list value"),
            Port(-2, Port_Types.FLOW, is_process=True),
            Port(-3, Port_Types.FLOW)
        ])

    def connection_update(self):
        self.port_sync(-1, 1, Port_Types.NUM)

    def get_loop_var(self):
        op = self.get_port(-1)
        match op.type:
            case Port_Types.PLAYER:
                return f"p{self.id}"  
            case Port_Types.CARD:
                return f"c{self.id}"
            case Port_Types.SPOT:
                return f"s{self.id}"
            case Port_Types.NUM:  
                return f"i{self.id}"
        
    def _get_default(self, p):
        if p == 1:
            return "range(1)"
        
    def _get_text(self):
        input = [self.get_output(-1)] + self.get_input()  
        return "for {0} in {1}:\n".format(*input)
        
    def _get_output(self, p):
        return self.get_loop_var()
        
class Break(Node):
    categories = ((Categories.PROCESS, Categories.LOOP),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, Port_Types.FLOW)
        ])
        
    def can_connect(self, *args):
        return self.scope_check(1, lambda p: isinstance(p.connection, For) and p.connection_port.is_process)
        
    def connection_update(self):
        if not self.scope_check(1, lambda p: isinstance(p.connection, For) and p.connection_port.is_process):
            self.get_port(1).clear()
        
    def _get_text(self):
        return "break\n"
        
class Continue(Node):
    categories = ((Categories.PROCESS, Categories.LOOP),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, Port_Types.FLOW)
        ])
        
    def can_connect(self, *args):
        return self.scope_check(1, lambda p: isinstance(p.connection, For) and p.connection_port.is_process)
        
    def connection_update(self):
        if not self.scope_check(1, lambda p: isinstance(p.connection, For) and p.connection_port.is_process):
            self.get_port(1).clear()
        
    def _get_text(self):
        return "continue\n"
        
class Range(Node):
    categories = ((Categories.NUMERIC, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="min"),
            Port(2, Port_Types.NUM, description="max"),
            Port(-1, Port_Types.NUM, description="[min, ..., max]", is_array=True)
        ])
        
        set_input_element(self.get_port(1))
        set_input_element(self.get_port(2))
        self.set_port_pos()
        
    def _get_default(self, p):
        return "0"
        
    def _get_output(self, p):
        return "range({0}, {1})".format(*self.get_input())
       
class Player(Node):
    categories = (
        (Categories.TYPES, Categories.BASE),
        (Categories.PLAYER, Categories.BASE)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(-1, Port_Types.PLAYER)
        ])

    def _get_output(self, p):
        return "self.player"
       
class All_Players(Node):
    categories = ((Categories.PLAYER, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(-1, Port_Types.PLAYER, description="player list", is_array=True)
        ])

    def _get_output(self, p):
        return "self.game.get_players()"
        
class Card(Node):
    categories = (
        (Categories.TYPES, Categories.BASE),
        (Categories.CARD, Categories.BASE)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(-1, Port_Types.CARD, description="this card")
        ])

    def _get_output(self, p):
        return "self"
         
class Has_Tag(Node):
    categories = ((Categories.CARD, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="tag"),
            Port(2, Port_Types.CARD),
            Port(-1, Port_Types.BOOL, description="card has tag")
        ])
        
        set_dropdown_element(self.get_port(1), TAGS_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "\"\""
        elif p == 2:
            return "self"
        
    def _get_output(self, p):
        return "{1}.has_tag({0})".format(*self.get_input())
      
class Get_Name(Node):
    categories = ((Categories.CARD, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.CARD),
            Port(-1, Port_Types.STRING, description="card name")
        ])
        
    def _get_default(self, p):
        return "self"
        
    def _get_output(self, p):
        return "{0}.name".format(*self.get_input()) 
      
class Has_Name(Node):
    categories = ((Categories.CARD, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="name"),
            Port(2, Port_Types.CARD),
            Port(-1, Port_Types.BOOL, description="card has name")
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "\"\""
        elif p == 2:
            return "self"
        
    def _get_output(self, p):
        return "{1}.has_name({0})".format(*self.get_input())
        
class Length(Node):
    categories = ((Categories.CONTAINER, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

        self.set_ports([
            Port(1, Port_Types.ANY_TYPE, description="list", is_array=True),
            Port(-1, Port_Types.NUM, description="length of list")
        ])
        
    def _get_default(self, port):
        return "[]"
        
    def _get_output(self, p):
        return "len({})".format(*self.get_input())
        
class Filter(Node):
    categories = ((Categories.CONTAINER, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="condition"),
            Port(2, Port_Types.ANY_TYPE, description="list", is_array=True),
            Port(-1, Port_Types.NUM, description="filtered list", is_array=True)
        ])
        
        set_check_element(self.get_port(1))
        self.set_port_pos()
        
    def get_list_var(self):
        return f"x{self.id}"
        
    def connection_update(self):
        self.port_sync(-1, 2, Port_Types.NUM)
            
    def _get_default(self, p):
        if p == 1:
            return "True"
        elif p == 2:
            return "[]"
            
    def _get_output(self, p):
        self.lambda_input(self.get_port(-1).type, self.get_list_var())
        input = self.get_input() + [self.get_list_var()]
        self.clear_lambda_input(self.get_port(-1).type)
        return "[{2} for {2} in {1} if {0}]".format(*input)

class Gain(Node):
    categories = ((Categories.PLAYER, Categories.POINTS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

        self.set_ports([
            Port(1, Port_Types.CARD, description="extra card"),
            Port(2, Port_Types.NUM, description="points"),
            Port(3, Port_Types.PLAYER),
            Port(4, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW)
        ])
        
        set_input_element(self.get_port(2))
        self.set_port_pos()
     
    def _get_default(self, p):
        match p:
            case 1:
                return "None"
            case 2:
                return "0"
            case 3:
                return "self.player"
        
    def _get_text(self):
        return "{2}.gain({1}, self, extra={0})\n".format(*self.get_input())      

class Steal(Node):
    categories = ((Categories.PLAYER, Categories.POINTS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, Port_Types.CARD, description="extra card"),
            Port(2, Port_Types.NUM, description="points"),
            Port(3, Port_Types.PLAYER),
            Port(4, Port_Types.PLAYER, description="target"),
            Port(5, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW)
        ])
        
        set_input_element(self.get_port(2))
        self.set_port_pos()
     
    def _get_default(self, p):
        match p:
            case 1:
                return "None"
            case 2:
                return "0"
            case 3 | 4:
                return "self.player"
        
    def _get_text(self):
        return "{2}.steal({1}, self, {3}, extra={0})\n".format(*self.get_input())      
          
class Start_Select(Node):
    categories = ((Categories.FUNCTION, Categories.SELECT),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, Port_Types.CARD, description="selection", is_array=True),
            Port(2, Port_Types.FLOW)
        ])

    def _get_text(self):
        return "self.player.start_select(self, {0})\n".format(*self.get_input())

class Select(Node):
    categories = ((Categories.FUNCTION, Categories.SELECT),)
    def __init__(self, id, **kwargs):
        super().__init__(id, tag="func", **kwargs) 
        
        self.set_ports([
            Port(-1, Port_Types.CARD, description="selected card"),
            Port(-2, Port_Types.FLOW)
        ])
            
    def _get_text(self):
        return "\n\tdef select(self, card):\n"
        
    def _get_output(self, p):
        return "card"

class Start_Wait(Node):
    categories = ((Categories.FUNCTION, Categories.WAIT),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="wait type"),
            Port(2, Port_Types.FLOW)
        ])
        
        set_dropdown_element(self.get_port(1), WAIT_DICT)
        self.set_port_pos()
                
    def _get_text(self):
        return "self.start_wait({0})".format(*self.get_input())
        
    def _get_default(self, p):
        return "\"\""
        
class Run_Wait(Node):
    categories = ((Categories.FUNCTION, Categories.WAIT),)
    def __init__(self, id, **kwargs):
        super().__init__(id, tag="func", **kwargs) 
        
        self.set_ports([
            Port(-1, ["log"], description="data"),
            Port(-2, Port_Types.FLOW)
        ])
            
    def _get_text(self):
        return "\n\tdef run_wait(self, data):\n"
       
class End_Wait(Node):
    categories = ((Categories.FUNCTION, Categories.WAIT),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW)
        ])
            
    def _get_text(self):
        return "self.end_wait()\n"

class Extract_Value(Node):
    categories = ((Categories.FUNCTION, Categories.WAIT),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs) 
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="key"),
            Port(2, Port_Types.ANY_TYPE, description="log"),
            Port(-1, Port_Types.NUM, description="value")
        ])
        
        set_dropdown_element(self.get_port(1), WAIT_KEYS_DICT, const=True)
        self.set_port_pos()
        
    def _get_output(self, p):
        return "{1}.get({0})".format(*self.get_input())
        
    def _get_default(self, p):
        match p:
            case 1:
                return "0"
            case 2:
                return "{}"
        
    def eval_text(self, text):
        match text:
            case "card":
                return Port_Types.CARD
            case "player":
                return Port_Types.PLAYER
        
    def connection_update(self):
        ip = self.get_port(1)
        op = self.get_port(-1)
        
        text = ip.value
        t = self.eval_text(text)
        if t and t != op.type:
            op.update_type(t)
       
class Index(Node):
    categories = ((Categories.CONTAINER, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.NUM, description="index"),
            Port(2, Port_Types.ANY_TYPE, description="list", is_array=True),
            Port(-1, Port_Types.NUM, description="list value at index")
        ])
        
        set_input_element(self.get_port(1))
        self.set_port_pos()
        
    def connection_update(self):
        self.port_sync(-1, 2, Port_Types.NUM)

    def _get_output(self, p):
        return "{1}[{0}]".format(*self.get_input())
        
    def _get_default(self, p):
        if p == 1:
            return "-1"
        elif p == 2:
            return "player.string_to_deck(\"private\")"
            
class Copy_Card(Node):
    categories = ((Categories.CARD, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.CARD),
            Port(-1, Port_Types.CARD, description="card copy")
        ])
        
    def _get_default(self, p):
        return "self"

    def _get_output(self, p):
        return "{0}.copy()".format(*self.get_input())
   
class Get_New_Card(Node):
    categories = (
        (Categories.TYPES, Categories.BASE),
        (Categories.CARD, Categories.BASE)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="card name"),
            Port(-1, Port_Types.CARD)
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        self.set_port_pos()

    def _get_output(self, p):
        return "self.game.get_card({0})".format(*self.get_input())
        
    def _get_default(self, p):
        return "self.name"
     
class Transfom(Node):
    categories = ((Categories.CARD, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="new card name"),
            Port(2, Port_Types.CARD),
            Port(-1, Port_Types.CARD, description="new card")
        ])
        
        set_dropdown_element(self.get_port(1), SORTED_NAMES_DICT)
        self.set_port_pos()
        
        
    def _get_default(self, p):
        match p:
            case 1:
                return "self.name"
            case 2:
                return "self"

    def _get_output(self, p):
        return "self.game.transform({2}, self.game.get_card({1}))".format(*self.get_input())
            
class Swap_With(Node):
    categories = ((Categories.CARD, Categories.MOVE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        
        self.set_ports([
            Port(1, Port_Types.CARD),
            Port(2, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW)
        ])

    def _get_text(self):
        return "self.swap_with({0})\n".format(*self.get_input())
        
    def _get_default(self, p):
        return "self"
              
class Get_Deck(Node):
    categories = (
        (Categories.PLAYER, Categories.ATTRIBUTES),
        (Categories.CARD, Categories.CONTAINER)
    )
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="deck name"),
            Port(2, Port_Types.PLAYER),
            Port(-1, Port_Types.CARD, description="deck", is_array=True)
        ])
        
        set_dropdown_element(self.get_port(1), DECKS_DICT, value="private")
        self.set_port_pos()
        
    def _get_default(self, p):
        if p == 1:
            return "\"private\""
        elif p == 2:
            return "player"
            
    def _get_output(self, p):
        return "{1}.string_to_deck({0})".format(*self.get_input())
        
class Get_Score(Node):
    categories = ((Categories.PLAYER, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.PLAYER),
            Port(-1, Port_Types.NUM, description="score")
        ])
        
    def _get_default(self, p):
        return "player"

    def _get_output(self, p):
        return "{0}.score".format(*self.get_input())
    
class Cards_From_Vector(Node):
    categories = ((Categories.CARD, Categories.GRID),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.VEC, description="dx, dy"),
            Port(2, Port_Types.NUM, description="steps"),
            Port(3, Port_Types.NUM, description="da"),
            Port(4, Port_Types.BOOL, description="condition"),
            Port(5, Port_Types.BOOL, description="stop on empty"),
            Port(6, Port_Types.BOOL, description="stop on fail"),
            Port(7, Port_Types.BOOL, description="reverse"),
            Port(-1, Port_Types.CARD, description="cards", is_array=True)
        ])
        
        set_vec_element(self.get_port(1))
        set_input_element(self.get_port(2))
        set_input_element(self.get_port(3))
        set_check_element(self.get_port(5))
        self.get_port(5).hide()
        set_check_element(self.get_port(6))
        set_check_element(self.get_port(7))
        self.get_port(7).hide()
        self.set_port_pos()
        
    def _get_default(self, p):
        match p:
            case 1:
                return "0"
            case 2:
                return "1"
            case 3:
                return "360"
            case 4:
                return "True"
            case 5 | 6 | 7:
                return "False"

    def _get_output(self, p):
        self.lambda_input(Port_Types.CARD, "c")
        input = self.get_input()
        self.clear_lambda_input(Port_Types.CARD)
                
        text = (
            "self.spot.cards_from_vector("
                "{0}, "
                "steps={1}, "
                "da={2}, "
                "check=lambda c: {3}, "
                "stop_on_empty={4}, "
                "stop_on_fail={5}, "
                "reverse={6}"
            ")"
        ).format(*input)
        return text
        
class Get_Spot_Group(Node):
    categories = ((Categories.CARD, Categories.GRID),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="group"),
            Port(-1, Port_Types.SPOT, description="spots", is_array=True)
        ])
        
        set_dropdown_element(self.get_port(1), LOCAL_GROUP_DICT, const=True)
        self.set_port_pos()
        
    def _get_output(self, p):
        return "self.spot.get_spot_group({0})".format(*self.get_input())
        
class Get_Card_Group(Node):
    categories = ((Categories.CARD, Categories.GRID),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="group"),
            Port(2, Port_Types.BOOL, description="check"),
            Port(-1, Port_Types.CARD, description="cards", is_array=True)
        ])
        
        set_dropdown_element(self.get_port(1), LOCAL_GROUP_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return "True"
        
    def _get_output(self, p):
        self.lambda_input(Port_Types.CARD, "c")
        input = self.get_input()
        self.clear_lambda_input(Port_Types.CARD)
        return "self.spot.get_card_group({0}, check=lambda c: {1})".format(*input)
        
class Register(Node):
    categories = ((Categories.CARD, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.CARD),
            Port(-1, Port_Types.BOOL, description="new card?")
        ])
        
    def _get_default(self, p):
        return "self"

    def _get_output(self, p):
        return "self.register({})".format(*self.get_input())
        
class Get_Player(Node):
    categories = ((Categories.CARD, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.CARD),
            Port(-1, Port_Types.PLAYER, description="owner")
        ])
        
    def _get_default(self, p):
        return "self"

    def _get_output(self, p):
        return "{0}.player".format(*self.get_input())

class Set_Player(Node):
    categories = ((Categories.CARD, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.PLAYER),
            Port(2, Port_Types.CARD),
            Port(-1, Port_Types.BOOL, description="changed?")
        ])

    def _get_default(self, p):
        match p:
            case 1:
                return "self.player"
            case 2:
                return "self"

    def _get_output(self, p):
        return "{1}.change_player({0})".format(*self.get_input())
        
class Get_Spot(Node):
    categories = ((Categories.CARD, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.CARD),
            Port(-1, Port_Types.SPOT)
        ])
        
    def _get_default(self, p):
        return "self"

    def _get_output(self, p):
        return "{0}.spot".format(*self.get_input())
        
class Get_Direction_Of(Node):
    categories = ((Categories.CARD, Categories.GRID),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.SPOT),
            Port(-1, Port_Types.STRING, description="direction")
        ])
        
    def _get_default(self, p):
        return "self.spot"

    def _get_output(self, p):
        return "self.spot.get_direction({0})".format(*self.get_input())
        
class Get_Direction(Node):
    categories = ((Categories.CARD, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(-1, Port_Types.STRING, description="direction")
        ])

    def _get_output(self, p):
        return "self.direction"
        
class Set_Direction(Node):
    categories = ((Categories.CARD, Categories.ATTRIBUTES),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="direction"),
            Port(-1, Port_Types.BOOL, description="valid direction?")
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return "\"\""

    def _get_output(self, p):
        return "self.set_direction({0})".format(*self.get_input())
        
class Get_Card_At(Node):
    categories = ((Categories.CARD, Categories.GRID),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="direction"),
            Port(2, Port_Types.BOOL, description="check"),
            Port(-1, Port_Types.CARD)
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        match p:
            case 1:
                return "self.direction"
            case 2:
                return "True"

    def _get_output(self, p):
        self.lambda_input(Port_Types.CARD, "c")
        input = self.get_input()
        self.clear_lambda_input(Port_Types.CARD)
        return "self.spot.get_card_at({0}, check=lambda c: {1})".format(*input)
        
class Get_Spot_At(Node):
    categories = ((Categories.CARD, Categories.GRID),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="direction"),
            Port(-1, Port_Types.SPOT)
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return "self.direction"

    def _get_output(self, p):
        return "self.spot.get_spot_at({0})".format(*self.get_input())
        
class Copy_To(Node):
    categories = ((Categories.CARD, Categories.MOVE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.SPOT),
            Port(-1, Port_Types.BOOL, description="coppied?")
        ])
        
    def _get_default(self, p):
        return "self.spot"

    def _get_output(self, p):
        return "self.copy_to({0})".format(*self.get_input())
        
class Move_In(Node):
    categories = ((Categories.CARD, Categories.MOVE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.STRING, description="direction"),
            Port(2, Port_Types.CARD),
            Port(-1, Port_Types.BOOL, description="moved?")
        ])
        
        set_dropdown_element(self.get_port(1), DIRECTIONS_DICT, const=True)
        self.set_port_pos()
        
    def _get_default(self, p):
        return "self"

    def _get_output(self, p):
        return "{1}.move_in({0})".format(*self.get_input())
        
class Kill_Card(Node):
    categories = ((Categories.CARD, Categories.OPERATORS),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.CARD),
            Port(2, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW)
        ])
        
    def _get_default(self, p):
        return "self"

    def _get_text(self):
        return "{0}.kill(self)\n".format(*self.get_input())
        
class Slide_Card(Node):
    categories = ((Categories.CARD, Categories.MOVE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.VEC, description="dx, dy"),
            Port(2, Port_Types.NUM, description="max distance"),
            Port(3, Port_Types.CARD),
            Port(-1, Port_Types.NUM, description="distance")
        ])
        
        set_vec_element(self.get_port(1))
        set_input_element(self.get_port(2))
        self.get_port(2).hide()
        self.set_port_pos()
        
    def _get_default(self, p):
        match p:
            case 1:
                return "0"
            case 2:
                return "99"
            case 3:
                return "self"

    def _get_output(self, p):
        return "self.game.grid.slide({2}, {0}, max_dist={1})".format(*self.get_input())
        
class Add_To_Private(Node):
    categories = ((Categories.PLAYER, Categories.CARD),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.PLAYER),
            Port(2, Port_Types.CARD),
            Port(3, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW)
        ])
        
    def _get_default(self, p):
        match p:
            case 1:
                return "self.player"
            case 2:
                return "self"

    def _get_text(self):
        return "{0}.add_card(\"private\", {1}.copy())\n".format(*self.get_input())
        
class Process(Node):
    categories = ((Categories.PROCESS, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  

        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="value"),
            Port(2, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW)
        ])

    def _get_default(self, p):
        return ""
        
    def _get_text(self): 
        return "{0}\n".format(*self.get_input())
        
class Store_Value(Node):
    categories = ((Categories.PROCESS, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  

        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="value"),
            Port(2, Port_Types.FLOW),
            Port(-1, Port_Types.NUM, description="value", is_reference=True),
            Port(-2, Port_Types.FLOW)
        ])

    def connection_update(self):
        self.port_sync(-1, 1, Port_Types.NUM, default_is_array=False)

    def _get_output(self, p):
        return f"value_{self.id}"
        
    def _get_default(self, p):
        return "0"
        
    def _get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output(-1))
        return "{0} = {1}\n".format(*input) 
        
class Set_Value(Node):
    categories = ((Categories.PROCESS, Categories.BASE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)  

        self.set_ports([
            Port(1, Port_Types.ANY_TYPE_OR_ARRAY, description="new value"),
            Port(2, Port_Types.ANY_TYPE_OR_ARRAY, description="value"),
            Port(3, Port_Types.FLOW),
            Port(-1, Port_Types.NUM, description="value", is_reference=True),
            Port(-2, Port_Types.FLOW)
        ])
        
    def can_connect(self, p0, n1, p1):
        if p0.port != 2:
            return True
        return p1.is_reference

    def connection_update(self):
        c1 = self.get_port(1).connection
        c2 = self.get_port(2).connection
        if c1 and not c2:
            self.port_sync(1, 1, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(2, 1, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(-1, 1, Port_Types.NUM, default_is_array=False)
        elif c2 and not c1:
            self.port_sync(2, 2, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(1, 2, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(-1, 2, Port_Types.NUM, default_is_array=False)
        elif c1 and c2:
            self.port_sync(-1, 1, Port_Types.NUM, default_is_array=False)
        else:
            self.port_sync(1, 1, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(2, 1, Port_Types.ANY_TYPE_OR_ARRAY, default_is_array=False)
            self.port_sync(-1, 1, Port_Types.NUM, default_is_array=False)
            
    def _get_output(self, p):
        ip = self.get_port(2)
        if ip.connection:
            return ip.connection._get_output(ip.connection_port.port)
        return f"value_{self.id}"
        
    def _get_default(self, p):
        print(p)
        match p:
            case 1:
                return "0"
            case 2:
                return f"value_{self.id}"
        
    def _get_text(self):
        return "{1} = {0}\n".format(*self.get_input()) 
        
class Skip_Next_Move(Node):
    categories = ((Categories.CARD, Categories.MOVE),)
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)   
        
        self.set_ports([
            Port(1, Port_Types.FLOW),
            Port(-1, Port_Types.FLOW)
        ])

    def _get_text(self, p):
        return "self.skip_move = True\n"
        
        