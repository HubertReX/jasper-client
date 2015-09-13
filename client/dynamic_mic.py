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
import alteration
import re
import time
import datetime
import numpy
import analyse
import math

import fcntl
import termios
import struct

import stt
import yaml
import speaker
import jasperLogger
import str_formater
import logging

from modules.app_utils import *

# Dummy Alsa error handler
#http://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time
from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)



##########################################################################################
class DrawVolumeBar():

    def __init__(self, width=None, height=None):
        if not width or not height:
          self.width, self.height = self.getTerminalSize()
        else:
          self.width  = width
          self.height = height

    def getTerminalSize(self):
        import os
        env = os.environ
        
        def ioctl_GWINSZ(fd):
            try:
                import fcntl, termios, struct, os
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
            '1234'))
            except:
                return
            return cr
        
        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        
        if not cr:
            cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
        
        return int(cr[1]), int(cr[0])

    def color(self, this_color, string):
        return "\033[" + str(this_color) + "m" + string + "\033[0m"
    
    def save(self):
        #Saves cursor position'
        print '\033[s'
    
    def restore(self):
        'Restores cursor position'
        print '\033[u'

    def clear(self):
        """Clear screen"""
        sys.stdout.write('\033[2J')
        sys.stdout.flush()

    def reset_cursor(self):
        """return cursor to top left"""
        sys.stdout.write('\033[H')
        sys.stdout.flush()

    def bold(self, msg):
        return u'\033[1m%s\033[0m' % msg

    def progress(self, current, total, pitch, suffix):
        #COLS = struct.unpack('hh',  fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234'))[1]
        current = abs(current)
        total = abs(total)
        pitch = abs(pitch)

        prefix = '%3d / %3d' % (current, total)
        #suffix = '%4.1f s' % (12.1)
        bar_start = ' ['
        bar_end = '] '

        bar_size = self.width - len(prefix + bar_start + bar_end + suffix)
        if pitch > total:
          pitch = total-1
        pitch =  int(pitch   / (total / float(bar_size)))
        amount = int(current / (total / float(bar_size)))
        a = 15
        p = 10
        if amount > pitch:
          over_pitch = amount - pitch - 1
          amount = pitch
          remain = bar_size - amount - over_pitch - 1
        else:
          over_pitch = 0
          remain     = bar_size - pitch - 1

        
        if over_pitch == 0:
          #bar = '#' * amount + over_pitch + ' ' * remain
          bar = self.color(32, u"\u2588" * amount) + ' ' * (pitch - amount) + self.color(31, '|') + ' ' * remain
        else:
          bar = self.color(32, u"\u2588" * amount) + self.color(31, '|' + u"\u2588" * over_pitch) + ' ' * remain
        return self.bold(prefix) + bar_start + bar + bar_end + self.bold(suffix)

    def draw_bar(self, elements, header, pitch, frames_pers_sec, cut_off=None, split=None, verbose=False):
        if not verbose:
          print header
          return

        self.width, self.height = self.getTerminalSize()
        self.height = 15
        #self.save()
        self.reset_cursor()
        sys.stdout.write(header + '\n')
        #samps = numpy.fromstring(data, dtype=numpy.int16)
        #analyse.loudness(samps), analyse.musical_detect_pitch(samps)
        #print(analyse.loudness(samps))
        #print(analyse.musical_detect_pitch(samps))
        #print(analyse.detect_pitch(samps))

        if len(elements) < self.height - 2:
          offset = '\n' * (self.height - len(elements) - 4)
          sys.stdout.write(offset)
          last_n = len(elements)
        else:
          last_n = self.height - 4
        
        i      = last_n
        sec    = 999.0 
        for el in elements[-last_n:]:
          if cut_off > 0.0:
            max_el = cut_off
            if el > cut_off:
              el = cut_off
          else:
            max_el = max(elements)

          if i == split:
            sys.stdout.write('=' * (self.width-1) + '\n')  
          i -= 1

          new_sec = math.ceil(float(i)  / frames_pers_sec)
          if new_sec < sec:
            if sec == 999.0:
              sec = new_sec
              suffix = ' ' * 6
            else:
              sec = new_sec
              suffix = '%4.1f s' % (sec)
          else:
            suffix = ' ' * 6
          #suffix = '%4.1f s' % ( math.ceil(float(i) / frames_pers_sec))
          sys.stdout.write(self.progress(el, max_el, pitch, suffix) + '\n')
          sys.stdout.flush()         
        #self.restore()

    
    def get_sample_data(self):
        elements = []
        elements.append(  0.0)
        elements.append( 10.0)
        elements.append( 20.0)
        elements.append( 30.0)
        elements.append( 50.0)
        elements.append(  0.0)
        elements.append(  0.0)
        elements.append(135.5)
        elements.append(131.0)
        elements.append(128.0)
        elements.append(149.0)
        elements.append(160.0)
        elements.append(172.0)
        elements.append(180.0)
        elements.append(200.0)
        elements.append(150.0)
        elements.append(100.0)
        elements.append(110.0)
        elements.append(120.0)
        elements.append(300.0)
        return elements


