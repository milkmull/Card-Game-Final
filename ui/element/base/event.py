from ..utils.event import Event as _Event
        
class Event:
    def __init__(self):
        self._events = {}
        
    def add_event(self, 
        func=None, 
        args=None, 
        kwargs=None, 
        include_self=False,
        
        no_call=False,
        tag='update'
    ):
        if func is None:
            return
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        if include_self:
            args.insert(0, self)
        e = _Event(func=func, args=args, kwargs=kwargs, no_call=no_call)
        
        if tag not in self._events:
            self._events[tag] = []
        self._events[tag].append(e)

        return e
        
    def run_events(self, tag):
        if (events := self._events.get(tag)):
            for e in events:
                e()
                
    def peek_return(self, tag):
        if (events := self._events.get(tag)):
            for e in reversed(events):
                r = e.peek_return()
                if r is not None:
                    return r
                
    def get_return(self, tag):
        if (events := self._events.get(tag)):
            for e in reversed(events): 
                r = e.get_return()
                if r is not None:
                    return r