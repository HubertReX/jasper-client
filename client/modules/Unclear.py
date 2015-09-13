# -*- coding: utf-8 -*-
from sys import maxint
import random

WORDS = []

PRIORITY = -(maxint + 1)


def handle(text, mic, profile, logger, modules):
    """
        Reports that the user has unclear or unusable input.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """

    messages = ["Czy mogę prosić o powtórzenie?",
                "Powtórz proszę", 
                "Powiedz jeszcze raz",
                ]

    message = random.choice(messages)
    mic.say("Nie rozumiem polecenia |%s" % text)
    mic.say(message)
 

def isValid(text):
    return True
