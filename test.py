import pygame as pg

pg.init()
pg.freetype.init()

font = pg.freetype.Font(None)
window = pg.display.set_mode((1024, 576))
clip = pg.Rect(0, 0, 100, 20)

while True:
    
    if any({e.type == pg.QUIT for e in pg.event.get()}):
        break

    window.fill((0, 0, 0))
    window.set_clip(clip)
    
    pg.draw.rect(window, (255, 0, 0), clip)
    font.render_to(
        window,
        (0, 0),
        'this text should be clipped inside the red box',
        size=20,
        fgcolor=(255, 255, 255)
    )
    
    pg.display.flip()
    window.set_clip(None)
    
pg.quit()