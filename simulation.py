import math

from ui import ui

ui.init((0, 0))

import pygame as pg

import json
import random

from game.game import Game
from simulator.tree import Tree

random.seed(1)

mg = Game('s')
mg.add_cpus(num=3)
mg.start(0)

tree = Tree(mg)
tree.simulate(num=10000, max_deapth=99)

def draw_tree(surf, branch, start=(0, 0)):
    lines = {}

    da = 60 / len(branch)
    angle = 240 + (60 / (len(branch) + 1))
    
    if isinstance(branch, dict):
        
        branch = {key: branch[key] for key in random.sample(list(branch), k=len(branch))}

        for (pid, uid), subbranch in branch.items():

            end = (
                start[0] + (200 * math.cos(math.radians(angle))),
                start[1] - (200 * math.sin(math.radians(angle)))
            )
            pg.draw.line(surf, (0, 0, 0), start, end)
            lines[start] = draw_tree(surf, subbranch, start=end)
            
            angle += da
            

    return lines

surf = pg.Surface((1000, 5000)).convert()
surf.fill((255, 255, 255))

draw_tree(surf, tree.tree, start=surf.get_rect().midtop)

pg.image.save(surf, 'graph.jpg')


















    