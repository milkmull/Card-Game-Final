import re
import keyword

import pygame as pg

from ..compiler import Compiler

from ui.menu.menu import Menu
from ui.element.base.base import Base_Element
from ui.element.elements import Textbox, Button, Image, Check_Box, Live_Window
from ui.element.utils.image import get_arrow
from ui.color.ops import color_text

def style_text(text):
    style = {}
    
    number_style = {'fgcolor': (255, 205, 34)}
    for match in re.finditer(r'(?<![a-zA-Z^_])(-?[0-9]+)', text):
        style.update({i: number_style for i in range(match.start(), match.end())})
        
    keyword_style = {'fgcolor': (147, 199, 99), 'style': 1}
    for word in keyword.kwlist:
        for match in re.finditer(f'(?<![a-zA-Z^_])({word})( )', text):
            style.update({i: keyword_style for i in range(match.start(), match.end())})
   
    string_style = {'fgcolor': (236, 118, 0)}
    for match in re.finditer(r'''([/'"])([^'"]*)(['"])''', text):
        style.update({i: string_style for i in range(match.start(), match.end())})
        
    class_style = {'fgcolor': (160, 130, 189), 'style': 1}
    for match in re.finditer(r'(?<=class )([a-zA-Z0-9_]+)', text):
        style.update({i: class_style for i in range(match.start(), match.end())})
        
    def_style = {'fgcolor': (103, 140, 177), 'style': 1}
    for match in re.finditer(r'(?<=def )([a-zA-Z0-9_]+)', text):
        style.update({i: def_style for i in range(match.start(), match.end())})
        
    return style

def run(node):
    m = Menu(info_menu, init_args=[node])
    m.run()
    
