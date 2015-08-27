# -*- coding: utf-8 -*-
# a może teraz?
"""
    The Mic class handles all interactions with the microphone and speaker.
"""

import os
import sys
from wave import open as open_audio
import audioop
import pyaudio

import re
import time
import str_formater

import jasperLogger
import logging


class Mic:


    def __init__(self, logger, snd_dev):
        """
        Initiates the pocketsphinx instance.

        Arguments:
        speaker -- handles platform-independent audio output
        passive_stt_engine -- performs STT while Jasper is in passive listen mode
        acive_stt_engine -- performs STT while Jasper is in active listen mode
        """
        self.logger = logger
        self.snd_dev = snd_dev
        #self.THRESHOLD = 0
        # TODO: Consolidate variables from the next three functions
        self.THRESHOLD_MULTIPLIER = 1.8
        #RATE = 16000
        self.audio = pyaudio.PyAudio()
        self.FORMAT = pyaudio.paInt16
        self.RATE = 48000
        self.CHUNK = 8096 #1024
        self.CHANNELS = 1

    def getScore(self, data):
        rms = audioop.rms(data, 2)
        score = rms / 3.0
        return score

    def fetchThreshold(self):
        self.logger.debug("fetchThreshold")

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 2
        LAST_SAMPLES_NO = 20 # about 5 per sec

        # prepare recording stream
        #self.audio = pyaudio.PyAudio()
        #defaultSampleRate = self.audio.get_device_info_by_index(0)['defaultSampleRate']
        #self.logger.debug("defaultSampleRate: %s" % repr(defaultSampleRate))
        stream = self.audio.open(format=self.FORMAT,
                            channels=self.CHANNELS,
                            rate=self.RATE,
                            input=True,
                            input_device_index=0,
                            frames_per_buffer=self.CHUNK)

        # stores the audio data
        frames = []

        # stores the lastN score values
        #lastN = [i for i in range(20)]
        lastN = []
        #self.logger.debug("lastN: %s" % repr(lastN)) 

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, self.RATE / self.CHUNK * THRESHOLD_TIME):

            data = stream.read(self.CHUNK)
            frames.append(data)

            # save this data point as a score
            if len(lastN) >= LAST_SAMPLES_NO:
              lastN.pop(0)
            score = round(self.getScore(data) * 100.0) / 100.0

            lastN.append(score)
            #self.logger.debug("lastN: %s" % repr(lastN)) 

            average = sum(lastN) / len(lastN)
            self.logger.debug("score: %6.2f average: %6.2f" % (score, average))

        stream.stop_stream()
        stream.close()

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * self.THRESHOLD_MULTIPLIER

        return THRESHOLD

    def passiveListen(self, PERSONA):
        """
        Listens for PERSONA in everyday sound. Times out after LISTEN_TIME, so needs to be
        restarted.
        """

        # check if no threshold provided
        #if self.THRESHOLD == 0:
        #    self.THRESHOLD = self.fetchThreshold()

        text = raw_input("You: ")
        text = str_formater.unicodeToUTF8(text, self.logger)
        self.logger.info("Got %s; is waiting for %s" % (text, PERSONA))
        if text.upper() == PERSONA or text == "":
          return (True, PERSONA)
        else:
          return (False, text)


    def activeListen(self, THRESHOLD=None, RATE=48000, CHUNK=8096):
        """
            Records until a second of silence or times out after 12 seconds
        """

        AUDIO_FILE = "active.wav"
        self.RATE  = RATE
        self.CHUNK = CHUNK
        #RATE = 16000
        #RATE = 44100
        #CHUNK = 512
        LISTEN_TIME = 5
        LAST_SAMPLES_NO = 10

        # check if no threshold provided
        if THRESHOLD == None:
            THRESHOLD = self.fetchThreshold()
            self.logger.debug("THRESHOLD: %6.2f" % THRESHOLD)

        self.play("../static/audio/beep_hi.mp3")

        # prepare recording stream
        #audio = pyaudio.PyAudio()
        #defaultSampleRate = self.audio.get_device_info_by_index(0)['defaultSampleRate']
        #self.logger.debug("defaultSampleRate: %s" % repr(defaultSampleRate))
        stream = self.audio.open(format=self.FORMAT,
                            channels=self.CHANNELS,
                            input_device_index=0,
                            rate=self.RATE,
                            input=True,
                            frames_per_buffer=self.CHUNK)

        frames = []
        # increasing the range # results in longer pause after command generation
        #lastN = [THRESHOLD * 1.2 for i in range(30)]
        lastN = []
        #self.logger.debug("lastN: %s" % repr(lastN)) 

        for i in range(0, self.RATE / self.CHUNK * LISTEN_TIME):

            try:
              data = stream.read(self.CHUNK)
              frames.append(data)
              score = round(self.getScore(data) * 100.0) / 100.0
              
              if len(lastN) >= LAST_SAMPLES_NO:
                lastN.pop(0)
              lastN.append(score)
              #self.logger.debug("lastN: %s" % repr(lastN)) 

              average = sum(lastN) / float(len(lastN))
              self.logger.debug("score: %6.2f average: %6.2f THRESHOLD * 0.8: %6.2f" % (score, average, THRESHOLD * 0.8))

              # TODO: 0.8 should not be a MAGIC NUMBER!
              if average < THRESHOLD * 0.8 and len(lastN) == LAST_SAMPLES_NO:
                  break
            except IOError:
              self.logger.critical("IOError error reading chunk", exc_info=True)

        self.play("../static/audio/beep_lo.mp3")

        # save the audio data
        stream.stop_stream()
        stream.close()
        #self.audio.terminate()
        write_frames = open_audio(AUDIO_FILE, 'wb')
        write_frames.setnchannels(self.CHANNELS)
        write_frames.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        write_frames.setframerate(self.RATE)
        write_frames.writeframes(''.join(frames))
        write_frames.close()

        return AUDIO_FILE

    def play(self, audio_file): #OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"
        # alter phrase before speaking
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        self.logger.info("audio_file: " + audio_file  )
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        if 'mp3' in audio_file:
          os.system("mpg123 -q --audiodevice=%s %s" % (self.snd_dev, audio_file))
        else:
          os.system("aplay -D %s %s" % (self.snd_dev, audio_file))




if __name__ == "__main__":
    l = jasperLogger.jasperLogger(level=logging.DEBUG, logFile='persistentCache.log', console=True)
    logger = l.getLogger()

    logger.info("start")
    if len(sys.argv) < 2:
      snd_dev = "plughw:1,0"
    else:
      snd_dev = sys.argv[1]
    
    mic = Mic(logger, snd_dev)
    f = mic.activeListen(THRESHOLD=None, RATE=48000, CHUNK=8096)
    mic.play('active.wav')
