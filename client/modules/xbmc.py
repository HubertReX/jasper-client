# -*- coding: utf-8 -*-
# a może teraz?
import datetime
import base64
import json
import urllib2
import re
import app_utils

WORDS = ["PUŚĆ", "ODTWARZAJ", "GRAJ", "ZAGRAJ", "WSTRZYMAJ", "ZATRZYMAJ"]
HELP  = {"name": "multimedia",
         "description": "To zestaw komend służących do sterowania odtwarzeniem muzyki, filmów, seriali oraz zdjęć.",
         "samples": ["zagraj zespół kult", "odtwarzaj film gwiezdne wojny", "włącz radio ram", "zagraj utwór na zachód", "co jest grane", "tryb imprezy"],
         "topics": {"muzyka": "powiedz odtwarzaj lub graj lub zagraj lub puść,|"+
                              "następnie piosenkę i tytuł piosenki.|"+
                              "albo zagraj zespół lub artystę lub wykonawcę lub płyty,|" +
                              "a następnie właściwą nazwę wykonawcy.|"+
                              "Komenda ta, doda do kolejki odtwarzania wszystkie albumy wykonawcy.",
                    "film":   "powiedz odtwarzaj lub graj lub zagraj lub puść,| "+
                              "następnie film, " +
                              "a następnie polski tytuł filmu.|"+
                              "Jeżeli wyszukiwanie zwróci więcej niż jeden wynik,|"+
                              "to wszystkie filmy zostaną dodane do kolejki.|"+
                              "Nie trzeba wypowiadać pełnej nazwy filmu,| "+
                              "wystarczy użyć unikalnego słowa lub frazy",
                    "radio":  "powiedz graj radio nazwa stacji. Dostępne stajce radiowe to RAM, Trójka, RMF.",
                    "co jest grane":"powiedz co jest grane, aby poznać nazwę i inne dostępne informacje, o obecnie odtwarzanych multimediach.",
                    "tryb imprezy": "powiedz trym imprezy aby uruchomić odtawrzanie losowo wybranych utworów.",
                    "uwagi ogólne": "jeżeli nie udaje się prawidłowo rozpoznać nazwy artysty lub filmu,|"+
                                    "nazwę można przeliterować."
                    }
          }

SERWERS = {
'HTPC': {
 'NAME': "HTPC",
 'DEFAULT': False,  
 'HOST': "192.168.1.100",
 'PORT': 80,
 'USERNAME': 'xbmc',
 'PASSWORD': '1'
},
'OSMC': {
 'NAME': "OSMC",
 'DEFAULT': True,
 'HOST': "192.168.1.7",
 'PORT': 80,
 'USERNAME': 'osmc',
 'PASSWORD': ''
},
'HUBERT': {
 'NAME': "HUBERT",
 'HOST': "192.168.1.107",
 'PORT': 80,
 'USERNAME': 'kodi',
 'PASSWORD': ''
},
}

SERWERS['DEFAULT'] = SERWERS['HUBERT']

RADIO_STATIONS = {
'TRÓJKA': 'mmsh://stream.polskieradio.pl/program3?MSWMExt=.asf',
'RAM': 'http://stream4.nadaje.com:9220/ram',
'RMF': 'http://217.74.72.10:8000/rmf_fm',
}

AUDIO_PLAYER = 0
MOVIE_PLAYER = 1
PHOTO_PLAYER = 2

#PLAY_MSG   = '{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": %d}, "id": 1}'
CLEAR_MSG        = '{"jsonrpc": "2.0", "method": "Playlist.Clear",   "params": {"playlistid": %d}, "id": 1}'
ADD_ALBUM_MSG    = '{"jsonrpc": "2.0", "method": "Playlist.Add",     "params": {"playlistid": %d, "item": { "albumid" : %d}}, "id" : 1}'
ADD_SONG_MSG     = '{"jsonrpc": "2.0", "method": "Playlist.Add",     "params": {"playlistid": %d, "item": { "songid"  : %d}}, "id" : 1}'
ADD_MOVIE_MSG    = '{"jsonrpc": "2.0", "method": "Playlist.Add",     "params": {"playlistid": %d, "item": { "movieid" : %d}}, "id" : 1}'
ADD_SHOW_MSG     = '{"jsonrpc": "2.0", "method": "Playlist.Add",     "params": {"playlistid": %d, "item": { "tvshowid": %d}}, "id" : 1}'
GET_PLAYERS_MSG  = '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
PAUSE_MSG        = '{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid"  : %d }, "id": 1}'
PLAY_FILE_MSG    = '{"jsonrpc": "2.0", "method": "Player.Open",      "params": {"item": {"file": "%s"}},         "id" : "1"}'
PARTY_MODE_MSG   = '{"jsonrpc": "2.0", "method": "Player.Open",      "params": {"item": {"partymode": "%s"}}, "id" : "1"}'

