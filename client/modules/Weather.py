# -*- coding: utf-8 -*-
import re
import datetime
import feedparser
from app_utils import getTimezone
from semantic.dates import DateService
import arrow
import str_formater
import logging
import jasperLogger
import yaml

WORDS = ["POGODA", "PROGNOZA", "DZISIAJ", "JUTRO"]
HELP  = {"name": "pogoda",
         "description": "Możesz poznać lokalną prognozę pogody na dziś, jutro lub pojutrze",
         "samples": ["jaka jest prognoza pogody", "jaka będzie pogoda jutro", "prognoza na wtorek"],
         # "topics": {"muzyka": "powiedz odtwarzaj lub gra lub zagraj lub puść| "+
         #                       "następnie zespół lub zespołu lub artystę lub wykonawcę lub płyty|" +
         #                       "a następnie właściwą nazwę wykonawcy.|"+
         #                       "Kommenda ta, doda do kolejki odtwarzania wszystkie albumy wykonawcy.",
         #             "film":   "powiedz odtwarzaj lub graj lub zagraj lub puść| "+
         #                       "następnie film" +
         #                       "a następnie polski tytuł filmu.|"+
         #                       "Jeżeli wynik wyszukania zwróci więcej niż jeden wynik,"+
         #                       "to wszystkie filmy zostaną dodane do kolejki.|"+
         #                       "Nie trzeba wypowiadać pełnej nazwy filmu,|"+
         #                       "wystarczy użyć unikalnego słowa lub frazy",
         #            "uwagi ogólne": "jeżeli nie udaje się prawidłowo rozpoznać nazwy artysty lub filmu|"+
         #                            "nazwę można przeliterować."
         #            }
        }


def parseDirections(text):
    words = {
        'North': 'północny',
        'South': 'południowy',
        'East':  'wschodni',
        'West':  'zachodni',
        'Clear': 'czysto',
    }
    output = []
    for w in text:
      #print w
      #print words.get(w, '')
      output.append(words.get(w,''))
    #output = [words[w] for w in list(text)]
    #print output
    return ' '.join(output)

def parseDayOfWeek(text, logger):
    loc = arrow.locales.get_locale('pl')
    res = None
    for d in range(7):
      dow = loc.day_name(d+1)
      dow = str_formater.unicodeToUTF8(dow, logger)
      if dow.lower() in text:
        res = d
        break
    return res

def replaceAcronyms(text):
    """Replaces some commonly-used acronyms for an improved verbal weather report."""
    words = {
        'North':     'północny',
        'South':     'południowy',
        'East':      'wschodni',
        'West':      'zachodni',
        'Clear':     'bezchmurnie',
        'Mostly':    'przeważnie',
        'Partly ':   'częściowo',
        'Cloudy':    'pochmurnie',
        'Scattered': 'zanikające',
        'Clouds':    'zachmurzenie',
        'Clouds':    'zachmurzenie',
        'Rain Showers':'mrzawka',
        'Light':     'lekka',
    }
    acronyms = re.findall(r'\b(North|South|East|West|Clear|Mostly|Partly|Cloudy|Scattered|Clouds|Light|Rain Showers)\b', text)
    #print acronyms
    for w in acronyms:
        if words.has_key(w):
          text = text.replace(w, words[w])
    text = re.sub(r'(\d+)[ ]?&deg;','\g<1> stopni', text)
    text = re.sub(r'(\d+)[ ]?&#176;','\g<1> stopni', text)
    #text = re.sub(r'(\d+)[ ]?&deg;','\g<1> stopni', text)
    #text = re.sub(r'(\d+)[ ]?°',    '\g<1> stopni', text)
    text = re.sub(r'Maks\.:', 'maksymalnie ', text)
    text = re.sub(r'Min\.:', 'co najmniej ', text)
    #text = re.sub(r'stopni F', 'stopni Fahrenheita', text)
    #text = re.sub(r'stopni C', 'stopni Celciusza', text)
    text = re.sub(r'(\b)mph(\b)', '\g<1>mil na godzinę\g<2>', text)
    text = re.sub(r'(\b)kph(\b)', '\g<1>kilometrów na godzinę\g<2>', text)
    #text = re.sub(r'(\b\d+)[ ]?km\/h', '\g<1> kilometrów na godzinę', text)
    text = re.sub(r'(\b\d+)[ ]?km\/h', '\g<1> km/h', text)
    text = re.sub(r'(\b)in\.', '\g<1>cali', text)
    text = re.sub(r'(\b)mm\.', '\g<1>milimetrów', text)
    #text = re.sub(r'(\b\d+)[ ]?hPa', '\g<1> hPa', text)
    return text