##########################################################################################
class Mic:


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
        
        self.volume_bar         = DrawVolumeBar()
        #self.THRESHOLD = 0
        # TODO: Consolidate variables from the next three functions
        #self.THRESHOLD_MULTIPLIER = 1.8 # for PSM
        self.THRESHOLD_MULTIPLIER = 1.25 # 3 dB for dB
        #RATE = 16000
        #with noalsaerr():
        self.audio         = pyaudio.PyAudio()
        self.THRESHOLD     = None
        self.INPUT_DEVICE  = self.profile.get('input_device_name', 'hw:2,0')
        self.FORMAT        = pyaudio.paInt16
        self.RATE          = self.set_default_sample_rate()
        self.CHUNK         = 8192 #1024
        self.CHANNELS      = 1

    def __del__(self):
        if self.audio:
          self.audio.terminate()

    def set_default_sample_rate(self):
        cnt = self.audio.get_device_count()

        for el in range(cnt):
          info = self.audio.get_device_info_by_index(el)
          print "DEVICE: %s" % info["name"]
          if self.INPUT_DEVICE in info["name"]:
            self.INPUT_DEVICE_IDX = el
            print "self.INPUT_DEVICE_IDX: %d defaultSampleRate: %d" % (self.INPUT_DEVICE_IDX, int(info['defaultSampleRate']))
            return int(info['defaultSampleRate'])
          
        return 44100

    def find_input_device(self):
        device_index = None            
        for i in range( self.audio.get_device_count() ):     
            devinfo = self.audio.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )
            if self.INPUT_DEVICE in devinfo["name"]:
                print "#" * 40
                for key in devinfo.keys():
                  print "  %s: %s" % (key, str(devinfo[key]))

            for keyword in ["mic", "input"] :
                if devinfo["maxInputChannels"] > 0:
                    print( "Found an input: device %d - %s" % (i, devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def getScore(self, data):
        rms = audioop.rms(data, self.audio.get_sample_size(self.FORMAT))
        score = rms / 3.0
        return score

    def to_dB(self, data):
        return 20.0 * math.log10(data)
    
    def get_RMS(self, data):
        data = numpy.fromstring(data, dtype=numpy.int16)
        res = numpy.sqrt(numpy.mean(data**2))
        if math.isnan(res):
          res = 1.0
        return res

    def get_dB(self, data):
        return 20.0 * numpy.log10(data)

    def fetchThreshold(self, RATE=48000, CHUNK=8192, THRESHOLD_TIME=2, AVERAGE_TIME=None):
     
        print "rate %d chunk %d THRESHOLD_TIME %d AVERAGE_TIME %s" % (self.RATE, CHUNK, THRESHOLD_TIME, repr(AVERAGE_TIME))
        # number of seconds to allow to establish threshold
        #THRESHOLD_TIME  = 1  # in seconds
        THRESHOLD = None
        if not AVERAGE_TIME:
          AVERAGE_TIME = THRESHOLD_TIME
        LAST_SAMPLES_NO = int(AVERAGE_TIME * (self.RATE / CHUNK))
        print "self.CHANNELS:", self.CHANNELS
        print "self.INPUT_DEVICE_IDX:", self.INPUT_DEVICE_IDX
        # prepare recording stream
        stream = self.audio.open(format             = self.FORMAT,
                                 channels           = self.CHANNELS,
                                 input_device_index = self.INPUT_DEVICE_IDX,
                                 rate               = self.RATE,
                                 input              = True,
                                 frames_per_buffer  = CHUNK)

        # stores the audio data
        frames = []
        loudness_t = []
        loudness_t.append(30)
        # stores the lastN score values
        #lastN = [i for i in range(20)]
        lastN = []
        allN  = []
        gotKeyboardInterrupt = False
        #self.logger.debug("lastN: %s" % repr(lastN)) 

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, self.RATE / CHUNK * THRESHOLD_TIME):
          
          try:
            data = stream.read(CHUNK)
            #data = self.audioFilter(data)
            frames.append(data)

            # save this data point as a score
            if len(lastN) >= LAST_SAMPLES_NO:
              lastN.pop(0)
            #score = round(self.getScore(data) * 100.0) / 100.0
            score = round( self.to_dB(self.getScore(data)) * 100.0) / 100.0

            lastN.append(score)
            allN.append(score)
            #self.logger.debug("lastN: %s" % repr(lastN)) 

            average = sum(lastN) / len(lastN)
            #self.logger.debug("score: %6.2f average: %6.2f" % (score, average))
            #samps = numpy.fromstring(data, dtype=numpy.int16)
            #loudness = analyse.loudness(samps)
            #loudness_t.append(int(loudness) + 30)
            cut_off = 110.0 # 999.0
            split   = LAST_SAMPLES_NO

            # this will be the benchmark to cause a disturbance over!
            THRESHOLD = average * self.THRESHOLD_MULTIPLIER
            if THRESHOLD == average:
              THRESHOLD += 1

            header = '[ Current: %10.2f | Average: %10.2f | Threshold: %10.2f | Cut off: %10.2f | Average time: %4d s ]\n' % (score, average, THRESHOLD, cut_off, AVERAGE_TIME)

            self.volume_bar.draw_bar(allN, header, THRESHOLD, self.RATE / CHUNK, cut_off, split, verbose=True)
          except KeyboardInterrupt:
            print 'got break'
            gotKeyboardInterrupt = True
            break

        stream.stop_stream()
        stream.close()

        if gotKeyboardInterrupt:
          raise KeyboardInterrupt
        return THRESHOLD
    

    def passiveListen(self):
        """
        Listens for PERSONA in everyday sound. Times out after LISTEN_TIME, so needs to be
        restarted.
        """
        repeat = True
        while repeat:
          #try:
            #os.system('tmux send-keys -t jasper-debug "start\n"')
            #self.THRESHOLD = None
            
            self.volume_bar.save()
            audio = self.recordAudio(THRESHOLD=None, CHUNK=8192, LISTEN_TIME=60, RECORD_TIME=8, AVERAGE_TIME=20)
            self.volume_bar.restore()
            
            if audio:
              self.speaker.play("../static/audio/beep_hi.mp3")
              t1 = get_time(self.profile)
              transcribed = self.active_stt_engine.transcribe(audio)
              t2 = get_time(self.profile)
              runtime = get_runtime(t1, t2)
              #print "%s # Transcribed: %s  in %3.1f seconds" % (format_time(t2), transcribed, runtime)
              os.system('tmux send-keys -t jasper-debug "%s # transcribed: %s in %3.1f seconds\n\r"' % (format_time(t2), transcribed, runtime))
              #os.system('tmux send-keys -t jasper-debug "transcribed: %s persona: %s pos: %d  \n\n"' % (transcribed.upper(), self.PERSONA.upper(), self.PERSONA.upper().find(transcribed.upper() + " ")) )
              #print ' "transcribed: %s persona: %s pos: %d  \n\n"' % (transcribed.upper(), self.PERSONA.upper(), transcribed.upper().find(self.PERSONA.upper() + " ")) 
              msg = ""
              if transcribed:
                if transcribed.upper() == self.PERSONA.upper():
                  return (True, None)
                elif self.PERSONA.upper() in transcribed.upper() and transcribed.upper().find(self.PERSONA.upper() + " ") == 0:
                  msg = transcribed[transcribed.find(" ")+1:]
                  #print "you: %s:" % msg
                  return (True, msg)
                else:
                  # no PERSONA in phrase or stt failed
                  self.speaker.play("../static/audio/beep_lo.mp3")
            else:    
              return (False, None)
          #except KeyboardInterrupt:
          #  print 'got break'
          #  break
        return (False, None)


    def audioFilter(self, s):
        s = (numpy.fromstring(s, numpy.int16) - 450) / 10 * 30
        return struct.pack('h'*len(s), *s)

    def extractData(self, data):
        return numpy.fromstring(data, numpy.int16)

    def isAboveThreshold(self, lastN, THRESHOLD):
        size = len(lastN)
        if size < 3:
          return False

        if lastN[-3] < THRESHOLD and lastN[-2] >= THRESHOLD and lastN[-1] >= THRESHOLD:
          return True
        else:
          return False

    def isBelowThreshold(self, lastN, THRESHOLD):
        size = len(lastN)
        if size < 4:
          return False

        if lastN[-4] < THRESHOLD and lastN[-3] < THRESHOLD and lastN[-2] < THRESHOLD and lastN[-1] < THRESHOLD:
          return True
        else:
          return False

    def recordAudio(self, THRESHOLD=None, LISTEN=True, MUSIC=False, RATE=48000, CHUNK=8096, LISTEN_TIME=5, RECORD_TIME=None, AVERAGE_TIME=None):
        """
            Records until a second of silence or times out after 12 seconds
        """

        AUDIO_FILE = "active.wav"

        #self.RATE  = RATE
        self.CHUNK = CHUNK
        # TODO: 0.8 should not be a MAGIC NUMBER!
        THRESHOLD_LIMIT_RATIO = 1.0 #0.8 
        MAX_BUFFER = 200
        #RATE = 16000
        
        #LISTEN_TIME = 5
        if not AVERAGE_TIME:
          AVERAGE_TIME = LISTEN_TIME
        LAST_SAMPLES_NO = int(AVERAGE_TIME * (self.RATE / self.CHUNK))

        if not RECORD_TIME:
          RECORD_TIME = LISTEN_TIME
        LAST_FRAMES_NO = int(RECORD_TIME * (self.RATE / self.CHUNK))
        #LAST_SAMPLES_NO = 5

        # user can request pre-recorded sound
        if not LISTEN:
            if not os.path.exists(AUDIO_FILE):
                return None

            return AUDIO_FILE

        # check if no threshold provided
        if THRESHOLD == None:
          if not self.THRESHOLD:
            self.THRESHOLD = self.fetchThreshold(RATE=RATE, CHUNK=CHUNK)
        else:
          self.THRESHOLD = THRESHOLD
          
        self.THRESHOLD = abs(self.THRESHOLD)
        #self.logger.debug("THRESHOLD: %6.2f" % self.THRESHOLD)
        limit = round(self.THRESHOLD * THRESHOLD_LIMIT_RATIO * 100.0) / 100.0
        
        #self.speaker.play("../static/audio/beep_hi.mp3")
        # wait 330 ms in order not to record beep
        #time.sleep(0.33)
        # prepare recording stream
        #audio = pyaudio.PyAudio()
        #defaultSampleRate = audio.get_device_info_by_index(0)['defaultSampleRate']
        #self.logger.debug("defaultSampleRate: %s" % repr(defaultSampleRate))
        stream = self.audio.open(format              = self.FORMAT,
                                 channels            = self.CHANNELS,
                                 input_device_index  = self.INPUT_DEVICE_IDX,
                                 rate                = self.RATE,
                                 input               = True,
                                 frames_per_buffer   = self.CHUNK)

        frames  = []
        # increasing the range # results in longer pause after command generation
        #lastN = [THRESHOLD * 1.2 for i in range(30)]
        lastN   = []
        allN    = []
        header  = ''
        score   = 0.0
        average = 0.0
        cut_off = 120.0
        split   = LAST_SAMPLES_NO

        #self.logger.debug("lastN: %s" % repr(lastN)) 

        wasAbove = False
        wasBelow = False
        gotKeyboardInterrupt = False

        #self.volume_bar.save()

        for i in range(0, self.RATE / self.CHUNK * LISTEN_TIME):

            try:
              data = stream.read(self.CHUNK)
              #data = self.audioFilter(data)
              if len(frames) >= LAST_FRAMES_NO:
                frames.pop(0)
              frames.append(data)
              #score = round(self.getScore(data) * 100.0) / 100.0
              score = round(self.to_dB(self.getScore(data)) * 100.0) / 100.0

              if len(lastN) >= LAST_SAMPLES_NO:
                lastN.pop(0)
              lastN.append(score)
              if len(allN) >= MAX_BUFFER:
                allN.pop(0)
              allN.append(score)
              #self.logger.debug("lastN: %s" % repr(lastN)) 

              average = sum(lastN) / float(len(lastN))
              #self.THRESHOLD = average * self.THRESHOLD_MULTIPLIER
              if self.THRESHOLD == average:
                self.THRESHOLD += 1
              limit = round(self.THRESHOLD * THRESHOLD_LIMIT_RATIO * 100.0) / 100.0

              #self.logger.debug("score: %6.2f average: %6.2f THRESHOLD : %6.2f" % (score, average, THRESHOLD ))
              
              
              header = '[ Current: %10.2f | Average: %10.2f | Threshold : %10.2f | Cut off: %10.2f | Average time: %4d s | was Above: %d ]\n' % (score, average, limit, cut_off, AVERAGE_TIME, wasAbove)
                            
              self.volume_bar.draw_bar(allN, header, limit, self.RATE / self.CHUNK, cut_off, split, verbose=True)

              if not wasAbove and self.isAboveThreshold(lastN, limit):
                wasAbove = True

              if wasAbove and self.isBelowThreshold(lastN, limit):
                print "not above threshold any more"
                wasBelow = True
                break
              #if average < limit and len(lastN) == LAST_SAMPLES_NO:
              #    break
            except IOError:
              self.logger.critical("IOError error reading chunk", exc_info=True)
            except KeyboardInterrupt:
              print 'got break'
              # temporarly mask exception to clean up
              gotKeyboardInterrupt = True
              break

        #self.speaker.play("../static/audio/beep_lo.mp3")

        # save the audio data
        stream.stop_stream()
        stream.close()
        #self.audio.terminate()
        if wasBelow:
          write_frames = open_audio(AUDIO_FILE, 'wb')
          write_frames.setnchannels(self.CHANNELS)
          write_frames.setsampwidth(self.audio.get_sample_size(self.FORMAT))
          write_frames.setframerate(self.RATE)
          write_frames.writeframes(''.join(frames))
          write_frames.close()
        else:
          #finished after timeout and not threshold crossed - not record audio to file
          AUDIO_FILE = None
        self.volume_bar.clear()
        self.volume_bar.draw_bar(allN, header, limit, self.RATE / self.CHUNK, cut_off, split, verbose=True)
        #self.volume_bar.restore()
        
        if gotKeyboardInterrupt:
          # all is cleaned up - rerise exception
          #raise KeyboardInterrupt
          return None

        return AUDIO_FILE


    def loadAudio(self, AUDIO_FILE, THRESHOLD=None, LISTEN=True, MUSIC=False, RATE=48000, CHUNK=8096, LISTEN_TIME=5, AVERAGE_TIME=None):
        """
            Records until a second of silence or times out after 12 seconds
        """

        #AUDIO_FILE = "active.wav"
        if not AUDIO_FILE:
          print "No WAV file name given"
          return None
        else:
          if not os.path.isfile(AUDIO_FILE):
            print "Given WAV faile doesn't exist: %s " % AUDIO_FILE
            return None


        read_frames = open_audio(AUDIO_FILE, 'rb')
        self.CHANNELS = read_frames.getnchannels()
        sample_size = read_frames.getsampwidth()
        #self.audio.get_sample_size(self.FORMAT)
        self.RATE = read_frames.getframerate()
        
        

        #self.RATE  = RATE
        self.CHUNK = CHUNK

        THRESHOLD_LIMIT_RATIO = 1.0 #0.8 
        #RATE = 16000
        
        #LISTEN_TIME = 5
        if not AVERAGE_TIME:
          AVERAGE_TIME = LISTEN_TIME
        LAST_SAMPLES_NO = int(AVERAGE_TIME * (self.RATE / self.CHUNK))
        #LAST_SAMPLES_NO = 5

        # check if no threshold provided
        if THRESHOLD == None:
          if not self.THRESHOLD:
            self.THRESHOLD = self.fetchThreshold(RATE=RATE, CHUNK=CHUNK)
        else:
          self.THRESHOLD = THRESHOLD
        #self.logger.debug("THRESHOLD: %6.2f" % self.THRESHOLD)
        limit = round(self.THRESHOLD * THRESHOLD_LIMIT_RATIO * 100.0) / 100.0
        
        #self.speaker.play("../static/audio/beep_hi.mp3")
        # wait 330 ms in order not to record beep
        #time.sleep(0.33)
        # prepare recording stream
        #audio = pyaudio.PyAudio()
        #defaultSampleRate = audio.get_device_info_by_index(0)['defaultSampleRate']
        #self.logger.debug("defaultSampleRate: %s" % repr(defaultSampleRate))

        frames = []
        # increasing the range # results in longer pause after command generation
        #lastN = [THRESHOLD * 1.2 for i in range(30)]
        lastN = []
        allN  = []
        #self.logger.debug("lastN: %s" % repr(lastN)) 


        while True:

            try:
              data = read_frames.readframes(self.CHUNK)
              if not data:
                print "got end of file"
                break
              #data = self.audioFilter(data)
              frames.append(data)
              
              score = self.getScore(data)
              score = self.to_dB(score)
              
              #score = self.get_RMS(data)
              #score = self.get_dB(score)

              score = round(score * 100.0) / 100.0

              if len(lastN) >= LAST_SAMPLES_NO:
                lastN.pop(0)
              lastN.append(score)
              allN.append(score)
              #self.logger.debug("lastN: %s" % repr(lastN)) 

              average = sum(lastN) / float(len(lastN))
              #self.logger.debug("score: %6.2f average: %6.2f THRESHOLD : %6.2f" % (score, average, THRESHOLD))
              cut_off = 120.0
              #cut_off = 999.0
              split   = LAST_SAMPLES_NO
              header = '[ Current: %10.2f | Average: %10.2f | Threshold : %10.2f | Cut off: %10.2f | Average time: %4d s  ]\n' % (score, average, limit, cut_off, AVERAGE_TIME)
                            
              self.volume_bar.draw_bar(allN, header, limit, self.RATE / self.CHUNK, cut_off, split)
              arr = self.extractData(data)
              print len(arr), min(arr), max(arr), sum(arr)/len(arr)
              text = raw_input("<pause>")
            except IOError:
              self.logger.critical("IOError error reading chunk", exc_info=True)
              break
            except KeyboardInterrupt:
              print 'got break'
              break

        #self.speaker.play("../static/audio/beep_lo.mp3")

        # save the audio data
        #self.audio.terminate()

        read_frames.close()

        return AUDIO_FILE

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False, RATE=48000, CHUNK=8192, LISTEN_TIME=5, RECORD_TIME=60, AVERAGE_TIME=2):
                                
        self.speaker.play("../static/audio/beep_hi.mp3")
        audio_file = self.recordAudio(THRESHOLD=THRESHOLD, LISTEN=LISTEN, MUSIC=MUSIC, RATE=RATE, CHUNK=CHUNK, LISTEN_TIME=LISTEN_TIME, RECORD_TIME=RECORD_TIME, AVERAGE_TIME=AVERAGE_TIME) #RECORD_TIME=60, 
        self.speaker.play("../static/audio/beep_lo.mp3")

        if audio_file:
          return self.active_stt_engine.transcribe(audio_file, MUSIC)
        else:
          return None

    def say(self, phrase): #OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"
        # alter phrase before speaking
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        self.logger.info("JASPER: " + phrase  )
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        phrase = alteration.clean(phrase)
        self.speaker.say(phrase)

    def continousListen(self):
        repeat = True
        os.system('tmux send-keys -t jasper-debug "start\r\n"')
        while repeat:
          try:
            #self.THRESHOLD = None
            audio = mic.recordAudio(THRESHOLD=None, CHUNK=8192, LISTEN_TIME=60, RECORD_TIME=8, AVERAGE_TIME=20)
            if audio:
              self.speaker.play("../static/audio/beep_hi.mp3")
              t1 = get_time(self.profile)
              transcribed = self.active_stt_engine.transcribe(f)
              t2 = get_time(self.profile)
              runtime = get_runtime(t1, t2)
              #print "%s # Transcribed: %s  in %3.1f seconds" % (format_time(t2), transcribed, runtime)
              os.system('tmux send-keys -t jasper-debug "%s # transcribed: %s in %3.1f seconds\n\r"' % (format_time(t2), transcribed, runtime))
              #os.system('tmux send-keys -t jasper-debug "transcribed: %s persona: %s pos: %d  \n\n"' % (transcribed.upper(), self.PERSONA.upper(), self.PERSONA.upper().find(transcribed.upper() + " ")) )
              msg = ""
              if transcribed:
                if transcribed.upper() == self.PERSONA.upper():
                  msg = transcribed
                elif self.PERSONA.upper() in transcribed.upper() and transcribed.upper().find(self.PERSONA.upper() + " ") == 0:
                  msg = transcribed[transcribed.find(" ")+1:]
                if msg:
                  # send text command to jasper instance running in tmux session named jasper
                  print "send command to jaser %s" % msg
                  os.system('tmux send-keys -t jasper-debug "msg: %s\n\r"' % msg)
                  os.system('tmux send-keys -t jasper "%s\n\r"' % msg)
                  #cmd = "tmux send-keys -t jasper '%s\n'" % transcribed
                  #os.system(cmd)
                  if "KONIEC" in msg.upper():
                    break
                else:
                  # false activation or speach not recognised
                  self.speaker.play("../static/audio/beep_hi.mp3")
                
          except KeyboardInterrupt:
            print 'got break'
            break



