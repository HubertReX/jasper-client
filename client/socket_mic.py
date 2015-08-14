# -*- coding: utf-8 -*-
# a może teraz?
"""
A drop-in replacement for the Mic class that gets input from
named pipe. It can be anny source, by here the goal is to
communicate with www flask server, where voice recognition
is done through chrome browser. We get plain text with
no need for stt engine (chrome browser uses google engine).
"""
import re
import alteration
import os
import io
import str_formater
import socket

class Mic:
    prev = None

    def __init__(self, speaker, passive_stt_engine, active_stt_engine, logger):
        self.speaker = speaker
        self.first_run = True
        self.prev = ""
        #self.passive_stt_engine = passive_stt_engine
        #self.active_stt_engine = active_stt_engine
        self.logger = logger
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        self.client_address = None
        #server_address = (socket.gethostname(), 10000)
        server_address = ('', 10000)
        self.sock.bind(server_address)
        self.logger.debug('starting up on %s port %s' % self.sock.getsockname())
        self.sock.listen(1)

        return

    def passiveListen(self, PERSONA):
        return True, "JASPER"

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        #if self.first_run:
        #    self.first_run = False
        #    return ""
        #if not LISTEN:
        #    return self.prev
        stop = False
        data = ""
        #while not stop:
        if self.connection == None:
          self.logger.debug('waiting for a connection')
          self.connection, self.client_address = self.sock.accept()
          self.logger.debug('client connected: %s' % client_address)
        try:
            #print >>sys.stderr, 'client connected:', client_address
            #while True:
                data_size = connection.recv(1)
                if data_size:
                  data_size = ord(data_size)
                  self.logger.debug('received size %d' % (data_size))
                else:
                  raise Exception('Socket Connection Error', 'got empty str instead of message size')

                data = connection.recv(data_size)
                self.logger.debug('received "%s"' % data)
                if data:
                  #connection.sendall(data)
                  if data == "stop":
                    stop = True
                    #break
                else:
                  #self.connection = None
                  raise Exception('Socket Connection Error', 'got empty str instead of message data')
        except:
            #self.connection.close()
            self.connection = None

        input = str_formater.unicodeToUTF8(data, self.logger)
        self.prev = input
        return input

    def say(self, phrase, OPTIONS=None):
        #phrase = phrase.decode('utf8')
        #print "JAN: " + phrase
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        self.logger.info("JASPER: " + phrase  )
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        phrase = alteration.clean(phrase)
        #self.speaker.say(phrase)
        if self.connection:
          self.logger.debug('got connection, sending phrase')
          self.connection.send(chr(len(phrase)))
          self.connection.sendall(phrase)
