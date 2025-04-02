"""
This file contains the functions necessary for practising the task.
To run the 'colour categorisation' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from trial import single_trial, show_text
import random
from response import wait_for_key
from numpy import mean
from time import sleep

def practice(settings):
    # Show welcome 
    show_text(
                "Welcome to the experiment! You'll start by practising the task."
                "\n\nPress SPACE to start the practice.",
                settings["window"],
            )
    settings["window"].flip()
    wait_for_key(["space"], settings["keyboard"])

    practice_performance = []
    practice = True
    
    # Practice until done
    while practice:
        for i in range(5):
            # Generate random conditions
            trial_colour = random.randint(1,360)
            saturation = random.choice(["low", "medium", "high"])

            # Generate trial
            report: dict = single_trial(trial_colour, saturation, settings)

            # Save score
            practice_performance.append(report["performance"])

        # Check if the participant wants to continue
        avg_score = mean(practice_performance)
        show_text(
            f"Your average score on these 5 practice trials was {avg_score}."
            "\n\nPress SPACE to practice 5 more trials, or G to continue to the experiment.",
            settings["window"],
        )
        settings["window"].flip()
        keys = wait_for_key(["space", "g"], settings["keyboard"])

        if "g" in keys:
            practice = False
    
    # Show countdown 
    for i in range(4):
        show_text(
                f"The experiment will start in {3-i}",
                settings["window"],
            )
        settings["window"].flip()
        
        if i != 3:
            sleep(1)
