import pygame as pg

from ui import ui
from ui.element.base.text import Text
from data.constants import CONSTANTS

ui.init(size=CONSTANTS["screen_size"], flags=pg.RESIZABLE | pg.SCALED)
Text.load_font("data/fonts/courier_new.ttf")
Text.load_font("data/fonts/JetBrainsMonoNL-Regular.ttf")

from data.save import SAVE
if SAVE.failed_to_load:
    SAVE.reset_save()

from menu.main import run

if __name__ == "__main__":
    run()