SEND_NOTIFICATION = '{"jsonrpc": "2.0", "method": "GUI.ShowNotification", "params": {"title" : "%s", "message" : "%s"}, "id" : 1}' 

GET_PLAYED_PICTURE_MSG  = """{
    "jsonrpc": "2.0",
    "method": "Player.GetItem",
    "params": {
        "properties": [
            "title",
            "album",
            "artist",
            "season",
            "episode",
            "duration",
            "showtitle",
            "tvshowid",
            "file",
            "streamdetails"
        ],
        "playerid": 2
    },
    "id": "PictureGetItem"
}
"""

GET_PLAYED_VIDEO_MSG  = """{
    "jsonrpc": "2.0",
    "method": "Player.GetItem",
    "params": {
        "properties": [
            "title",
            "album",
            "artist",
            "season",
            "episode",
            "duration",
            "showtitle",
            "tvshowid",
            "file",
            "streamdetails"
        ],
        "playerid": 1
    },
    "id": "VideoGetItem"
}
"""
#            "thumbnail",
#            "fanart",

GET_PLAYED_AUDIO_MSG  = """{
    "jsonrpc": "2.0",
    "method": "Player.GetItem",
    "params": {
        "properties": [
            "title",
            "album",
            "year",
            "artist",
            "duration",
            "file",
            "streamdetails"
        ],
        "playerid": 0
    },
    "id": "AudioGetItem"
}
"""
#            "thumbnail",
#            "fanart",

GET_PLAYLIST     = """{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "Playlist.GetItems",
  "params": {
    "playlistid": %d
  }
}
"""

#OPEN_MSG   = '{"jsonrpc": "2.0", "method": "Player.Open",      "params": {"item":{"playlistid": %d, "position" : 0}}, "id": 1}'
OPEN_MSG   = '{"jsonrpc": "2.0", "method": "Player.Open",      "params": {"item":{"playlistid": %d, "position" : 0}, "options": {"shuffled" : %s }}, "id": 1}'

GET_ALBUMS_FROM_ARTIST = """{
  "jsonrpc": "2.0",
  "method": "AudioLibrary.GetAlbums",
  "params": {
    "limits": {
      "start": 0,
      "end": 30
    },
    "filter": {
      "field": "artist",
      "operator": "contains",
      "value": "%s"
    },
    "properties": [
      "title",
      "artist",
      "year"
    ],
    "sort": {
      "order": "ascending",
      "method": "year",
      "ignorearticle": true
    }
  },
  "id": "libAlbums"
}
"""

GET_ALBUMS = """{
  "jsonrpc": "2.0",
  "method": "AudioLibrary.GetAlbums",
  "params": {
    "limits": {
      "start": 0,
      "end": 30
    },
    "filter": {
      "field": "album",
      "operator": "contains",
      "value": "%s"
    },
    "properties": [
      "title",
      "artist",
      "year"
    ],
    "sort": {
      "order": "ascending",
      "method": "year",
      "ignorearticle": true
    }
  },
  "id": "libAlbums"
}
"""

GET_SONGS = """{
  "jsonrpc": "2.0",
  "method": "AudioLibrary.GetSongs",
  "params": {
    "limits": {
      "start": 0,
      "end": 30
    },
    "filter": {
      "field": "title",
      "operator": "contains",
      "value": "%s"
    },
    "properties": [
      "file",
      "title",
      "artist",
      "year"
    ],
    "sort": {
      "order": "ascending",
      "method": "title",
      "ignorearticle": true
    }
  },
  "id": "libSongs"
}
"""

GET_MOVIES = """
{
  "jsonrpc": "2.0",
  "params": {
    "sort": {
      "order": "ascending",
      "method": "year"
    },
    "filter": {
      "operator": "contains",
      "field": "title",
      "value": "%s"
    },
    "properties": [
      "title",
      "year"
    ]
  },
  "method": "VideoLibrary.GetMovies",
  "id": "libMovies"
}
"""

