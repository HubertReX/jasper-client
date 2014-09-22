# -*- coding: utf-8 -*-
"""
A Speaker handles audio output from Jasper to the user

Speaker methods:
    say - output 'phrase' as speech
    play - play the audio in 'filename'
    isAvailable - returns True if the platform supports this implementation
"""
# może teraz?
import os
import re
import json
import shelve
import time
import datetime
import str_formater
import subprocess
import persistent_cache

PHRASES_CACHE_DB    = 'cache_phrases.db'


class GoogleSpeaker:

    """
    Uses the google speech synthesizer - requires to be on-line
    """ 
    def __init__(self, logger):
        self.logger = logger
        self.cache = persistent_cache.audioCache(PHRASES_CACHE_DB, logger)
        self.cache.listCacheEntries()

    @classmethod
    def isAvailable(cls):
        return True


    def useTTS(self, phrase):
        try:
          #cmd = "wget -q --restrict-file-names=nocontrol --referer=\"http://translate.google.com\" -U Mozilla -O say.mp3 \"http://translate.google.com/translate_tts?ie=UTF-8&tl=pl&q=%s\" && avconv -y -v quiet -i say.mp3 -f wav say.wav" % phrase
          self.logger.debug("command for google translator: %s" % phrase)
          phrase = str_formater.unicodeToUTF8(phrase, self.logger)
          cmd = ["/home/pi/jasper/client/tts.sh", phrase]
          subprocess.call(cmd)
          audio_file = "say.wav"
        except:
          self.logger.critical("fatal error using google tts", exc_info=True)
          audio_file = None
        
        return audio_file

    def say(self, phrase):
        #phrase = str_formater.utf8ToUnicode(phrase, self.logger)
        if "|" in phrase:
            #phrases = re.compile(u'\. |, |: |; |\n', re.UNICODE).split(phrase)
            phrases = re.compile('\|').split(phrase)
        elif len(phrase) > 30 :
            phrases = re.compile('\. |, |: |; |\n').split(phrase)
        else:
            phrases = [phrase]
        
        audio_sentance = ""
        index = 0
        for p in phrases:
            self.logger.debug("JASPER: " + p)
            audio_file = None
            #self.speaker.say(p)
            #time.sleep(1)

            #p = str_formater.unicodeToUTF8(p, self.logger)
            # ~ means do not cache - used when prases are unlikely to reacure in exact forme, for example current time
            cache = True
            if '~' in p:
              cache = False
              p = p.replace('~','')
            if self.cache.hasKey(p) and cache:
              audio_file = self.cache.getFromCache(p)
            else:
              audio_file = self.useTTS(p)
              
              if audio_file: 
                if cache:
                  audio_file = self.cache.addToCache(p, audio_file)
                else:
                  index += 1
                  tmp_file = "tmp_%04d.wav" % (index)
                  os.system("mv %s %s" % (audio_file, tmp_file))
                  audio_file = tmp_file
            audio_sentance += ' ' + audio_file
            self.logger.debug('audio_sentance %s' % audio_sentance )
                  
        self.play(audio_sentance)

    def play(self, filename):      
        os.system("aplay -D hw:1,0 " + filename)

class DummySpeaker:

    """
    Logs phrase - nothing more. Just for debug.
    """
    def __init__(self, logger):
        self.logger = logger

    @classmethod
    def isAvailable(cls):
        return True

    def say(self, phrase):
        self.logger.info("Say phrase: %s" % phrase)
        #self.play("say.wav")

    def play(self, filename):
        self.logger.info("Play file: %s" % filename)

class eSpeakSpeaker:

    """
    Uses the eSpeak speech synthesizer included in the Jasper disk image
    """
    def __init__(self, logger):
        self.logger = logger

    @classmethod
    def isAvailable(cls):
        return os.system("which espeak") == 0

    def say(self, phrase, OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        os.system("espeak " + json.dumps(phrase) + OPTIONS)
        self.play("say.wav")

    def play(self, filename):
        os.system("aplay -D hw:1,0 " + filename)


class saySpeaker:
    """
    Uses the OS X built-in 'say' command
    """
    def __init__(self, logger):
        self.logger = logger

    @classmethod
    def isAvailable(cls):
        return os.system("which say") == 0

    def shellquote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"

    def say(self, phrase):
        os.system("say " + self.shellquote(phrase))

    def play(self, filename):
        os.system("afplay " + filename)


def newSpeaker(logger):
    """
    Returns:
        A speaker implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    for cls in [GoogleSpeaker, eSpeakSpeaker, saySpeaker]:
        if cls.isAvailable():
            return cls(logger)
    logger.critical("Platform is not supported", exc_info=True)
