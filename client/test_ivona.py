import pyvona
import sys

filename = "test_ivona.mp3"

ivona = pyvona.Voice('GDNAJCB7IGSUWGJE5EWQ', 'tLd1c3R1+3YbXscd6ILnuamY87uTycP2ngeer0S/')
ivona.codec          = "mp3"
ivona.region         = 'eu-west'
ivona.voice_name     = 'Maja'
ivona.language       = 'pl-PL'
ivona.speech_rate    = 'medium'
ivona.sentence_break = 400
#res = ivona.list_voices()

#print res
ivona.fetch_voice(sys.argv[1], filename)
#ivona.speak(args[1])
#os.system("aplay -D %s %s" % ("plughw:1,0", filename))
#os.system("mpg123 -q --audiodevice= %s %s" % ("plughw:1,0", filename))