GET_SHOWS = """
{
  "jsonrpc": "2.0",
  "params": {
    "sort": {
      "order": "ascending",
      "method": "year"
    },
    "filter": {
      "operator": "contains",
      "field": "title",
      "value": "%s"
    },
    "properties": [
      "title",
      "year"
    ]
  },
  "method": "VideoLibrary.GetTVShows",
  "id": "libTVShows"
}
"""

def unicodeToUTF8(u):
    #logger.debug('unicodeToUTF8 got %s as %s' % (u, type(u)) )
    s = ""
    try:
      if isinstance(u, unicode):
        #logger.debug('unicodeToUTF8 got unicode %s as %s' % (u, str(type(u))))
        s = u.encode('utf-8')
      elif isinstance(u, list):
        s = []
        for k in u:
          s.append(unicodeToUTF8(k))
      elif isinstance(u, dict):
        s = dict()
        for k in u.keys():
          #logger.debug('unicodeToUTF8 got key %s as %s' % (k, str(type(u[k]))))
          #s[k] = u[k].decode('utf-8')
          s[k] = unicodeToUTF8(u[k])
      else:
        s = u
    except:
      print 'unicodeToUTF8 error'
      s = u #s.decode('utf-8', "ignore")
    #logger.debug('unicodeToUTF8 will return %s as %s' % (s, str(type(s))))
    return s



def send_json(msg, server_name='DEFAULT', timeout=4):
    s = SERWERS[server_name]
    url = "http://%s:%d/jsonrpc" % (s['HOST'], s['PORT'])
    req = urllib2.Request(url, msg);
    #req.add_header('Authorization', 'Basic eGJtYzox');
    req.add_header('Authorization', b'Basic ' + base64.b64encode(s['USERNAME'] + b':' + s['PASSWORD']))
    req.add_header('Content-type', 'application/json');
    res = None
    print msg
    try:
      res = urllib2.urlopen(req, timeout=timeout).read();
      print res
    except Exception, e:
      res = '{ "error": "%s"}' % repr(e).replace('"', '')
    return res
    #print res

class Mic:
    def say(self, msg):
        print "say:", msg



def start_party_mode(mode='music'):
    msg = PARTY_MODE_MSG % mode
    res = json.loads(send_json(msg) )
    if res.has_key('result'):
      return res['result']
    else:
      print "error starting party mode %s " % mode
      return None


def get_active_players():
    msg = GET_PLAYERS_MSG
    res = json.loads(send_json(msg) )
    if res.has_key('result'):
      return res['result']
    else:
      print "error retriving active players"
      return None

def pausePlayer():
    ap = get_active_players()
    if len(ap) == 0:
      print 'can not play or pause - nothing is currently playing'
      return
    id = ap[0]['playerid']
    msg = PAUSE_MSG % id
    res = json.loads(send_json(msg) )
    
    if res.has_key('result'):
      return res['result']
    else:
      print "error pausing active player %d" % id
      return None

def play_file(f, timeout=4):
    msg = PLAY_FILE_MSG % f
    res = json.loads(send_json(msg, timeout=timeout))
    if res.has_key('result'):
      return True
    else:
      return False

  
def play_radio(radio, mic):
    if RADIO_STATIONS.has_key(radio):
      res = play_file(RADIO_STATIONS[radio], timeout=8)
      mic.say('Uruchamiam radio %s' % radio)
    else:
      res = False
    
    return res

