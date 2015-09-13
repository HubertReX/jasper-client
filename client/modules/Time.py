# -*- coding: utf-8 -*-
# a może teraz?
import datetime
import re
from app_utils import *
from semantic.dates import DateService

WORDS = ["CZAS", "GODZINA", "GODZINĘ"]


def handle(text, mic, profile, logger, modules):
    """
        Reports the current time based on the user's timezone.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """

    tz = getTimezone(profile)
    now = datetime.datetime.now(tz=tz)
    #service = DateService()
    #response = service.convertTime(now)
    response = format_hour(now)
    mic.say("Teraz jest godzina|~ %s." % response)


def isValid(text):
    """
        Returns True if input is related to the time.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(czas|godzina)\b', text, re.IGNORECASE))
