#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import sys
import logging
import speaker
import stt
from conversation import Conversation


def isLocal():
    if len(sys.argv) > 1:
        for i in sys.argv.items() == "--local"
    return res

if isLocal():
    from local_mic import Mic
else:
    from mic import Mic


class jasperLogger:

    def __init__(self, level=logging.DEBUG, logFile='jasper.log'):
      self.logger = logging.getLogger('jasper')
      self.logger.setLevel(level)
      self.fh = logging.FileHandler(logFile)
      self.fh.setLevel(level)
      self.formatter = logging.Formatter('%(asctime)s %(module)s %(levelname)s %(message)s')
      self.fh.setFormatter(self.formatter)
      self.logger.addHandler(self.fh)

    def getLogger(self):
      return self.logger

    def logError(self, msg):
      self.logger.error(msg, exc_info=True)

if __name__ == "__main__":

    l = jasperLogger(level=logging.DEBUG)
    log = l.getLogger()

    log.info( "===========================================================")
    log.info( " JASPER The Talking Computer                               ")
    log.info( " Copyright 2013 Shubhro Saha & Charlie Marsh               ")
    log.info( "===========================================================")

    profile = yaml.safe_load(open("profile.yml", "r"))

    try:
        api_key = profile['keys']['GOOGLE_SPEECH']
    except KeyError:
        api_key = None

    try:
        stt_engine_type = profile['stt_engine']
    except KeyError:
        log.warn( "stt_engine not specified in profile, defaulting to PocketSphinx")
        stt_engine_type = "sphinx"

    try:
      spk = speaker.newSpeaker(log)
      passiveSTT = stt.PocketSphinxSTT(logger=log)
      activeSTT  = stt.newSTTEngine(stt_engine_type, logger=log, api_key=api_key)
      mic = Mic(spk, passiveSTT, activeSTT, log)
    except:
        log.critical( "fatal error creating mic", exc_info=True)
        exit(1)

    addendum = ""
    if 'first_name' in profile:
        addendum = ", %s" % profile["first_name"]
    mic.say("Czym mogę służyć%s?" % addendum)

    conversation = Conversation("ON", mic, profile, log)

    conversation.handleForever()