def get_currently_playing():
    ap = get_active_players()
    if len(ap) == 0:
      return 'nic nie jest w tej chwili odtwarzane'
    id = ap[0]['playerid']
    res = ''

    if id == AUDIO_PLAYER:
      msg = GET_PLAYED_AUDIO_MSG
      response = json.loads(send_json(msg) )
    elif id == MOVIE_PLAYER:
      msg = GET_PLAYED_VIDEO_MSG
      response = json.loads(send_json(msg) )
    elif id == PHOTO_PLAYER:
      msg = GET_PLAYED_PICTURE_MSG
      response = json.loads(send_json(msg) )
    else:
      return 'nic nie jest w tej chwili odtwarzane'
    
    if response:
      if response.has_key('result'):  
        item = response['result']['item']

        if item['type'] == 'song':
          # if url stream
          if '://' in item['file'] and not 'smb://' in item['file'] :
            # if knonw radio station
            for key in RADIO_STATIONS.keys():
              if item['file'] == RADIO_STATIONS[key]:
                res += 'teraz gra radio |~' + key

                # if has title
                if len(item['title']) > 0:
                   res += ' utwór ' + unicodeToUTF8(item['title'])
                break
          # regular song
          else:
            if len(item['title']) > 0:
             res += 'teraz jest odtwarzany utwór |~' + unicodeToUTF8(item['title'])
            if len(item['artist']) > 0:
             res += ' wykonawca ' + unicodeToUTF8(','.join(item['artist']))
            if len(item['album']) > 0:
             res += ' z albumu ' + unicodeToUTF8(item['album'])
            if item['year'] > 0:
             res += ' z roku ' + str(item['year'])

        # movie/video from library
        elif item['type'] == 'movie':
          if len(item['title']) > 0:
             res += 'teraz jest odtwarzany film |~' + unicodeToUTF8(item['title'])
        # tv show
        elif item['type'] == 'episode':
          if len(item['showtitle']) > 0:
            res += ' teraz jest odtwarzany serial |~' + unicodeToUTF8(item['showtitle'])
          if item['season'] > 0:
            res += ' sezon ' + str(item['season'])
          if item['episode'] > 0:
            res += ' odcinek ' + str(item['episode'])

        # video clip
        elif item['type'] == 'musicvideo':
          if len(item['title']) > 0:
           res += 'teraz jest odtwarzany teledysk |~' + unicodeToUTF8(item['title'])
          if len(item['artist']) > 0:
           res += ' wykonawca ' + unicodeToUTF8(','.join(item['artist']))
          if len(item['album']) > 0:
           res += ' z albumu ' + unicodeToUTF8(item['album'])

        # just any file
        elif item['type'] == 'unknown':
          if len(item['label']) > 0:
             res += 'teraz gra |~' + unicodeToUTF8(item['label'])
    return res

def get_albums_list_from_artist(artist):
    msg = GET_ALBUMS_FROM_ARTIST % artist
    res = json.loads(send_json(msg))
    albums_list = []
    if res.has_key('result'):
      for album in res['result']['albums']:
          el = album['albumid']
          artists = ''
          for item in album['artist']: 
            artists += ' ' + app_utils.upperUTF8(unicodeToUTF8(item))
          if el not in albums_list and app_utils.upperUTF8(artist) in artists:
              print ' '.join(album['artist']), album['title'], album['year'], album['albumid']
              #print "add"
              albums_list.append(el)


      return albums_list
    elif res.has_key('error'):
        print("no albums found: %s" % res['error'] )
        return None


def get_albums(album):
    msg = GET_ALBUMS % app_utils.lowerUTF8(album)
    res = json.loads(send_json(msg))
    
    albums_list = []
    if res.has_key('result'):
      if res['result']['limits']['total'] > 0:
        print 'albums list:'
        for album in res['result']['albums']:
          el = album['albumid']
          artists = ''
          #for item in album['title']: 
          #  artists += ' ' + app_utils.upperUTF8(unicodeToUTF8(item))
          if el not in albums_list:
              print ' '.join(album['artist']), album['title'], album['year'], album['albumid']
              #print "add"
              albums_list.append(el)

        return albums_list
      elif res.has_key('error'):
        print("no albums found: %s" % res['error'] )
        return None
    elif res.has_key('error'):
      print("no albums found: %s" % res['error'] )
      return None


def get_songs(song):
    msg = GET_SONGS % song
    res = json.loads(send_json(msg))
    
    songs_list = []
    if res.has_key('result'):
      if res['result']['limits']['total'] > 0:
        print 'songs list:'
        for song in res['result']['songs']:
          el = song['songid']
          artists = ''
          #for item in album['title']: 
          #  artists += ' ' + app_utils.upperUTF8(unicodeToUTF8(item))
          if el not in songs_list:
              print ' '.join(song['artist']), song['title'], song['year'], song['file']
              #print "add"
              songs_list.append(el)

        return songs_list
      elif res.has_key('error'):
        print("no songs found: %s" % res['error'] )
        return None
    elif res.has_key('error'):
      print("no songs found: %s" % res['error'] )
      return None

def get_movie_by_name(movie):
    msg = GET_MOVIES % movie
    res = json.loads(send_json(msg) )
    movies_list = []
    if res.has_key('result'):
      if res['result']['limits']['total'] > 0:
          for movie in res['result']['movies']:
              #print album['title'], album['year'], album['albumid']
              el = movie['movieid']
              if el not in movies_list:
                  #print "add"
                  movies_list.append(el)

      return movies_list
    elif res.has_key('error'):
        print("no movies found: %s" % res['error'] )
        return None

