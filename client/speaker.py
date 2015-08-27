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
import pyvona



class GoogleSpeaker:

    """
    Uses the google speech synthesizer - requires to be on-line
    """ 
    def __init__(self, logger, profile):
        self.logger = logger
        self.profile = profile
        self.snd_dev = profile['snd_dev']
        PHRASES_CACHE_DB    = 'cache_phrases_google.db'
        self.cache = persistent_cache.audioCache(PHRASES_CACHE_DB, logger, 'google', self.snd_dev)
        #self.cache.listCacheEntries()
        self.ivona = pyvona.Voice(profile['ivona-tts']['access_key'], profile['ivona-tts']['secret_key'])
        self.ivona.codec          = "mp3"
        self.ivona.region         = profile['ivona-tts']['region']
        self.ivona.voice_name     = profile['ivona-tts']['voice']
        self.ivona.speech_rate    = profile['ivona-tts']['speech_rate']
        self.ivona.sentence_break = profile['ivona-tts']['sentence_break']

    @classmethod
    def isAvailable(cls):
        return True


    def useTTS(self, phrase):
        try:
          #cmd = "wget -q --restrict-file-names=nocontrol --referer=\"http://translate.google.com\" -U Mozilla -O say.mp3 \"http://translate.google.com/translate_tts?ie=UTF-8&tl=pl&q=%s\" && avconv -y -v quiet -i say.mp3 -f wav say.wav" % phrase
          audio_file = None
          self.logger.debug("command for google translator: %s" % phrase)
          phrase = str_formater.unicodeToUTF8(phrase, self.logger)
          cmd = ["/home/osmc/jasper/client/tts.sh", phrase]
          res = subprocess.call(cmd)
          if res == 0:
            audio_file = "say.mp3"
        except:
          self.logger.critical("fatal error using google tts", exc_info=True)
        
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
                  tmp_file = "tmp_%04d.mp3" % (index)
                  os.system("mv %s %s" % (audio_file, tmp_file))
                  audio_file = tmp_file
                audio_sentance += ' ' + audio_file
              else:
                self.logger.error('Google TTS failed! (possibly too many request)')
                audio_file_1 = self.cache.getFromCache('Wybacz')
                audio_file_2 = self.cache.getFromCache('ale wystąpił problem techniczny z tą operacją')
                audio_sentance = '%s %s' % (audio_file_1, audio_file_2)
                break
            
            self.logger.debug('audio_sentance %s' % audio_sentance)
                  
        self.play(audio_sentance)

    def play(self, filename):      
        #os.system("aplay -D plughw:1,0 " + filename)
        #os.system("aplay -D %s %s" % (self.snd_dev, filename))
        if 'mp3' in filename:
          cmd = "mpg123 -q --audiodevice=%s %s" % (self.snd_dev, filename)
        else:
          cmd = "aplay -D %s %s" % (self.snd_dev, filename)
        self.logger.debug("play cmd: %s" % cmd)
        os.system(cmd)


