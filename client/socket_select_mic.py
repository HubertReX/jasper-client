# -*- coding: utf-8 -*-
# a może teraz?
"""
A drop-in replacement for the Mic class that gets input from
named pipe. It can be anny source, by here the goal is to
communicate with www flask server, where voice recognition
is done through chrome browser. We get plain text with
no need for stt engine (chrome browser uses google engine).
"""
import socket
import select
import Queue

import alteration
import str_formater


class Mic:
    prev = None

    def __init__(self, speaker, passive_stt_engine, active_stt_engine, logger):
        self.speaker = speaker
        self.first_run = True

        # socket listen timeout [s]
        self.timeout_passive = 3
        self.timeout_active = 2
        self.ip = 'localhost'
        self.port = 10000
        self.connection_queue = 5
        # Bind the socket to the port
        self.server_address = (self.ip, self.port)

        # self.passive_stt_engine = passive_stt_engine
        # self.active_stt_engine = active_stt_engine
        self.logger = logger

        self.reinit_server_socket()

    def clean_up_sockets(self):
        for s in self.inputs + self.outputs:
            try:
                s.close()
            except:
                pass

            try:
                del self.message_queues[s]
            except:
                pass

    def reinit_server_socket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)

        self.logger.debug('socket:: starting up on %s port %s' % self.server_address)
        self.logger.debug('socket:: server: %s' % repr(self.server))
        self.server.bind(self.server_address)

        # Listen for incoming connections
        self.server.listen(self.connection_queue)

        # Sockets from which we expect to read
        self.inputs = [self.server]

        # Sockets to which we expect to write
        self.outputs = []

        # Outgoing message queues (socket:Queue)
        self.message_queues = {}

        self.readable = []
        self.writable = []
        self.exceptional = []
        self.last_msg = ""

    def broadcast_message(self, msg):
        # add message to all queues except server one
        for s in self.message_queues:
            if s is not self.server:
                try:
                    cln = str(s.getpeername())
                except:
                    cln = str(repr(s))
                self.logger.debug('socket:: send msg "%s" to %s' % (msg, cln))
                self.message_queues[s].put(chr(len(msg)) + msg)
                if s not in self.outputs:
                    self.outputs.append(s)

    def process_readable(self):
        data = None
        # Handle inputs
        for s in self.readable:
            self.logger.debug('socket:: processing socket: %s  (server: %s)' % (repr(s), repr(self.server) ))
            if str(repr(s)) == str(repr(self.server)):
                self.logger.debug('socket:: new connection ')
                try:
                    # A "readable" server socket is ready to accept a connection
                    self.logger.debug('socket:: new connection 1')
                    connection, client_address = s.accept()
                    self.logger.debug('socket:: new connection 2')
                    connection.setblocking(0)
                    self.logger.debug('socket:: new connection 3')
                    self.inputs.append(connection)
                    self.logger.debug('socket:: new connection 4')

                    # Give the connection a queue for data we want to send
                    self.message_queues[connection] = Queue.Queue()
                    self.logger.debug('socket:: new connection 5')
                except:
                    self.logger.error("socket:: error processing new connection", exc_info=True)
            else:
                data = s.recv(1024)

                if data:
                    # A readable client socket has data
                    if len(data) > 1:
                        data = data[1:]
                    self.logger.debug('socket:: received "%s" from %s' % (data, str(s.getpeername())))
                    return data
                    # self.message_queues[s].put(chr(len(data)) + data.upper())
                    # message_queues[s].put(data.upper())

                    # Add output channel for response
                    #if s not in self.outputs:
                    #    self.outputs.append(s)
                else:
                    # Interpret empty result as closed connection
                    self.logger.debug('socket:: closing connection with client after reading no data')
                    # Stop listening for input on the connection
                    if s in self.outputs:
                        self.outputs.remove(s)
                    self.inputs.remove(s)
                    s.close()

                    # Remove message queue
                    del self.message_queues[s]

        return data

    def process_writable(self):
        # Handle outputs
        for s in self.writable:
            try:
                next_msg = self.message_queues[s].get_nowait()
            except Queue.Empty:
                # No messages waiting so stop checking for writability.
                self.logger.debug('socket:: output queue for %s is empty' % str(s.getpeername()))
                self.outputs.remove(s)
            else:
                self.logger.debug('socket:: sending "%s" to %s' % (next_msg, str(s.getpeername())))
                s.send(next_msg)

    def process_exceptional(self):
        # Handle "exceptional conditions"
        for s in self.exceptional:
            self.logger.debug('socket:: handling exceptional condition for %s' % str(s.getpeername()))
            # Stop listening for input on the connection
            self.inputs.remove(s)
            if s in self.outputs:
                self.outputs.remove(s)
            s.close()

            # Remove message queue
            del self.message_queues[s]

    @staticmethod
    def list_sockets(sockets_list):
        res = []
        for s in sockets_list:
            try:
                res.append(str(s.getpeername()))
            except:
                res.append(str(repr(s)))

        res = ', '.join(res)

        return res

    def process_communication(self, timeout):
        # Wait for at least one of the sockets to be ready for processing
        self.logger.debug('socket:: waiting for the next event')

        self.logger.debug('socket:: select: inputs[%s], outputs[%s]' % (
            self.list_sockets(self.inputs), self.list_sockets(self.outputs)))
        self.readable, self.writable, self.exceptional = select.select(self.inputs, self.outputs, self.inputs, timeout)
        self.logger.debug('socket:: got results: readable[%s], writable[%s], exceptional[%s]' % (
            self.list_sockets(self.readable), self.list_sockets(self.writable), self.list_sockets(self.exceptional)))

        data = self.process_readable()
        self.process_writable()
        self.process_exceptional()

        return data

    def passiveListen(self, PERSONA):
        # send ENQuiry - now we're actively waiting for input from client
        self.broadcast_message(chr(5))
        data = None
        if self.inputs:
            data = self.process_communication(self.timeout_passive)
        else:
            self.logger.debug('socket:: something went terribly wrong - restarting socket server!')
            self.clean_up_sockets()
            self.reinit_server_socket()

        if not data:
            self.logger.info("No disturbance detected")
            return None, None
        else:
            self.last_msg = data
            self.logger.debug('socket:: last_msg %s' % data)

        return True, "JASPER"

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        data = None

        self.logger.debug('socket:: activeListen')
        if not self.last_msg:
            # send ENQuiry - now we're actively waiting for input from client
            self.broadcast_message(chr(5))
            data = self.process_communication(self.timeout_active)
            while not data:
                data = self.process_communication(self.timeout_active)
        else:
            data = self.last_msg
            self.last_msg = ""

        input_str = str_formater.unicodeToUTF8(data, self.logger)
        return input_str

    def say(self, phrase, OPTIONS=None):
        # phrase = phrase.decode('utf8')
        # print "JAN: " + phrase
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        self.logger.info("JASPER: " + phrase)
        self.logger.info(">>>>>>>>>>>>>>>>>>>")
        phrase = alteration.clean(phrase)
        #self.speaker.say(phrase)
        self.logger.debug('socket:: sending phrase')
        self.broadcast_message(phrase)
        #self.process_writable()
        self.last_msg = self.process_communication(self.timeout_active)
