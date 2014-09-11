#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A Speaker handles audio output from Jasper to the user

Speaker methods:
    say - output 'phrase' as speech
    play - play the audio in 'filename'
    isAvailable - returns True if the platform supports this implementation
"""
import os
import json


class GoogleSpeaker:

    """
    Uses the google speech synthesizer - requires to be on-line
    """
    def __init__(self, logger):
        self.logger = logger

    @classmethod
    def isAvailable(cls):
        return True

    def say(self, phrase):
        cmd = "wget -q --restrict-file-names=nocontrol --referer=\"http://translate.google.com\" -U Mozilla -O say.mp3 \"http://translate.google.com/translate_tts?ie=UTF-8&tl=pl&q=%s\" && avconv -y -v quiet -i say.mp3 -f wav say.wav" % phrase
        self.logger.debug("command for google translator: %s" % cmd)
        os.system(cmd)
        self.play("say.wav")

    def play(self, filename):
        os.system("aplay -D hw:2,0 " + filename)

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
        os.system("aplay -D hw:2,0 " + filename)


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
