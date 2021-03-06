# -*- coding: utf-8 -*-
"""
helper class to handle persistent cache using shelve

"""
# może teraz?
import os
import sys
import re
import shelve
import time
import datetime
import jasperLogger
import logging

PHRASES_CACHE_DB    = 'cache_phrases_%s.db'
MAX_INDEX_KEY       = '<MAX_INDEX>'
PHRASES_CACHE_DIR   = '../static/audio/cache/'



class persistentCache(object):

    def __init__(self, db_file, logger, voice, snd_dev, mode='c'):
        self.cache     = shelve.open(db_file, mode)
        self.logger    = logger
        self.voice     = voice
        self.snd_dev   = snd_dev
        self.CACHE_DIR = PHRASES_CACHE_DIR + voice + '/'

    def hasKey(self, key):
        return self.cache.has_key(key.strip())

    def addToCache(self, key, value):
        self.cache[key.strip()] = value

    def getFromCache(self, key):
        if self.hasKey(key.strip()):
          return self.cache[key.strip()]

class audioCache(persistentCache):

    def addToCache(self, phrase, audio_file):
        file_name = None
        try:
          try:
            index = self.cache.get(MAX_INDEX_KEY, 0) + 1
            cache_file = "%s%04d.mp3" % (self.CACHE_DIR, index)
            os.system('test -d "%s" || mkdir -p "%s" && cp %s "%s"' % (self.CACHE_DIR, self.CACHE_DIR, audio_file, cache_file) )
            size = os.path.getsize(cache_file)
            ts = time.time()
            cache_entry = {'file_name': cache_file, 
                           'file_size': size,
                           'hits'     : 1, 
                           'last_hit' : datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),
                          }
          finally:
            self.cache[phrase] = cache_entry
            self.cache[MAX_INDEX_KEY] = index
            self.logger.debug("phrase added to cache: %s %s" % (phrase, cache_file))
            file_name = cache_file
        except:
          self.logger.critical("fatal error adding entry to cache", exc_info=True)
        return file_name

    def getFromCache(self, phrase):
        phrase = phrase.strip()
        cache_entry = self.cache[phrase]
        ts = time.time()
        cache_entry['hits']     = cache_entry['hits'] + 1
        cache_entry['last_hit'] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        self.cache[phrase] = cache_entry
        self.logger.debug("got hit (%d) in cache, for phrase: %s cache file name: %s" % (cache_entry['hits'], phrase, cache_entry['file_name']))
        
        return cache_entry['file_name']

    def convertWavToMp3(self):
        sorted_list = sorted(self.cache, key=lambda m: m)
        for phrase in sorted_list:
            if phrase <> MAX_INDEX_KEY:
              el = self.cache[phrase]
              #old_file = el['file_name']
              #new_file = '/'.join(old_file.split('/')[:-1]) + '/google/' + old_file.split('/')[-1]
              #print new_file 
              #os.system('avconv -y -i %s -f mp3 %s' % (old_file, new_file))
              #size = os.path.getsize(new_file)
              #el['file_name'] = new_file
              #el['file_size'] = size
              new_phrase = phrase.strip()
              if new_phrase != phrase:
                self.removeFromCache(phrase)
                self.cache[new_phrase] = el


    def listCacheEntries(self, sort='hits'):
        index = self.cache.get(MAX_INDEX_KEY, 0)
        self.logger.info("Phrases cache entries (max=%d):" % index)
        
        #for phrase in self.cache.keys():
        if sort == 'phrase':
          sorted_list = sorted(self.cache, key=lambda m: m)
        else:
          sorted_list = sorted(self.cache, key=lambda m: self.cache[m][sort] if m <> MAX_INDEX_KEY else 0)
        self.logger.info("file name                             file size hits last hit            phrase")
        total_size = 0
        for phrase in sorted_list:
            if phrase <> MAX_INDEX_KEY:
              ce = self.cache[phrase]
              size = ce.get('file_size', -1)
              self.logger.info("%s %9d %4d %s %s" % (ce['file_name'], size, ce['hits'], ce['last_hit'], phrase))
              if not self.checkFile(ce['file_name']):
                self.logger.info('file %s is not present - deleting' % ce['file_name'])
                self.removeFromCache(phrase)
              else:
                #size = os.path.getsize(ce['file_name'])
                total_size += size
                #ce['file_size'] = size
                #self.logger.info("file size %d" % size)
                #self.cache[phrase] = ce
        #self.logger.info("Total bytes used %d" % total_size)
        self.logger.info("Total bytes used   {:15,}".format(total_size))
        stats = os.statvfs(self.CACHE_DIR)
        free = stats.f_bavail * stats.f_frsize
        #self.logger.info("Bytes free on disk %d" % free)
        self.logger.info("Bytes free on disk {:15,}".format(free))

    def play(self, filename):
        if self.checkFile(filename):
          #os.system("aplay -D plughw:1,1 " + filename)
          self.logger.info("mpg123 -q --audiodevice=%s %s" % (self.snd_dev, filename))
          os.system("mpg123 -q --audiodevice=%s %s" % (self.snd_dev, filename))

    def findPhrase(self, phrase):
        res = [(key, self.cache[key]) for key in self.cache.keys() if re.match(phrase, key)]
        if res:
          self.logger.info("file name                             file size hits last hit            phrase")
          for key, el in res:
            size = el.get('file_size', -1)
            self.logger.info("%s %9d %4d %s %s" % (el['file_name'], size, el['hits'], el['last_hit'], key))
        else:
          self.logger.info("No phrease matching regular expression: %s" % phrase)
        return

    def checkFile(self, filename):
        res = os.path.isfile(filename)
        #self.logger.info('is file %s present: %s' % (filename, str(res)))
        return res

    def removeFromCache(self, phrase):
        if self.hasKey(phrase):
          del self.cache[phrase]
          #try:
          #  os.system("rm %s" phrase)
          #except:
          #  pass
          self.logger.info("removed phrase from cache: %s" % phrase)
        else:
          self.logger.info("cannot remove, phrase not found in cache: %s" % phrase)

    def deleteFile(self, filename):
        if self.checkFile(filename):
          try:
            os.system("rm %s" % filename)
            self.logger.info("deleted file: %s" % filename)
          except:
            self.logger.error("error deleting file: %s" % filename, exc_info=True)
        else:
          self.logger.info("file doesn't exist: %s" % filename)