class IvonaSpeaker:

    """
    Uses the Ivona speech synthesizer - requires to be on-line
    """ 
    def __init__(self, logger, profile):
        self.logger = logger
        self.profile = profile
        self.snd_dev = profile['snd_dev']
        PHRASES_CACHE_DB    = 'cache_phrases_%s.db' % profile['ivona-tts']['voice']
        self.cache = persistent_cache.audioCache(PHRASES_CACHE_DB, logger, profile['ivona-tts']['voice'], self.snd_dev)
        #self.cache.listCacheEntries()
        self.ivona = pyvona.Voice(profile['ivona-tts']['access_key'], profile['ivona-tts']['secret_key'])
        self.ivona.codec          = "mp3"
        self.ivona.region         = profile['ivona-tts']['region']
        self.ivona.voice_name     = profile['ivona-tts']['voice']
        self.ivona.language       = "pl-PL"
        self.ivona.speech_rate    = profile['ivona-tts']['speech_rate']
        self.ivona.sentence_break = profile['ivona-tts']['sentence_break']

    @classmethod
    def isAvailable(cls):
        return True


    def useIvonaTTS(self, phrase):
        try:
          #cmd = "wget -q --restrict-file-names=nocontrol --referer=\"http://translate.google.com\" -U Mozilla -O say.mp3 \"http://translate.google.com/translate_tts?ie=UTF-8&tl=pl&q=%s\" && avconv -y -v quiet -i say.mp3 -f wav say.wav" % phrase
          audio_file = "say.mp3"
          self.logger.debug("command for ivona translator: %s" % phrase)
          phrase = str_formater.unicodeToUTF8(phrase, self.logger)
          
          res = self.ivona.fetch_voice(phrase, audio_file)
          self.logger.debug("ivona res: %s" % repr(res))
        except:
          self.logger.critical("fatal error using ivona tts", exc_info=True)
        
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
            
            p = p.strip()
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
              self.logger.debug("got file from cache: %s" + audio_file)
              audio_sentance += ' ' + audio_file
            else:
              audio_file = self.useIvonaTTS(p)
              
              if audio_file: 
                if cache:
                  audio_file = self.cache.addToCache(p, audio_file)
                else:
                  index += 1
                  tmp_file = "tmp_%04d.mp3" % (index)
                  os.system("mv %s %s" % (audio_file, tmp_file))
                  audio_file = tmp_file
                
                audio_sentance += ' ' + audio_file
              else:
                self.logger.error('Ivona TTS failed! (possibly too many request)')
                audio_file_1 = self.cache.getFromCache('Wybacz')
                audio_file_2 = self.cache.getFromCache('ale wystąpił problem techniczny z tą operacją')
                audio_sentance = '%s %s' % (audio_file_1, audio_file_2)
                break
            
            self.logger.debug('audio_sentance %s' % audio_sentance)
                  
        self.play(audio_sentance)

    def play(self, filename):      
        #os.system("aplay -D plughw:1,0 " + filename)
        #os.system("aplay -D %s %s" % (self.snd_dev, filename))
        if not filename:
          self.logger.error("play command failed! audo file name is empty" % cmd)
          return

        if 'mp3' in filename:
          cmd = "mpg123 -q --audiodevice=%s %s" % (self.snd_dev, filename)
        else:
          cmd = "aplay -D %s %s" % (self.snd_dev, filename)
        self.logger.debug("play cmd: %s" % cmd)
        os.system(cmd)

class DummySpeaker:

    """
    Logs phrase - nothing more. Just for debug.
    """
    def __init__(self, logger, profile):
        self.logger = logger
        self.profile = profile

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
    def __init__(self, logger, profile):
        self.logger = logger
        self.profile = profile
        self.snd_dev = profile['snd_dev']

    @classmethod
    def isAvailable(cls):
        return os.system("which espeak") == 0

    def say(self, phrase, OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        os.system("espeak " + json.dumps(phrase) + OPTIONS)
        self.play("say.wav")

    def play(self, filename):
        # plughw:1,0
        os.system("aplay -D %s %s" % (self.snd_dev, filename))


class saySpeaker:
    """
    Uses the OS X built-in 'say' command
    """
    def __init__(self, logger, profile):
        self.logger = logger
        self.profile = profile

    @classmethod
    def isAvailable(cls):
        return os.system("which say") == 0

    def shellquote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"

    def say(self, phrase):
        os.system("say " + self.shellquote(phrase))

    def play(self, filename):
        os.system("afplay " + filename)


def newSpeaker(logger, profile):
    """
    Returns:
        A speaker implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """
    tts_engine = profile['tts_engine'].lower()
    
    if tts_engine == 'google':
      return GoogleSpeaker(logger, profile)
    elif tts_engine == 'ivona':
      return IvonaSpeaker(logger, profile)
    elif tts_engine == 'espeak':
      return eSpeakSpeaker(logger, profile)
    elif tts_engine == 'say':
      return saySpeaker(logger, profile)
    elif tts_engine == 'dummy':
      return DummySpeaker(logger, profile)

    #for cls in [GoogleSpeaker, eSpeakSpeaker, saySpeaker]:
    #    if cls.isAvailable():
    #        return cls(logger, profile)
    logger.critical("Platform is not supported", exc_info=True)
