# -*- coding: utf-8 -*-
# a może teraz?
import datetime
import base64
import json
import urllib2
import re

WORDS = ["PUŚĆ", "ODTWARZAJ", "GRAJ", "ZAGRAJ", "WSTRZYMAJ", "ZATRZYMAJ"]

HOST = "192.168.1.100"
PORT = 80
USERNAME = 'xbmc'
PASSWORD = '1'
PLAY_MSG   = '{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 0 }, "id": 1}'
CLEAR_MSG  = '{"jsonrpc": "2.0", "method": "Playlist.Clear",   "params": {"playlistid":1}, "id": 1}'
ADD_MSG    = '{"jsonrpc": "2.0", "method": "Playlist.Add",     "params": {"playlistid":1, %s}, "id" : 1}'
ALBUM_ITEM = '"item" :{ "albumid" : %d}'
OPEN_MSG   = '{"jsonrpc": "2.0", "method": "Player.Open",      "params": {"item":{"playlistid":1, "position" : 0}}, "id": 1}'
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
        print msg

def get_albums_list_from_artist(artist):
    msg = GET_ALBUMS_FROM_ARTIST % artist
    res = json.loads(send_json(msg))
    albums_list = []
    if res.has_key('result'):
      for album in res['result']['albums']:
          print album['title'], album['year']
          albums_list.append(ALBUM_ITEM % album['albumid'])
      return albums_list
    elif res.has_key('error'):
        print("no albums found: %s" % res['error'] )
        return None

def play_albums(albums_list):
      send_json(CLEAR_MSG)
      msg = ADD_MSG % ','.join(albums_list)
      print send_json(msg)
      print send_json(OPEN_MSG)

def play_artist(artist):
    list = get_albums_list_from_artist(artist)
    if list:
        play_albums(list)


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
              zespołu|zespół|artystę|wykonawcę|płytę %ARTIST% $
                | album|płytę %ALBUM%
              muzykę dla dzieci
              losowę muzykę
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

    print " ".join(phrases)
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
            break
    for c in CONTENT_MOVIE:
        if c in phrases:
            content_type = "SHOW"
            index = phrases.index(c) + 1
            show = " ".join(phrases[index:])
            break
    if not content_type:
        mic.say("Wybacz, ale nie rozumiem polecenia")
        return
    if content_type == "MUSIC":
        print(artist)
        play_artist(artist)

def isValid(text):
    """
        Returns True if the text is related to the weather.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(puść|odtwarzaj|graj|zagraj|wstrzymaj|zatrzymaj)\b', text, re.IGNORECASE))


if __name__ == "__main__":
    m = Mic()
    t = "odtwarzaj wykonawcę kult"
    handle(t, m, None, None)
    #get_albums_list_from_artist('metallica')

