# -*- coding: utf-8 -*-
# a może teraz?
import os
import sys
import logging

class jasperLogger:

    def __init__(self, level=logging.DEBUG, logFile='jasper.log', console=False):
      self.logger = logging.getLogger('jasper')
      self.logger.setLevel(level)
      if console:
        self.handler = logging.StreamHandler(sys.stdout)
        self.formatter = logging.Formatter('%(module)s %(levelname)s %(message)s')
      else:
        self.handler = logging.FileHandler(logFile)
        self.formatter = logging.Formatter('%(asctime)s %(module)s %(levelname)s %(message)s')
      self.handler.setLevel(level)
      #self.formatter = logging.Formatter('%(message)s')
      self.handler.setFormatter(self.formatter)
      self.logger.addHandler(self.handler)

    def getLogger(self):
      return self.logger

    def logError(self, msg):
      self.logger.error(msg, exc_info=True)
