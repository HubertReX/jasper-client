#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import sys
import jasperLogger
import logging
import speaker
import stt
from conversation import Conversation
import argparse
import shelve

parser = argparse.ArgumentParser(
description='the Jasper client')
parser.add_argument('--local', '-l', action='store_true',
                    help="use local mic (input from keyboard); useful for debug")
parser.add_argument('--half-local', '-hl', action='store_true',
                    help="use keyboard for passive and mic for active listen")
parser.add_argument('--dynamic', '-d', action='store_true',
                    help="dynamic mic uses adaptive threshold with full recognition in passive mode")
parser.add_argument('--pipe', '-p', action='store_true',
                    help="use mic as named pipe (input from www server)")
parser.add_argument('--sock', '-s', action='store_true',
                    help="use mic as socket (input from Android cliente over tcp socket)")
parser.add_argument('--no-speaker', '-n', action='store_true',
                    help="do not use speach synthesiser (output to console and log); useful for debug")
parser.add_argument('--log-to-console', '-c', action='store_true',
                    help="log everything to console instead of jasper.log file")
args = parser.parse_args()


def isLocal():
    return args.local

if args.local:
    from local_mic import Mic
elif args.pipe:
    from pipe_mic import Mic
elif args.half_local:
    from half_local_mic import Mic
elif args.dynamic:
    from dynamic_mic import Mic
elif args.sock:
    from socket_select_mic import Mic
else:
    from mic import Mic


#class jasperLogger:
#
#    def __init__(self, level=logging.DEBUG, logFile='jasper.log'):
#      self.logger = logging.getLogger('jasper')
#      self.logger.setLevel(level)
#      self.fh = logging.FileHandler(logFile)
#      self.fh.setLevel(level)
#      self.formatter = logging.Formatter('%(asctime)s %(module)s %(levelname)s %(message)s')
#      self.fh.setFormatter(self.formatter)
#      self.logger.addHandler(self.fh)
#
#    def getLogger(self):
#      return self.logger
#
#    def logError(self, msg):
#      self.logger.error(msg, exc_info=True)

if __name__ == "__main__":
    con = args.log_to_console
    l = jasperLogger.jasperLogger(level=logging.DEBUG, console=con)
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
        log.warn("stt_engine not specified in profile, defaulting to PocketSphinx")
        stt_engine_type = "sphinx"
    
    log.debug("command line args: %s" % args)
    
    try:
      if args.no_speaker:
        spk = speaker.DummySpeaker(log, profile)
      else:
        spk = speaker.newSpeaker(log, profile)
      
      if not args.pipe and not args.sock and not args.local and not args.half_local and not args.dynamic:
        passiveSTT = stt.PocketSphinxSTT(logger=log)
        activeSTT  = stt.newSTTEngine(stt_engine_type, logger=log, api_key=api_key)
      elif args.half_local or args.dynamic:
        passiveSTT = None
        activeSTT  = stt.newSTTEngine(stt_engine_type, logger=log, api_key=api_key)
      else:
        passiveSTT = None
        activeSTT  = None

      mic = Mic(spk, passiveSTT, activeSTT, log, profile=profile)      
    except:
        log.critical( "fatal error creating mic", exc_info=True)
        exit(1)

    addendum = ""
    if 'first_name' in profile:
        addendum = ", %s" % profile["first_name"]
    mic.say("Czym mogę służyć%s?" % addendum)

    conversation = Conversation(mic, profile, log)

    conversation.handleForever()
