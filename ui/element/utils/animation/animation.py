from ....math.bezier import Bezier

class Animation:
    def __init__(
        self,
        
        element,
        attr,
        
        end,
        start=None,
        
        frames=1,
        delay=0,
        
        method='linear',
        strict=False
 
    ):
    
        self.element = element
        self.attr = attr
        
        if isinstance(end, int):
            end = [end]
        if isinstance(start, int):
            start = [start]

        self.start_value = start
        self.end_value = end
        self.auto_start = start is None
        
        self.frames = frames
        self.delay = delay
        
        self.method = method
        self.strict = strict
        
    @property
    def step_size(self):
        return 1 / self.frames
        
    @property
    def total_time(self):
        return self.frames + self.delay
        
    @property
    def equation(self):
        return getattr(Bezier, self.method)
        
    @property
    def current_value(self):
        return getattr(self.element, self.attr)
        
    def start(self):
        if self.auto_start and not self.start_value:
            start = self.current_value
            if isinstance(start, int):
                start = [start]
            elif start is None:
                start = [0 for _ in self.end_value]
            self.start_value = start
        else:
            self.set_value(self.start_value)
                
    def update(self, t):
        if self.start_value is None:
            self.start()

        cv = []
        for s, e in zip(self.start_value, self.end_value):
            v = s + ((e - s) * self.equation(t))
            if self.strict:
                v = int(round(v))
            cv.append(v)
        self.set_value(cv)

    def set_value(self, value):
        if value is not None:
            if len(value) == 1:
                value = value[0]
            else:
                value = tuple(value)
            setattr(self.element, self.attr, value)
 
    def end(self, reverse):
        self.set_value(self.end_value if not reverse else self.start_value) 
        if self.auto_start and reverse:
            self.start_value = None
            
            
            
            
            
            
        