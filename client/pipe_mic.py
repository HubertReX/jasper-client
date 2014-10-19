# -*- coding: utf-8 -*-
# a może teraz?
"""
A drop-in replacement for the Mic class that gets input from
named pipe. It can be anny source, by here the goal is to
communicate with www flask server, where voice recognition
is done through chrome browser. We get plain text with
no need for stt engine (chrome browser uses google engine).
"""
import re
import alteration
import os
import time
import str_formater

PIPE_NAME = '/home/pi/flask/jasper_pipe_mic'

class Mic:
    prev = None

    def __init__(self, speaker, passive_stt_engine, active_stt_engine, logger):
        self.speaker = speaker
        #self.passive_stt_engine = passive_stt_engine
        #self.active_stt_engine = active_stt_engine
        self.logger = logger
        try:
            if not os.path.exists(PIPE_NAME):
                os.mkfifo(PIPE_NAME)
            self.pipein = open(PIPE_NAME, 'r')
        except:
            self.logger.error("error preparing named pipe", exc_info=True)
            exit(1)
        return

    def passiveListen(self, PERSONA):
        return True, "JAN"

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        if not LISTEN:
            return self.prev
        stop = False
        while not stop:
            input = self.pipein.readline()[:-1]
            if input:
                stop = True
        input = str_formater.unicodeToUTF8(input, self.logger)
        self.prev = input
        return input

    def say(self, phrase, OPTIONS=None):
        #phrase = phrase.decode('utf8')
        #print "JAN: " + phrase
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        self.logger.info("JAN: " + phrase  )
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        phrase = alteration.clean(phrase)
        self.speaker.say(phrase)
