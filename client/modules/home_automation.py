# -*- coding: utf-8 -*-
import urllib
import re
import app_utils
import json
from time import sleep

WORDS = ["OTWÓRZ", "ZAMKNIJ", "WŁĄCZ", "WYŁĄCZ", "URUCHOM", "ZMIEŃ", "PRZEŁĄCZ", "DEKODER"]


HELP  = {"name": "dom",
         "description": "Zestaw kommend do sterowania oświetleniem, roletami i urządzeniami RTV.",
         "samples": ["włącz głośniki", "zamknij rolety", "włącz telewizor", "przełącz źródło na dekoder", "szukaj nagranie kraina lodu", "szukaj program fakty"],
         "topics": {"rolety":  "powiedz zamknij lub otwórz rolety,| ewentulanie roletę"+
                               "upewnij się czy nic nie blokuje rolet przed zamknięciem.",
                    "głośniki": "powiedz włącz lub wyłącz głośniki,| "+
                                "dopuszczalna jest również forma głośnik.",
                    "telewizor": "powiedz włącz lub wyłącz telewizor,| "+
                                 "zamiast telewizor możesz również powiedzieć TV.",
                    "źródło": "powiedz zmień lub przełącz następnie źródło na:| "+
                              "HDMI jeden lub malinkę aby telewizor wyświetlił odtwarzacz multimedialny KODI.| "+
                              "HDMI dwa lub dekoder lub NC plus aby telewizor wyświetlił obraz z dekodera NC plus.",
                    "htpc": "Powiedz włącz lub wyłącz HTPC aby uruchomić komputer z multimediam w mens room.| "+
                            "Komputer będzie jedynie usypiany lub wzbudzany co zajmie tylko kilka sekund."+
                            "Bez włączenia HTPC większość filmów i zdjęć| będzie niedostępna w odtwarzaczu multimedialnym KODI.",
                    "uwagi ogólne": "...,|"+
                                     "."
                    }
          }

HOST = "192.168.1.7"
PORT = "5000"
# 50 = 80%

test = """
HELP  = {"name": ".",
         "description": ".",
         "samples": ["komenda", "komenda", "komenda"],
         "topics": {"temat 1":  ",| "+
                                ".",
                    "temat 2": ",| "+
                               ".",
                    "uwagi ogólne": "...,|"+
                                    "."
                    }
          }
"""

PRIORITY = 4

class jasperCommand:
    fun   = None
    param = None
    val   = None

    def __init__(self, fun=None, param=None, val=None):
      self.fun   = fun
      self.param = param
      self.val   = val


def sendCommands(commands, mic, logger):
      server = 'http://' + HOST + ':' + PORT +'/_run_cmd?fun=%s&param=%s&val=%s'
      
      for command in commands:
        url = server % (command.fun, command.param, command.val)
        
        try:
          if command.param <> "":
            logger.debug('home automation will responde with %s' % url)
            res = urllib.urlopen(url).read()
            #r = json.loads(res)
            #if r.has_key('result'):
            #  result = r['result']
            #  if result:
            #    mic.say(result)
            #logger.debug('raw response form flask serwer: %s' % res)
            #mic.say('okey')
            try:
              i = int(command.param)
            except:
              i = -1

            if i >= 0 and command.fun == 'NCPLUS':
              sleep(0.250)
            else:
              sleep(0.450)
          else:
            logger.debug('home automation will wait for 0.4 sec')
            sleep(0.450)
        except:
          logger.error("fatal error sending command to flask server", exc_info=True)
          mic.say("Wybacz, ale wystąpił problem techniczny.")
          break

