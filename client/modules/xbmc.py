# -*- coding: utf-8 -*-
# a może teraz?
import datetime
import base64
import json
import urllib2

HOST = "192.168.1.100"
PORT = 80
USERNAME = 'xbmc'
PASSWORD = '1'
PLAY_MSG   = '{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 0 }, "id": 1}'
CLEAR_MSG  = '{"jsonrpc": "2.0", "method": "Playlist.Clear",   "params": {"playlistid":1}, "id": 1}'
ADD_MSG    = '{"jsonrpc": "2.0", "method": "Playlist.Add",     "params": {"playlistid":1, %s}, "id" : 1}'
ALBUM_ITEM = '"item" :{ "albumid" : %d}'
"""{
  "jsonrpc": "2.0",
  "method": "Playlist.Add",
  "params": {
    "playlistid": 1,
    "item": {
      "albumid": 394
    },
    "item": {
      "albumid": 2494
    }
    
  },
  "id": 1
}
"""
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
    except:
      res = ""
    return res
    #print res

def get_albums_list_from_artist(artist):
    msg = GET_ALBUMS_FROM_ARTIST % artist
    res = json.loads(send_json(msg))
    print res
    if res.has_key('result'):
      send_json(CLEAR_MSG)
      albums_list = []
      for album in res['result']['albums']:
        albums_list.append(ALBUM_ITEM % album['albumid'])
      msg = ADD_MSG % ','.join(albums_list)
      print msg
      print send_json(msg)
      print send_json(OPEN_MSG)
    elif res.has_key('error'):
      print "no albums found: %s" % res['error']


print get_albums_list_from_artist('metallica')

