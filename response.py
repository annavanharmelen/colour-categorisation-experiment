"""
This file contains the functions necessary for
creating the interactive response dial at the end of a trial.
To run the 'colour categorisation' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual, event
from psychopy.hardware.keyboard import Keyboard
from time import time
import numpy as np
import random


RADIUS_COLOUR_WHEEL = 3 #6
INNER_RADIUS_COLOUR_WHEEL = 2.25 #4.5

def create_colours(n_colours, saturation, just_one=False):
    if saturation not in ["low", "medium", "high"]:
        raise ValueError("Saturation must be 'low', 'medium', or 'high'.")
    else:
        saturation = {"low": 0.2, "medium": 0.5, "high": 1}[saturation]

    if just_one:
        return [just_one, saturation, 0.5]
    
    return [[hue, saturation, 0.5] for hue in range(n_colours)]

def create_colour_wheel(offset, saturation, settings):
    # Determine colour range
    colours = create_colours(settings["n_colours"], saturation)

    # Parameters for the colour wheel
    radius = settings["deg2pix"](RADIUS_COLOUR_WHEEL)
    inner_radius = settings["deg2pix"](INNER_RADIUS_COLOUR_WHEEL)

    # Draw the colour wheel using segments
    colour_wheel = []
    for i in range(settings["n_colours"]):
        # Create a wedge for each segment
        wedge = visual.ShapeStim(
            settings["window"],
            vertices=[
                [
                    inner_radius * np.cos(np.radians(i + offset)),
                    inner_radius * np.sin(np.radians(i + offset)),
                ],
                [radius * np.cos(np.radians(i + offset)), radius * np.sin(np.radians(i + offset))],
                [
                    radius * np.cos(np.radians(i + 1 + offset)),
                    radius * np.sin(np.radians(i + 1 + offset)),
                ],
                [
                    inner_radius * np.cos(np.radians(i + 1 + offset)),
                    inner_radius * np.sin(np.radians(i + 1 + offset)),
                ],
            ],
            fillColor=colours[i],
            lineColor=None,
            colorSpace="hsv",
        )
        colour_wheel.append(wedge)

    return colour_wheel, colours


def make_marker(radius, inner_radius, settings):
    # Create a marker for the selected colour preview
    marker = visual.Rect(
        settings["window"],
        width=15,
        height=settings["deg2pix"](radius - inner_radius),
        fillColor=None,
        lineColor=(1, 1, 1),
    )

    return marker


def get_colour(mouse_pos, offset, colours):
    # Extract mouse position
    mouse_x, mouse_y = mouse_pos

    # Determine current colour based on mouse position
    angle = (np.degrees(np.arctan2(mouse_y, mouse_x)) + 360) % 360
    colour_angle = angle - offset
    if colour_angle > 360:
        colour_angle -= 360
    current_colour = colours[int(colour_angle)]

    return current_colour, angle


def move_marker(marker, mouse_pos, offset, colours, radius, inner_radius, settings):
    # Get current selected colour and use for marker
    current_colour, angle = get_colour(mouse_pos, offset, colours)
    marker.fillColor = current_colour

    # Fix the marker's position to the colour wheel's radius
    marker.pos = (
        settings["deg2pix"]((radius + inner_radius) / 2 * np.cos(np.radians(angle))),
        settings["deg2pix"]((radius + inner_radius) / 2 * np.sin(np.radians(angle))),
    )

    # Rotate the marker to follow the curve of the donut
    marker.ori = -angle + 90  # Adjust to span across the width of the donut

    marker.draw()

    return current_colour


def evaluate_response(selected_colour, target_colour, colours):
    # Determine position of both colours on colour wheel
    selected_colour_id = colours.index(selected_colour) + 1
    target_colour_id = colours.index(target_colour) + 1

    # Calculate the distance between the two colours
    abs_rgb_distance = abs(selected_colour_id - target_colour_id)

    if abs_rgb_distance > 180:
        rgb_distance = 360 - abs_rgb_distance
        rgb_distance_signed = abs_rgb_distance - 360
    else:
        rgb_distance = abs_rgb_distance
        rgb_distance_signed = abs_rgb_distance

    performance = round(100 - rgb_distance / 180 * 100)

    return {
        "abs_rgb_distance": abs_rgb_distance,
        "rgb_distance": rgb_distance,
        "rgb_distance_signed": rgb_distance_signed,
        "performance": performance,
    }


def get_response(
    target_colour,
    target_item,
    saturation,
    settings,
):
    keyboard: Keyboard = settings["keyboard"]

    # Check for pressed 'q'
    check_quit(keyboard)

    # These timing systems should start at the same time, this is almost true
    idle_reaction_time_start = time()
    keyboard.clock.reset()

    # Prepare the colour wheel and initialise variables
    offset = random.randint(0, 360)
    colour_wheel, colours = create_colour_wheel(offset, saturation, settings)
    mouse = event.Mouse(visible=True, win=settings["window"])
    mouse.getPos()
    marker = make_marker(RADIUS_COLOUR_WHEEL, INNER_RADIUS_COLOUR_WHEEL, settings)
    marker.colorSpace="hsv"
    selected_colour = None

    # Wait until participant starts moving the mouse
    while not mouse.mouseMoved():
        # Draw each wedge
        for wedge in colour_wheel:
            wedge.draw()

        # Draw the central square
        target_item.draw()

        settings["window"].flip()

    response_started = time()
    idle_reaction_time = response_started - idle_reaction_time_start

    # Show colour wheel and get participant response
    while not selected_colour:
        # Check for pressed 'q'
        check_quit(keyboard)

        # Draw each wedge
        for wedge in colour_wheel:
            wedge.draw()

        # Draw the central square
        target_item.draw()

        # Move the marker
        current_colour = move_marker(
            marker,
            mouse.getPos(),
            offset,
            colours,
            RADIUS_COLOUR_WHEEL,
            INNER_RADIUS_COLOUR_WHEEL,
            settings,
        )

        # Flip the display
        settings["window"].flip()

        # Check for mouse click
        if mouse.getPressed()[0]:  # Left mouse click
            selected_colour = current_colour

    response_time = time() - response_started
    mouse = event.Mouse(visible=False, win=settings["window"])

    return {
        "idle_reaction_time_in_ms": round(idle_reaction_time * 1000, 2),
        "response_time_in_ms": round(response_time * 1000, 2),
        "selected_colour": selected_colour,
        "colour_wheel_offset": offset,
        **evaluate_response(selected_colour, target_colour, colours),
    }


def wait_for_key(key_list, keyboard):
    keyboard: Keyboard = keyboard
    keyboard.clearEvents()
    keys = event.waitKeys(keyList=key_list)

    return keys


def check_quit(keyboard):
    if keyboard.getKeys("q"):
        raise KeyboardInterrupt()
