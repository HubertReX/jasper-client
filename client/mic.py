# -*- coding: utf-8 -*-
# a może teraz?
"""
    The Mic class handles all interactions with the microphone and speaker.
"""

import os
from wave import open as open_audio
import audioop
import pyaudio
import alteration
import re
import time
import str_formater

class Mic:

    speechRec = None
    speechRec_persona = None

    def __init__(self, speaker, passive_stt_engine, active_stt_engine, logger, profile):
        """
        Initiates the pocketsphinx instance.

        Arguments:
        speaker -- handles platform-independent audio output
        passive_stt_engine -- performs STT while Jasper is in passive listen mode
        acive_stt_engine -- performs STT while Jasper is in active listen mode
        """
        if not profile:
          print "WARNING: got empty profile - using default values"
          profile = {}
        self.profile            = profile
        self.speaker            = speaker
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine  = active_stt_engine
        self.logger             = logger
        self.PERSONA            = self.profile.get('persona', 'Jasper')

    def readChunk(self, stream, chunk):
        try:
          data = stream.read(chunk)
        except IOError,e:
          if e[1] == pyaudio.paInputOverflowed:
            print e
            data = '\x00'*16*512*1 #value*format*chunk*nb_channels
        return data

    def getScore(self, data):
        rms = audioop.rms(data, 2)
        score = rms / 3
        return score

    def fetchThreshold(self, RATE=48000, CHUNK=8192, THRESHOLD_TIME=4, AVERAGE_TIME=4):

        # TODO: Consolidate variables from the next three functions
        THRESHOLD_MULTIPLIER = 1.8
        RATE = 16000
        #RATE = 48000
        CHUNK = 1024

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # prepare recording stream
        audio = pyaudio.PyAudio()
        defaultSampleRate = audio.get_device_info_by_index(0)['defaultSampleRate']
        self.logger.debug("defaultSampleRate: %s" % repr(defaultSampleRate))
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(20)]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            data = stream.read(CHUNK)
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        return THRESHOLD

    def passiveListen(self):
        """
        Listens for PERSONA in everyday sound. Times out after LISTEN_TIME, so needs to be
        restarted.
        """

        THRESHOLD_MULTIPLIER = 1.8
        AUDIO_FILE = "passive.wav"
        RATE = 16000
        #RATE = 48000
        CHUNK = 1024

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # number of seconds to listen before forcing restart
        LISTEN_TIME = 10

        # prepare recording stream
        audio = pyaudio.PyAudio()
        
        #defaultSampleRate = audio.get_device_info_by_index(0)['defaultSampleRate']
        #self.logger.debug("defaultSampleRate: %s" % repp(defaultSampleRate))
        
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(30)]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            data = stream.read(CHUNK)
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        # save some memory for sound data
        frames = []

        # flag raised when sound disturbance detected
        didDetect = False

        # start passively listening for disturbance above threshold
        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = stream.read(CHUNK)
            frames.append(data)
            score = self.getScore(data)

            if score > THRESHOLD:
                didDetect = True
                break

        # no use continuing if no flag raised
        if not didDetect:
            self.logger.info("No disturbance detected")
            return

        # cutoff any recording before this disturbance was detected
        frames = frames[-20:]

        # otherwise, let's keep recording for few seconds and save the file
        DELAY_MULTIPLIER = 1
        for i in range(0, RATE / CHUNK * DELAY_MULTIPLIER):

            data = stream.read(CHUNK)
            frames.append(data)

        # save the audio data
        stream.stop_stream()
        stream.close()
        audio.terminate()
        write_frames = open_audio(AUDIO_FILE, 'wb')
        write_frames.setnchannels(1)
        write_frames.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        write_frames.setframerate(RATE)
        write_frames.writeframes(''.join(frames))
        write_frames.close()

        # check if PERSONA was said
        transcribed = self.passive_stt_engine.transcribe(AUDIO_FILE, PERSONA_ONLY=True)

        if self.PERSONA in transcribed:
            return (THRESHOLD, self.PERSONA)

        return (False, transcribed)

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        """
            Records until a second of silence or times out after 12 seconds
        """

        AUDIO_FILE = "active.wav"
        RATE = 16000
        #RATE = 44100
        CHUNK = 1024
        LISTEN_TIME = 12

        # user can request pre-recorded sound
        if not LISTEN:
            if not os.path.exists(AUDIO_FILE):
                return None

            return self.active_stt_engine.transcribe(AUDIO_FILE)

        # check if no threshold provided
        if THRESHOLD == None:
            THRESHOLD = self.fetchThreshold()

        self.speaker.play("../static/audio/beep_hi.mp3")

        # prepare recording stream
        audio = pyaudio.PyAudio()
        defaultSampleRate = audio.get_device_info_by_index(0)['defaultSampleRate']
        self.logger.debug("defaultSampleRate: %s" % repr(defaultSampleRate))
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        frames = []
        # increasing the range # results in longer pause after command generation
        lastN = [THRESHOLD * 1.2 for i in range(30)]

        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            try:
              data = stream.read(CHUNK)
              frames.append(data)
              score = self.getScore(data)

              lastN.pop(0)
              lastN.append(score)

              average = sum(lastN) / float(len(lastN))

              # TODO: 0.8 should not be a MAGIC NUMBER!
              if average < THRESHOLD * 0.8:
                  break
            except IOError:
              self.logger.critical("IOError error reading chunk", exc_info=True)

        self.speaker.play("../static/audio/beep_lo.mp3")

        # save the audio data
        stream.stop_stream()
        stream.close()
        audio.terminate()
        write_frames = open_audio(AUDIO_FILE, 'wb')
        write_frames.setnchannels(1)
        write_frames.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        write_frames.setframerate(RATE)
        write_frames.writeframes(''.join(frames))
        write_frames.close()

        return self.active_stt_engine.transcribe(AUDIO_FILE, MUSIC)

    def say(self, phrase): #OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"
        # alter phrase before speaking
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        self.logger.info("JASPER: " + phrase  )
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        phrase = alteration.clean(phrase)
        self.speaker.say(phrase)