def get_show_by_name(show):
    msg = GET_SHOWS % show
    res = json.loads(send_json(msg) )
    shows_list = []
    if res.has_key('result'):
      if res['result']['limits']['total'] > 0:
          for show in res['result']['tvshows']:
              #print album['title'], album['year'], album['albumid']
              el = show['tvshowid']
              if el not in shows_list:
                  #print "add"
                  shows_list.append(el)

      return shows_list
    elif res.has_key('error'):
        print("no shows found: %s" % res['error'] )
        return None

def play_movies(movie, shuffled=False):
      movies_list = get_movie_by_name(movie)
      if movies_list:
          send_json(CLEAR_MSG % MOVIE_PLAYER)
          for el in movies_list:
             send_json(ADD_MOVIE_MSG % (MOVIE_PLAYER, el))
          #print send_json(GET_PLAYLIST % MOVIE_PLAYER)
          send_json(OPEN_MSG % (MOVIE_PLAYER, str(shuffled).lower()))
          return True
      else:
          return False


def play_shows(show, shuffled=False):
      shows_list = get_show_by_name(show)
      if shows_list:
          send_json(CLEAR_MSG % MOVIE_PLAYER)
          for el in shows_list:
             send_json(ADD_SHOW_MSG % (MOVIE_PLAYER, el))
          #print send_json(GET_PLAYLIST % MOVIE_PLAYER)
          send_json(OPEN_MSG % (MOVIE_PLAYER, str(shuffled).lower()))
          return True
      else:
          return False

def play_albums(albums_list, shuffled=False):
      send_json(CLEAR_MSG % AUDIO_PLAYER)
      for el in albums_list:
         send_json(ADD_ALBUM_MSG % (AUDIO_PLAYER, el))
      #print send_json(GET_PLAYLIST % AUDIO_PLAYER)
      send_json(OPEN_MSG % (AUDIO_PLAYER, str(shuffled).lower()))

def play_songs(song, shuffled=False):
    songs_list = get_songs(song)
    if songs_list:
        
        send_json(CLEAR_MSG % AUDIO_PLAYER)
        for el in songs_list:
           send_json(ADD_SONG_MSG % (AUDIO_PLAYER, el))
        #print send_json(GET_PLAYLIST % AUDIO_PLAYER)
        send_json(OPEN_MSG % (AUDIO_PLAYER, str(shuffled).lower()))
        return True
    else:
        return False

def play_album(album, shuffled=False):
    album_list = get_albums(album)
    if album_list:
        play_albums(album_list, shuffled)
        return True
    else:
        return False


def play_artist(artist, shuffled=False):
    album_list = get_albums_list_from_artist(artist)
    if album_list:
        play_albums(album_list, shuffled)
        return True
    else:
        return False