def handle(text, mic, profile, logger, modules):
    """
        Responds to user-input, typically speech text, with a sample of
        Hacker News's top headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    text = app_utils.lowerUTF8(text)
    
    
    command  = jasperCommand()
    commands = []
    logger.debug('home automation got cmd %s' % text)
    
    numbers = app_utils.getNumbers(text)
    
    if 'włącz' in text or 'otwórz' in text or 'uruchom' in text:
        command.val = 'on'
    if 'wyłącz' in text or 'zamknij' in text:
        command.val = 'off'

    if 'głośnik' in text:
        if command.val:
          command.fun = 'ZWAVE'
          command.param = 'speakers'
          commands.append(command)
    if 'rolety' in text or 'roletę' in text:
        if command.val:
          command.fun = 'ZWAVE'
          command.param = 'roller'
          commands.append(command)

    if 'telewizor' in text or 'tv' in text:
        if command.val:
          command.fun = 'TV'
          command.param = 'power'
          commands.append(command)
   
    # change TV source to malinka, dekoder or htpc
    if 'źródło' in text :
        if 'hdmi 2' in text or 'hdmi dwa' in text or 'malinka' in text or 'malinkę' in text or 'kodi' in text or 'xbmc' in text:
            command.fun = 'TV'
            command.param = 'HDMI2'
            commands.append(command)
        if 'hdmi 3' in text or 'hdmi trzy' in text or 'dekoder' in text or 'nc plus' in text:
            command.fun = 'TV'
            command.param = 'HDMI3'
            commands.append(command)
#        if 'hdmi 3' in text or 'hdmi trzy' in text or 'htpc' in text :
#            fun = 'TV'
#            param = 'HDMI3'    
    elif 'szukaj' in text:
      command.fun = 'NCPLUS'
      phrases = text.split()
      if 'nagranie' in text:
        pos = phrases.index('nagranie')
        phrase = ' '.join(phrases[pos+1:])
        print phrase
        command.param = 'LIST'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = '0'
        commands.append(command)
      elif 'program' in text:
        pos = phrases.index('program')
        phrase = ' '.join(phrases[pos+1:])
        print phrase
        command.param = 'EPG'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'OK'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'OK'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = ''
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'DOWN'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'DOWN'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'DOWN'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'DOWN'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'OK'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = ''
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'DOWN'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'DOWN'
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = ''
        commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'RIGHT'
        commands.append(command)

      sms = app_utils.textToSMS(phrase)
      print sms
      for code in sms:
        command = jasperCommand(command.fun)
        command.param = str(code)
        commands.append(command)
        
      command.param = 'OK'
      commands.append(command)
      command = jasperCommand(command.fun)

    elif ('program' in text or 'kanał' in text) and len(numbers) > 0:
        command.fun = 'NCPLUS'
        channel = str(numbers[0])
        for digit in channel:
          command = jasperCommand(command.fun)
          command.param = digit
          commands.append(command)
        command = jasperCommand(command.fun)
        command.param = 'OK'
        commands.append(command)
    elif 'kanał tvn' in text:
      command.fun = 'NCPLUS'
      command.param = '1'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = 'OK'
      commands.append(command)
    elif 'kanał tvn 24' in text:
      command.fun = 'NCPLUS'
      command.param = '6'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = 'OK'
      commands.append(command)
    elif 'kanał hbo' in text:
      command.fun = 'NCPLUS'
      command.param = '5'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = '0'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = 'OK'
      commands.append(command)
    elif 'kanał canal plus' in text or 'kanał kanał plus' in text or 'kanał kanal plus' in text:
      command.fun = 'NCPLUS'
      command.param = '3'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = '0'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = 'OK'
      commands.append(command)
    elif 'kanał mini mini' in text:
      command.fun = 'NCPLUS'
      command.param = '9'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = '0'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = 'OK'
      commands.append(command)
    elif 'kanał cartoon network' in text:
      command.fun = 'NCPLUS'
      command.param = '1'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = '0'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = '1'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = 'OK'
      commands.append(command)
    elif 'kanał ale kino' in text:
      command.fun = 'NCPLUS'
      command.param = '4'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = '1'
      commands.append(command)
      command = jasperCommand(command.fun)
      command.param = 'OK'
      commands.append(command)
    
    else:
    
        # all other set-top box commands
        if 'dekoder' in text :
            command.fun = 'NCPLUS'
            numbers = app_utils.getNumbers(text)
            if len(numbers) > 0:
              repeat = numbers[0]
            else:
              repeat = 1

            if 'włącz dekoder' in text or 'uruchom dekoder' in text or 'wyłącz dekoder' in text:
              command.param = 'power'
              commands.append(command)
            elif ' n ' in text or 'kanały' in text :
              command.param = 'N'
              commands.append(command)
            elif 'epg' in text or 'program' in text :
              command.param = 'EPG'
              commands.append(command)
              command = jasperCommand(command.fun)
              command.param = 'OK'
              commands.append(command)
            elif 'vod' in text or 'video on demand' in text:
              command.param = 'VOD'
              commands.append(command)
            elif 'vod plus' in text or 'vod net' in text:
              command.param = 'BLUE'
              commands.append(command)
            elif 'radio' in text:
              command.param = 'RADIO'
              commands.append(command)
            elif 'info' in text:
              command.param = 'INFO'
              commands.append(command)
            elif 'opcje' in text:
              command.param = 'OPT'
              commands.append(command)
            elif 'play' in text or 'odtwarzaj' in text:
              command.param = 'PLAY'
              commands.append(command)
            elif 'pause' in text or 'pauza' in text or 'wstrzymaj' in text:
              command.param = 'PAUSE'
              commands.append(command)
            elif 'stop' in text or 'zatrzymaj' in text:
              command.param = 'STOP'
              commands.append(command)
            elif ('przewijaj' in text or 'przewiń' in text) and 'do przodu' in text:
              command.param = 'FF'
              for j in range(repeat):
                commands.append(command)
            elif ('przewijaj' in text or 'przewiń' in text) and 'do tyłu' in text:
              command.param = 'REV'
              for j in range(repeat):
                commands.append(command)
            elif 'nagraj' in text or 'nagrywaj' in text:
              command.param = 'REC'
              commands.append(command)
            elif 'lista' in text or 'nagrania' in text or 'nagrane' in text:
              command.param = 'LIST'
              commands.append(command)
            elif 'up' in text or 'do góry' in text:
              command.param = 'UP'
              for j in range(repeat):
                commands.append(command)
            elif 'down' in text or 'do dołu' in text or 'w dół' in text:
              command.param = 'DOWN'
              for j in range(repeat):
                commands.append(command)
            elif 'left' in text or 'lewo' in text:
              command.param = 'LEFT'
              for j in range(repeat):
                commands.append(command)
            elif 'right' in text or 'prawo' in text:
              command.param = 'RIGHT'
              for j in range(repeat):
                commands.append(command)
            elif 'ok' in text or 'enter' in text or 'zatwierdź' in text or 'wybierz' in text:
              command.param = 'ok'
              commands.append(command)
            elif 'back' in text or 'wstecz' in text or 'wróć' in text or 'cofnij' in text:
              command.param = 'BACK'
              commands.append(command)
            elif 'głośniej' in text or 'podgłoś' in text:
              command.param = 'VOL_P'
              for j in range(repeat):
                commands.append(command)
            elif 'ciszej' in text or 'ścisz' in text:
              command.param = 'VOL_M'
              for j in range(repeat):
                commands.append(command)
            elif 'wycisz' in text or 'cisza' in text:
              command.param = 'MUTE'
            elif 'następny kanał' in text or 'następny program' in text:
              command.param = 'PR_P'
              commands.append(command)
            elif 'poprzedni kanał' in text or 'poprzedni program' in text:
              command.param = 'PR_M'
              commands.append(command)
            else:
              #unknown key for nc plus
              command.fun = None
        if 'htpc' in text :
          if val == 'off':
            command.fun   = 'X10'
            command.param = 'power'   
            commands.append(command)
          else:
            command.fun   = 'WOL'
            command.param = 'HTPC'
            commands.append(command)

    if len(commands) > 0: # and (fun <> 'ZWAVE' or (fun == 'ZWAVE' and val)):
      sendCommands(commands, mic, logger)
    else:
      logger.info("home automation invalid cmd %s" % text)
      mic.say("Wybacz, ale nie rozumiem tego polecenia dla inteligentnego domu.")


def isValid(text):
    """
        Returns True if the input is related to Hacker News.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    #print('is it home automation command: %s' % text.decode('utf-8'))
    return bool(re.search(r'\b(włącz|wyłącz|zamknij|otwórz|przełącz|zmień|uruchom|dekoder|szukaj nagranie|szukaj program)\b', text, re.IGNORECASE))
