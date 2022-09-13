from ui.element.standard.textbox import Textbox
from ui.color.ops import gen_colors

COIN = (
    Textbox(
        text='Tails',
        text_color=(255, 0, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    ),
    Textbox(
        text='Heads',
        text_color=(0, 255, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    ),
    Textbox(
        text='Flip',
        text_color=(255, 255, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    )
) 

DICE = []
for i, color in enumerate(gen_colors(6)):
    DICE.append(
        Textbox(
            text=str(i + 1),
            text_color=color,
            text_outline_color=(0, 0, 0),
            text_outline_width=2
        )
    )
DICE.append(
    Textbox(
        text='Roll',
        text_color=(255, 255, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    )
)

SELECT = Textbox(
    text='Selecting',
    text_size=15,
    text_color=(255, 255, 0),
    text_outline_color=(0, 0, 0),
    text_outline_width=2
)

VOTE = {
    'rotate':  Textbox(
        text='Rotate',
        text_size=15,
        text_color=(255, 255, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    ), 
    'keep':  Textbox(
        text='Keep', 
        text_size=15, 
        text_color=(255, 255, 0),
        text_outline_color=(0, 0, 0),
        text_outline_width=2
    )
}