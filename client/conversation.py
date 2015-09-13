# -*- coding: utf-8 -*-
from notifier import Notifier
from musicmode import *
from brain import Brain
from mpd import MPDClient
import str_formater
from modules.app_utils import *

class Conversation(object):

    def __init__(self, mic, profile, logger):
        self.persona = profile['persona']
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile, logger)
        self.notifier = Notifier(profile, logger)
        self.logger = logger

    def delegateInput(self, text):
        """A wrapper for querying brain."""
        got_hit = False
        # check if input is meant to start the music module
        if any(x in text.upper() for x in ["SPOTIFY", "MUSIC"]):
            # check if mpd client is running
            try:
                client = MPDClient()
                client.timeout = None
                client.idletimeout = None
                client.connect("localhost", 6600)
            except:
                self.logger.warning("Failed to init MPDClient")
                self.mic.say("Wybacz, ale najwyraźniej usługa Spotify nie działa")
                return
            
            self.logger.info("waiting for Spotify playlist")
            self.mic.say("Poczekaj chwilę, wczytuję listę utworów Spotify")
            music_mode = MusicMode(self.persona, self.mic, self.logger)
            music_mode.handleForever()
            return
        else:
          if " następnie " in lowerUTF8(text):
            l_text = text.split(" następnie ")
            for text in l_text:
              new_got_hit = self.brain.query(text)
              got_hit = got_hit or new_got_hit
          else:
            got_hit = self.brain.query(text)
        return got_hit

    def handleForever(self):
        """Delegates user input to the handling function when activated."""
        initial_threshold = None #self.mic.fetchThreshold(RATE=48000, CHUNK=8192, THRESHOLD_TIME=4, AVERAGE_TIME=4)
        repeat = True
        while repeat:

            # Print notifications until empty
            notifications = self.notifier.getAllNotifications()
            for notif in notifications:
                notif = str_formater.unicodeToUTF8(notif, self.logger)
                self.logger.info("Got new notification: %s" % notif )
                #self.mic.say(notif)

            try:
                threshold, transcribed = self.mic.passiveListen()
            except KeyboardInterrupt:
                threshold = None
                repeat = False
            except:
                self.logger.critical("fatal error processing passive listen", exc_info=True)
                continue

            if threshold:
                if transcribed:
                  input = transcribed
                else:
                  input = self.mic.activeListen(initial_threshold, RATE=44100, CHUNK=8196, LISTEN_TIME=6, AVERAGE_TIME=5)
                  input = str_formater.unicodeToUTF8(input, self.logger)

                self.logger.debug("got input %s" % (input))
                if input:
                    if any(x in input.upper() for x in ["KONIEC"]):
                      repeat = False
                      self.logger.info("Quiting after voice request")
                      self.mic.say("Kończę pracę. Do usłyszenia.")
                    #elif any(x in input.upper().replace('ł','Ł') for x in ["PRZEŁADUJ"]):
                    elif any(x in upperUTF8(input) for x in ["PRZEŁADUJ"]):
                      self.brain.reload_modules()
                    elif any(x in upperUTF8(input) for x in ["ECHO"]):
                            self.mic.say(input)
                            #self.mic.play(input)
                    else:
                      self.delegateInput(input)
                else:
                    self.mic.say("Powtórz proszę.")
#            else:
#              if any(x in transcribed.upper() for x in ["KONIEC"]):
#                      repeat = False
#                      self.logger.info("Quiting after voice request")
#                      self.mic.say("Kończę pracę. Do usłyszenia.") 
#              elif any(x in upperUTF8(transcribed) for x in ["PRZEŁADUJ"]):
#                      self.brain.reload_modules()
