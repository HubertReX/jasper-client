"""PyAudio Example: Play a wave file."""

import pyaudio
import wave
import sys
import math
import audioop
import random
import struct

CHUNK = 1024

THRESHOLD_MULTIPLIER = 1.8
#RATE = 160

THRESHOLD_TIME = 1
LISTEN_TIME = 10

def getScore(data):
    rms = audioop.rms(data, 2)
    #score = rms / 3
    #print "score:", score, " rms:", rms
    return rms

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()
print "sample width:", wf.getsampwidth()
print "get_format_from_width:", p.get_format_from_width(wf.getsampwidth())
print "channels:", wf.getnchannels()
print "framerate:", wf.getframerate()
RATE = wf.getframerate()
print "chunks per sec", RATE/CHUNK

lastN = [10 for i in range(20)]
print lastN
average = sum(lastN) / len(lastN)
print "average: ", average

# open stream (2)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# read data
data = wf.readframes(CHUNK)

# play stream (3)
while data != '':
    lastN.pop(0)
    score = getScore(data)
    lastN.append(score)
    #print lastN
    average = sum(lastN) / len(lastN)
    print "score:", score, " average: ", average
    #, " sum:", sum(lastN), " len:", len(lastN), " lastN:", lastN
  
    stream.write(data)
    data = wf.readframes(CHUNK)

# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()

THRESHOLD = average * THRESHOLD_MULTIPLIER
print "THRESHOLD: ", THRESHOLD 