def info_menu(menu, node, show_full_out=False, last_port=None):
    body = menu.body
    elements = []
    
    original_node = node
    node = original_node.copy()
    node.enabled = False
    node.refresh = False
    elements.append(node)

    text_window = Live_Window(
        size=(700, 400),
        fill_color=(41, 49, 52),
        outline_width=5,
        inf_width=True
    )
    text_window.rect.midright = (body.width - 30, body.centery)
    elements.append(text_window)
  
    text_label = Textbox(
        size=(text_window.rect.width, 20),
        pad=5,
        centery_aligned=True
    )
    text_label.rect.bottomleft = (text_window.rect.left, text_window.outline_rect.top)
    text_window.add_child(text_label, current_offset=True)
    
    out_text = Textbox(
        font_name='JetBrainsMonoNL-Regular.ttf',
        text_size=17,
        text_color=(224, 226, 228)
    )
    out_text.font.strength = 0.06
    text_window.join_elements([out_text], border=5)
    
    node.rect.center = (text_window.rect.left // 2, body.centery)
    node.update_position(all=True)
    
    def draw(self, surf):
        start = self.port.rect.center
        end = text_window.outline_rect.midleft
        
        xs, ys = start
        xe, ye = end
        
        midx = (text_window.outline_rect.left + node.background_rect.right) // 2
        
        if self.port.port < 0:
            points = (
                start,
                (midx, ys),
                (midx, ye),
                end
            )
            
        else:
            points = (
                start,
                (xs - 15, ys),
                (xs - 15, node.background_rect.top - 15),
                (midx, node.background_rect.top - 15),
                (midx, ye),
                end
            )
        
        pg.draw.lines(surf, self.port.color, False, points, width=3)
    
    wire = Base_Element(draw=draw)
    setattr(wire, 'port', None)
    elements.append(wire)

    full_output = Check_Box(value=show_full_out)
    full_output.rect.topright = (node.rect.right - 10, node.rect.bottom + 20)
    full_output.add_event(
        tag='set',
        func=lambda: wire.port.button.left_click()
    )
    elements.append(full_output)
    
    tb = Textbox(
        text='Full Output:'
    )
    tb.rect.midright = (full_output.rect.left - 5, full_output.rect.centery)
    elements.append(tb)
    tb.add_event(
        tag='left_click',
        func=full_output.left_click
    )
    
    def refresh():
        port = wire.port.port
        menu.args = [original_node.get_port(port).connection]
        menu.kwargs = {
            'show_full_out': full_output.value,
            'last_port': original_node.get_port(port).connection_port.port
        }
        menu.refresh()

    navigation_button = Button.Text_Button(
        text='Go To',
        size=(100, 25),
        centerx_aligned=True,
        centery_aligned=True,
        outline_color=(255, 255, 255),
        outline_width=3,
        border_radius=5,
        hover_color=(100, 100, 100),
        func=refresh
    )
    navigation_button.rect.midtop = (node.rect.centerx, full_output.rect.bottom + 20)
    elements.append(navigation_button)
    
    back_button = Button.Text_Button(
        text='Back',
        size=(200, 25),
        centerx_aligned=True,
        centery_aligned=True,
        outline_color=(255, 255, 255),
        outline_width=3,
        border_radius=5,
        hover_color=(255, 0, 0),
        tag='exit'
    )
    back_button.rect.midtop = (node.rect.centerx, navigation_button.rect.bottom + 20)
    elements.append(back_button)
    
    back_button.add_animation(
        [{
            'attr': 'text_color',
            'end': (0, 0, 0)
        }],
        tag='hover'
    )
    
    compiler = Compiler(
        original_node.manager.nodes,
        card=original_node.manager.card,
    )
    compiled_text = compiler.compile(ignore_missing=True, mark=True).strip() or 'Error: No Start Node Found'

    def view_text(visible_port, node, port): 
        wire.port = visible_port
        
        navigation_button.set_on_off(port.connection)
        navigation_button.remove_child(navigation_button.last_born)

        if full_output:
            full_text = compiled_text
  
        elif port.port < 0:
            if node.is_func and port.is_flow:
                full_text = node.get_func_out()
            else:
                full_text = node.get_text() if port.is_flow else node.get_output(port.port)

        elif port.is_flow:
            if port.connection:
                full_text = node.get_text() if port.is_flow else node.get_output(port.port)
                
            else:
                full_text = 'No Connection'

        else:
            input = node.get_input_from(port.port)
            for op in node.get_output_ports():
                output = node.get_text() if op.is_flow else node.get_output(op.port)
                if input in output:
                    full_text = output
                    break
            else:
                full_text = 'Error: No Data Found'
                
        full_text = full_text.strip()
       
        if port.connection:
        
            if port.port > 0:
                node = port.connection
                port = port.connection_port
            
            i = Button.Image_Button(
                image=get_arrow(
                    '<' if visible_port.port > 0 else '>',
                    (20, 20),
                    padding=(5, 5),
                    color=visible_port.color
                ),
                func=refresh
            )
            navigation_button.add_child(i)
            if not visible_port.port > 0:
                i.rect.midleft = (navigation_button.rect.right + 10, navigation_button.rect.centery)
            else:
                i.rect.midright = (navigation_button.rect.left - 10, navigation_button.rect.centery)
            
        text_style = style_text(Compiler.unmark(full_text))
        ranges = Compiler.get_ranges(
            full_text,
            node.id,
            port=port.port if not port.is_flow else 0
        )
        style = {
            'bgcolor': visible_port.color,
            'fgcolor': color_text(visible_port.color)
        }
        for s, e in ranges:
            text_style.update({i: style for i in range(s, e)})

        out_text.text_style = text_style
        out_text.set_text(Compiler.unmark(full_text).strip(), force=True)
        text_window.join_elements([out_text], border=5)
        text_window.outline_color = visible_port.color

        text_label.text_color = color_text(visible_port.color)
        text_label.fill_color = visible_port.color
        text_label.set_text(f"Port {visible_port.port} {'Input' if visible_port.port > 0 else 'Output'}:")
        
    found_port = False

    for p in node.ports:
        if p.parent_port:
            continue
            
        b = Button.Text_Button(
            size=p.rect.inflate(5, 5).size,
            func=view_text,
            args=[p, original_node, original_node.get_port(p.port)]
        )   
        b.rect.center = p.rect.center
        b.set_parent(p, current_offset=True)
        elements.append(b)
        setattr(p, 'button', b)
        
        if last_port is None or (last_port is not None and p.port == last_port):
            b.left_click()
            found_port = True
    
    return elements
 