# -*- coding: utf-8 -*-
# a może teraz?

def unicodeToStr(u, logger):
    logger.debug('unicodeToStr got %s as %s' % (repr(u), str(type(u))))
    s = ""
    try:
      s = u.decode('unicode').encode("ascii", "ignore")
    except:
      logger.error('unicodeToStr error', exc_info=True)
      s = u
    logger.debug('unicodeToStr will return %s as %s' % (repr(s), str(type(s))))
    return s

def utf8ToStr(u, logger):
    logger.debug('utf8ToStr got %s as %s' % (repr(u), str(type(u))))
    s = ""
    try:
      s = u.decode('utf-8').encode("ascii", "ignore")
    except:
      logger.error('utf8ToStr error', exc_info=True)
      s = u
    logger.debug('utf8ToStr will return %s as %s' % (repr(s), str(type(s))))
    return s

def utf8ToUnicode(s, logger):
    #logger.debug('utf8ToUnicode got %s as %s' % (s, str(type(s))))
    u = u""
    try:
      if not isinstance(s, unicode):
        u = s.decode('utf-8')
      elif type(s) == type(dict()):
        for k in s.keys():
          u[k] = s[k].decode('utf-8')
      else:
        u = s
    except:
      logger.error('utf8ToUnicode error', exc_info=True)
      u = s
    #logger.debug('utf8ToUnicode will return %s as %s' % (u, str(type(u))))
    return u


def unicodeToUTF8(u, logger):
    #logger.debug('unicodeToUTF8 got %s as %s' % (u, type(u)) )
    s = ""
    try:
      if isinstance(u, unicode):
        #logger.debug('unicodeToUTF8 got unicode %s as %s' % (u, str(type(u))))
        s = u.encode('utf-8')
      elif isinstance(u, list):
        s = []
        for k in u:
          s.append(unicodeToUTF8(k, logger))
      elif isinstance(u, dict):
        s = dict()
        for k in u.keys():
          #logger.debug('unicodeToUTF8 got key %s as %s' % (k, str(type(u[k]))))
          #s[k] = u[k].decode('utf-8')
          s[k] = unicodeToUTF8(u[k], logger)
      else:
        s = u
    except:
      logger.error('unicodeToUTF8 error', exc_info=True)
      s = u #s.decode('utf-8', "ignore")
    #logger.debug('unicodeToUTF8 will return %s as %s' % (s, str(type(s))))
    return s

def checkFormat(s, logger):
    logger.debug('checkFormat got %s as %s' % (s, str(type(s))))
    return s
