# -*- coding: utf-8 -*-
# a może teraz?
"""
A drop-in replacement for the Mic class that allows for all I/O to occur
over the terminal. Useful for debugging. Unlike with the typical Mic
implementation, Jasper is always active listening with local_mic.
"""
import re
import alteration
import re
import time
import str_formater

class Mic:
    prev = None

    def __init__(self, speaker, passive_stt_engine, active_stt_engine, logger, snd_dev, input_device_index=0):
        self.speaker = speaker
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine
        self.logger = logger
        self.prev = ""
        return

    def fetchThreshold(self, RATE=48000, CHUNK=8192, THRESHOLD_TIME=4, AVERAGE_TIME=4):
        return 1

    def passiveListen(self, PERSONA):
        try:
          text = raw_input("You: ")
          text = str_formater.unicodeToUTF8(text, self.logger)
        except KeyboardInterrupt:
          return (True, "koniec")

        self.logger.info("Got %s; is waiting for %s" % (text, PERSONA))
        if text.upper() == PERSONA or text == "":
          return (True, None)
        else:
          return (True, text)

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        if not LISTEN:
            return self.prev

        input = raw_input("YOU: ")
        input = str_formater.unicodeToUTF8(input, self.logger)
        self.prev = input
        return input

    def say(self, phrase, OPTIONS=None):
        #phrase = phrase.decode('utf8')
        #print "JAN: " + phrase
        #self.logger.info(">>>>>>>>>>>>>>>>>>>")
        #self.logger.info("JASPER: " + phrase  )
        #self.logger.info(">>>>>>>>>>>>>>>>>>>")
        phrase = alteration.clean(phrase)
        self.speaker.say(phrase)
