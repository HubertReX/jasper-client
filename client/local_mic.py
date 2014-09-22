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

    def __init__(self, speaker, passive_stt_engine, active_stt_engine, logger):
        self.speaker = speaker
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine
        self.logger = logger
        return

    def passiveListen(self, PERSONA):
        return True, "JASPER"

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        if not LISTEN:
            return self.prev

        input = raw_input("YOU: ")
        input = str_formater.unicodeToUTF8(input, self.logger)
        self.prev = input
        return input

    def say(self, phrase, OPTIONS=None):
        #phrase = phrase.decode('utf8')
        print "JAN: " + phrase
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        self.logger.info("JASPER: " + phrase  )
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        phrase = alteration.clean(phrase)
        self.speaker.say(phrase)
