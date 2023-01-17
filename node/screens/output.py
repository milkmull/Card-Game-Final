import pygame as pg

from ..compiler import Compiler
from ..node.node_base import Port_Types

from ui.scene.scene import Scene

from ui.element.base.base import Base_Element
from ui.element.elements import Textbox, Button, Check_Box, Live_Window
from ui.element.utils.image import get_arrow
from ui.color.ops import color_shade

def run(node):
    m = Scene(info_scene, init_args=[node], fill_color=(32, 32, 40))
    m.run()
    for n in node.manager.nodes:
        n.mark = False
    
def info_scene(scene, node, show_full_out=False, last_port=None):
    body = scene.body
    elements = []
    
    original_node = node
    node = original_node.copy()
    for p in node.ports:
        if not p.hidden:
            p.set_visible(True)
    node.enabled = False
    node.refresh = False
    elements.append(node)
    
    id_text = Textbox(
        text=f"Node ID: {original_node.id}",
        text_size=25
    )
    id_text.rect.topleft = (20, 20)
    elements.append(id_text)

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
        font_name="JetBrainsMonoNL-Regular.ttf",
        text_size=17,
        text_color=(224, 226, 228),
        enabled=False
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
        
        pg.draw.lines(surf, Port_Types.get_color(self.port), False, points, width=3)
    
    wire = Base_Element(draw=draw)
    setattr(wire, "port", None)
    elements.append(wire)

    full_output = Check_Box(value=show_full_out)
    full_output.rect.topright = (node.rect.right - 10, node.rect.bottom + 20)
    full_output.add_event(
        tag="set_text",
        func=lambda: wire.port.button.run_events("left_click")
    )
    elements.append(full_output)
    
    tb = Textbox(
        text="Full Output:"
    )
    tb.rect.midright = (full_output.rect.left - 5, full_output.rect.centery)
    elements.append(tb)
    tb.add_event(
        tag="left_click",
        func=full_output.left_click
    )
    
    def refresh():
        port = wire.port.true_port
        scene.args = [original_node.get_port(port).connection]
        scene.kwargs = {
            "show_full_out": full_output.value,
            "last_port": original_node.get_port(port).connection_port.true_port
        }
        scene.refresh()

    navigation_button = Button.Text_Button(
        text="Go To",
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

    compiler = Compiler(
        original_node.manager.nodes,
        card=original_node.manager.card,
    )
    compiled_text = compiler.compile(ignore_missing=True, mark=True).strip() or "Error: No Start Node Found"

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
                full_text = "No Connection"

        else:
            input = node.get_input_from(port.port)
            for op in node.get_output_ports():
                output = node.get_text() if op.is_flow else node.get_output(op.port)
                print(op.port, node)
                if input in output:
                    full_text = output
                    break
            else:
                full_text = "Error: No Data Found"
                
        full_text = full_text.strip()
       
        if port.connection:
        
            if port.port > 0:
                node = port.connection
                port = port.connection_port
            
            i = Button.Image_Button(
                image=get_arrow(
                    "<" if visible_port.port > 0 else ">",
                    (20, 20),
                    pad=(5, 5),
                    color=Port_Types.get_color(visible_port)
                ),
                func=refresh
            )
            navigation_button.add_child(i)
            if not visible_port.port > 0:
                i.rect.midleft = (navigation_button.rect.right + 10, navigation_button.rect.centery)
            else:
                i.rect.midright = (navigation_button.rect.left - 10, navigation_button.rect.centery)
            
        text_style = out_text.style_text(Compiler.unmark(full_text))
        ranges = Compiler.get_ranges(
            full_text,
            node.id,
            port=port.true_port if not port.is_flow else 0
        )
        color = Port_Types.get_color(visible_port)
        style = {
            "bgcolor": color,
            "fgcolor": color_shade(color)
        }
        for s, e in ranges:
            text_style.update({i: style for i in range(s, e)})

        out_text.set_text(Compiler.unmark(full_text).strip(), force=True, style=text_style)
        text_window.join_elements([out_text], border=5)
        text_window.outline_color = color

        text_label.text_color = color_shade(color)
        text_label.fill_color = color
        text_label.set_text(f"Port {visible_port.port} {'Input' if visible_port.port > 0 else 'Output'}:")
        
        if text_window.y_scroll_bar.visible:
            text_label.pad["right"] = text_window.y_scroll_bar.width
        else:
            text_label.pad["right"] = 5
        
    found_port = False

    for p in node.ports:
        if p.parent_port or p.hidden:
            continue
            
        b = Button.Text_Button(
            size=p.rect.inflate(5, 5).size,
            func=view_text,
            args=[p, original_node, original_node.get_port(p.port)]
        )   
        b.rect.center = p.rect.center
        b.set_parent(p, current_offset=True)
        elements.append(b)
        setattr(p, "button", b)
        
        if not found_port and (last_port is None or (last_port is not None and p.port == last_port)):
            b.run_events("left_click")
            found_port = True
            
    back_button = Button.Text_Button(
        text="Back",
        size=(200, 25),
        centerx_aligned=True,
        centery_aligned=True,
        outline_color=(255, 255, 255),
        outline_width=3,
        border_radius=5,
        hover_color=(255, 0, 0),
        tag="exit"
    )
    back_button.rect.midbottom = (body.centerx, body.height - 20)
    elements.append(back_button)
    
    back_button.add_animation(
        [{
            "attr": "text_color",
            "end": (0, 0, 0)
        }],
        tag="hover"
    )
    
    return elements