
class Node_Menu(Compound_Object):
    def __init__(self, ne):
        super().__init__()
        
        self.ne = ne

        p = Live_Popup(size=(450, 350), vel=60)
        p.set_inflation(x=175, y =-100)
        p.rect.midtop = (WIDTH // 2, HEIGHT)
        self.rect = p.rect
        self.add_child(p, current_offset=True)
        self.popup = p
        
        up_arrow = get_arrow('u', (16, 16))
        
        popup_button = Button.image_button(up_arrow, padding=(5, 5), func=self.popup_control, tag='u')
        popup_button.rect.bottomright = self.popup.rect.topright
        popup_button.rect.y -= 20
        self.add_child(popup_button, current_offset=True)
        self.popup_button = popup_button
 
        self.tabs = {}

        self.node_groups = {}
        self.node_buttons = {}
        self.node_labels = {}
        
        for name, n in Node.NODE_DATA.items():
            if hasattr(n, 'cat'):
                cat = n.cat
                subcat = getattr(n, 'subcat', 'base')
                if cat not in self.node_groups:
                    self.node_groups[cat] = {}
                if subcat not in self.node_groups[cat]:
                    self.node_groups[cat][subcat] = [name]
                else:
                    self.node_groups[cat][subcat].append(name)
                img = Node.get_cached_img(name)
                b = Button.image_button(img, border_radius=0, func=self.get_node, args=[name], padding=(0, 5), color2=(50, 50, 50))
                self.node_buttons[name] = b
                if subcat not in self.node_labels:
                    self.new_subcat(subcat)
                    
        cat = 'group'
        self.node_groups[cat] = {}
        for name, data in Node.GROUP_DATA.items():
            subcat = data.get('subcat', 'base')
            if subcat not in self.node_groups[cat]:
                self.node_groups[cat][subcat] = [name]
            else:
                self.node_groups[cat][subcat].append(name)
            img = Node.get_cached_img(name)
            b = Button.image_button(img, border_radius=0, func=self.get_group_node, args=[name])
            self.node_buttons[name] = b
            if subcat not in self.node_labels:
                self.new_subcat(subcat)
                
        for cat in self.node_groups:
            for subcat in self.node_groups[cat]:
                self.node_groups[cat][subcat].sort(key=lambda name: self.node_buttons[name].rect.height)
                     
        self.tabs['node'] = {'button': None, 'tabs': {}, 'subtab': list(self.node_groups)[0]}
        x = self.rect.x - 5
        y = self.rect.y + 5
        for subtab, _ in self.node_groups.items():
            b = Button.text_button(subtab, func=self.set_node_subtab, args=[subtab], padding=(5, 2))
            b.rect.topright = (x, y)
            self.tabs['node']['tabs'][subtab] = b
            self.add_child(b, current_offset=True)
            y += b.rect.height + 5
            
        b = Button.text_button('nodes', func=self.set_tab, args=['node'], padding=(10, 5))
        b.rect.midbottom = (self.rect.x + (self.rect.width // 3), self.rect.y - 10)
        self.add_child(b, current_offset=True)
        self.tabs['node']['button'] = b
            
        self.tabs['info'] = {'button': None, 'tabs': {}, 'subtab': 'cards'}
        x = self.rect.x - 5
        y = self.rect.y + 5
        subtabs = ('cards', 'types', 'tags', 'decks', 'requests', 'logs')
        for subtab in subtabs:
            b = Button.text_button(subtab, func=self.set_info_subtab, args=[subtab], padding=(5, 2))
            b.rect.topright = (x, y)
            self.tabs['info']['tabs'][subtab] = b
            self.add_child(b, current_offset=True)
            y += b.rect.height + 5

        b = Button.text_button('info', func=self.set_tab, args=['info'], padding=(10, 5))
        b.rect.midbottom = (self.rect.x + ((2 * self.rect.width) // 3), self.rect.y - 10)
        self.add_child(b, current_offset=True)
        self.tabs['info']['button'] = b
        
        self.tab = None
        self.set_tab('node')
        self.start_force_down()
            
    def new_subcat(self, subcat):
        tb = Textbox(subcat, tsize=40, underline=True)
        space_width = tb.get_text_rect(' ').width
        spaces = ((self.popup.rect.width - tb.rect.width) // space_width) - 1
        tb.set_message(subcat + (' ' * spaces))
        tb = tb.to_static()
        self.node_labels[subcat] = tb
                
    def set_tab(self, tab):
        self.start_force_up()
        for t in self.tabs:
            ev = t == tab
            for b in self.tabs[t]['tabs'].values():
                b.set_enabled(ev)
                b.set_visible(ev)
            if ev:
                self.tabs[t]['button'].color1 = (255, 0, 0)
            else:
                self.tabs[t]['button'].color1 = (0, 0, 0)
        self.tab = tab
        b = self.tabs[tab]['tabs'][self.tabs[tab]['subtab']]
        b.run_func()
        
    def set_subtab(self, subtab):
        for st, b in self.tabs[self.tab]['tabs'].items():
            if st == subtab:
                b.color1 = (0, 0, 255)
            else:
                b.color1 = (0, 0, 0)
        self.tabs[self.tab]['subtab'] = subtab

    def set_node_subtab(self, subtab):
        items = []
        for subcat in self.node_groups[subtab]:
            items.append(self.node_labels[subcat])
            for name in self.node_groups[subtab][subcat]:
                items.append(self.node_buttons[name])
        self.popup.join_objects(items, xpad=10, ypad=10, dir='x', pack=True)
        
        self.set_subtab(subtab)
        
    def set_info_subtab(self, subtab):
        if subtab == 'cards':
            self.get_cards()
        if subtab == 'types':
            self.get_types()
        elif subtab == 'tags':
            self.get_tags()
        elif subtab == 'decks':
            self.get_decks()
        elif subtab == 'requests':
            self.get_requests()
        elif subtab == 'logs':
            self.get_logs()
            
        self.set_subtab(subtab)
        
    def get_cards(self):
        from card.cards import get_playable_card_data
        card_data = get_playable_card_data()
        
        objects = []
        offsets = []
        y = 20
        
        for type in card_data:
            tb = Textbox.static_textbox(type, tsize=15)
            objects.append(tb)
            x = (self.popup.rect.width // 2) - tb.rect.width - 10
            offsets.append((x, y))
            for name in sorted(card_data[type]):
                b = Button.text_button(name, func=self.get_node, args=['String'], kwargs={'val': name}, tsize=15, padding=(5, 2))
                objects.append(b)
                x = (self.popup.rect.width // 2) + 10
                offsets.append((x, y))
                y += b.rect.height
            y += b.rect.height
               
        self.popup.join_objects_custom(offsets, objects)
        
    def get_types(self):
        with open('data/node/sheet_info.json', 'r') as f:
            data = json.load(f)
            
        objects = []
        offsets = []
        y = 20
        
        for deck in data['types']:
            b = Button.text_button(deck, func=self.get_node, args=['String'], kwargs={'val': deck}, tsize=15, padding=(5, 2))
            objects.append(b)
            x = (self.popup.rect.width - b.rect.width) // 2
            offsets.append((x, y))
            y += b.rect.height + 5
        self.popup.join_objects_custom(offsets, objects)
        
    def get_tags(self):
        with open('data/node/sheet_info.json', 'r') as f:
            data = json.load(f)
            
        objects = []
        offsets = []
        y = 20
        
        for cat in data['tags']:
            tb = Textbox.static_textbox(cat, tsize=15)
            objects.append(tb)
            x = (self.popup.rect.width // 2) - tb.rect.width - 10
            offsets.append((x, y))
            for tag in data['tags'][cat]:
                b = Button.text_button(tag, func=self.get_node, args=['String'], kwargs={'val': tag}, tsize=15, padding=(5, 2))
                objects.append(b)
                x = (self.popup.rect.width // 2) + 10
                offsets.append((x, y))
                y += b.rect.height
            y += b.rect.height

        self.popup.join_objects_custom(offsets, objects)
    
    def get_decks(self):
        with open('data/node/sheet_info.json', 'r') as f:
            data = json.load(f)
            
        objects = []
        offsets = []
        y = 20
        
        for deck in data['decks']:
            b = Button.text_button(deck, func=self.get_node, args=['String'], kwargs={'val': deck}, tsize=15, padding=(5, 2))
            objects.append(b)
            x = (self.popup.rect.width - b.rect.width) // 2
            offsets.append((x, y))
            y += b.rect.height + 5
        self.popup.join_objects_custom(offsets, objects)
        
    def get_requests(self):
        with open('data/node/sheet_info.json', 'r') as f:
            data = json.load(f)
            
        objects = []
        offsets = []
        y = 20
        
        for req in data['requests']:
            b = Button.text_button(req, func=self.get_node, args=['String'], kwargs={'val': req}, tsize=20, padding=(5, 2))
            objects.append(b)
            x = (self.popup.rect.width - b.rect.width) // 2
            offsets.append((x, y))
            y += b.rect.height + 5   
        self.popup.join_objects_custom(offsets, objects)
        
    def get_logs(self):
        with open('data/node/sheet_info.json', 'r') as f:
            data = json.load(f)
            
        objects = []
        offsets = []
        y = 20
        
        def run_log_menu(*args):
            m = Menu(get_objects=screens.log_menu, args=args)
            m.run()
        
        for log, d in data['logs'].items():
            b = Button.text_button(log, func=run_log_menu, args=[log, d], tsize=12, padding=(5, 2))
            objects.append(b)
            x = (self.popup.rect.width - b.rect.width) // 2
            offsets.append((x, y))
            y += b.rect.height + 5 
        self.popup.join_objects_custom(offsets, objects)
        
    def is_open(self):
        return self.popup_button.tag == 'd'
        
    def flip_arrow(self):
        img = self.popup_button.first_born
        img.set_image(pg.transform.flip(img.image, False, True))
        
    def popup_control(self):
        self.flip_arrow()
        if self.popup_button.tag == 'd':
            self.popup_button.set_tag('u')
            self.popup.start_force_down()
        elif self.popup_button.tag == 'u':
            self.popup_button.set_tag('d')
            self.popup.start_force_up()
            
    def start_force_down(self):
        if self.popup_button.tag == 'd':
            self.flip_arrow()
            self.popup_button.set_tag('u')
            self.popup.start_force_down()
            
    def start_force_up(self):
        if self.popup_button.tag == 'u':
            self.flip_arrow()
            self.popup_button.set_tag('d')
            self.popup.start_force_up()
            
    def get_node(self, *args, **kwargs):
        self.ne.get_node(*args, **kwargs)
        self.start_force_down()
        
    def get_group_node(self, *args, **kwargs):
        self.ne.get_group_node(*args, **kwargs)
        self.start_force_down()
        
    def draw(self, surf):
        super().draw(surf)
        if self.popup.is_visible():
            points = (
                (self.popup.total_rect.right - 2, self.rect.top),
                (self.rect.left, self.rect.top),
                (self.rect.left, self.rect.bottom - 2),
                (self.popup.total_rect.right - 2, self.rect.bottom - 2)
            )
            pg.draw.lines(surf, (255, 255, 255), not self.popup.scroll_bar.visible, points, width=3)
