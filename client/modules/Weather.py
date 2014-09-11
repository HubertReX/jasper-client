#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import datetime
import feedparser
from app_utils import getTimezone
from semantic.dates import DateService

WORDS = ["POGODA", "PROGNOZA", "DZISIAJ", "JUTRO"]


def replaceAcronyms(text):
    """Replaces some commonly-used acronyms for an improved verbal weather report."""

    def parseDirections(text):
        words = {
            'N': 'północ',
            'S': 'południe',
            'E': 'wschód',
            'W': 'zachód',
        }
        output = [words[w] for w in list(text)]
        return ' '.join(output)
    acronyms = re.findall(r'\b([NESW]+)\b', text)

    for w in acronyms:
        text = text.replace(w, parseDirections(w))

    text = re.sub(r'(\b\d+)F(\b)', '\g<1> Fahrenheita\g<2>', text)
    text = re.sub(r'(\b\d+)C(\b)', '\g<1> Celciusza\g<2>', text)
    text = re.sub(r'(\b)mph(\b)', '\g<1>mil na godzinę\g<2>', text)
    text = re.sub(r'(\b)kph(\b)', '\g<1>kilometrów na godzinę\g<2>', text)
    text = re.sub(r'(\b)in\.', '\g<1>cali', text)
    text = re.sub(r'(\b)mm\.', '\g<1>milimetrów', text)

    return text


def getForecast(profile):
    return feedparser.parse("http://polish.wunderground.com/auto/rss_full/"
                            + str(profile['location']))['entries']


def handle(text, mic, profile, logger):
    """
        Responds to user-input, typically speech text, with a summary of
        the relevant weather for the requested date (typically, weather
        information will not be available for days beyond tomorrow).

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """

    if not profile['location']:
        mic.say(
            "Wybacz, ale nie mogę podać prognozy pogody. Wprowadź proszę w ustawieniach miasto.")
        return

    tz = getTimezone(profile)

    service = DateService(tz=tz)
    date = service.extractDay(text)
    if not date:
        date = datetime.datetime.now(tz=tz)
    weekday = service.__daysOfWeek__[date.weekday()]

    if date.weekday() == datetime.datetime.now(tz=tz).weekday():
        date_keyword = "Dzisiaj"
    elif date.weekday() == (
            datetime.datetime.now(tz=tz).weekday() + 1) % 7:
        date_keyword = "Jutro"
    else:
        date_keyword = weekday

    forecast = getForecast(profile)

    output = None

    for entry in forecast:
        try:
            date_desc = entry['title'].split()[0].strip().lower()
            if date_desc == 'Prognoza': #For global forecasts
            	date_desc = entry['title'].split()[2].strip().lower()
            	weather_desc = entry['description']

            elif date_desc == 'Obecne': #For first item of global forecasts
            	continue
            else:
            	weather_desc = entry['description'].split('|')[1] #US forecasts

            if weekday == date_desc:
                output = "Prognoza pogody na " + \
                     date_keyword + weather_desc + "."
                break
        except:
            continue

    if output:
        output = replaceAcronyms(output)
        mic.say(output)
    else:
        mic.say(
            "Wybacz, ale brak prognozy")


def isValid(text):
    """
        Returns True if the text is related to the weather.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(pogoda|temperatura|prognoza)\b', text, re.IGNORECASE))
