
class Timer:
    def __init__(
        self,
        start_time=0,
        stop_time=None,
        time_step=1
    ):
        self.start_time = start_time
        self.stop_time = stop_time
        self.time_step = time_step
        self.time = start_time
        
    def __str__(self):
        return str(self.time)
        
    def __repr__(self):
        return str(self.time)
        
    def __bool__(self):
        return bool(self.time)
        
    def __eq__(self, time):
        return self.time == time
        
    def __gt__(self, time):
        return self.time > time
        
    def __lt__(self, time):
        return self.time < time
        
    def step(self, step=None):
        if step is None:
            step = self.time_step
        self.time += step
        if self.stop_time is not None:
            if self.time >= self.stop_time:
                self.reset()
                return True
        
    def set(self, time):
        self.time = time
        
    def reset(self):
        self.time = self.start_time