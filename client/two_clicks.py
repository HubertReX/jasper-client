#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Instead of adding silence at start and end of recording (values=0) I add the original audio . This makes audio sound more natural as volume is >0. See trim()
#I also fixed issue with the previous code - accumulated silence counter needs to be cleared once recording is resumed.

from array import array
from struct import pack
from sys import byteorder
import copy
import pyaudio
import wave

THRESHOLD = 1500  # audio levels not normalised.
THRESHOLD_SILENCE = 2000  # almost silence.
CHUNK_SIZE = 1024
SILENT_CHUNKS = 1 * 44100 / 1024  # about 3sec
FORMAT = pyaudio.paInt16
FRAME_MAX_VALUE = 2 ** 15 - 1
NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
RATE = 44100
CHANNELS = 1
TRIM_APPEND = RATE / 4

def is_peak(data_chunk):
    """Returns 'True' if below the 'silent' threshold"""
    return max(data_chunk) > THRESHOLD

def is_silent(data_chunk):
    """Returns 'True' if below the 'silent' threshold"""
    return max(data_chunk) < THRESHOLD_SILENCE

def normalize(data_all):
    """Amplify the volume out to max -1dB"""
    # MAXIMUM = 16384
    normalize_factor = (float(NORMALIZE_MINUS_ONE_dB * FRAME_MAX_VALUE)
                        / max(abs(i) for i in data_all))

    r = array('h')
    for i in data_all:
        r.append(int(i * normalize_factor))
    return r

def trim(data_all):
    _from = 0
    _to = len(data_all) - 1
    for i, b in enumerate(data_all):
        if abs(b) > THRESHOLD:
            _from = max(0, i - TRIM_APPEND)
            break

    for i, b in enumerate(reversed(data_all)):
        if abs(b) > THRESHOLD:
            _to = min(len(data_all) - 1, len(data_all) - 1 - i + TRIM_APPEND)
            break

    return copy.deepcopy(data_all[_from:(_to + 1)])

def record():
    """Record a word or words from the microphone and 
    return the data as an array of signed shorts."""

    p = pyaudio.PyAudio()
    defaultSampleRate = p.get_device_info_by_index(0)['defaultSampleRate']
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)

    silent_chunks = 0
    first_clap = False
    second_clap = False
    data_all = array('h')

    while True:
        # little endian, signed short
        data_chunk = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            data_chunk.byteswap()
        data_all.extend(data_chunk)

        silent = not is_peak(data_chunk)
        max_peak = max(data_chunk)
        bar = int ( 2 * max_peak * 100 / FRAME_MAX_VALUE)
        print '%6d' % max_peak, 'G' * bar
        if first_clap:
            if silent:
                silent_chunks += 1
                #print "silent_chunks ", silent_chunks 
                if second_clap and silent_chunks > SILENT_CHUNKS:
                    break
            elif not second_clap: 
                print "no more silence"
                #second clap within min 250 or max 500 ms
                if silent_chunks > 8:
                  #first_clap = False
                  print "too late %d !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" % silent_chunks
                if silent_chunks >= 4 and silent_chunks <= 8:
                  second_clap = True
                  print "second_clap %d -----------------------------------------------------------------------------------------------" % silent_chunks
                if silent_chunks > 0 and silent_chunks < 4:
                  print "too soon %d !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" % silent_chunks
                silent_chunks = 0
        elif not silent:
            print "first_clap -----------------------------------------------------------------------------------------------"
            first_clap = True              
            

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    #data_all = trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as is_peak() function)
    #data_all = normalize(data_all)
    return sample_width, data_all

def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    return
    data = pack('<' + ('h' * len(data)), *data)
  
    wave_file = wave.open(path, 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(RATE)
    wave_file.writeframes(data)
    wave_file.close()

if __name__ == '__main__':
    print("Wait in silence to begin recording; wait in silence to terminate")
    record_to_file('demo.wav')
    print("done - result written to demo.wav")
