"""
Main script for running the 'colour categorisation' experiment,
made by Anna van Harmelen, 2025

see README.md for instructions if needed
"""

# Import necessary stuff
import traceback
from psychopy import core, event
import pandas as pd
from participantinfo import get_participant_details
from set_up import get_monitor_and_dir, get_settings
from practice import practice
from time import time
from numpy import mean
from practice import practice
import datetime as dt
from block import (
    create_block_list,
    block_break,
    long_break,
    finish,
    quick_finish,
)
from trial import single_trial

N_BLOCKS = 24
TRIALS_PER_BLOCK = 45


def main():
    """
    Data formats / storage:
     - eyetracking data saved in one .edf file per session
     - all trial data saved in one .csv per session
     - subject data in one .csv (for all sessions combined)
    """

    # Set whether this is a test run or not
    testing = True

    # Get monitor and directory information
    monitor, directory = get_monitor_and_dir(testing)

    # Get participant details and save in same file as before
    old_participants = pd.read_csv(
        rf"{directory}\participantinfo.csv",
        dtype={
            "participant_number": int,
            "session_number": int,
            "age": int,
            "trials_completed": str,
        },
    )
    new_participants = get_participant_details(old_participants, testing)

    # Initialise set-up
    settings = get_settings(monitor, directory)
    settings["keyboard"].clearEvents()

    # Practice until participant wants to stop
    practice(settings)

    # Initialise some stuff
    start_of_experiment = time()
    data = []
    current_trial = 0
    finished_early = True
    mouse = event.Mouse(visible=False, win=settings["window"])

    # Start experiment
    try:
        # Create a list of blocks, each containing a list of trials
        blocks = create_block_list(N_BLOCKS, TRIALS_PER_BLOCK, settings["n_colours"])

        for block in blocks[:2] if testing else blocks:
            # Create temporary variable for saving block performance
            block_performance = []

            # Run trials per pseudo-randomly created info
            for trial_colour in block[1]:
                current_trial += 1
                start_time = time()

                # Generate trial
                report: dict = single_trial(trial_colour, block[0], settings)
                end_time = time()

                # Save trial data
                data.append(
                    {
                        "trial_number": current_trial,
                        "block": blocks.index(block) + 1,
                        "block_type": block[0],
                        "start_time": str(
                            dt.timedelta(seconds=(start_time - start_of_experiment))
                        ),
                        "end_time": str(
                            dt.timedelta(seconds=(end_time - start_of_experiment))
                        ),
                        "target_colour": trial_colour,
                        **report,
                    }
                )

                block_performance.append(report["performance"])

            # Calculate average performance score for most recent block
            avg_score = round(mean(block_performance))

            # Break after end of block, unless it's the last block.
            if blocks.index(block) + 1 == N_BLOCKS // 2:
                long_break(
                    N_BLOCKS,
                    avg_score,
                    settings,
                )
            elif blocks.index(block) + 1 < N_BLOCKS:
                while calibrated:
                    calibrated = block_break(
                        block + 1,
                        N_BLOCKS,
                        avg_score,
                        settings,
                    )

        finished_early = False

    except Exception as e:
        print("An error occurred during the experiment:")
        # Print the error
        print(e.__class__.__name__ + ": " + str(e))
        traceback.print_exc()

    finally:
        # Save all collected trial data to a new .csv
        pd.DataFrame(data).to_csv(
            rf"{settings['directory']}\data_session_{new_participants.session_number.iloc[-1]}{'_test' if testing else ''}.csv",
            index=False,
        )

        # Register how many trials this participant has completed
        new_participants.loc[new_participants.index[-1], "trials_completed"] = str(
            len(data)
        )

        # Save participant data to existing .csv file
        new_participants.to_csv(
            rf"{settings['directory']}\participantinfo.csv", index=False
        )

        # Done!
        if finished_early:
            quick_finish(settings)
        else:
            # Thanks for meedoen
            finish(N_BLOCKS, settings)

        core.quit()


if __name__ == "__main__":
    main()
