#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib2
import sys

import vocabcompiler
import traceback

lib_path = os.path.abspath('../client')
sys.path.append(lib_path)

import speaker as speak
speaker = speak.newSpeaker()

def configure():
    try:
        urllib2.urlopen("http://www.google.com").getcode()

        print "CONNECTED TO INTERNET"
        print "COMPILING DICTIONARY"
        vocabcompiler.compile("../client/sentences.txt", "../client/dictionary.dic", "../client/languagemodel.lm")

        print "STARTING CLIENT PROGRAM"
        os.system("$JASPER_HOME/jasper/client/start.sh &")

    except:
        print "COULD NOT CONNECT TO NETWORK"
        traceback.print_exc()
        speaker.say("Witaj, nie udało mi się połączyć z internetem. Muszę, więc zakończyć.")

if __name__ == "__main__":
    print "==========STARTING JASPER CLIENT=========="
    print "=========================================="
    print "COPYRIGHT 2013 SHUBHRO SAHA, CHARLIE MARSH"
    print "=========================================="
    speaker.say("Witaj... nazywam się Ania... proszę poczekaj chwilę, aż będę gotowa")
    configure()