def parseCurrentConditions(text):
    #<![CDATA[Temperatura: 61° F / 16° C | Wilgotność: 82% | Ciśnienie: 30.12cali / 1020hPa (Ciśnienie stabilne) | Warunki pogodowe: Clear | Kierunek wiatru: East | Prędkość wiatru: 8mph / 13km/h<img src="http://server.as5000.com/AS5000/adserver/image?ID=WUND-00071&C=0" width="0" height="0" border="0"/>]]>
    res = []
    text = text.replace('<![CDATA[', '').split('<img')[0]
    for t in text.split('|'):
      part = t.split(':')
      factor = part[0]
      if ' / ' in part[1]:
        value = part[1].split(' / ')[1]
      else:
        value = part[1]
      res.append(factor + '|' + value)
    return '|'.join(res)

def getForecast(profile):
    return feedparser.parse("http://polish.wunderground.com/auto/rss_full/"
                            + str(profile['location']))['entries']


def handle(text, mic, profile, logger, modules):
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
    mic.say("Pobieram prognozę pogody...")
    #str_formater.checkFormat(text, logger)
    text = str_formater.unicodeToUTF8(text, logger)
    tz = getTimezone(profile)

    service = DateService(tz=tz)
    loc = arrow.locales.get_locale('pl')
    #loc.day_name(1).lower()

    #date = service.extractDay(text)
    #if not date:
    dow = parseDayOfWeek(text.lower(), logger)
    if dow:
      now_dow = arrow.utcnow().weekday()
      if dow > now_dow:
        date = arrow.utcnow().replace(days=dow - now_dow)
      else:
        date = arrow.utcnow().replace(days=dow - now_dow + 7)
    if 'dzisiaj' in text.lower():
      date = arrow.utcnow()
    elif 'jutro' in text.lower():
      date = arrow.utcnow().replace(days=+1)
    elif 'pojutrze' in text.lower():
      date = arrow.utcnow().replace(days=+2)
    else:
      date = arrow.utcnow()

    weekday = loc.day_name(date.weekday()+1).lower()
    weekday = str_formater.unicodeToUTF8(weekday, logger).replace('Ś','ś')
    

    if date.weekday() == arrow.utcnow().weekday():
        date_keyword = "dzisiaj"
    elif date.weekday() == arrow.utcnow().replace(days=+1).weekday():
        date_keyword = "jutro"
    else:
        date_keyword = weekday

    #logger.debug("date_keyword %s weekday %s" % (date_keyword, weekday))
    forecast = getForecast(profile)
    output = ""
    #weekday = 'niedziela'
    
    #for entry in forecast:
    #  print entry['title']
    for entry in forecast:
        try:
            entry = str_formater.unicodeToUTF8(entry, logger)
            #str_formater.checkFormat(entry['title'].split()[0].strip().lower(), logger)
            date_desc = entry['title'].split()[0].strip().lower().replace('Ś','ś')
            #logger.debug('date_desc %s' % date_desc)
            if date_desc == 'prognoza': #For global forecasts
              date_desc = entry['title'].split()[2].strip().lower().replace('Ś','ś')
              #logger.debug('date_desc %s' % date_desc)
              weather_desc = entry['summary_detail']['value']

            elif date_desc == 'obecne': #For first item of global forecasts
                output += "Obecne warunki pogodowe:|" + \
                     parseCurrentConditions(entry['summary_detail']['value']) + "| "
                continue
            else:
              weather_desc = entry['summary_detail']['value'].split('|')[1] #US forecasts

            if weekday == date_desc:
                output += "Prognoza pogody na " + \
                     date_keyword + ',| ' + weather_desc
                break
        except:
            logger.error("error parsing forecast", exc_info=True)

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

class Mic:
    def say(self, msg):
        print "say:", msg

if __name__ == "__main__":
    m = Mic()
    l = jasperLogger.jasperLogger(level=logging.DEBUG, logFile='persistentCache.log', console=True)
    logger = l.getLogger()
    profile = yaml.safe_load(open("/home/osmc/jasper/client/profile.yml", "r"))

    #t = "odtwarzaj wykonawcę kult"
    t = "prognoza pogody na środę"
    handle(t, m, profile, logger, None)
