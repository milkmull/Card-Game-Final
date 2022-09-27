from ..utils.animation.animation import Animation as _Animation
from ..utils.animation.sequence import Sequence

class Animation:
    def __init__(self):
        self.animations = {}
        self.active_animations = []
        self.frozen_tags = set()
        
    @property
    def moving(self):
        return any({a.attr in ('x', 'y', 'pos') for s in self.active_animations for a in s.sequence})
        
    def add_animation(self, animations, tag='temp', loop=False):
        for kwargs in animations:
            if 'element' not in kwargs:
                kwargs['element'] = self
  
        a = Sequence(
            [_Animation(**kwargs) for kwargs in animations], 
            tag=tag,
            loop=loop
        )

        if tag == 'temp':
            self.active_animations.append(a)
        else:
            if tag not in self.animations:
                self.animations[tag] = []
            self.animations[tag].append(a)
            
        return a
        
    def run_animations(self, tag, reverse=False):
        if tag in self.frozen_tags:
            return
            
        if (animations := self.animations.get(tag)):
            for a in animations:
                if a not in self.active_animations:
                    self.active_animations.append(a)
                a.start(reverse=reverse)
                    
    def cancel_animation(self, tag):
        if (animations := self.animations.get(tag)):
            for a in animations:
                a.cancel()
                if a in self.active_animations:
                    self.active_animations.remove(a)
                
    def freeze_animation(self, tag):
        self.frozen_tags.add(tag)
        
    def unfreeze_animation(self, tag):
        if tag in self.frozen_tags:
            self.frozen_tags.remove(tag)
        
    def unfreeze_all_animation(self):
        self.frozen_tags.clear()
                
    def update_animations(self):
        i = 0
        while i < len(self.active_animations):
            a = self.active_animations[i]
            a.step()
            if a.finished:
                self.active_animations.pop(i)
            else:
                i += 1
         