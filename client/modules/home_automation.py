# -*- coding: utf-8 -*-
import urllib
import re
import app_utils
import json

WORDS = ["OTWÓRZ", "ZAMKNIJ", "WŁĄCZ", "WYŁĄCZ", "GŁOŚNIKI", "ROLETY", "URUCHOM"]

PRIORITY = 4

def handle(text, mic, profile, logger):
    """
        Responds to user-input, typically speech text, with a sample of
        Hacker News's top headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    #text = text.encode('utf-8')
    server = 'http://192.168.1.110:5000/_run_cmd?fun=ZWAVE&param=%s&val=%s'
    fun = None
    param = None
    val = None
    logger.debug('home automation got cmd %s' % text)
    if 'głośnik' in text.lower():
        fun = 'ZWAVE'
        param = 'speakers'
    if 'rolety' in text.lower():
        fun = 'ZWAVE'
        param = 'roller'
    if 'telewizor' in text.lower() or 'tv' in text.lower():
        fun = 'TV'
        param = 'power'
   
    # change TV source to malinka, dekoder or htpc
    if 'źródło' in text.lower() :
        if 'hdmi 1' in text.lower() or 'hdmi jeden' in text.lower() or 'malinka' in text.lower() :
            fun = 'TV'
            param = 'HDMI1'
        if 'hdmi 2' in text.lower() or 'hdmi dwa' in text.lower() or 'dekoder' in text.lower() :
            fun = 'TV'
            param = 'HDMI2'
        if 'hdmi 3' in text.lower() or 'hdmi trzy' in text.lower() or 'htpc' in text.lower() :
            fun = 'TV'
            param = 'HDMI3'
    else:
    # toggle power in dekoder or htpc
        if 'dekoder' in text.lower() :
            fun = 'NCPLUS'
            param = 'power'
        if 'htpc' in text.lower() :
            fun = 'WOL'
            param = 'HTPC'

    if 'włącz' in text.lower() or 'otwórz' in text.lower():
        val = 'on'
    if 'wyłącz' in text.lower() or 'zamknij' in text.lower():
        val = 'off'
        if fun == 'WOL':
            fun = 'X10'
            val = 'power'

    if (fun and param) and (fun <> 'ZWAVE' or (fun == 'ZWAVE' and val)):
      url = server % (param, val)
      logger.debug('home automation will responsde with %s' % url)
      try:
        res = urllib.urlopen(url).read()
        #r = json.loads(res)
        #if r.has_key('result'):
        #  result = r['result']
        #  if result:
        #    mic.say(result)
        mic.say('okey')
      except:
        logger.error("fatal error sending command to flask server", exc_info=True)
        mic.say("Wybacz, ale wystąpił problem techniczny.")
    else:
      logger.info("home automation invalid cmd %s" % text, exc_info=True)


def isValid(text):
    """
        Returns True if the input is related to Hacker News.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    #print('is it home automation command: %s' % text.decode('utf-8'))
    return bool(re.search(r'\b(włącz|wyłącz|zamknij|otwórz) (rolety|głośnik)\b', text, re.IGNORECASE))
