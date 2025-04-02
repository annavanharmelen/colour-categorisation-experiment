"""
This file contains the functions necessary for
creating and running a full block of trials start-to-finish.
To run the 'colour categorisation' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

import random
from trial import show_text
from response import wait_for_key

def create_block_list(n_blocks, n_trials, n_colours):
    if n_blocks % 3 != 0:
        raise Exception(
            "Expected number of blocks to be divisible by 3, otherwise each block type cannot occur the same number of times."
        )
    if n_colours % n_trials != 0:
        raise Exception(
            "Expected number of colours to be divisible by number of trials, otherwise not all blocks can be the same length."
        )
    if n_blocks * n_trials != n_colours * 3:
        raise Exception(
            "Expected number of blocks * number of trials to be equal to number of colours * 3, otherwise not all colours can be used exactly once."
        )

    # Generate equal distribution of block types
    block_types = ["low", "medium", "high"]
    blocks = (
        n_blocks // 3 * [block_types[0]]
        + n_blocks // 3 * [block_types[1]]
        + n_blocks // 3 * [block_types[2]]
    )

    # Generate random distribution of all colours over all block types
    type_colours = []
    for _, i in enumerate(block_types):
        colours = list(range(1, n_colours+1, 1))
        random.shuffle(colours)
        type_colours.append(
            [colours[i : i + n_trials] for i in range(0, len(colours), n_trials)]
        )
    # unpack the nested list of colours
    type_colours = [element for innerList in type_colours for element in innerList]

    # Shuffle block types, with colours still attached
    block_colours = list(zip(blocks, type_colours))
    random.shuffle(block_colours)

    return block_colours


def block_break(current_block, n_blocks, avg_score, settings, eyetracker):
    blocks_left = n_blocks - current_block

    show_text(
        f"You scored {avg_score}% correct on the previous block. "
        f"\n\nYou just finished block {current_block}, you {'only ' if blocks_left == 1 else ''}"
        f"have {blocks_left} block{'s' if blocks_left != 1 else ''} left. "
        "Take a break if you want to, but try not to move your head during this break."
        "\n\nPress SPACE when you're ready to continue.",
        settings["window"],
    )
    settings["window"].flip()

    if eyetracker:
        keys = wait_for_key(["space", "c"], settings["keyboard"])
        if "c" in keys:
            eyetracker.calibrate()
            eyetracker.start()
            return True
    else:
        wait_for_key(["space"], settings["keyboard"])

    # Make sure the keystroke from starting the experiment isn't saved
    settings["keyboard"].clearEvents()

    return False


def long_break(n_blocks, avg_score, settings, eyetracker):
    show_text(
        f"You scored {avg_score}% correct on the previous block. "
        f"\n\nYou're halfway through! You have {n_blocks // 2} blocks left. "
        "Now is the time to take a longer break. Maybe get up, stretch, walk around."
        "\n\nPress SPACE whenever you're ready to continue again.",
        settings["window"],
    )
    settings["window"].flip()

    if eyetracker:
        keys = wait_for_key(["space", "c"], settings["keyboard"])
        if "c" in keys:
            eyetracker.calibrate()
            return True
    else:
        wait_for_key(["space"], settings["keyboard"])

    # Make sure the keystroke from starting the experiment isn't saved
    settings["keyboard"].clearEvents()

    return False


def finish(n_blocks, settings):
    show_text(
        f"Congratulations! You successfully finished all {n_blocks} blocks!"
        "You're completely done now. Press SPACE to exit the experiment.",
        settings["window"],
    )
    settings["window"].flip()

    wait_for_key(["space"], settings["keyboard"])


def quick_finish(settings):
    settings["window"].flip()
    show_text(
        f"You've exited the experiment. Press SPACE to close this window.",
        settings["window"],
    )
    settings["window"].flip()

    wait_for_key(["space"], settings["keyboard"])
