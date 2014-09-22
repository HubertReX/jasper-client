# -*- coding: utf-8 -*-

import logging
from os import listdir
from recompile import *


def logError():
    logger = logging.getLogger('jasper')
    fh = logging.FileHandler('jasper.log')
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.error('Failed to execute module', exc_info=True)


class Brain(object):

    def __init__(self, mic, profile, logger):
        """
        Instantiates a new Brain object, which cross-references user
        input with a list of modules. Note that the order of brain.modules
        matters, as the Brain will cease execution on the first module
        that accepts a given input.

        Arguments:
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
        """

        self.logger = logger
        self.mic = mic
        self.profile = profile
        self.modules = self.get_modules()

    def reload_modules(self):
        self.modules = self.get_modules()

    def get_modules(self):
        """
        Dynamically loads all the modules in the modules folder and sorts
        them by the PRIORITY key. If no PRIORITY is defined for a given
        module, a priority of 0 is assumed.
        """

        folder = 'modules'

        def get_module_names():
            module_names = [m.replace('.py', '')
                            for m in listdir(folder) if m.endswith('.py')]
            module_names = map(lambda s: folder + '.' + s, module_names)
            return module_names

        def import_module(name):
            self.logger.info("Loading module: %s" % name)
            #mod = __import__(name)
            res = recompile(name)
            
            if res == "ok":
              mod = sys.modules[name]
            else:
              try:
                mod = sys.modules[name]
                self.logger.error("error reloading module %s - will use old one\n%s" % (name, res), exc_info=True)
              except:
                mod = object()
                self.logger.error("error loading module %s\n%s" % (name, res), exc_info=True)
            #components = name.split('.')
            #for comp in components[1:]:
            #    mod = getattr(mod, comp)
            if hasattr(mod, 'WORDS'):
              self.logger.info("    key words: %s" % ', '.join(mod.WORDS))
            return mod

        def get_module_priority(m):
            try:
                return m.PRIORITY
            except:
                return 0

        modules = map(import_module, get_module_names())
        modules = filter(lambda m: hasattr(m, 'WORDS'), modules)
        modules.sort(key=get_module_priority, reverse=True)
        return modules


    def query(self, text):
        """
        Passes user input to the appropriate module, testing it against
        each candidate module's isValid function.

        Arguments:
        text -- user input, typically speech, to be parsed by a module
        """
        for module in self.modules:
            if module.isValid(text):

                try:
                    module.handle(text, self.mic, self.profile, self.logger)
                    break
                except:
                    #logError()
                    self.logger.error("Failed to execute module", exc_info=True)
                    self.mic.say(
                        "Wybacz, ale wystąpił problem techniczny z tą operacją. Spróbuj później.")
                    break