if __name__ == "__main__":
    l = jasperLogger.jasperLogger(level=logging.DEBUG, logFile='persistentCache.log', console=True)
    logger = l.getLogger()

    logger.info("start")
    if len(sys.argv) < 2:
      voice = 'google'
    else:
      voice = sys.argv[1]

    ac = audioCache(PHRASES_CACHE_DB % voice, logger, voice, 'plughw:1,0')
    ac.convertWavToMp3()
    ac.listCacheEntries()
    help_msg = "\nhelp - to show this help message\nlist [sort hits|last_hit|file_name|file_size|phrase]- to list all cache entries\nfind reg_exp - to find phrases matching regular expression\ntest file - to test if file is present\nplay file - to play file frome cache\nremove phrase - to remove phrase from cache\ndelete filename - to delete file name\nexit - to quit"
    logger.info(help_msg)
    repeat = True
    while repeat:
      #cmd = raw_input("what next: ").encode('utf8')
      cmd = raw_input("what next: ")
      res = cmd.split(' ')
      if res:
        if res[0] == 'help':
          logger.info(help_msg)
        elif res[0] == 'list':
          sort = 'hits'
          if len(res) == 3:
            if res[1] == 'sort':
              if '|' + res[2] + '|' in '|hits|last_hit|file_name|file_size|phrase|':
                sort = res[2]
          ac.listCacheEntries(sort)
        elif res[0] == 'test':
          res = ac.checkFile(res[1])
          logger.info('is file %s present: %r' % (res[1], res))
        elif res[0] == 'play':
          ac.play(res[1])
        elif res[0] == 'find':
          ac.findPhrase(' '.join(res[1:]))          
        elif res[0] == 'remove':
          ac.removeFromCache(' '.join(res[1:]))
        elif res[0] == 'delete':
          ac.deleteFile(res[1])
        elif res[0] == 'exit':
          repeat = False
        else:
          logger.info('command not found')
      else:
        repeat = False
    exit(0)
