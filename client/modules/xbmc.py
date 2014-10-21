# -*- coding: utf-8 -*-
# a może teraz?
import datetime
import base64
import json
import urllib2
import re

WORDS = ["PUŚĆ", "ODTWARZAJ", "GRAJ", "ZAGRAJ", "WSTRZYMAJ", "ZATRZYMAJ"]
HELP  = {"name": "xbmc",
         "description": "XBMC służy do sterowania odtwarzeniem muzyki, filmów, seriali oraz zdjęć.",
         "samples": ["zagraj zespół kult", "odtwazaj film gwiezdne wojny", "włacz radio ram"],
         "topics": {"muzyka": "powiedz odtwarzaj lub gra lub zagraj lub puść,|"+
                               "następnie zespół lub zespołu lub artystę lub wykonawcę lub płyty,|" +
                               "a następnie właściwą nazwę wykonawcy.|"+
                               "Kommenda ta, doda do kolejki odtwarzania wszystkie albumy wykonawcy.",
                     "film":   "powiedz odtwarzaj lub graj lub zagraj lub puść,| "+
                               "następnie film, " +
                               "a następnie polski tytuł filmu.|"+
                               "Jeżeli wyszukiwanie zwróci więcej niż jeden wynik,|"+
                               "to wszystkie filmy zostaną dodane do kolejki.|"+
                               "Nie trzeba wypowiadać pełnej nazwy filmu,| "+
                               "wystarczy użyć unikalnego słowa lub frazy",
                    "uwagi ogólne": "jeżeli nie udaje się prawidłowo rozpoznać nazwy artysty lub filmu,|"+
                                    "nazwę można przeliterować."
                    }
          }

HOST = "192.168.1.100"
PORT = 80
USERNAME = 'xbmc'
PASSWORD = '1'

AUDIO_PLAYER = 0
MOVIE_PLAYER = 1
PHOTO_PLAYER = 2

#PLAY_MSG   = '{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": %d}, "id": 1}'
CLEAR_MSG        = '{"jsonrpc": "2.0", "method": "Playlist.Clear",   "params": {"playlistid": %d}, "id": 1}'
ADD_ALBUM_MSG    = '{"jsonrpc": "2.0", "method": "Playlist.Add",     "params": {"playlistid": %d, "item": { "albumid" : %d}}, "id" : 1}'
ADD_MOVIE_MSG    = '{"jsonrpc": "2.0", "method": "Playlist.Add",     "params": {"playlistid": %d, "item": { "movieid" : %d}}, "id" : 1}'
GET_PLAYLIST     = """{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "Playlist.GetItems",
  "params": {
    "playlistid": %d
  }
}"""

OPEN_MSG   = '{"jsonrpc": "2.0", "method": "Player.Open",      "params": {"item":{"playlistid": %d, "position" : 0}}, "id": 1}'
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
      "description",
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
def send_json(msg):
    url = "http://%s:%d/jsonrpc" % (HOST, PORT)
    req = urllib2.Request(url, msg);
    #req.add_header('Authorization', 'Basic eGJtYzox');
    req.add_header('Authorization', b'Basic ' + base64.b64encode(USERNAME + b':' + PASSWORD))
    req.add_header('Content-type', 'application/json');
    res = None
    try:
      res = urllib2.urlopen(req, timeout=2).read();
    except Exception, e:
      res = '{ "error": "%s"}' % repr(e).replace('"', '')
    return res
    #print res

class Mic:
    def say(self, msg):
        print "say:", msg

def get_albums_list_from_artist(artist):
    msg = GET_ALBUMS_FROM_ARTIST % artist
    res = json.loads(send_json(msg))
    albums_list = []
    if res.has_key('result'):
      for album in res['result']['albums']:
          #print album['title'], album['year'], album['albumid']
          el = album['albumid']
          if el not in albums_list:
              #print "add"
              albums_list.append(el)


      return albums_list
    elif res.has_key('error'):
        print("no albums found: %s" % res['error'] )
        return None

def get_move_by_name(movie):
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

def play_movies(movie):
      movies_list = get_move_by_name(movie)
      if movies_list:
          send_json(CLEAR_MSG % MOVIE_PLAYER)
          for el in movies_list:
             send_json(ADD_MOVIE_MSG % (MOVIE_PLAYER, el))
          #print send_json(GET_PLAYLIST % MOVIE_PLAYER)
          send_json(OPEN_MSG % MOVIE_PLAYER)
          return True
      else:
          return False

def play_albums(albums_list):
      send_json(CLEAR_MSG % AUDIO_PLAYER)
      for el in albums_list:
         send_json(ADD_ALBUM_MSG % (AUDIO_PLAYER, el))
      #print send_json(GET_PLAYLIST % AUDIO_PLAYER)
      send_json(OPEN_MSG % AUDIO_PLAYER)

def play_artist(artist):
    list = get_albums_list_from_artist(artist)
    if list:
        play_albums(list)
        return True
    else:
        return False


def handle(text, mic, profile, logger):
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
    ACTION_PLAY = ["PUŚĆ", "ODTWARZAJ", "GRAJ", "ZAGRAJ"]
    ACTION_PAUSE = ["WSTRZYMAJ", "ZATRZYMAJ"]
    CONTENT_ARTIST = ["ZESPÓŁ", "ARTYSTĘ", "ARTYSTKĘ", "WYKONAWCĘ", "PŁYTY"]
    CONTENT_ALBUM = ["ALBUM", "PŁYTĘ"]
    CONTENT_MOVIE = ["FILM"]
    CONTENT_SHOW = ["SERIAL", "ODCINEK"]

    init_play = False
    init_pause = False
    phrases = text.decode('utf-8').upper().encode("utf-8").split(" ")

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
        mic.say("Wybacz, ale nie rozumiem polecenia")
        return

    content_type = None
    for c in CONTENT_ARTIST:
        if c in phrases:
            content_type = "MUSIC"
            index = phrases.index(c) + 1
            artist = " ".join(phrases[index:])
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
        mic.say("Wybacz, ale nie rozumiem polecenia")
        return
    if content_type == "MUSIC":
        res = play_artist(artist)
        if not res:
            mic.say("Wybacz, ale nie znaleziono artysty o nazwie %s" % artist)

    if content_type == "MOVIE":
        res = play_movies(movie)
        if not res:
            mic.say("Wybacz, ale nie znaleziono filmu o nazwie %s" % movie)

def isValid(text):
    """
        Returns True if the text is related to the weather.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(puść|odtwarzaj|graj|zagraj|wstrzymaj|zatrzymaj)\b', text, re.IGNORECASE))


if __name__ == "__main__":
    m = Mic()
    #t = "odtwarzaj wykonawcę kult"
    t = "odtwarzaj film ralf demolka"
    handle(t, m, None, None)
    #get_albums_list_from_artist('metallica')

