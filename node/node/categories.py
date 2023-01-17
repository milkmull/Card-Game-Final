from enum import StrEnum

class Categories(StrEnum):
    FUNCTION = "Function"
    PROCESS = "Process"
    BOOLEAN = "Boolean"
    NUMERIC = "Numeric"
    STRING = "String"
    CONTAINER = "Container"
    PLAYER = "Player"
    CARD = "Card"
    SPOT = "Spot"
    TYPES = "Types"
    OTHER = "Other"
    
    BASE = "Base"
    CONDITIONAL = "Conditional"
    OPERATORS = "Operators"
    COMPARE = "Compare"
    LOOP = "Loop"
    LISTS = "Lists"
    ATTRIBUTES = "Attributes"
    GRID = "Grid"
    MOVE = "Move"
    POINTS = "Points"
    MULTIPLIER = "Multiplier"
    
    SELECT = "Select"
    WAIT = "Wait"