if __name__ == "__main__":
    l = jasperLogger.jasperLogger(level=logging.DEBUG, logFile='persistentCache.log', console=True)
    logger = l.getLogger()
    profile = yaml.safe_load(open("profile.yml", "r"))
    #spk = speaker.DummySpeaker(logger, profile)
    spk = speaker.newSpeaker(logger, profile)
    activeSTT  = stt.newSTTEngine(profile['stt_engine'], logger=logger, api_key=profile['keys']['GOOGLE_SPEECH'])

    logger.info("start")
    if len(sys.argv) < 2:
      f = "active.wav"
    else:
      f = sys.argv[1]
    
    
    mic = Mic(spk, activeSTT, activeSTT, logger, profile)
    #f = 'samples/wlacz_dekoder_ncplusAt1003_4m_RodeM3_SBLive.wav'
    #f = 'samples/wlacz_dekoder_ncplusAt1003_1m_RodeM3_SBLive.wav'
    #mic.find_input_device()
    #print f
    #raw_input("<pause>")
    #t = mic.fetchThreshold(               RATE=48000, CHUNK=8192, THRESHOLD_TIME=60, AVERAGE_TIME=3)
    mic.find_input_device()
    #f = mic.recordAudio(THRESHOLD=None, RATE=48000, CHUNK=8192, LISTEN_TIME=20, RECORD_TIME=6, AVERAGE_TIME=3)
    f = mic.continousListen()
    #mic.loadAudio(f, THRESHOLD=120.0, RATE=48000, CHUNK=8192, LISTEN_TIME=8,    AVERAGE_TIME=None)
    #f = mic.activeListen(THRESHOLD=None, RATE=48000, CHUNK=8192, LISTEN_TIME=5,    AVERAGE_TIME=3)
    #print f
    #mic.speaker.play(f)
    
    
    #if f:
    #  t1 = get_time()
    #  transcribed = activeSTT.transcribe(f)
    #  t2 = get_time()
    #  runtime = get_runtime(t1, t2)
    #  print "%s # Transcribed: %s  in %3.1f seconds" % (format_time(t2), transcribed, runtime)
    
    #cmd = "tmux send-keys -t jasper '%s\n'" % transcribed
    #os.system(cmd)

    #bar = DrawVolumeBar()
    #elements = bar.get_sample_data()
    #pitch = 150.0
    #header = '[ Pitch: %d ]' % pitch
    #bar.draw_bar(elements, header, pitch, 5.85, cut_off=200.0, split=5)
    del mic

