from .animation import Animation

class Sequence:
    def __init__(
        self,
        sequence,
        tag='',
        loop=False,
        name=None,
        end_func=None
    ):

        self.sequence = sequence
        self.tag = tag
        self.loop = loop
        self.name = name
        self.end_func=end_func
        self.index = 0

        self.dir = 1
        self.t = 0
        self.current_frame = 0

        self.start_next()
        
    @property
    def animation(self):
        return self.sequence[self.index]

    @property
    def reverse(self):
        return self.dir == -1
        
    @property
    def finished(self):
        if self.dir == -1:
            return self.index == 0 and self.current_frame <= 0
        return self.index == len(self.sequence) - 1 and self.current_frame >= self.animation.total_time
            
    @property
    def finished_current(self):
        if self.dir == -1:
            return self.current_frame <= 0
        return self.current_frame >= self.animation.total_time
        
    @property
    def delayed(self):
        return self.current_frame <= self.animation.delay
        
    def add_animation(self, element, index=-1, **kwargs):
        a = Animation(element, **kwargs)
        self.sequence.insert(index, a)
        return a
        
    def start(self, reverse=False):
        f = self.finished
        self.dir = 1 if not reverse else -1
        self.t = 1 if reverse else 0
        if f and self.index == 0:
            self.start_next()
            
    def start_next(self):
        if not self.reverse:
            self.animation.start()
        self.current_frame = 0 if not self.reverse else self.animation.frames

    def step(self):
        if not self.finished:
            self.current_frame += self.dir
            
            if self.current_frame > self.animation.delay:
                self.t += (self.dir * self.animation.step_size)
                self.animation.update(self.t)

            if self.finished_current:
                self.end()
            
    def end(self):
        self.animation.end(self.reverse)
        if not self.finished:
            self.t = 0 if not self.reverse else 1
            self.index += self.dir
            self.start_next()
        elif self.loop:
            self.t = 0 if not self.reverse else 1
            self.index = (self.index + self.dir) % len(self.sequence)
            self.start_next()
        else:
            self.t = 1 if not self.reverse else 0   

    def cancel(self):
        self.index = 0
        self.dir = 1
        self.t = 0
        self.current_frame = 0
        for a in self.sequence[::-1]:
            a.end(True)
        