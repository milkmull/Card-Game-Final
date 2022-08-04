
class Context_Manager(Compound_Object):
    def __init__(self, ne):
        super().__init__()
        self.rect = pg.Rect(0, 0, 1, 1)
        
        self.ne = ne
        self.node = None
        
        self.objects_dict = {}
        
        kwargs = {'size': (100, 25), 'border_radius': 0, 'color1': (255, 255, 255), 'fgcolor': (0, 0, 0), 'tsize': 12}
        
        b = Button.text_button('copy', func=self.ne.copy_nodes, **kwargs)
        self.objects_dict['copy'] = b
        
        b = Button.text_button('delete', func=self.ne.delete_nodes, **kwargs)
        self.objects_dict['delete'] = b
        
        b = Button.text_button('transform', **kwargs)
        self.objects_dict['transform'] = b
        
        b = Button.text_button('info', func=Menu.build_and_run, **kwargs)
        self.objects_dict['info'] = b
        
        b = Button.text_button('spawn required', func=self.ne.get_required, **kwargs)
        self.objects_dict['spawn'] = b
        
        b = Button.text_button('group', func=self.ne.create_new_group_node, **kwargs)
        self.objects_dict['group'] = b
        
        b = Button.text_button('ungroup', func=self.ne.ungroup_node, **kwargs)
        self.objects_dict['ungroup'] = b
        
        b = Button.text_button('paste', func=self.ne.paste_nodes, **kwargs)
        self.objects_dict['paste'] = b
        
        b = Button.text_button('select all', func=self.ne.drag_manager.select_all, **kwargs)
        self.objects_dict['select_all'] = b
        
        b = Button.text_button('clean up', func=self.ne.spread, **kwargs)
        self.objects_dict['clean_up'] = b
        
        self.close()
        
    @property
    def objects(self):
        return list(self.objects_dict.values())
        
    def is_open(self):
        return self.rect.topleft != (-100, -100)
        
    def open(self, pos, node):
        self.clear_children()

        if node:
            selected = self.ne.get_selected()

        x, y = self.rect.topleft
        for name, b in self.objects_dict.items():
            add = False
            
            if node:
                if name == 'copy':
                    if not selected:
                        b.set_args(kwargs={'nodes': [node]})
                        add = True
                    elif node in selected:
                        b.set_args(kwargs={'nodes': selected})
                        add = True
                elif name == 'delete':
                    if not selected:
                        b.set_args(kwargs={'nodes': [node]})
                        add = True
                    elif node in selected:
                        b.set_args(kwargs={'nodes': selected})
                        add = True
                elif name == 'transform':
                    if node.can_transform():
                        b.set_func(node.transform)
                        add = True
                elif name == 'info':
                    b.set_args(args=[screens.info_menu, node])
                    add = True
                elif name == 'spawn':
                    if node.get_required():
                        b.set_args(args=[node])
                        add = True
                elif name == 'group':
                    add = [n for n in selected if not n.is_group() and n is not node]
                elif name == 'ungroup':
                    add = node.is_group()
                    if add:
                        b.set_args(args=[node])

            else:
                if name == 'paste':
                    add = self.ne.copy_data
                elif name == 'select_all':
                    add = True
                elif name == 'clean_up':
                    add = True
                    
            if name == 'select_all':
                add = True
                
            if add:
                b.rect.topleft = (x, y)
                self.add_child(b, current_offset=True)
                y += b.rect.height
            else:
                self.remove_child(b)
                
        x, y = pos
        w = self.children[0].rect.width
        h = sum([c.rect.height for c in self.children])
        if y + h > HEIGHT:
            y -= h
        if x + w > WIDTH:
            x -= w
        self.rect.topleft = (x, y)
            
    def close(self):
        self.rect.topleft = (-100, -100)
        for b in self.objects_dict.values():
            b.rect.topleft = self.rect.topleft

    def draw(self, surf):
        super().draw(surf)
        if self.is_open():
            for b in self.children[1:]:
                pg.draw.line(surf, (0, 0, 0), (b.rect.x + 5, b.rect.y - 1), (b.rect.right - 5, b.rect.y - 1), width=2)