def handle(text, mic, profile, logger, modules):
    """
        Responds to user-input, typically speech text, with a summary of
        the relevant weather for the requested date (typically, weather
        information will not be available for days beyond tomorrow).

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
        typical command:
        puść|odtwarzaj|graj|zagraj
            [mi|teraz|proszę|wszystkie płyty|płytę]
              zespołu|zespół|artystę|wykonawcę|płyty %ARTIST% $
                | album|płytę %ALBUM%
              muzykę dla dzieci
              losowo muzykę
              radio %RADIO%
              filmiki dla dzieci
              film %MOVIE%
              plik %FILE%
              serial %SHOW%
              zdjęcia|pokaz zdjęć losowo|%FOLDER%

    """
    global SERWERS
    SERWERS['DEFAULT'] = SERWERS[profile['xbmc_server'].upper()]
    ACTION_PLAY = ["PUŚĆ", "ODTWARZAJ", "GRAJ", "ZAGRAJ"]
    ACTION_PAUSE = ["WSTRZYMAJ", "ZATRZYMAJ"]
    CONTENT_ARTIST = ["ZESPÓŁ", "ARTYSTĘ", "ARTYSTKĘ", "WYKONAWCĘ", "PŁYTY"]
    CONTENT_SONG   = ["UTWÓR", "PIOSENKĘ", "PIOSENKE", "KAWAŁEK"]
    CONTENT_RADIO  = ["RADIO"]
    CONTENT_ALBUM  = ["ALBUM", "PŁYTĘ"]
    CONTENT_MOVIE  = ["FILM"]
    CONTENT_SHOW   = ["SERIAL", "ODCINEK"]

    init_play = False
    init_pause = False
    #phrases = text.decode('utf-8').upper().encode("utf-8").split(" ")
    phrases = app_utils.upperUTF8(text).split(" ")


    if app_utils.upperUTF8(text) == 'CO JEST GRANE':
      msg = get_currently_playing()
      if msg:
        mic.say(msg)
      return

    if app_utils.upperUTF8(text) == 'TRYB IMPREZY':
      msg = start_party_mode('music')
      if msg:
        mic.say('Napełniam szklaneczki')
      return

    #print " ".join(phrases)
    for a in ACTION_PLAY:
        if a in phrases:
            init_play = True
            break
    for a in ACTION_PAUSE:
        if a in phrases:
            init_pause = True
            break

    if (init_pause and init_play) or (not init_pause and not init_play):
        print("play %d pause %d" % (init_play, init_pause))
        mic.say("Wybacz, ale nie rozumiem polecenia, multimedialnego wstrzymaj lub uruchom")
        return
    
    content_type = None
    
    if init_pause or (init_play and len(phrases) == 1):
      pausePlayer()
      return
    
    shuffled = False
    if 'LOSOWO' in phrases:
      shuffled = True
    
    for c in CONTENT_ARTIST:
        if c in phrases:
            content_type = "ARTIST"
            index = phrases.index(c) + 1
            artist = " ".join(phrases[index:])
            break
    for c in CONTENT_ALBUM:
        if c in phrases:
            content_type = "ALBUM"
            index = phrases.index(c) + 1
            album = " ".join(phrases[index:])
            break
    for c in CONTENT_SONG:
        if c in phrases:
            content_type = "SONG"
            index = phrases.index(c) + 1
            song = " ".join(phrases[index:])
            break
    for c in CONTENT_RADIO:
        if c in phrases:
            content_type = "RADIO"
            index = phrases.index(c) + 1
            radio = " ".join(phrases[index:])
            break
    for c in CONTENT_ALBUM:
        if c in phrases:
            content_type = "ALBUM"
            index = phrases.index(c) + 1
            album = " ".join(phrases[index:])
            break
    for c in CONTENT_MOVIE:
        if c in phrases:
            content_type = "MOVIE"
            index = phrases.index(c) + 1
            movie = " ".join(phrases[index:])
            #print movie
            break
    for c in CONTENT_SHOW:
        if c in phrases:
            content_type = "SHOW"
            index = phrases.index(c) + 1
            show = " ".join(phrases[index:])
            break

    if not content_type:
        mic.say("Wybacz, ale nie rozumiem polecenia multimedialnego")
        return
    if content_type == "RADIO":
        res = play_radio(radio, mic)
        if not res:
            mic.say("Wybacz, ale nie znaleziono stacji radiowej o nazwie|~ %s" % radio)
    if content_type == "ARTIST":
        res = play_artist(artist, shuffled)
        if not res:
            mic.say("Wybacz, ale nie znaleziono artysty o nazwie|~ %s" % artist)
    if content_type == "ALBUM":
        res = play_album(album, shuffled)
        if not res:
            mic.say("Wybacz, ale nie znaleziono albumu o nazwie|~ %s" % album)
    if content_type == "SONG":
        res = play_songs(song, shuffled)
        if not res:
            mic.say("Wybacz, ale nie znaleziono utworu o nazwie|~ %s" % song)
    if content_type == "MOVIE":
        res = play_movies(movie, shuffled)
        if not res:
            mic.say("Wybacz, ale nie znaleziono filmu zatytułowanego|~ %s" % movie)
    if content_type == "SHOW":
        res = play_show(show, shuffled)
        if not res:
            mic.say("Wybacz, ale nie znaleziono serialu o nazwie|~ %s" % show)

def isValid(text):
    """
        Returns True if the text is related to the weather.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(puść|odtwarzaj|graj|zagraj|wstrzymaj|zatrzymaj|co jest grane|tryb imprezy)\b', text, re.IGNORECASE))


if __name__ == "__main__":
    m = Mic()
    #t = "odtwarzaj wykonawcę kult"
    t = "odtwarzaj film ralf demolka"
    handle(t, m, None, None)
    #get_albums_list_from_artist('metallica')

