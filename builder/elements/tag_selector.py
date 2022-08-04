
class Tag_Selector(Dropdown_Multi_Select):
    def __init__(self, card):
        from data.save import SAVE
        all_tags = SAVE.get_sheet_info('tags')
        tags = all_tags['biomes'] + all_tags['descriptors']
        super().__init__(tags, 3)
        self.card = card
        
        for tag in self.card.tags:
            self.add_value(tag)
        
    def add_value(self, tag):
        if super().add_value(tag):
            self.card.add_tag(tag)
        
    def remove_value(self, tb, b):
        tag = tb.get_message()
        super().remove_value(tb, b)
        self.card.remove_tag(tag)
