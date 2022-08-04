from ui.element.elements import Input, Dropdown

class Input_Dropdown(Input, Dropdown):
    def __init__(self, **kwargs):
        Input.__init__(self, **kwargs)
        Dropdown.__init__(self, **kwargs)