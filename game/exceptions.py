
class InfiniteLoop(Exception):
    pass
    
class CardNotFound(Exception):
    def __init__(self, name):
        super().__init__(f"Card of name '{name}' not found")