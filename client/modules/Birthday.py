#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
from facebook import *
from app_utils import getTimezone

WORDS = ["URODZINY"]


def handle(text, mic, profile, logger):
    """
        Responds to user-input, typically speech text, by listing the user's
        Facebook friends with birthdays today.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    oauth_access_token = profile['keys']["FB_TOKEN"]

    graph = GraphAPI(oauth_access_token)

    try:
        results = graph.request(
            "me/friends", args={'fields': 'id,name,birthday'})
    except GraphAPIError:
        mic.say(
            "Nie mam uprawnienia do twojego konta na Fejsbuku. Sprawdź ustawienia.")
        return
    except:
        mic.say(
            "Wybacz, ale ta usługa jest chwilowo niedostępna.")
        return

    needle = datetime.datetime.now(tz=getTimezone(profile)).strftime("%m/%d")

    people = []
    for person in results['data']:
        try:
            if needle in person['birthday']:
                people.append(person['name'])
        except:
            continue

    if len(people) > 0:
        if len(people) == 1:
            output = people[0] + " ma dzisiaj urodziny."
        else:
            output = "Oto znajomi, którzy dzisiaj obchodzą urodziny " + \
                ", ".join(people[:-1]) + " oraz " + people[-1] + "."
    else:
        output = "Nitk z twoich znajomych nie obchodzi dzisiaj urodzin."

    mic.say(output)


def isValid(text):
    """
        Returns True if the input is related to birthdays.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'urodziny', text, re.IGNORECASE))
