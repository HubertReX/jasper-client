#!/usr/bin/env python
# -*- coding: utf-8 -*-
from notifier import Notifier
from musicmode import *
from brain import Brain
from mpd import MPDClient


class Conversation(object):

    def __init__(self, persona, mic, profile, logger):
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile, logger)
        self.notifier = Notifier(profile, logger)
        self.logger = logger

    def delegateInput(self, text):
        """A wrapper for querying brain."""

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
                self.mic.say(
                    "Wybacz, ale najwyraźniej usługa Spotify nie działa")
                return
            
            self.logger.info("waiting for Spotify playlist")
            self.mic.say("Poczekaj chwilę, wczytuję listę utworów Spotify")
            music_mode = MusicMode(self.persona, self.mic, self.logger)
            music_mode.handleForever()
            return

        self.brain.query(text)

    def handleForever(self):
        """Delegates user input to the handling function when activated."""
        repeat = True
        while repeat:

            # Print notifications until empty
            notifications = self.notifier.getAllNotifications()
            for notif in notifications:
                self.logger.info("Got new notification: %s" % notif.encode('utf-8') )

            try:
                threshold, transcribed = self.mic.passiveListen(self.persona)
            except:
                continue

            if threshold:
                input = self.mic.activeListen(threshold)
                self.logger.debug("got threshold %s and input %s" % (threshold, repr(input) ) )
                if input:
                    if any(x in input.upper() for x in ["KONIEC"]):
                      repeat = False
                      self.logger.info("Quiting after voice request")
                      self.mic.say("Kończę pracę. Do usłyszenia.")
                    else:
                      self.delegateInput(input)
                else:
                    self.mic.say("Powtórz poroszę.")
