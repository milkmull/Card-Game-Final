from ..ui import get_size
from ..element.utils.container import Container

def center_elements_x(elements, marginx=0):
    x = 0
    for e in elements:
        e.rect.midleft = (x, 0)
        x += e.rect.width + marginx
        
    r = elements[0].rect.unionall([e.rect for e in elements])

    w, h = get_size()
    rx, ry = r.topleft
    r.center = (w // 2, h // 2)
    for e in elements:
        e.rect.move_ip(r.x - rx, r.y - ry)
        
    return Container(data=elements.copy())

def center_elements_y(elements, marginy=0):
    y = 0
    for e in elements:
        e.rect.midtop = (0, y)
        y += e.rect.height + marginy
        
    r = elements[0].rect.unionall([e.rect for e in elements])

    w, h = get_size()
    rx, ry = r.topleft
    r.center = (w // 2, h // 2)
    for e in elements:
        e.rect.move_ip(r.x - rx, r.y - ry)
        
    return Container(data=elements.copy())