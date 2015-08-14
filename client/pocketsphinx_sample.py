from os import environ, path
from itertools import izip
import sys

try:
  from pocketsphinx import *
except:
  from pocketsphinx import *

from sphinxbase import *

MODELDIR = "/usr/local/share/pocketsphinx/model"
DATADIR = "model"

# Create a decoder with certain model
#config = Decoder.default_config()
#config.set_string('-hmm', path.join(MODELDIR, 'hmm/en_US/hub4wsj_sc_8k'))
#config.set_string('-lm', path.join(MODELDIR, 'lm/en_US/hub4.5000.DMP'))
#config.set_string('-dict', path.join(MODELDIR, 'lm/en_US/hub4.5000.dic'))
#decoder = Decoder(config)
decoder = Decoder(hmm='/usr/local/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k', lm='languagemodel.lm', dict='dictionary.dic')

if len(sys.argv) > 2:
  fname = sys.argv[1]
else:
  fname = 'active.wav'

# Decode static file.
f = file(fname , 'rb')
f.seek(44)

decoder.decode_raw(f)

# Retrieve hypothesis.
hypothesis = decoder.get_hyp()
#print 'Best hypothesis: ', hypothesis.best_score, hypothesis.hypstr
print 'Best hypothesis: ', repr(hypothesis)
print 'Best decoder: ', repr(decoder)

exit()


print 'Best hypothesis segments: ', [seg.word for seg in decoder.get_seg()]

# Access N best decodings.
print 'Best 10 hypothesis: '
for best, i in izip(decoder.nbest(), range(10)):
    print best.hyp().best_score, best.hyp().hypstr




# Decode streaming data.
decoder = Decoder(config)
decoder.start_utt('goforward')
stream = open(path.join(DATADIR, 'goforward.raw'), 'rb')
while True:
    buf = stream.read(1024)
    if buf:
        decoder.process_raw(buf, False, False)
    else:
        break
decoder.end_utt()
print 'Stream decoding result:', decoder.hyp().hypstr
