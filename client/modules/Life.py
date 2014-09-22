# -*- coding: utf-8 -*-
import random
import re

WORDS = ["JAKI", "JEST", "SENS", "ŻYCIA"]


def handle(text, mic, profile, logger):
    """
        Responds to user-input, typically speech text, by relaying the
        meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    messages = ["Odpowiedź brzmi 42, głupcze.",
                "Odpowiedź brzmi 42. Ile razy mam to powtarzać?",
                "Odpowiedź brzmi 42. Zdaję się, że już to mówiłam..."
                ]

    message = random.choice(messages)

    mic.say(message)


def isValid(text):
    """
        Returns True if the input is related to the meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bjaki jest sens życia\b', text, re.IGNORECASE))
