# -*- coding: utf-8 -*-
import re
from facebook import *


WORDS = ["FACEBOOK", "FEJSBUK", "POWIADOMIENIE", "POWIADOMIENIA"]


def handle(text, mic, profile, logger):
    """
        Responds to user-input, typically speech text, with a summary of
        the user's Facebook notifications, including a count and details
        related to each individual notification.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    oauth_access_token = profile['keys']['FB_TOKEN']

    graph = GraphAPI(oauth_access_token)

    try:
        results = graph.request("me/notifications")
    except GraphAPIError:
        logger.error("error getting response form facebook api, for key: %s" % oauth_access_token, exc_info=True)
        mic.say(
            "Nie mam uprawnienia do twojego konta na Fejsbuku. Sprawdź ustawienia.")
        return
    except:
        logger.error("error getting response form facebook api, for key: %s" % oauth_access_token, exc_info=True)
        mic.say(
            "Wybacz, ale ta usługa jest chwilowo niedostępna.")

    if not len(results['data']):
        mic.say("Brak nowych powiadomień na Fejsbuku")
        return

    updates = []
    for notification in results['data']:
        updates.append(notification['title'])

    count = len(results['data'])
    mic.say("Masz " + str(count) +
            " nowych powiadomień na Fejsbuku. " + " ".join(updates) + ". ")

    return


def isValid(text):
    """
        Returns True if the input is related to Facebook notifications.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(powiadomienie|powiadomienia|fejsbuk|Facebook)\b', text, re.IGNORECASE))
