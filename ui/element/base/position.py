import pygame as pg

from .base import Base_Element

class AnchorError(Exception):
    def __init__(self, anchor):
        super().__init__(f"Invalid anchor '{anchor}'")

class Position(Base_Element):
    ANCHORS = (
        'left',
        'right',
        'centerx',
        'top',
        'bottom',
        'centery'
    )
    
    STUCK_ANCHORS = (
        'topleft',
        'midleft',
        'bottomleft',
        'midbottom',
        'bottomright',
        'midright',
        'topright',
        'midtop',
        'center'
    )
    
    @classmethod
    def check_anchor(cls, anchor):
        if anchor is not None:
            if anchor not in cls.ANCHORS:
                raise AnchorError(anchor)
                
    @classmethod
    def check_stuck_anchor(cls, anchor):
        if anchor is not None:
            if anchor not in cls.STUCK_ANCHORS:
                raise AnchorError(anchor)
    
    def __init__(
        self,
        
        x=0,
        y=0,
        pos=None,
        width=0,
        height=0,
        size=None,
        
        **kwargs
    ):
        super().__init__(**kwargs)
        
        if pos is not None:
            x, y = pos
        if size is not None:
            width, height = size
        self.rect = pg.Rect(x, y, width, height)

        self.parent = None
        
        self.stuck = False
        stuck_anchor = None
        self.stuck_pos = None
        
        self.anchors = {
            'left': (None, 0),
            'right': (None, 0),
            'centerx': (None, 0),
            'top': (None, 0),
            'bottom': (None, 0),
            'centery': (None, 0)
        }
        
        self.limits = {
            'left': None,
            'right': None,
            'top': None,
            'bottom': None
        }

        self.children = []
        
    @property
    def total_rect(self):
        self.update_position()
        return self.rect.unionall([c.total_rect for c in self.children if c.visible and isinstance(c, Position)])
        
    @property
    def all_children(self):
        children = set()
        for c in self.children:
            children.add(c)
            if hasattr(c, 'all_children'):
                children |= c.all_children
        return children

    @property
    def size(self):
        return self.rect.size
        
    @size.setter
    def size(self, size):
        self.rect.size = size
        
    @property
    def pos(self):
        return self.rect.topleft
        
    @pos.setter
    def pos(self, pos):
        self.rect.topleft = pos
        
    @property
    def x(self):
        return self.rect.x
        
    @x.setter
    def x(self, x):
        self.rect.x = x
        
    @property
    def y(self):
        return self.rect.y
        
    @y.setter
    def y(self, y):
        self.rect.y = y
        
    @property
    def width(self):
        return self.rect.width
        
    @width.setter
    def width(self, width):
        self.size = (width, self.rect.height)
        
    @property
    def height(self):
        return self.rect.height
        
    @height.setter
    def height(self, height):
        self.size = (self.rect.width, height)
        
    @property
    def centerx(self):
        return self.rect.centerx
        
    @centerx.setter
    def centerx(self, centerx):
        self.rect.centerx = centerx
        
    @property
    def centery(self):
        return self.rect.centery
        
    @centery.setter
    def centery(self, centery):
        self.rect.centery = centery
        
    @property
    def center(self):
        return self.rect.center
        
    @center.setter
    def center(self, center):
        self.rect.center = center
        
    @property
    def left_offset(self):
        return self.anchors['left'][1]
        
    @left_offset.setter
    def left_offset(self, left_offset):
        self.anchors['left'] = (self.anchors['left'][0], left_offset)
        
    @property
    def right_offset(self):
        return self.anchors['right'][1]
        
    @right_offset.setter
    def right_offset(self, right_offset):
        self.anchors['right'] = (self.anchors['right'][0], right_offset)
        
    @property
    def centerx_offset(self):
        return self.anchors['centerx'][1]
        
    @centerx_offset.setter
    def centerx_offset(self, centerx_offset):
        self.anchors['centerx'] = (self.anchors['centerx'][0], centerx_offset)
        
    @property
    def top_offset(self):
        return self.anchors['top'][1]
        
    @top_offset.setter
    def top_offset(self, top_offset):
        self.anchors['top'] = (self.anchors['top'][0], top_offset)
        
    @property
    def bottom_offset(self):
        return self.anchors['bottom'][1]
        
    @bottom_offset.setter
    def bottom_offset(self, bottom_offset):
        self.anchors['bottom'] = (self.anchors['bottom'][0], bottom_offset)
        
    @property
    def centery_offset(self):
        return self.anchors['centery'][1]
        
    @centery_offset.setter
    def centery_offset(self, centery_offset):
        self.anchors['centery'] = (self.anchors['centery'][0], centery_offset)

    @property
    def first_born(self):
        if self.children:
            return self.children[0]
            
    @property
    def last_born(self):
        if self.children:
            return self.children[-1]
            
    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)

    def collidepoint_all(self, p):
        if self.rect.collidepoint(p):
            return True
        for c in self.children:
            if c.collidepoint_all(p):
                return True
        return False
        
    def get_relative_position(self, o=None):
        if o is None:
            if self.parent:
                o = self.parent
            else:
                return self.rect.topleft
        return (self.rect.left - o.rect.left, self.rect.top - o.rect.top)

    def add_child(self, child, **kwargs):
        if child not in self.children:
            self.children.append(child)
        child.parent = None
        child.set_parent(self, **kwargs)    
        
    def remove_child(self, child):
        while child in self.children:
            self.children.remove(child)
            
    def clear_children(self):
        self.children.clear()
        
    def get_children(self):
        return self.children
            
    def move_children(self):
        for c in self.get_children():
            c.update_position()
            c.move_children()
            
    def hit_any(self, inclusive=False):
        p = pg.mouse.get_pos()
        if self.rect.collidepoint(p):
            return True
        return self.hit_children(inclusive=inclusive)
                
    def hit_children(self, inclusive=False):
        for c in self.children:
            if c.enabled or (not c.enabled and inclusive):
                if c.hit_any():
                    return True
            
    def copy_position(self, other):
        self.parent = other.parent
        self.stuck = other.stuck
        self.stuck_pos = other.stuck_pos
        self.stuck_anchor = other.stuck_anchor
        self.limits = other.limits.copy()
        self.anchors = {anchor: (a, o) for anchor, (a, o) in other.anchors.items()}

    def set_stuck(self, stuck, anchor='topleft'):
        self.stuck = stuck
        if stuck:
            Position.check_stuck_anchor(anchor)
            if self.parent:
                ax, ay = getattr(self.rect, anchor)
                px, py = self.parent.rect.topleft
                self.stuck_pos = (ax - px, ay - py)
            else:
                self.stuck_pos = getattr(self.rect, anchor)
            self.stuck_anchor = anchor
            
    def swap_stuck(self, other):
        self.stuck_pos, other.stuck_pos = other.stuck_pos, self.stuck_pos
        self.stuck_anchor, other.stuck_anchor = other.stuck_anchor, self.stuck_anchor

    def set_limits(
        self,
        left=None,
        right=None,
        top=None,
        bottom=None
    ):
        self.limits['left'] = left
        self.limits['right'] = right
        self.limits['top'] = top
        self.limits['bottom'] = bottom

    def set_anchors(
        self,
        
        left=None,
        left_offset=0,
        
        right=None,
        right_offset=0,
        
        centerx=None,
        centerx_offset=0,
        
        top=None,
        top_offset=0,
        
        bottom=None,
        bottom_offset=0,
        
        centery=None,
        centery_offset=0
    ):
        
        anchors = (
            left,
            right,
            centerx,
            top,
            bottom,
            centery
        )

        for anchor in anchors:
            Position.check_anchor(anchor)
        
        self.anchors['left'] = (left, left_offset)
        self.anchors['right'] = (right, right_offset)
        self.anchors['centerx'] = (centerx, centerx_offset)
        self.anchors['top'] = (top, top_offset)
        self.anchors['bottom'] = (bottom, bottom_offset)
        self.anchors['centery'] = (centery, centery_offset)
            
    def set_parent(
        self, 
        parent,
        
        current_offset=False,
        contain=False,
        center=False,
        
        left_limit=None,
        right_limit=None,
        top_limit=None,
        bottom_limit=None,
        
        left_anchor=None,
        left_offset=0,
        
        right_anchor=None,
        right_offset=0,
        
        centerx_anchor=None,
        centerx_offset=0,
        
        top_anchor=None,
        top_offset=0,
        
        bottom_anchor=None,
        bottom_offset=0,
        
        centery_anchor=None,
        centery_offset=0
    ):
        
        if self.parent is not None:
            self.parent.remove_child(self)
        self.parent = parent

        if contain:
            left_limit = right_limit = top_limit = bottom_limit = 0
            
        if center:
            centerx_anchor = 'centerx'
            centery_anchor = 'centery'
            centerx_offset = centery_offset = 0
            
        self.set_limits(
            left=left_limit,
            right=right_limit,
            top=top_limit,
            bottom=bottom_limit
        )
        
        self.set_anchors(
            left=left_anchor,
            left_offset=left_offset,
            
            right=right_anchor,
            right_offset=right_offset,
            
            centerx=centerx_anchor,
            centerx_offset=centerx_offset,
            
            top=top_anchor,
            top_offset=top_offset,
            
            bottom=bottom_anchor,
            bottom_offset=bottom_offset,
            
            centery=centery_anchor,
            centery_offset=centery_offset
        )
 
        self.set_stuck(False)
        self.update_position()
        if current_offset:
            self.set_stuck(True)
    
    def update_stuck(self):
        if self.parent:
            p = (
                self.parent.rect.x + self.stuck_pos[0],
                self.parent.rect.y + self.stuck_pos[1]
            )
            setattr(
                self.rect,
                self.stuck_anchor,
                p
            )
        else:
            setattr(self.rect, self.stuck_anchor, self.stuck_pos)
            
    def update_anchors(self):
        if self.anchors['left'][0] is not None and self.anchors['right'][0] is not None:
            self.rect.width = (
                (getattr(self.parent.rect, self.anchors['right'][0]) + self.anchors['right'][1]) -
                (getattr(self.parent.rect, self.anchors['left'][0]) + self.anchors['left'][1])
            )
        
        if self.anchors['centerx'][0] is not None:
            self.rect.centerx = getattr(self.parent.rect, self.anchors['centerx'][0]) + self.anchors['centerx'][1]
        if self.anchors['left'][0] is not None:
            self.rect.left = getattr(self.parent.rect, self.anchors['left'][0]) + self.anchors['left'][1]
        if self.anchors['right'][0] is not None:
            self.rect.right = getattr(self.parent.rect, self.anchors['right'][0]) + self.anchors['right'][1]
            
        if self.anchors['top'][0] is not None and self.anchors['bottom'][0] is not None:
            self.rect.height = (
                (getattr(self.parent.rect, self.anchors['bottom'][0]) + self.anchors['bottom'][1]) -
                (getattr(self.parent.rect, self.anchors['top'][0]) + self.anchors['top'][1])
            )
        
        if self.anchors['centery'][0] is not None:
            self.rect.centery = getattr(self.parent.rect, self.anchors['centery'][0]) + self.anchors['centery'][1]
        if self.anchors['top'][0] is not None:
            self.rect.top = getattr(self.parent.rect, self.anchors['top'][0]) + self.anchors['top'][1]
        if self.anchors['bottom'][0] is not None:
            self.rect.bottom = getattr(self.parent.rect, self.anchors['bottom'][0]) + self.anchors['bottom'][1]
            
    def update_limits(self):
        if self.limits['left'] is not None:
            if self.parent.rect.left - self.rect.left > self.limits['left']:
                self.rect.left = self.parent.rect.left - self.limits['left']
        if self.limits['right'] is not None:
            if self.rect.right - self.parent.rect.right > self.limits['right']:
                self.rect.right = self.parent.rect.right + self.limits['right']
        if self.limits['top'] is not None:
            if self.parent.rect.top - self.rect.top > self.limits['top']:
                self.rect.top = self.parent.rect.top - self.limits['top']
        if self.limits['bottom'] is not None:
            if self.rect.bottom - self.parent.rect.bottom > self.limits['bottom']:
                self.rect.bottom = self.parent.rect.bottom + self.limits['bottom']
        
    def update_position(self, all=False):
        if self.stuck:
            self.update_stuck()

        elif self.parent:
            self.update_anchors()
            self.update_limits()

        if all:
            for c in self.get_children():
                c.update_position(all=True)
                
    def set_cursor(self):
        for o in self.children:
            if o.visible and o.enabled:
                if o.set_cursor():
                    return True
                    
    def child_events(self, events):
        for c in sorted(self.children, key=lambda c: c.layer, reverse=True):
            if c.enabled:
                c.events(events)
                
    def events(self, events):
        self.child_events(events)

    def child_update(self):
        for c in self.children:
            if c.refresh:
                c.update()
   
    def update(self):
        self.update_position()
        self.child_update()
        
    def child_draw(self, surf):
        for c in sorted(self.children, key=lambda c: c.layer):
            if c.visible:
                c.draw(surf)
                
    def draw(self, surf):
        self.child_draw(surf)
        
    def draw_on(self, surf, rect, method=None):
        if method is None:
            method = self.draw
            
        self.update_position(all=True)
            
        dx, dy = rect.topleft
        self.rect.move_ip(-dx, -dy)
        self.move_children()
        method(surf)
        self.rect.move_ip(dx, dy)
        self.move_children()
     