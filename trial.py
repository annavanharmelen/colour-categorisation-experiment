"""
This file contains the functions necessary for
creating and running a single trial start-to-finish,
including eyetracker triggers.
To run the 'colour categorisation' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual
from response import create_colours, get_response, wait_for_key
import numpy as np
from time import sleep
from random import randint


def show_text(input, window, pos=(0, 0), colour="#ffffff"):
    textstim = visual.TextStim(
        win=window, font="Courier New", text=input, color=colour, pos=pos, height=22
    )

    textstim.draw()


def single_trial(target_colour_id, saturation, settings):
    # Determine colour
    target_colour = create_colours(1, saturation, just_one=target_colour_id)

    # Create square to indicate target colour
    target_item = visual.Rect(
        settings["window"],
        width=settings["deg2pix"](2),
        height=settings["deg2pix"](2),
        fillColor=target_colour,
        lineColor=None,
        colorSpace="hsv",
    )

    # Run trial: get_response handles both the displaying and the response
    response = get_response(target_colour, target_item, saturation, settings)

    # Give feedback
    target_item.draw()
    visual.TextStim(
        win=settings["window"],
        text=f"{response['performance']}",
        font="Courier New",
        height=22,
        pos=(0, 0),
        color=[-1, -1, -1],
        bold=True,
    ).draw()
    settings["window"].flip()
    sleep(0.3)

    return response
