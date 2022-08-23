
class InfiniteLoop(Exception):
    pass
    
class CardNotFound(Exception):
    def __init__(self, name):
        super().__init__(f"Card of name '{name}' not found")
        
class DeckNotFound(Exception):
    def __init__(self, deck):
        super().__init__(f"Deck of name '{deck}' not found")