import pygame as pg

from ui import ui
from data.constants import CONSTANTS

ui.init(size=CONSTANTS['screen_size'], flags=pg.SCALED | pg.RESIZABLE)

from data.save import SAVE
if SAVE.failed_to_load:
    SAVE.reset_save()

from menu.main import run

if __name__ == '__main__':
    run()
