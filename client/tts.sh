#!/bin/sh

wget -q --restrict-file-names=nocontrol --referer="http://translate.google.com" -U Mozilla -O say.mp3 "http://translate.google.com/translate_tts?ie=UTF-8&tl=pl&q=$1" && avconv -y -v quiet -i say.mp3 -f wav say.wav
