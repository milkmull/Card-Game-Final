class Event:
    def __init__(
        self,
        
        func=None,
        args=None,
        kwargs=None,
        
        no_call=False
    ):
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.return_value = None
        
        self.no_call = no_call
        
    def __call__(self):
        if self.func is not None:
            self.return_value = self.func(
                *[(a if self.no_call or not callable(a) else a()) for a in self.args],
                **{key: (value if self.no_call or not callable(value) else value()) for key, value in self.kwargs.items()}
            )
            return self.return_value
        
    def set_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def set_func(self, func, args=[], kwargs={}):    
        self.func = func
        self.set_args(*args, **kwargs)

    def peek_return(self):
        return self.return_value

    def get_return(self):
        r = self.return_value
        self.return_value = None
        return r